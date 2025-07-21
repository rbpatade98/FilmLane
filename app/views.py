from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie,Wishlist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.contrib import messages
import razorpay
import random

from django.contrib import messages
from django.contrib.auth.hashers import make_password

from django.views.decorators.csrf import csrf_exempt
from .models import Membership
from django.utils import timezone
from datetime import timedelta
import json
from django.http import JsonResponse



# Create your views here.





def validate_password(password):
    # Check minimum length
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")

    # Check maximum length
    if len(password) > 128:
        raise ValidationError("Password cannot exceed 128 characters.")

    # Initialize flags for character checks
    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False
    special_characters = "@$!%*?&"

    # Check for character variety
    for char in password:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
        elif char in special_characters:
            has_special = True

    if not has_upper:
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not has_lower:
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not has_digit:
        raise ValidationError("Password must contain at least one digit.")
    if not has_special:
        raise ValidationError(
            "Password must contain at least one special character (e.g., @$!%*?&)."
        )

    # Check against common passwords
    common_passwords = [
        "password",
        "123456",
        "qwerty",
        "abc123",
    ]  # Add more common passwords
    if password in common_passwords:
        raise ValidationError("This password is too common. Please choose another one.")

#signup: Handles user registration, password validation, and creating new user accounts.
def signup(req):
    if req.method == "POST":
        uname = req.POST["uname"]
        email = req.POST["email"]
        upass = req.POST["upass"]
        ucpass = req.POST["ucpass"]
        context = {}
        try:
            validate_password(upass)
        except ValidationError as e:
            context["errmsg"] = str(e)
            return render(req, "signup.html", context)

        if uname == "" or email == "" or upass == "" or ucpass == "":
            context["errmsg"] = "Field can't be empty"
            return render(req, "signup.html", context)
        
                
        elif upass != ucpass:
            context["errmsg"] = "Password and confirm password doesn't match"
            return render(req, "signup.html", context)
        elif uname.isdigit():
            context["errmsg"] = "Username cannot consist solely of numbers."
            return render(req, "signup.html", context)
        else:
            try:
                userdata = User.objects.create(
                    username=uname, email=email, password=upass
                )
                userdata.set_password(upass)
                userdata.save()
                return redirect("/signin")
            except:
                context["errmsg"] = "User Already exists"
                return render(req, "signup.html", context)
    else:
        context = {}
        context["errmsg"] = ""
        return render(req, "signup.html", context)



from django.utils import timezone
from .models import Membership

#signin: Handles user login, password verification, and checking if the user's membership is active.
def signin(req):
    if req.method == "POST":
        email = req.POST["email"]
        upass = req.POST["upass"]
        context = {}

        if email == "" or upass == "":
            context["errmsg"] = "Field can't be empty"
            return render(req, "signin.html", context)


        else:
            try:
                user = User.objects.get(email=email)  # Retrieve user by email
                userdata = authenticate(username=user.username, password=upass)

                if userdata is not None:
                    login(req, userdata)

                    try:
                        membership = Membership.objects.get(user=userdata)
                        if membership.end_date and membership.end_date > timezone.now():
                            return redirect("/mainpage")  #  Membership active
                        else:
                            messages.warning(req, "Your membership has expired. Please renew to continue.")
                            return redirect("/membership")  #  Expired
                    except Membership.DoesNotExist:
                        messages.warning(req, "You don't have an active plan. Please purchase a membership.")
                        return redirect("/membership") #  No plan found
                else:
                    context["errmsg"] = "Invalid username and password"
                    return render(req, "signin.html", context)
            except:
                context["errmsg"] = "User doesn't exist"
                return render(req, "signin.html", context)
    else:
        return render(req, "signin.html")

#forgot_password: Handles the forgotten password process by accepting a username and 
#directing the user to reset their password.

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            return redirect('reset_password', username=username)
        except User.DoesNotExist:
            messages.error(request, 'Username does not exist.')
            return redirect('forgot_password')
    return render(request, 'forgot_password.html')

#reset_password: Allows users to reset their password once they've provided a valid username.
def reset_password(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'Invalid user.')
        return redirect('forgot_password')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        else:
            user.password = make_password(password1)
            user.save()
            messages.success(request, 'Password successfully reset. Please log in.')
            return redirect('signin')  # or your login URL name

    return render(request, 'reset_password.html', {'username': username})

