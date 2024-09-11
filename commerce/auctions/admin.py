from django.contrib import admin
from .models import AuctionList, Bid, Comment, User, WatchList

class AuctionListAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "bid", "seller", "winner", "available")

class BidAdmin(admin.ModelAdmin):
    list_display = ("auctioner", "bid", "listing_bid")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("commenter", "message", "comment_on")


# Register your models here.
admin.site.register(AuctionList, AuctionListAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User)
admin.site.register(WatchList)