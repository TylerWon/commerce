from django import forms
from django.core.validators import MinValueValidator
from django.forms import ModelForm, Textarea
from django.utils.translation import ugettext_lazy as _

from .models import User, Category, Bid, Listing, Comment

# Represents a form which the user can use to create a new listing
class CreateListingForm(ModelForm):
    startingBid = forms.DecimalField(initial="00.00")
    
    class Meta:
        model = Listing
        exclude = ["active", "lister", "interestedUsers", "date"]
        widgets = {
            "description": Textarea(attrs={
                "class": "form-control col-lg-6 col-md-4"
            })
        }
        error_messages = {
            "title": {
                "max_length": _("The title is too long.")
            },
        }