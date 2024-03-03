from django.contrib import admin
from .models import Listings, Categories, User, Bids, Comments, Watchlist

# Register your models here.
admin.site.register(Listings)
admin.site.register(Categories)
admin.site.register(User)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(Watchlist)
