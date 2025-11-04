from urllib.parse import urlparse


def get_domain(url):
    """
    Extracts the domain from a given URL.
    """
    if not url:
        return ""
    return urlparse(url).netloc
