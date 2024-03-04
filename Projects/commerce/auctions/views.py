from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .models import User, Listings, Categories, Bids, Watchlist, Comments
from .forms import CreateListingForm, BidSubmit, CommentSubmit


def index(request):

    # Filter for active listings
    listings = Listings.objects.filter(is_active=True)
    
    return render(request, "auctions/index.html", {
        "listings": listings,
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
    # Retrieve listing from id and store to variable
    # Return error if listing doesn't exist
    try:
        listing = Listings.objects.get(id=id)
    except Listings.DoesNotExist:
        return render(request, "auctions/error.html", {
                        "message": "Listing Not Found.",
                    })
    
    # Import Comments
    comments = Comments.objects.filter(listing=listing)
    
    # Check if listing is in user's watchlist
    on_watchlist = Watchlist.objects.filter(
        user = request.user,
        item=listing
        ).exists()
        
    ## HIGHEST BID WINNER LOGIC
    # Initialize winner is False
    is_winner = False

    #Determine if current user is highest bidder and if listing is closed
    if not listing.is_active:
        highest_bid = Bids.objects.filter(listing=listing).order_by("-bid_amt").first()
        if highest_bid and highest_bid.user == request.user:
            is_winner = True
    
    if request.method == "POST":
        ## BID SUBMISSION LOGIC
        # Store bid from form to variable if valid
        if "place_bid" in request.POST:
            bid = BidSubmit(request.POST)
            if bid.is_valid():
                bid_amount = bid.cleaned_data["bid_amt"]

                # Check if bid is higher than list price or current highest bid
                if bid_amount > (listing.highest_bid or listing.list_price):
                    # Update Bids databas
                    new_bid = Bids(
                        bid_amt = bid_amount,
                        bid_time = timezone.now(),
                        user = request.user,
                        listing=listing
                    )
                    new_bid.save()

                    # Update highest bid field for listing
                    listing.update_highest_bid(bid_amount)

                    return HttpResponseRedirect(reverse("index"))
                
                else:
                    return render(request, "auctions/error.html", {
                                "message": "Bid Too Low.",
                            })  
    
        ## WATCHLIST LOGIC
        elif "watchlist_action" in request.POST:
            if on_watchlist:
                # Remove from watchlist
                Watchlist.objects.filter(user=request.user, item=listing).delete()
            else:
                # Add to watchlist
                new_watchlist_item = Watchlist(user=request.user, item=listing)
                new_watchlist_item.save()
            return HttpResponseRedirect(reverse("listing_page", args=[id]))
        
        ## AUCTION CLOSE LOGIC
        elif "close_auction" in request.POST:
            #make sure lister is the closer
            if request.user == listing.user:
                listing.is_active = False
                listing.save()
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "auctions/error.html", {
                            "message": "Not Authorized.",
                        })

        ## COMMENT LOGIC
        elif "submit_comment" in request.POST:
            # Store form in variable
            comment_form = CommentSubmit(request.POST)
            # Check validity and store to database
            if comment_form.is_valid():
                comment_submission = Comments(
                        comment = comment_form.cleaned_data["comment"],
                        comment_time = timezone.now(),
                        user = request.user,
                        listing=listing
                    )
                comment_submission.save()
                return HttpResponseRedirect(reverse("listing_page", args=[id]))
            
            else:
                return render(request, "auctions/error.html", {
                                "message": "Comment Invalid.",
                            })

    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "form" : BidSubmit,
            "on_watchlist": on_watchlist,
            "is_winner": is_winner,
            "comments": comments,
            "comment_submit": CommentSubmit
        })
    

def closed(request):
    # Display closed listings for registered users
    listings = Listings.objects.filter(is_active=False)
    
    return render(request, "auctions/closed.html", {
        "listings": listings,
    })

@login_required
def watchlist(request):

    # Create a filtered list of Watchlist items based on user
    user_watchlist = Watchlist.objects.filter(user=request.user)
    
    return render(request, "auctions/watchlist.html", {
        "watchlist": user_watchlist,
    })

def category_list(request):

    # Store categories into variable
    categories = Categories.objects.all

    return render(request, "auctions/category_list.html", {
        "categories": categories,
    })

def category_page(request, name):
    try:
        # Filter categories by name
        category = Categories.objects.get(name=name)

        # Pull listings in that category
        listings = Listings.objects.filter(category=category, is_active=True)

        return render(request, "auctions/category_page.html", {
            "category": category,
            "listings": listings,
        })
    
    except Categories.DoesNotExist:
        return render(request, "auctions/error.html", {
            "message": "Category Does Not Exist."
        })