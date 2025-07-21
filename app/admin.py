from django.contrib import admin
from .models import Movie,Wishlist
from .models import Membership

# Register your models here.
class MovieAdmin(admin.ModelAdmin):
    list_display=[
        "userid",
        "movieid",
        "title",
        "description",
        "category",
        "image",
        "video",
    ]
    
class WishlistAdmin(admin.ModelAdmin):
    list_display=[
        "userid",
        "movieid",
        "qty",
    ]
admin.site.register(Movie,MovieAdmin)
admin.site.register(Wishlist,WishlistAdmin)
admin.site.register(Membership)


from django.contrib import admin
from .models import WatchHistory

admin.site.register(WatchHistory)