#userlogout: Logs out the user and redirects them to the home page.
def userlogout(req):
    logout(req)
    return redirect("/")

# def membership(req):
#     return render(req,"membership.html")

#membership: Displays the membership page with a payment gateway integration for Razorpay.
def membership(req):
    if req.user.is_authenticated:
        ott = Movie.objects.filter(userid=req.user.id)
        amount = 149
        user = req.user
        client = razorpay.Client(
            auth=("rzp_test_wH0ggQnd7iT3nB", "eZseshY3oSsz2fcHZkTiSlCm")
        )
        
        try:
            data = {
                "amount": int(amount * 100),
                "currency": "INR",
                "receipt": str(random.randrange(1000, 90000)),
            }
            payment = client.order.create(data=data)

            context = {"data": payment, "amount": amount}
            return render(req, "membership.html", context)
        except ValidationError as e:
            context = {}
            context["errmsg"] = (
                "An error occurred while creating payment order. Please try again"
            )
            print(e)
            return render(req, "membership.html", context)
    else:
        return redirect("/mainpage")

#payment_success: Handles successful payment responses and
# activates the user’s membership for a specified duration.
@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        try:
            if not request.user.is_authenticated:
                print("User not authenticated (probably missing credentials)")
                return JsonResponse({"error": "unauthenticated"}, status=401)

            user = request.user
            membership, created = Membership.objects.get_or_create(user=user)
            membership.activate_membership(duration_days=30)
            print(f"Membership activated for {user.username}")
            return JsonResponse({"status": "success"})
        except Exception as e:
            print("Error in payment_success:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)

#index: Renders the home page (index.html).
def index(req):
    return render(req, "index.html")

#moviedetails: Displays the detailed view of a selected movie.
def moviedetails(req,movieid):
    allmovie=Movie.objects.get(movieid=movieid)
    context={"allmovie":allmovie}
    return render(req, "movie-detail.html", context)


def hollywood(req):
    allmovies = Movie.moviemanager.hollywood_list
    context = {"allmovie": allmovies}
    return render(req, "mainpage.html", context)

def anime(req):
    allmovies = Movie.moviemanager.anime_list
    context = {
        "allmovie": allmovies,
        **get_membership_context(req.user)
    }
    return render(req, "mainpage.html", context)


def action(req):
    allmovies = Movie.moviemanager.action_list
    context = {
        "allmovie": allmovies,
        **get_membership_context(req.user)
    }
    return render(req, "mainpage.html", context)


def comedy(req):
    allmovies = Movie.moviemanager.comedy_list
    context = {
        "allmovie": allmovies,
        **get_membership_context(req.user)
    }
    return render(req, "mainpage.html", context)

def horror(req):
    allmovies = Movie.moviemanager.horror_list
    context = {
        "allmovie": allmovies,
        **get_membership_context(req.user)
    }
    return render(req, "mainpage.html", context)

def scifi(req):
    allmovies = Movie.moviemanager.scifi_list
    context = {
        "allmovie": allmovies,
        **get_membership_context(req.user)
    }
    return render(req, "mainpage.html", context)

#Displays movies based on a specific category (e.g., Anime, Action, etc
def category_view(request, category_name):
    categories = ['Anime', 'Action', 'Comedy', 'Horror', 'Scifi', 'Hollywood']

    if category_name not in categories:
        return redirect('mainpage')

    movies = Movie.objects.filter(category=category_name)
    
    membership = None
    is_expired = False
    days_left = None

    if request.user.is_authenticated:
        try:
            membership = Membership.objects.get(user=request.user)
            is_expired = not membership.check_membership_status()

            if membership.end_date and not is_expired:
                days_left = (membership.end_date - timezone.now()).days
        except Membership.DoesNotExist:
            is_expired = True

    return render(request, "mainpage.html", {
        "allmovie": movies,
        "membership": membership,
        "is_expired": is_expired,
        "days_left": days_left,
        "selected_category": category_name
    })


#  Handles displaying the video player page for a specific movie.

#This view uses the membership_required decorator to ensure users with active memberships can access the video.

from .models import WatchHistory
# @membership_required
def video(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)

    if request.user.is_authenticated:
        # Create or update watch history
        WatchHistory.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={'watched_on': timezone.now()}
        )

    context = {"allmovie": movie}
    return render(request, "video.html", context)

