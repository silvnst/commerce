from typing import List
from django.contrib.auth import authenticate, login, logout, decorators
from django.db import IntegrityError
from django.db.models.lookups import IntegerGreaterThanOrEqual
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import BidForm, Category, CommentForm, ListingForm, User, Listing, Bid


def index(request):

    active_listings = Listing.objects.filter(active=True).all()

    return render(request, "auctions/index.html", {
        "active_listings": active_listings,
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

@decorators.login_required
def create_listing(request):
    
    form = ListingForm()
    

    if request.method == "POST":
    
        f = ListingForm(request.POST)
        
        if f.is_valid():
            current_id = request.user.id
            current_user = User.objects.get(id=current_id)
            
            m = f.save(commit=False)
            m.creator = current_user    
            m.save()
            
            cats = request.POST.getlist('category')
            for c in cats:
                m.category.add(Category.objects.get(pk=c))

            listing_id = m.id
            
            return HttpResponseRedirect("/listings/" + str(listing_id))

        else:
            return render(request, "auctions/create_listing.html", {
            "form": f
        })
        
    else:

        return render(request, "auctions/create_listing.html", {
            "form": form
        })

def listing_page(request, listing):
    
    listing_object = Listing.objects.get(id=listing)

    latest_bid = listing_object.all_bids.all().order_by('-value').first()

    watchlist = False
    
    comments = listing_object.all_comments.all()

    comment_form = CommentForm()

    if listing_object.watchlist.filter(id=request.user.id):
        watchlist = True

    bid_form = BidForm()

    if listing_object.all_bids.exists():
        max_bid = max(listing_object.starting_bid, latest_bid.value)
    else:
        max_bid = listing_object.starting_bid


    if request.method == "POST":
            
        form = BidForm(request.POST)

        if form.is_valid() and float(request.POST['value']) > max_bid:
            
            f = form.save(commit=False)
            f.user = request.user
            f.article = listing_object
            f.save()

            return HttpResponseRedirect(reverse("listing", kwargs={'listing': listing}))

        else:

            return render(request, "auctions/listing.html", {
                "listing" : listing_object,
                "message_warning" : "There have been a problem with your bid. Did you make a bid higher than the current price?",
                "bid_form" : bid_form,
                "max_bid" : max_bid,
                "latest_bid" : latest_bid,
                "watchlist": watchlist,
                "comments": comments,
                "comment_form": comment_form,
            })

    else:

        message_success = False
        
        try:
            if listing_object.all_bids.all().get(value=max_bid).user.id == request.user.id:
                message_success = 'You are the highest bidder.'

        except:
            message_success = False

        return render(request, "auctions/listing.html", {
            "listing" : listing_object,
            "bid_form" : bid_form,
            "max_bid" : max_bid,
            "latest_bid" : latest_bid,
            "message_success" : message_success,
            "watchlist": watchlist,
            "comments": comments,
            "comment_form": comment_form
        })

@decorators.login_required
def deactivate_listing(request, listing):
    
    listing_object = Listing.objects.get(id=listing)
    
    
    if listing_object.active:
        listing_object.active = False

    else:
        listing_object.active = True

    listing_object.save()

    return HttpResponseRedirect(reverse("listing", kwargs={'listing': listing}))

@decorators.login_required
def comment(request, listing):
    
    f = CommentForm(request.POST)

    if f.is_valid():
        a = f.save(commit=False)
        a.user = request.user
        a.article = Listing.objects.get(id=listing)
        a.save()

    return HttpResponseRedirect(reverse("listing", kwargs={'listing': listing}))

@decorators.login_required
def watchlist(request, listing):
    
    listing_object = Listing.objects.get(id=listing)
        
    if listing_object.watchlist.filter(pk=request.user.id).exists():
        listing_object.watchlist.remove(request.user)

    else:
        listing_object.watchlist.add(request.user)

    return HttpResponseRedirect(reverse("listing", kwargs={'listing': listing}))

@decorators.login_required
def my_watchlist(request):
    
    u = User.objects.get(pk=request.user.id)
    all_obj = u.watch_list.all()

    return render(request, "auctions/my_watchlist.html", {
        "objects" : all_obj
    })

def categories(request):

    all_cat = Category.objects.all()

    return render(request, "auctions/categories.html", {
        "categories": all_cat,
    })

def categories_single(request, id):
    cat_obj = Category.objects.get(id=id)

    all_obj = cat_obj.category_items.all()

    return render(request, "auctions/category.html", {
        "category": cat_obj.category_name,
        "objects" : all_obj
    })
