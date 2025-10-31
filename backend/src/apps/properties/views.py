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


class PropertyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update property basic information"""

    model = Property
    form_class = PropertyForm
    template_name = "properties/property_update.html"
    success_url = reverse_lazy("properties:property-list")

    def test_func(self):
        property_obj = self.get_object()
        return property_obj.owner == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        property_obj = self.object

        if self.request.POST:
            context["coordinates_form"] = CoordinatesForm(
                self.request.POST,
                instance=getattr(property_obj, "coordinates", None),
            )
            context["rating_form"] = RatingForm(
                self.request.POST,
                instance=getattr(property_obj, "rating", None),
            )
            context["house_rules_form"] = HouseRulesForm(
                self.request.POST,
                instance=getattr(property_obj, "house_rules", None),
            )
            context["host_form"] = HostForm(
                self.request.POST,
                instance=getattr(property_obj, "host", None),
            )
            context["sub_description_form"] = SubDescriptionForm(
                self.request.POST,
                instance=getattr(property_obj, "sub_description", None),
            )
            context["image_formset"] = ImageFormSet(
                self.request.POST,
                instance=property_obj,
            )
            context["location_formset"] = LocationDescriptionFormSet(
                self.request.POST,
                instance=property_obj,
            )
            context["highlight_formset"] = HighlightFormSet(
                self.request.POST,
                instance=property_obj,
            )
        else:
            context["coordinates_form"] = CoordinatesForm(
                instance=getattr(property_obj, "coordinates", None)
            )
            context["rating_form"] = RatingForm(
                instance=getattr(property_obj, "rating", None)
            )
            context["house_rules_form"] = HouseRulesForm(
                instance=getattr(property_obj, "house_rules", None)
            )
            context["host_form"] = HostForm(
                instance=getattr(property_obj, "host", None)
            )
            context["sub_description_form"] = SubDescriptionForm(
                instance=getattr(property_obj, "sub_description", None)
            )
            context["image_formset"] = ImageFormSet(instance=property_obj)
            context["location_formset"] = LocationDescriptionFormSet(instance=property_obj)
            context["highlight_formset"] = HighlightFormSet(instance=property_obj)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        coordinates_form = context["coordinates_form"]
        rating_form = context["rating_form"]
        house_rules_form = context["house_rules_form"]
        host_form = context["host_form"]
        sub_description_form = context["sub_description_form"]
        image_formset = context["image_formset"]
        location_formset = context["location_formset"]
        highlight_formset = context["highlight_formset"]

        # Validate all forms
        all_valid = all(
            [
                form.is_valid(),
                coordinates_form.is_valid(),
                rating_form.is_valid(),
                house_rules_form.is_valid(),
                host_form.is_valid(),
                sub_description_form.is_valid(),
                image_formset.is_valid(),
                location_formset.is_valid(),
                highlight_formset.is_valid(),
            ]
        )

        if all_valid:
            with transaction.atomic():
                # Save main property
                self.object = form.save()

                # Save related models
                coordinates = coordinates_form.save(commit=False)
                coordinates.property = self.object
                coordinates.save()

                rating = rating_form.save(commit=False)
                rating.property = self.object
                rating.save()

                house_rules = house_rules_form.save(commit=False)
                house_rules.property = self.object
                house_rules.save()

                host = host_form.save(commit=False)
                host.property = self.object
                host.save()

                sub_description = sub_description_form.save(commit=False)
                sub_description.property = self.object
                sub_description.save()

                # Save formsets
                image_formset.instance = self.object
                image_formset.save()

                location_formset.instance = self.object
                location_formset.save()

                highlight_formset.instance = self.object
                highlight_formset.save()

            messages.success(self.request, "Property updated successfully!")
            return redirect(self.success_url)
        else:
            messages.error(self.request, "Please correct the errors below.")
            return self.form_invalid(form)
