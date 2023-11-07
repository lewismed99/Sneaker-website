from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listings, Comment, Bid

def listing(request, id):
    listingData=Listings.objects.get(pk=id)
    isListingInWatchlist=request.user in listingData.watchlist.all()
    allComments=Comment.objects.filter(listing=listingData)
    isOwner=request.user.username == listingData.owner.username
    return render(request,"auctions/listing.html",{
        "listing":listingData,
        "isListingInWatchlist":isListingInWatchlist,
        "allComments":allComments,
        "testPrice":listingData.price.bid,
        "isOwner":isOwner

    })

def closeAuction(request,id):
    listingData=Listings.objects.get(pk=id)
    listingData.isActive=False
    listingData.save()
    isOwner=request.user.username == listingData.owner.username
    allComments=Comment.objects.filter(listing=listingData)
    isListingInWatchlist=request.user in listingData.watchlist.all()
    return render(request,"auctions/listing.html",{

        "listing":listingData,
        "isListingInWatchlist":isListingInWatchlist,
        "allComments":allComments,
        "testPrice":listingData.price.bid,
        "isOwner":isOwner,
        "message":"congratulations your auction is closed"



    })

def addBid(request,id):
    newBid=request.POST["newBid"]
    #now we need listing data
    listingData=Listings.objects.get(pk=id)
    isListingInWatchlist=request.user in listingData.watchlist.all()
    allComments=Comment.objects.filter(listing=listingData)
    isOwner=request.user.username == listingData.owner.username
    if float(newBid)>listingData.price.bid:
        updateBid=Bid(user=request.user, bid=float(newBid))
        updateBid.save()
        listingData.price=updateBid
        listingData.save()
        return render(request,"auctions/listing.html",{
            "listing":listingData,
            "message":"Bid was updated sucessfully",
            "update" :True,
            "isListingInWatchlist":isListingInWatchlist,
            "allComments":allComments,        
            "isOwner":isOwner
        })
    #HttpResponseRedirect(reverse("listing",args=(id,), kwargs=({"message":"successful Buy"}) ))
    else:
        return render(request,"auctions/listing.html",{
            "listing":listingData,
            "message":"bid updated failed",
            "update":False,
            "isOwner":isOwner


        })
    
    #HttpResponseRedirect(reverse(listing,args=(id,), kwargs=({"message":"failed Buy"})))
    

def addComment(request,id):
    currentUser=request.user
    listingData=Listings.objects.get(pk=id)
    message=request.POST['newComment']#this what we are getting form the form

    newComment=Comment(
        author=currentUser,
        listing=listingData,
        message=message
    )
    newComment.save()
    return HttpResponseRedirect(reverse("listing",args=(id, )))
def displayWatchlist(request):
    currentUser=request.user
    listings=currentUser.listingWatchlist.all()
    return render(request,"auctions/watchlist.html",{
            "listings":listings


    })


def removeWatchlist(request,id):
    listingData=Listings.objects.get(pk=id)
    currentUser=request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing",args=(id, )))

def addWatchlist(request,id):
    listingData=Listings.objects.get(pk=id)
    currentUser=request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing",args=(id, )))

def index(request):
    activeListings=Listings.objects.filter(isActive=True)
    allCategories=Category.objects.all()
    return render(request, "auctions/index.html",{
        "listings":activeListings,
        "categories":allCategories

    })

def displayCategory(request):
    if request.method=="POST":
        categoryFromForm=request.POST['category']
        category=Category.objects.get(categoryName=categoryFromForm)

        activeListings=Listings.objects.filter(isActive=True, category=category)
        allCategories=Category.objects.all()
        return render(request, "auctions/index.html",{
        "listings":activeListings,
        "categories":allCategories,
        })


def createListing(request):
    if request.method=="GET":
        allCategories=Category.objects.all()
        return render(request,"auctions/create.html",{
            "categories":allCategories

        })
    else:
        # get data from the form
        title=request.POST["title"]
        description=request.POST["description"]
        imageurl=request.POST["imageurl"]
        price=request.POST["price"]
        category=request.POST["category"]
        #who is the user
        currentUser=request.user
        #get all content aqbout particular catgeory
        categoryData=Category.objects.get(categoryName=category)



        #create a new listing object
        bid=Bid(bid=float(price), user=currentUser)
        bid.save()
        
        newListing=Listings(
            title=title,
            description=description,
            imageUrl=imageurl,
            price=bid,    
            category=categoryData,
            owner=currentUser

        )
        #insert the new object in our database
        newListing.save()
        #Redirect to index page
        return HttpResponseRedirect(reverse("index"))


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
