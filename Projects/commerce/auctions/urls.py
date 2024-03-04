from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:id>", views.listing_page, name="listing_page"),
    path("closed", views.closed, name="closed"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category_list", views.category_list, name="category_list"),
    path("category/<str:name>", views.category_page, name="category_page")
]
