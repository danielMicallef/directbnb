from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib import messages
from django.db import transaction

from .models import Property, Coordinates, Rating, HouseRules, Host, SubDescription
from .forms import (
    PropertyForm,
    CoordinatesForm,
    RatingForm,
    HouseRulesForm,
    HostForm,
    SubDescriptionForm,
    ImageFormSet,
    LocationDescriptionFormSet,
    HighlightFormSet,
)


class PropertyListView(LoginRequiredMixin, ListView):
    """List all properties for the logged-in user"""

    model = Property
    template_name = "properties/property_list.html"
    context_object_name = "properties"
    paginate_by = 10

    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user).select_related(
            "coordinates", "rating"
        )


class PropertyDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View details of a specific property"""

    model = Property
    template_name = "properties/property_detail.html"
    context_object_name = "property"

    def test_func(self):
        property_obj = self.get_object()
        return property_obj.owner == self.request.user

    def get_queryset(self):
        return Property.objects.select_related(
            "coordinates",
            "rating",
            "house_rules",
            "host",
            "sub_description",
        ).prefetch_related(
            "amenities",
            "amenities__values",
            "images",
            "location_descriptions",
            "highlights",
            "co_hosts",
        )


class PropertyUpdateView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Update property information by sections"""

    model = Property
    template_name = "properties/property_update.html"
    context_object_name = "property"

    def test_func(self):
        property_obj = self.get_object()
        return property_obj.owner == self.request.user

    def get_queryset(self):
        return Property.objects.select_related(
            "coordinates",
            "rating",
            "house_rules",
            "host",
            "sub_description",
        ).prefetch_related(
            "images",
            "location_descriptions",
            "highlights",
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        section = request.POST.get("section")

        try:
            with transaction.atomic():
                if section == "basic":
                    # Update basic property information
                    self.object.title = request.POST.get("title", "")
                    self.object.description = request.POST.get("description", "")
                    self.object.room_type = request.POST.get("room_type", "")
                    person_capacity = request.POST.get("person_capacity", "")
                    self.object.person_capacity = (
                        int(person_capacity) if person_capacity else None
                    )
                    self.object.save()
                    messages.success(request, "Basic information updated successfully!")

                elif section == "location":
                    # Update or create coordinates
                    latitude = request.POST.get("coordinates-latitude")
                    longitude = request.POST.get("coordinates-longitude")

                    if latitude and longitude:
                        coords, created = Coordinates.objects.update_or_create(
                            property=self.object,
                            defaults={
                                "latitude": float(latitude),
                                "longitude": float(longitude),
                            },
                        )
                        messages.success(request, "Location updated successfully!")
                    else:
                        messages.error(
                            request, "Please provide both latitude and longitude."
                        )
                        return redirect(request.path)

                elif section == "house-rules":
                    # Update or create house rules
                    additional = request.POST.get("house_rules-additional", "")
                    HouseRules.objects.update_or_create(
                        property=self.object,
                        defaults={"additional": additional},
                    )
                    messages.success(request, "House rules updated successfully!")

                elif section == "host":
                    # Update or create host information
                    name = request.POST.get("host-name", "")
                    host_id = request.POST.get("host-host_id", "")
                    Host.objects.update_or_create(
                        property=self.object,
                        defaults={"name": name, "host_id": host_id},
                    )
                    messages.success(request, "Host information updated successfully!")

                else:
                    messages.error(request, f"Unknown section: {section}")

        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error updating property: {str(e)}")

        return redirect(request.path)
