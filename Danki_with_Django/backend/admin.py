from django.contrib import admin
from .models import AnonymousUser, Correction, Decks, Error
# Register your models here.
admin.site.register(AnonymousUser)
admin.site.register(Correction)
admin.site.register(Decks)
admin.site.register(Error)
