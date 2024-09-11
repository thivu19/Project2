from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class AuctionList(models.Model):
    CATEGORIES = {
        "Accessories": "Accessories",
        "Clothing": "Clothing",
        "Electronics": "Electronics",
        "Home": "Home",
        "Shoes": "Shoes",
        "Sports": "Sports",
        "Toys": "Toys",
        "Others": "Others",
    }
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null= True, related_name="winner")

    available = models.BooleanField(default=True)
    bid = models.IntegerField(default=0)
    name = models.CharField(max_length=64)
    image = models.ImageField(default="fallback.png", blank=True)
    description = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=12, choices=CATEGORIES, default="Others")

    def __str__(self):
        return f"{self.id} {self.name}"

class Bid(models.Model):
    bid = models.IntegerField()
    listing_bid = models.ForeignKey(AuctionList, on_delete=models.CASCADE, related_name="bids")
    auctioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctioner")

    def __str__(self):
        return f"{self.auctioner} bid {self.bid} on {self.listing_bid}"

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    message = models.CharField(max_length=200)
    comment_on = models.ForeignKey(AuctionList, on_delete=models.CASCADE, related_name="comment_on")

    def __str__(self):
        return f"{self.commenter} {self.comment_on} {self.message}"
    
class WatchList(models.Model):
    watcher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watcher")
    listings = models.ManyToManyField(AuctionList, blank=True, related_name="listings")

    def __str__(self):
        return f"{self.watcher}"