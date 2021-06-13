from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listings/<int:listing>", views.listing_page, name="listing"),
    path("listings/<int:listing>/comment", views.comment, name="comment"),
    path("listings/<int:listing>/deactivate", views.deactivate_listing, name="deactivate_listing"),
    path("listings/<int:listing>/watchlist", views.watchlist, name="watchlist"),
    path("my_watchlist", views.my_watchlist, name="my_watchlist"),
    path("categories/", views.categories, name="categories"),
    path("categories/<int:id>", views.categories_single, name="cateogries_single"),
]
