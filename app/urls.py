from django.urls import path
from . import views
from django.urls import path, include



urlpatterns = [

    path("", views.index, name="index"),
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin, name="signin"),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:username>/', views.reset_password, name='reset_password'),
    path("mainpage/", views.mainpage, name="mainpage"),
    path("membership/", views.membership, name="membership"),
    path('moviedetails/<int:movieid>/', views.moviedetails, name="moviedetails"),
    path("userlogout/", views.userlogout, name="userlogout"),
    path("hollywood/", views.hollywood, name="hollywood"),
    path("action/", views.action, name="action"),
    path("anime/", views.anime, name="anime"),
    path("comedy/", views.comedy, name="comedy"),
    path("horror/", views.horror, name="horror"),
    path("scifi/", views.scifi, name="scifi"),
    path("video/<int:movieid>",views.video,name="video"),
    path("wishlist/",views.wishlist,name="wishlist"),
    path("removefavourite/<int:movieid>",views.removefavourite,name="removefavourite"),
    path("addtofav/<int:movieid>",views.addtofav,name="addtofav"),
    path('search/', views.search_movies, name='search_movies'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('watch-history/', views.watch_history, name='watch_history'),
    path('auth/', include('social_django.urls', namespace='social')), 

    path('faq/', views.faq, name='faq'),
    path('help-center/', views.help_center, name='help_center'),
    path('terms-of-use/', views.terms_of_use, name='terms_of_use'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('category/<str:category_name>/', views.category_view, name='category'),



     
]