# Various Django Imports.

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.template.defaulttags import register
from django.template.defaulttags import register

# Imports from .models
from .models import User, Listing, Comment, Bid


# Custom function to get dictionary key.
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def index(request):
    """ 
    Shows all active listings. 
    """
    # Attempt to map highest bid amount to each items' ID.
    di = {}
    for obj in Listing.objects.filter(is_active=True):
        try: 
            di[obj.id] = sorted([bid.bid_amount for bid in obj.bids.all()])[-1]
        except:
            di[obj.id] = obj.starting_bid
    
    #print(di) - For Debugging 

    # Return index template
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(is_active=True),
        "di": di
    })


def categories(request):
    """
    Returns a page with a clickable button for each category(see models.py for further reference).
    """
    human_readable = []
    for obj in Listing.CHOICES:

        # For each listing choice, we add the human readable format, and the machine-readable as well.
        human_readable+= [[obj[0], obj[1]]]
    
    # Returns categories.html, giving it access to variables.
    return render(request, "auctions/categories.html", {
        'li': human_readable,
        "bo": False
    })

def sort(request, code):
    """
    Returns sorted, active listings.
    """
    filtered = Listing.objects.filter(category=code, is_active=True)

    # Returns page with variables. 
    return render(request, "auctions/categories.html", {
        "bo": True,
        "listings": filtered,
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

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@login_required
def create(request):
    """
    Allows the user to create a new listing. 
    """
    # Checks if request is a POST request. 
    if request.method == "POST":

        # For debugging - print(request.user.username)

        # We get the POST request's data.
        name_listing = request.POST["name"]
        starting_bid = request.POST["start"]
        pic = request.POST["picture_url"]
        choice = request.POST["category"]
        desc = request.POST["description"]
        owner = request.user.username

        # Creates a listing and saves it. 
        new_listing = Listing(name=name_listing, starting_bid=starting_bid, picture_url=pic, description=desc, owner=owner, category=choice, is_active=True)
        new_listing.save()
        
        # Redirects to the index page. 
        return HttpResponseRedirect(reverse("index"))
    
    # Otherwise, return create.html, with variables.
    return render(request, "auctions/create.html", {
        "list1": Listing.CHOICES
    })

def listing_view(request, id):
    if request.method == "POST":
        try:
            request.POST["comment"]
            c1 = Comment(comment=request.POST["comment_text"], user=request.POST["user_name"])
            c1.save()
            listing = Listing.objects.get(pk=id)
            listing.comments.add(c1)
            return HttpResponseRedirect(reverse("listing", args=(id,)))
        except:
            try:
                listing = Listing.objects.get(pk=id)
                # Checks if the POST is from the bid form
                request.POST["bid_POST"]
                # Gets amount and user, converts amount to an integer
                amount = int(request.POST["bid"])
                user = request.POST["user"]
                # For debugging - print(amount, user)
                # If there are no bids, then we will check if the bid we've gotten is greater than the starting_bid
                try:
                    user = User.objects.get(username=request.user.username)
                    user.watchlist.get(pk=id)
                    boolean = True
                except:
                    boolean = False
                    
                if len([obj.bid_amount for obj in listing.bids.all()])==0:

                    if listing.starting_bid > amount:
                        
                        # For debugging - print("NAY")
                        li_bid = [obj.bid_amount for obj in listing.bids.all()]
                        li_bid.sort()
                        li_owner = [obj.bid_owner for obj in listing.bids.all()]
                        return render(request, "auctions/listing.html", {
                            "listing": listing,
                            "category": dict(Listing.CHOICES)[listing.category],
                            "b": boolean, 
                            "comments": listing.comments.all(),
                            "err": "Sorry, the bid must be at least greater than the starting bid.",
                            "a": len(li_bid),
                            "curr_price": li_bid[-1],
                        })

                    else:
                        # For debugging - print("YES")

                        b1 = Bid(bid_owner=user, bid_amount=amount)
                        b1.save()
                        listing.curr_highest_bidder = request.user.username
                        listing.save()
                        print(listing.curr_highest_bidder)
                        listing.bids.add(b1)
                        li_bid = [obj.bid_amount for obj in listing.bids.all()]
                        li_bid.sort()
                        li_owner = [obj.bid_owner for obj in listing.bids.all()]
                        return render(request, "auctions/listing.html", {
                            "listing": listing,
                            "category": dict(Listing.CHOICES)[listing.category],
                            "b": boolean, 
                            "comments": listing.comments.all(),
                            "err": "Nice, the bid went through!",
                            "a": len(li_bid),
                            "curr_price": li_bid[-1],
                        })
                else:
                    # If there is a bid
                    li = [[obj.bid_amount, obj.bid_owner] for obj in listing.bids.all()]
                    li_2 = sorted(li, key=lambda each:each[0])
                    if amount <= li_2[-1][0]:
                        # For debugging - print("NAY")
                        li_bid = [obj.bid_amount for obj in listing.bids.all()]
                        li_owner = [obj.bid_owner for obj in listing.bids.all()]
                        li_bid.sort()
                        return render(request, "auctions/listing.html", {
                            "listing": listing,
                            "category": dict(Listing.CHOICES)[listing.category],
                            "b": boolean, 
                            "comments": listing.comments.all(),
                            "err": "Sorry, the bid must be greater than the last bid.",
                            "a": len(li_bid),
                            "curr_price": li_bid[-1],
                        })
                    else:
                        # For debugging - print("YES")
                        b1 = Bid(bid_owner=user, bid_amount=amount)
                        b1.save()
                        listing.curr_highest_bidder = request.user.username
                        listing.save()
                        print(listing.curr_highest_bidder)
                        listing.bids.add(b1)
                        li_bid = [obj.bid_amount for obj in listing.bids.all()]
                        li_owner = [obj.bid_owner for obj in listing.bids.all()]
                        li_bid.sort()
                        return render(request, "auctions/listing.html", {
                            "listing": listing,
                            "category": dict(Listing.CHOICES)[listing.category],
                            "b": boolean, 
                            "comments": listing.comments.all(),
                            "err": "Nice, the bid went through!",
                            "a": len(li_bid),
                            "curr_price": li_bid[-1]
                        })
            except:
                pass
        
    listing = Listing.objects.get(pk=id)
    if listing:
        try:
            request.GET.get('close_listing')
            a = request.GET.get('close_listing').strip()
            # If the GET result isn't false or something else, and the user is indeed the listing owner, then we change is_active to false
            if a=="true" and request.user.username==listing.owner:
                listing.is_active = False
                listing.save()
                return HttpResponseRedirect(reverse("index"))
            else:
                return HttpResponseRedirect(reverse("listing", args=(id)))
        except:
            try:
                user = User.objects.get(username=request.user.username)
                user.watchlist.get(pk=id)
                boolean = True
            except:
                boolean = False
            print(listing.curr_highest_bidder)
            li_bid = [obj.bid_amount for obj in listing.bids.all()]
            li_bid.sort()
            li_owner = [obj.bid_owner for obj in listing.bids.all()]
            return render(request, "auctions/listing.html", {   
                "listing": listing,
                "category": dict(Listing.CHOICES)[listing.category],
                "b": boolean, 
                "comments": listing.comments.all(),
                "a": len(li_bid),
                "curr_price": li_bid[-1] if len(li_bid)>0 else listing.starting_bid,
            })
    else:
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
def watchlist(request):
    if request.method == "POST":
        try:
            request.POST["unwatch"]
            user = User.objects.get(username=request.user.username)
            id_listing = int(request.POST["id"])
            listing = Listing.objects.get(pk=id_listing)
            user.watchlist.remove(listing)
            listings = user.watchlist.all()
            return render(request, "auctions/watchlist.html", {
                "listings": listings
            })
        except:
            user = User.objects.get(username=request.user.username)
            id_listing = int(request.POST["id"])
            listing = Listing.objects.get(pk=id_listing)
            user.watchlist.add(listing)
            listings = user.watchlist.all()
            return render(request, "auctions/watchlist.html", {
                "listings": listings
            })
    user = User.objects.get(username=request.user.username)
    listings = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
            "listings": listings
    })