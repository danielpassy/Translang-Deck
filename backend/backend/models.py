from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import pre_save

MAX_USERTOKEN_LENGHT = 300


class User(AbstractUser):
    pass


class AnonymousUser(models.Model):
    """
    Store information on visitor
    """

    userID = models.CharField(max_length=MAX_USERTOKEN_LENGHT)
    timeStamp = models.DateTimeField(auto_now_add=True)


class Decks(models.Model):
    deck = models.FileField(upload_to="decks/")
    userID = models.CharField(max_length=MAX_USERTOKEN_LENGHT)
    timeStamp = models.DateTimeField(auto_now_add=True)


class Correction(models.Model):
    """
    Saves the data while waiting for the user to correct
    any error on the deck making process
    The fields deck only append by default
    """

    fields = models.CharField(max_length=10000)
    userID = models.CharField(max_length=MAX_USERTOKEN_LENGHT)
    timeStamp = models.DateTimeField(auto_now_add=True)


def append_fields(sender, instance, **kwargs):
    """
    Make any .save() operation to
    append to  fields instead of overwritting it
    """
    try:
        instance_on_db = Correction.objects.get(pk=instance.pk)
        instance.fields = instance_on_db.fields + instance.fields
    except:
        pass


pre_save.connect(append_fields, sender=Correction)


class Error(models.Model):
    TYPE_CHOICES = (
        ("Input", "Input"),
        ("Translation", "Translation"),
        ("Multiple_Translation", "Multiple Translation"),
    )

    word = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    related_correction = models.ForeignKey(
        "Correction", on_delete=models.CASCADE, related_name="errors"
    )
    timeStamp = models.DateTimeField(auto_now_add=True)

