from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

# Represents data for a User in the User table of the database
class User(AbstractUser):
    pass

    def __str__(self):
        return f"{self.username}"

# Represents data for a Category in the Category table of the database
class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title}"

# Represents data for Listing in the Listing table of the database
class Listing(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=70)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings")
    startingBid = models.DecimalField(max_digits=19, decimal_places=2, validators=[MinValueValidator(limit_value=0)])
    description = models.CharField(max_length=500, blank=True)
    image = models.URLField(max_length=5000, blank=True)
    lister = models.ForeignKey(User, blank=True, on_delete=models.CASCADE, related_name="listings")
    interestedUsers = models.ManyToManyField(User, blank=True, related_name="watchlist")
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"

# Represents data for a Bid in the Bid table of the database
class Bid(models.Model):
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.bidder}: ${self.amount}"

# Represents data for a Comment in the Comment table of the database
class Comment(models.Model):
    content = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now=True)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.commenter} at {self.date} on the listing {self.listing.title}"
