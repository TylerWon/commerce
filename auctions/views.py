from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Bid, Listing, Comment
from .forms import CreateListingForm, BidForm, CommentForm

# EFFECTS: render page that displays all of the currently active auction listings
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
@login_required
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
@login_required
def createListing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)

        if form.is_valid():
            listing = form.save(commit=False)
            listing.lister = request.user
            listing.save()
            form.save_m2m()

            listingId = listing.id
            return HttpResponseRedirect(reverse("listing", args=[listingId]))
        else:
            return render(request, "auctions/createListing.html", {
                "form": form
            })
    else:
        return render(request, "auctions/createListing.html", {
            "form": CreateListingForm()
        })

# EFFECTS: render page that displays all of the categories
def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })

# EFFECTS: render page that displays all active auction listings for category
def category(request, category):
    categoryObj = Category.objects.get(title=category)
    listings = categoryObj.listings.all().filter(active=True)

    return render(request, "auctions/index.html", {
        "category": category,
        "listings": listings
    })

# EFFECTS: render page that displays the details of the listing that has id = id
def listing(request, listingId):
    return render(request, "auctions/listing.html", {
        "listing": Listing.objects.get(id=listingId),
        "bidform": BidForm(),
        "inWatchlist": inWatchlist(request, listingId),
        "commentform": CommentForm()
    })

# EFFECTS: render page that displays a user's listings
def userListings(request, username):
    user = User.objects.get(username=username)

    return render(request, "auctions/userListings.html", {
        "username": user.username,
        "activeListings": user.listings.all().filter(active=True),
        "previousListings": user.listings.all().filter(active=False)
    })

# EFFECTS: if request is POST, load data into BidForm
#               1. if form is valid, create a new Bid, add it to the database, and redirect to listing bid was made on
#               2. otherwise, reload the same page and notify user that form data was invalid
@login_required
def bid(request, listingId):
    if request.method == "POST":
        form = BidForm(request.POST)

        if form.is_valid():
            bid = form.save(commit=False)
            bid.bidder = request.user
            bid.listing = Listing.objects.get(id=listingId)
            bid.save()

            return HttpResponseRedirect(reverse("listing", args=[listingId]))
        else:
            return render(request, "auctions/listing.html", {
                "listing": Listing.objects.get(id=listingId),
                "form": form
            })

# EFFECTS: render page that displays the items in the user's watchlist
@login_required
def watchlist(request, username):
    return render(request, "auctions/watchlist.html", {
        "watchlist": User.objects.get(username=username).watchlist.all()
    })

# EFFECTS: if request is POST:
#               1. if POST data contains "add", then add listing to user's watchlist
#               2. otherwise, remove listing from user's watchlist
#          redirect to listing and display notification that item was either added/removed to user's watchlist
@login_required
def alterWatchlist(request, username):
    if request.method == "POST":
        user = request.user
        listingId = int(request.POST["listingId"])
        listing = Listing.objects.get(id=listingId)

        try:
            request.POST["add"]
            user.watchlist.add(listing)

            msg = f"Listing: '{ listing.title }' was added to your watchlist."
        except:
            user.watchlist.remove(listing)

            msg = f"Listing: '{ listing.title }' was removed from your watchlist."
            
        messages.info(request, msg) 
        return HttpResponseRedirect(reverse("listing", args=[listingId]))

# EFFECTS: closes a listing by setting the listing to inactive and making the highest bidder the winner (if there is a bidder)
@login_required
def closeListing(request, listingId):
    listing = Listing.objects.get(id=listingId)
    listing.active = False # might need to save?

    print(listing.active)

    if listing.bids.all().count() == 0:
        msg = f"Listing: '{ listing.title }' was closed."
    else:
        winner = listing.bids.all().last().bidder
        listing.winner = winner
        
        msg = f"Listing: '{ listing.title }' was sold to '{ winner.username }'." 
    
    listing.save()
    messages.info(request, msg)
    return HttpResponseRedirect(reverse("listing", args=[listingId]))

# EFFECTS: if request is POST, load data into CommentForm
#               1. if form is valid, create a new comment, add it to the database, and display notification that comment was added
#               2. otherwise, reload the same page and notify the user that form data was invalid                 
@login_required
def comment(request, listingId):
    if request.method == "POST":
        form = CommentForm(request.POST)
        listing = Listing.objects.get(id=listingId)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.commenter = request.user
            comment.listing = listing
            comment.save()

            messages.info(request, "Added comment")
            
            return HttpResponseRedirect(reverse("listing", args=[listingId]))            
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bidform": BidForm(),
                "inWatchlist": inWatchlist(request, listingId),
                "commentform": form
            })

# EFFECTS: if method is POST:
#               - remove comment from listing with id = listingId
#               - notify user that comment was removed
@login_required
def deletecomment(request, listingId):
    if request.method == "POST":
        commentId = int(request.POST["commentId"])

        Comment.objects.get(id=commentId).delete()

        messages.info(request, "Removed comment.")
        return HttpResponseRedirect(reverse("listing", args=[listingId]))

# EFFECTS: determines if listing with listingId is in the user's watchlist
def inWatchlist(request, listingId):
    user = request.user

    if user.is_authenticated:
        try:
            user.watchlist.all().get(id=listingId)
            return True
        except:
            return False
    else:
        return False