# Various Django Imports. 
from django.contrib.auth.models import AbstractUser
from django.db import models

# The Listing model.
class Listing(models.Model):

    # Machine-readable codes for different categories. 
    FASHION = "FA"
    TOYS = "TO"
    ELECTRONICS = "EL"
    HOME = "HO"
    BOOKS = "BO"
    SPORTS = "SP"
    NOCHOICE = "NO"

    # Various choices that the user can select for their Category.

    CHOICES = (
        (NOCHOICE, 'No Category Listed'),
        (FASHION, 'Fashion'),
        (TOYS, 'Toys'),
        (ELECTRONICS, 'Electronics'),
        (HOME, 'Home'),
        (BOOKS, 'Books'),
        (SPORTS, 'Sports'),
    )

    category = models.CharField(
        max_length=2,
        choices=CHOICES,
        blank=True
    )
    # Various model Fields. 
    name = models.CharField(max_length=200, blank=False)
    starting_bid = models.IntegerField(blank=False)
    category = models.CharField(max_length=100, blank=True)
    picture_url = models.CharField(max_length=300, blank=True, default="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1024px-No_image_available.svg.png")

    description = models.CharField(max_length=1000, blank=False, default="Description not provided!")
    owner = models.CharField(max_length=50, default="Owner not provided!")
    is_active = models.BooleanField(default=True)
    curr_highest_bidder = models.CharField(max_length=50, default="No current highest bidder!")

    # The string representation of the class.
    def __str__(self):
        return f"{self.id} {self.name}, {self.starting_bid}, {self.category}, {self.picture_url}, {self.description}"


# The Comment Model.
class Comment(models.Model):

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments', default=1)
    comment = models.CharField(max_length=150)
    user = models.CharField(max_length=350)

    # The string representation of the class.
    def __str__(self):
        return f"{self.user}: {self.comment}"

# The Bid Model is defined here. 
class Bid(models.Model):

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default=1, related_name='bids')
    bid_amount = models.IntegerField()
    bid_owner = models.CharField(max_length=400)

    # The string representation of the class.
    def __str__(self):
        return f"{self.bid_owner}: {self.bid_amount}"

# The User Model, which inherits from Django's AbstractUser Class.
class User(AbstractUser):
    watchlist = models.ManyToManyField(Listing, blank=True, related_name='watch')