#Displays the watch history of the authenticated user, showing all the movies they have watched.
def watch_history(request):
    if not request.user.is_authenticated:
        return redirect('signin')

    history = WatchHistory.objects.filter(user=request.user)
    context = {'watch_history': history}
    return render(request, 'watch_history.html', context)

#wishlist: Displays the movies that the user has added to their wishlist.
def wishlist(req):
    user = req.user
    allwishlist = Wishlist.objects.filter(userid=user.id)

    if req.user.is_authenticated:
        context = {
            'allwishlist':allwishlist,
            'username':user,
        }
    else:
        context={
            'allwishlist':allwishlist,
        }
    return render(req, 'watchlist.html', context)

#addtofav: Adds a movie to the wishlist or updates the quantity if the movie is already in the wishlist.
def addtofav(req,movieid):
    if req.user.is_authenticated:
        user=req.user
    else:
        user=None

    allmovie=get_object_or_404(Movie,movieid=movieid)
    wishitem,created=Wishlist.objects.get_or_create(movieid=allmovie,userid=user)
    if not created:
        wishitem.qty+=1
    else:
        wishitem.qty = 1
    wishitem.save()
    return redirect("/wishlist")

#removefavourite: Removes a movie from the user's wishlist.
def removefavourite(req,movieid):
    user=req.user
    wishitems=Wishlist.objects.get(movieid=movieid,userid=user.id)
    wishitems.delete()
    return redirect("/wishlist")




def mainpage(request):
    membership = None
    is_expired = False
    days_left = None

    if request.user.is_authenticated:
        try:
            membership = Membership.objects.get(user=request.user)
            is_expired = not membership.check_membership_status()

            if membership.end_date and not is_expired:
                days_left = (membership.end_date - timezone.now()).days
        except Membership.DoesNotExist:
            is_expired = True

    current_time = timezone.now()
    hour = current_time.hour  # Extract hour from current_time

    # Decide greeting based on hour
    if 5 <= hour < 12:
        greeting = "Good Morning"
    elif 12 <= hour < 17:
        greeting = "Good Afternoon"
    elif 17 <= hour < 21:
        greeting = "Good Evening"
    else:
        greeting = "Good Night"

    allmovie = Movie.objects.all()
    return render(request, "mainpage.html", {
        "allmovie": allmovie,
        "membership": membership,
        "is_expired": is_expired,
        "days_left": days_left, #  Make sure this is included
        "current_time": current_time,  # Already assigned once
        "greeting": greeting,  
        
        
    })

def get_membership_context(user):
    membership = None
    is_expired = True
    days_left = None

    if user.is_authenticated:
        try:
            membership = Membership.objects.get(user=user)
            is_expired = not membership.check_membership_status()
            if membership.end_date and not is_expired:
                days_left = (membership.end_date - timezone.now()).days
        except Membership.DoesNotExist:
            is_expired = True

    return {
        "membership": membership,
        "is_expired": is_expired,
        "days_left": days_left
    }



#It fetches the movie from the database using its movieid.
#The movie object is passed to the template where the video is displayed.
def video(req,movieid):
    allmovie=Movie.objects.get(movieid=movieid)
    context={"allmovie":allmovie}
    return render(req,"video.html",context)

#Handles the movie search functionality, allowing users to search movies by title.
def search_movies(request):
    query = request.GET.get('q')
    results = Movie.objects.filter(title__icontains=query) if query else Movie.objects.all()

    context = {
        'allmovie': results,
        **get_membership_context(request.user)  # Adds membership data
    }

    return render(request, 'mainpage.html', context)

    





def membership_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/signin')
        try:
            membership = Membership.objects.get(user=request.user)
            if not membership.check_membership_status():
                return redirect('/membership')
        except Membership.DoesNotExist:
            return redirect('/membership')
        return view_func(request, *args, **kwargs)
    return wrapper

# USAGE OF DECORATOR
@membership_required
def video(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)

    if request.user.is_authenticated:
        WatchHistory.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={'watched_on': timezone.now()}
        )

    context = {"allmovie": movie}
    return render(request, "video.html", context)


#Displays the FAQ page.
def faq(request):
    return render(request, 'faq.html')

#Displays the help center page.
def help_center(request):
    return render(request, 'help_center.html')

#Displays the terms of use page.
def terms_of_use(request):
    return render(request, 'terms_of_use.html')

#Displays the privacy policy page.
def privacy_policy(request):
    return render(request, 'privacy_policy.html')

