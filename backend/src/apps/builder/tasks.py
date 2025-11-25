import io
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Optional

import requests
from celery import shared_task
from django.conf import settings
from loguru import logger

from apps.builder.models import LeadRegistration
from apps.properties.models import Property


def create_deployment_bundle(build_output: Path) -> io.BytesIO:
    """
    Create a zip file from the build output directory.
    
    Args:
        build_output: Path to the dist/build directory
        
    Returns:
        BytesIO object containing the zipped files
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in build_output.rglob('*'):
            if file_path.is_file():
                # Get relative path from build_output
                arcname = file_path.relative_to(build_output)
                zip_file.write(file_path, arcname)
    
    zip_buffer.seek(0)
    return zip_buffer


def check_project_exists(project_name: str, base_url: str, headers: dict) -> bool:
    """Check if a Cloudflare Pages project exists."""
    try:
        response = requests.get(f"{base_url}/{project_name}", headers=headers)
        return response.status_code == 200
    except requests.HTTPError:
        return False


def create_project(project_name: str, base_url: str, headers: dict) -> dict:
    """
    Create a new Cloudflare Pages project.
    
    Args:
        project_name: Name for the new project
        base_url: Base API URL
        headers: Request headers with authorization
        
    Returns:
        dict: Created project information
    """
    payload = {
        "name": project_name,
        "production_branch": "main",
        "build_config": {
            "build_command": "",  # Already built
            "destination_dir": "",
            "root_dir": ""
        }
    }
    
    response = requests.post(base_url, headers=headers, json=payload)
    response.raise_for_status()
    
    return response.json().get('result', {})


def configure_custom_domain(
    project_name: str,
    domain: str,
    base_url: str,
    headers: dict
) -> dict:
    """
    Add a custom domain to the Cloudflare Pages project.
    
    Args:
        project_name: Name of the project
        domain: Custom domain to add (e.g., "example.com")
        base_url: Base API URL
        headers: Request headers
        
    Returns:
        dict: Domain configuration result
    """
    domain_url = f"{base_url}/{project_name}/domains"
    
    payload = {
        "name": domain
    }
    
    try:
        response = requests.post(domain_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json().get('result', {})
        logger.info(f"Custom domain configured: {domain}")
        
        # Log DNS instructions if needed
        if result.get('verification_record'):
            logger.info(f"DNS verification required: {result['verification_record']}")
        
        return result
    except requests.HTTPError as e:
        logger.error(f"Failed to configure custom domain: {e}")
        # Don't fail the entire deployment if domain config fails
        return {}


def deploy_to_cloudflare_pages(
    project_name: str,
    build_output: Path,
    domain: Optional[str] = None,
    branch: str = "main"
) -> dict:
    """
    Deploy to Cloudflare Pages using Direct Upload API.
    
    Args:
        project_name: Name of the Cloudflare Pages project (will be created if doesn't exist)
        build_output: Path to the build output directory (e.g., dist/)
        domain: Optional custom domain to configure
        branch: Git branch name (default: "main")
        
    Returns:
        dict: Deployment information including URL
        
    Raises:
        requests.HTTPError: If API requests fail
    """
    account_id = settings.CLOUDFLARE_ACCOUNT_ID
    api_token = settings.CLOUDFLARE_API_TOKEN
    
    if not account_id or not api_token:
        raise ValueError("CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN must be set")
    
    base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects"
    headers = {
        "Authorization": f"Bearer {api_token}",
    }
    
    # Step 1: Ensure project exists (create if it doesn't)
    project_exists = check_project_exists(project_name, base_url, headers)
    
    if not project_exists:
        logger.info(f"Creating new Cloudflare Pages project: {project_name}")
        create_project(project_name, base_url, headers)
    
    # Step 2: Create deployment bundle
    logger.info(f"Creating deployment bundle from {build_output}")
    zip_bundle = create_deployment_bundle(build_output)
    
    # Step 3: Upload deployment using Direct Upload
    logger.info(f"Uploading deployment to Cloudflare Pages")
    deployment_url = f"{base_url}/{project_name}/deployments"
    
    files = {
        'file': ('deployment.zip', zip_bundle, 'application/zip')
    }
    
    # Optional: Add deployment metadata
    data = {
        'branch': branch,
    }
    
    response = requests.post(
        deployment_url,
        headers=headers,
        files=files,
        data=data,
        timeout=300  # 5 minute timeout for large uploads
    )
    response.raise_for_status()
    
    deployment_info = response.json()
    result = deployment_info.get('result', {})
    
    logger.info(f"Deployment successful: {result.get('url')}")
    
    # Step 4: Configure custom domain if provided
    if domain:
        logger.info(f"Configuring custom domain: {domain}")
        configure_custom_domain(project_name, domain, base_url, headers)
    
    return {
        'deployment_id': result.get('id'),
        'url': result.get('url'),
        'deployment_url': result.get('deployment_trigger_metadata', {}).get('url'),
        'project_name': project_name,
        'custom_domain': domain,
    }


def get_deployment_status(project_name: str, deployment_id: str) -> dict:
    """
    Get the status of a deployment.
    
    Args:
        project_name: Name of the project
        deployment_id: ID of the deployment
        
    Returns:
        dict: Deployment status information
    """
    account_id = settings.CLOUDFLARE_ACCOUNT_ID
    api_token = settings.CLOUDFLARE_API_TOKEN
    
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/{project_name}/deployments/{deployment_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json().get('result', {})


def export_property_to_theme(property_obj: Property, lead: LeadRegistration) -> Path:
    """
    Export property data as JSON for Astro to consume.
    
    Args:
        property_obj: Property instance to export
        lead: LeadRegistration instance
        
    Returns:
        Path to the created JSON file
    """
    # Get the theme directory path
    # Assuming themes are in /app/../themes/theme-mountain
    theme_path = Path("/app").parent / "themes" / "theme-mountain"
    data_path = theme_path / "src" / "data"
    data_path.mkdir(parents=True, exist_ok=True)
    
    # Serialize property data
    property_data = {
        "id": str(property_obj.id),
        "title": property_obj.title,
        "description": property_obj.description,
        "room_type": property_obj.room_type,
        "person_capacity": property_obj.person_capacity,
        "is_super_host": property_obj.is_super_host,
        "is_guest_favorite": property_obj.is_guest_favorite,
        "language": property_obj.language,
        
        # Images
        "images": [
            {
                "url": img.image.url if img.image else img.url,
                "title": img.title,
            }
            for img in property_obj.images.all()
        ],
        
        # Rating
        "rating": {
            "accuracy": property_obj.rating.accuracy,
            "checking": property_obj.rating.checking,
            "cleanliness": property_obj.rating.cleanliness,
            "communication": property_obj.rating.communication,
            "location": property_obj.rating.location,
            "value": property_obj.rating.value,
            "guest_satisfaction": property_obj.rating.guest_satisfaction,
            "review_count": property_obj.rating.review_count,
        } if hasattr(property_obj, 'rating') else None,
        
        # Coordinates
        "coordinates": {
            "latitude": property_obj.coordinates.latitude,
            "longitude": property_obj.coordinates.longitude,
        } if hasattr(property_obj, 'coordinates') else None,
        
        # Host
        "host": {
            "name": property_obj.host.name,
            "host_id": property_obj.host.host_id,
        } if hasattr(property_obj, 'host') else None,
        
        # Amenities
        "amenities": [
            {
                "title": amenity.title,
                "values": [
                    {
                        "title": val.title,
                        "subtitle": val.subtitle,
                        "icon": val.icon,
                        "available": val.available,
                    }
                    for val in amenity.values.all()
                ]
            }
            for amenity in property_obj.amenities.all()
        ],
        
        # Highlights
        "highlights": [
            {
                "title": highlight.title,
                "subtitle": highlight.subtitle,
                "icon": highlight.icon,
            }
            for highlight in property_obj.highlights.all()
        ],
        
        # Location descriptions
        "location_descriptions": [
            {
                "title": loc.title,
                "content": loc.content,
            }
            for loc in property_obj.location_descriptions.all()
        ],
        
        # Lead/Theme info
        "lead": {
            "domain": lead.domain_name,
            "theme": lead.theme.name if lead.theme else None,
            "color_scheme": lead.color_scheme.name if lead.color_scheme else None,
            "email": lead.email,
            "phone": str(lead.phone_number) if lead.phone_number else None,
        }
    }
    
    # Write to JSON file
    output_file = data_path / f"property-{lead.id}.json"
    with open(output_file, 'w') as f:
        json.dump(property_data, f, indent=2, default=str)
    
    logger.info(f"Exported property data to {output_file}")
    return output_file


@shared_task(bind=True, max_retries=3)
def build_and_deploy_site(self, property_id: int, lead_id: str):
    """
    Build Astro site and deploy to Cloudflare Pages.
    
    Args:
        property_id: ID of the property to deploy
        lead_id: UUID of the lead registration (as string)
    """
    try:
        # Get property and lead
        property_obj = Property.objects.get(id=property_id)
        lead = LeadRegistration.objects.get(id=lead_id)
        
        logger.info(f"Building site for property {property_id}, lead {lead_id}")
        
        # Step 1: Export property data to theme
        export_property_to_theme(property_obj, lead)
        
        # Step 2: Build Astro site
        theme_path = Path("/app").parent / "themes" / "theme-mountain"
        
        if not theme_path.exists():
            raise FileNotFoundError(f"Theme directory not found: {theme_path}")
        
        logger.info(f"Building Astro site at {theme_path}")
        result = subprocess.run(
            ["bun", "run", "build"],
            cwd=theme_path,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Build output: {result.stdout}")
        
        # Step 3: Deploy to Cloudflare Pages
        project_name = f"property-{lead.id}"
        build_output = theme_path / "dist"
        
        if not build_output.exists():
            raise FileNotFoundError(f"Build output not found: {build_output}")
        
        logger.info(f"Deploying to Cloudflare Pages: {project_name}")
        deployment_info = deploy_to_cloudflare_pages(
            project_name=project_name,
            build_output=build_output,
            domain=lead.domain_name if lead.domain_name else None
        )
        
        logger.info(f"Deployment complete: {deployment_info['url']}")
        
        # Step 4: Update lead with deployment info
        lead.extra_requirements = lead.extra_requirements or {}
        lead.extra_requirements['deployment_url'] = deployment_info['url']
        lead.extra_requirements['cloudflare_project'] = project_name
        lead.extra_requirements['deployment_id'] = deployment_info['deployment_id']
        lead.save(update_fields=['extra_requirements'])
        
        return {
            'success': True,
            'property_id': property_id,
            'lead_id': str(lead_id),
            'deployment_info': deployment_info
        }
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Build failed: {e.stderr}")
        raise self.retry(exc=e, countdown=120)
    except Exception as exc:
        logger.error(f"Deployment failed: {exc}")
        raise self.retry(exc=exc, countdown=120)
