from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Categories(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Listings(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="listings"
    )
    item = models.CharField(max_length=64)
    list_price = models.DecimalField(decimal_places=2, max_digits=8)
    highest_bid = models.DecimalField(
        decimal_places=2, 
        max_digits=8, 
        null=True,
        blank=True
    )
    description = models.CharField(max_length=500)
    image = models.URLField(max_length=500)
    category = models.ForeignKey(
        Categories, 
        on_delete=models.CASCADE, 
        related_name="listings", 
        null=True, 
        blank = True
    )
    created = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.item}"
    
    # Define a function to calculate the highest bid
    def update_highest_bid(self, bid_amt):
        if not self.highest_bid or bid_amt > self.highest_bid:
            self.highest_bid = bid_amt
            self.save()


class Bids(models.Model):
    bid_amt = models.DecimalField(decimal_places=2, max_digits=8)
    bid_time = models.DateTimeField()
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="bids"
    )
    listing = models.ForeignKey(
        Listings, 
        on_delete=models.CASCADE, 
        related_name="bids"
    )

    def __str__(self):
        return f"{self.user} bid {self.bid_amt} on {self.listing} @ {self.bid_time}"


class Comments(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="comments"
    )
    comment = models.CharField(max_length=500)
    comment_time = models.DateTimeField()
    listing = models.ForeignKey(
        Listings, 
        on_delete=models.CASCADE, 
        related_name="comments"
    )

    def __str__(self):
        return f"{self.user} commented on {self.listing} @ {self.comment_time}"


class Watchlist(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="watchlist"
    )
    item = models.ForeignKey(
        Listings, 
        on_delete=models.CASCADE, 
        related_name="watchlist"
    )

    def __str__(self):
        return f"{self.item} is on {self.user}'s Watchlist"