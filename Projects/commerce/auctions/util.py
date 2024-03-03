from django.db.models import Max

# from .models import Listings


def current_price(listings):
    """
    Returns the current price for each listing.
    Highest bid will be used, or starting price if no bids.
    """
    # Iterate over listings
    for listing in listings:
        bids = listing.bids.all()
        # find the highest bid
        max_bid = bids.aggregate(Max("bid_amt"))["bid_amt__max"]
        # if no bids, current price is the one set by lister
        if max_bid is not None:
            return max_bid
        else:
            return listing.list_price
    