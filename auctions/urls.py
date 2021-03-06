from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.createListing, name="createListing"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.category, name="category"),
    path("listings/<int:listingId>", views.listing, name="listing"),
    path("listings/<int:listingId>/bid", views.bid, name="bid"),
    path("listings/<int:listingId>/closelisting", views.closeListing, name="closelisting"),
    path("listings/<int:listingId>/comment", views.comment, name="comment"),
    path("listings/<int:listingId>/deletecomment", views.deletecomment, name="deletecomment"),
    path("users/<str:username>/listings", views.userListings, name="userlistings"),
    path("users/<str:username>/mylistings", views.userListings, name="mylistings"),
    path("users/<str:username>/watchlist", views.watchlist, name="watchlist"),
    path("users/<str:username>/watchlist/alterwatchlist", views.alterWatchlist, name="alterWatchlist")
]
