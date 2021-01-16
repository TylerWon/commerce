from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Bid, Listing, Comment
from .forms import CreateListingForm

# EFFECTS: renders page which displays all of the currently active auction listings
def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True)
    })

# EFFECTS: if request is POST, check if a User can be found with the username/password entered
#               1. if authentication successful, log the user in and redirect them to default page
#               2. otherwise, reload the same page and notify user log in credentials are invalid
#          otherwise, render log in page for first time viewing
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

# EFFECTS: logs the user out and renders the default page
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# EFFECTS: if request is POST, ensure password matches confirmation then attempt to create a new user
#               1. if new user can be created, log the user in and redirect them to default page
#               2. otherwise, reload same page and notify user that username is already taken
#          otherwise, render register page for first time viewing
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# EFFECTS: if request is POST, load data into CreateListingForm
#               1. if form is valid, create a new Listing, add it the the database, and redirect to new listing
#               2. otherwise, reload the same page and notify user that form data was invalid
#          otherwise, render create listing page for first time viewing
def createListing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)

        if form.is_valid():
            listing = form.save(commit=False)
            listing.lister = request.user
            listing.save()
            form.save_m2m()

            # TODO: redirect to new listing
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/createListing.html", {
                "form": form
            })
    else:
        return render(request, "auctions/createListing.html", {
            "form": CreateListingForm()
        })
