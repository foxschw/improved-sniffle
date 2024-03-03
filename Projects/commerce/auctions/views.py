from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .models import Categories
from .models import User, Listings
from .forms import CreateListingForm


def index(request):
    return render(request, "auctions/index.html",{
        "listings": Listings.objects.all()
    })


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


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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
    

@login_required
def create_listing(request):
    if request.method == "POST":
        # Save retrieved form to variable
        form = CreateListingForm(request.POST)
        if form.is_valid():
            # Create an entry but don't save it yet
            instance = form.save(commit=False)
            # Add username and timestamp
            instance.user = request.user
            instance.created = timezone.now()
            # Save listing
            instance.save()
            # Redirect home
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/error.html", {
                "message": "Failed To Create Listing.",
                "errors": form.errors # Include form errors
            })
    else:
        return render(request, "auctions/create_listing.html", {
            "form": CreateListingForm
        })
    

def listing_page(request, id):
    try:
        listing = Listings.objects.get(id=id)
    except Listings.DoesNotExist:
        return render(request, "auctions/error.html", {
                "message": "Listing Does Not Exist.",
            })
    return render(request, "auctions/listing.html", {
        "listing": listing
    })