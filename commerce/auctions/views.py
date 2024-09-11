from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms

from .models import *

#--Display default active auctions
def index(request):
    return render(request, "auctions/index.html", {
        "auctions": AuctionList.objects.all()
    })

# Get the lastest primary key
def getLastPk(obj):
    if(obj.objects.first() is None):
        return 1
    else:
        get_pk = obj.objects.order_by("-pk")[0]
        last_pk = get_pk.pk + 1
        return last_pk

#--Display default login page
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

#--Default logout
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

#--Display default register page
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

# Display infomation for a specific lisiting
def listing(request, listing_id):
    listing = AuctionList.objects.get(id=listing_id)
    comments = Comment.objects.filter(comment_on=listing_id)
    num_bidder = Bid.objects.filter(listing_bid=listing_id).count()-1

    if request.user.is_authenticated:
        watched = WatchList.objects.filter(watcher=request.user, listings=listing)
        if watched.exists():
            watching = True
        else:
            watching =  False

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "watching": watching,
            "comments": comments,
            "count": num_bidder
        })
    
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "count": num_bidder
    })

# Update bid for a certain listing
def bid(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            # Take in the data the user submitted and save it as form
            form = BidForm(request.POST)
            new_bid = int(form.data["bid"])
            listing_id = form.data["listing_id"]
            listing = AuctionList.objects.get(id=listing_id)
            listing_bid = listing.bid

            comments = Comment.objects.filter(comment_on=listing_id)
            num_bidder = Bid.objects.filter(listing_bid=listing_id).count()-1

            # Check if new bid is greater than the current bid listing
            if (new_bid > listing_bid):
                listing.bid = new_bid
                listing.save()

                bid_obj = Bid(
                    id = getLastPk(Bid), 
                    bid = new_bid, 
                    listing_bid = listing, 
                    auctioner = request.user)
                bid_obj.save()

                num_bidder = Bid.objects.filter(listing_bid=listing_id).count()-1
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "comments": comments,
                    "count": num_bidder,
                    "message": "Successfully placed a bid."
                })
            else:
                form = BidForm(request.POST)
                listing_id = form.data["listing_id"]
                listing = AuctionList.objects.get(id=listing_id)
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "comments": comments,
                    "count": num_bidder,
                    "message": "Bid is too low."
                })
    
    form = BidForm(request.POST)
    listing_id = form.data["listing_id"]
    listing = AuctionList.objects.get(id=listing_id)

    comments = Comment.objects.filter(comment_on=listing_id)
    num_bidder = Bid.objects.filter(listing_bid=listing_id).count()-1
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "count": num_bidder,
        "message": "Login before placing a bid."
    })

# Class that has bid form content
class BidForm(forms.Form):
    bid_price = forms.IntegerField(label="bid_price")

# Add comment for a certain listing
@login_required
def comment(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        new_comment = form.data["comment"]
        listing_id = form.data["listing_id"]
        listing = AuctionList.objects.get(id=listing_id)

        comment_obj = Comment(id=getLastPk(Comment), commenter=request.user, message=new_comment, comment_on=listing)
        comment_obj.save()

        return redirect("listing", listing_id=listing_id)
        
# Class that has comment form content
class CommentForm(forms.Form):
    comment_msg = forms.CharField(widget=forms.Textarea, label="comment_msg")

# Display list of all categories
def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": AuctionList.CATEGORIES
    })

# Display list of auctions for a specific category
def categories_choice(request, category_name):
    list_by_category = AuctionList.objects.filter(category=category_name)

    return render(request, "auctions/categories_choice.html", {
        "category": category_name,
        "auctions": list_by_category
    })

# Create a new listing
@login_required
def create(request):
    if request.method == "POST":
        form = CreateForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            description = form.cleaned_data.get("description")
            bid = form.cleaned_data.get("bid")
            category = form.cleaned_data.get("category")
            image = form.cleaned_data.get("image")
            
            # Create a new listing with the information
            new_listing = AuctionList.objects.create(
                id = getLastPk(AuctionList), 
                name = name, 
                description = description, 
                bid = bid, 
                category = category, 
                image = image, 
                seller = request.user, 
                available = True)
            new_listing.save()
            # Create a new starting bid for the listing
            start_bid = Bid.objects.create(
                id = getLastPk(Bid), 
                bid = bid, 
                listing_bid = new_listing, 
                auctioner = request.user)
            start_bid.save()

            return HttpResponseRedirect(reverse("index"))
    
    form = CreateForm()
    return render(request, "auctions/create.html", {
        "form": form,
        "categories": AuctionList.CATEGORIES
    })

# Class that has create listing form content
class CreateForm(forms.ModelForm):
    class Meta:
        model = AuctionList
        fields = ("name", "description", "bid", "category", "image")
        labels = {
            "name": "",
            "description": "",
            "bid": "",
            "category": "",
            "image": "",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Name"}),
            "description": forms.TextInput(attrs={"class": "form-control", "placeholder": "Description"}),
            "bid": forms.NumberInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "image": forms.FileInput(),
        }

# Display user watchlist
@login_required
def watchlist(request):
    watchlist, created = WatchList.objects.get_or_create(watcher=request.user)
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist.listings.all()
    })

# Add/Remove from watchlist
@login_required
def edit_watchlist(request, listing_id):
    listing = AuctionList.objects.get(id=listing_id)
    watch = WatchList.objects.filter(watcher=request.user, listings=listing)

    if watch.exists():
        watched = WatchList.objects.get(watcher=request.user).listings.remove(listing)
        watching = False
        message = "Successfully deleted listing from watchlist."
    else:
        watched, created = WatchList.objects.get_or_create(watcher=request.user)
        watched.listings.add(listing)
        watching = True
        message = "Successfully added listing to watchlist."
        
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watching": watching,
        "message": message
    })  

# Close user listing
def close(request, listing_id):
    listing = AuctionList.objects.get(id=listing_id)
    bid_obj = Bid.objects.filter(listing_bid=listing).order_by("-bid")[0]
    highest_bid = bid_obj.bid
    winner = bid_obj.auctioner

    listing.winner = winner
    listing.available = False
    listing.save()

    return render(request, "auctions/close.html", {
        "listing": listing,
        "highest_bid": highest_bid,
        "winner": winner 
    })