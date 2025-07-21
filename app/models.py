from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone
from datetime import timedelta

# Create your models here.

class CustomManager(models.Manager):
    def hollywood_list(self):
        return self.filter(category__exact="Hollywood")

    def anime_list(self):
        return self.filter(category__exact="Anime")
    
    def action_list(self):
        return self.filter(category__exact="Action")
    
    def comedy_list(self):
        return self.filter(category__exact="Comedy")
    
    def horror_list(self):
        return self.filter(category__exact="Horror")
    
    def scifi_list(self):
        return self.filter(category__exact="Scifi")

#This model stores information about movies.

"""
userid: A foreign key referencing the User model (indicating who uploaded the movie).
movieid: An auto-incrementing primary key.
title: The title of the movie (up to 1000 characters).
description: A description of the movie (can be left blank).
category: A field with predefined choices (like "Hollywood", "Anime", etc.).
image: An image associated with the movie (uploaded to 'photos').
video: A video file associated with the movie (uploaded to 'videos').
"""
class Movie(models.Model):
    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    movieid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=1000)
    description = models.TextField(blank=True, null=True)

    CATEGORY_CHOICES = (
        ("Hollywood", "Hollywood"),
        ("Anime", "Anime"),
        ("Action", "Action"),
        ("Comedy", "Comedy"),
        ("Horror", "Horror"),
        ("Scifi", "Scifi"),

        

    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='photos')  # Ensure this image exists
    video = models.FileField(upload_to="videos")
   
    objects = models.Manager()
    moviemanager = CustomManager()

    def __str__(self):
        return self.title


"""
This model stores the wishlist of a user for specific movies.

Fields:
        userid: A foreign key referencing the User model.
        movieid: A foreign key referencing the Movie model.
        qty: The quantity of the movie in the wishlist (default is 0).
"""
class Wishlist(models.Model):
    userid=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    movieid=models.ForeignKey(Movie,on_delete=models.CASCADE,null=True)
    qty=models.PositiveIntegerField(default=0)

"""
This model stores the subscription details for a user.

Fields:
        user: A one-to-one relationship with the User model.
        razorpay_subscription_id: The subscription ID from Razorpay.
        start_date: The date and time when the subscription started.
        end_date: The date and time when the subscription will end.
        is_active: A boolean indicating if the membership is active.

Methods:
        activate_membership: Activates the membership for a given duration (default is 30 days).
        check_membership_status: Checks if the membership is still active based on the current date.
"""

class Membership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    razorpay_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def activate_membership(self, duration_days=30):
        self.start_date = timezone.now()
        self.end_date = self.start_date + timedelta(days=duration_days)
        self.is_active = True
        self.save()

    def check_membership_status(self):
        if timezone.now() > self.end_date:
            self.is_active = False
            self.save()
        return self.is_active

    def __str__(self):
        return f"{self.user.username}'s Membership"


"""
This model keeps track of which movies a user has watched.

Fields:
        user: A foreign key referencing the User model.
        movie: A foreign key referencing the Movie model.
        watched_on: The date and time when the movie was watched.
"""
class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched_on = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'movie')  # Prevent duplicates
        ordering = ['-watched_on']

    def __str__(self):
        return f"{self.user.username} watched {self.movie.title}"
    
