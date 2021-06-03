# Imports from Django and .models

from django.contrib import admin
from .models import Listing, Comment, Bid, User

# The Models for Listing, Bid and Comment are registered here, so the admin can control them.

admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(User)
