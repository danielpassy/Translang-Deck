from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
import json
from os.path import join, basename
from os import environ
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView


from rest_framework import status
from AnkiCardOTron import AnkiCardOTron
from DankiBackEnd import settings
from .serializers import DeckSerializer, CorrectionSerializer, ErrorSerializer
from .models import Decks, Correction, Error
from .util import get_create_uuidd, FileValidator

# loggin
import logging

logger = logging.getLogger(__file__)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class GetCSRFToken(APIView):
    def get(self, request, format=None):
        return Response({"success": "CSRF cookie set"})


def some_view(request):
    """
    Example view showing all the ways you can log messages.
    """
    logger.debug("This logs a debug message.")
    return HttpResponse("this worked")


def testEnv(request):
    """ for Debug purpose """
    a = environ["FOO"]
    return HttpResponse(f"the env value is {a}")


@api_view(["POST"])
@csrf_protect
def request_deck(request, method):
    # check for UID, if not present, create one.
    userID = get_create_uuidd(request)

    if method == "file":
        try:
            file = request.FILES["file"]
        except KeyError:
            return Response(
                "You need to upload a file", status=status.HTTP_400_BAD_REQUEST
            )

        file_handler = FileValidator()
        valid_file = file_handler.is_valid(file)
        if not valid_file:
            return Response(file_handler.error, status=status.HTTP_400_BAD_REQUEST)
        else:
            ankitron_instance = AnkiCardOTron.AnkiCardOTron(file_path=file, in_memory=1)

    # TODO: is it needed to implement input sanitizing?
    elif method == "list":
        try:
            word_list = request.data["word_list"]
        except KeyError:
            return Response(
                "You need to upload a file", status=status.HTTP_400_BAD_REQUEST
            )
        ankitron_instance = AnkiCardOTron.AnkiCardOTron(
            word_list=word_list, in_memory=1
        )

    # perform the translation
    ankitron_instance.translate()
    # in the case some correction is needed
    if ankitron_instance.number_errors() > 0:

        # field
        fields = ankitron_instance.serialize()
        correction = Correction.objects.create(fields=fields, userID=userID)
        errors = ankitron_instance.errors()
        error_instance_list = []
        for error in errors:
            error_instance_list.append(
                Error.objects.create(
                    word=error["word"],
                    type=error["type"],
                    related_correction=correction,
                )
            )

        # retrieve the instance on the DB to account for the errors
        correction_updated = Correction.objects.get(pk=correction.pk)
        serializer = CorrectionSerializer(correction_updated)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # FIND A WAY TO TRANSLATE OONLY WHAT IS NEEDED!
    # TODO: CHANGE GENERATE TOGETHER WITH PATH, UPLOAD CHANGE TO PACKAGE ASWEL.

    deck_path = ankitron_instance.generate_deck(settings.MEDIA_ROOT)
    # get only the deck name
    deck_name = basename(deck_path)
    db_object = Decks.objects.create(userID=userID, deck=deck_name)
    serializer = DeckSerializer(db_object)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@csrf_protect
def correct(request):
    """
    Receive the correction data from the user
    attempts to do the process again
    return the deck or another request for corrections

    fields: ID (deck ID)
            errors
                word
                correction
    if any of the errors is ommited, it's, then, discarted


    """
    userID = get_create_uuidd(request)
    data = request.data

    # ---------------------- Start of Checks ---------------------------------- #

    # check for the Correction object in the db
    if not "id" in data.keys():
        try:
            corrections = Correction.objects.filter(userID=userID)
            if len(corrections) == 0:
                raise ObjectDoesNotExist
            options = str([correction.pk for correction in corrections])
            options = options[1:-1]
            return Response(
                f"You need to specify the id of the Deck, options: {options}",
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ObjectDoesNotExist:
            return Response(
                "You need to specify the id of the Deck",
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Check for corrections in the input
    try:
        word_list = data["errors"]
    except KeyError:
        return Response(
            "You need to input 'errors' dict with the 'correction' and the 'word' is attempts to correct",
            status=status.HTTP_400_BAD_REQUEST,
        )
    # Check if the user is owner of the Correction object
    try:
        correction = Correction.objects.get(pk=data["id"])
        if correction.userID != userID:
            return Response(
                "You have no permission to correct this Deck",
                status=status.HTTP_400_BAD_REQUEST,
            )
    except ObjectDoesNotExist:
        return Response(
            f"The Deck with {data['id']} doesn't exist, we only keep decks for 1 hour"
        )

    # check for the presence of correction in every error entry
    for entry in data["errors"]:
        try:
            if not entry["correction"]:
                return Response(
                    f"You must insert a correction for the word {entry['word']} or delete this error entry if you want to ignore it",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            corrections = True
        except KeyError:
            # in case there're no corrections to be issued.
            corrections = False

    # --------------------- End of Checks ---------------------------------- #

    # if the user input corrections
    if not corrections:
        ankitron_instance = AnkiCardOTron.AnkiCardOTron(empty=True)
        Error.objects.filter(pk=correction.pk).delete()

    if corrections:
        word_list = [entry["correction"] for entry in data["errors"]]

        # proccess news words
        ankitron_instance = AnkiCardOTron.AnkiCardOTron(
            word_list=word_list, in_memory=True
        )
        ankitron_instance.translate()

        # delete old errors
        Error.objects.filter(related_correction=correction.pk).delete()

        # in the case some correction is needed
        if ankitron_instance.number_errors() > 0:

            # get the new words
            fields = ankitron_instance.serialize()

            # modify for the new entries.
            correction.fields = fields
            correction.save()

            errors = ankitron_instance.errors()
            error_instance_list = []
            # deleted the old errors first.
            for error in errors:
                error_instance_list.append(
                    Error.objects.create(
                        word=error["word"],
                        type=error["type"],
                        related_correction=correction,
                    )
                )
            # retrieve the instance on the DB to account for the errors
            correction_updated = Correction.objects.get(pk=correction.pk)
            serializer = CorrectionSerializer(correction_updated)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # in the obscure event that everything works just fine.
    previous_word = correction.fields
    ankitron_instance.deserialize(previous_word)
    deck_path = ankitron_instance.generate_deck(settings.MEDIA_ROOT)

    # get only the deck name
    deck_name = basename(deck_path)

    # save to the db, delete the related fields
    db_object = Decks.objects.create(userID=userID, deck=deck_name)
    correction.delete()
    serializer = DeckSerializer(db_object)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# View to return the static front-end code
def index(request):
    try:
        with open(join(settings.STATIC_ROOT, "build", "index.html")) as f:
            return HttpResponse(f.read())
    except FileNotFoundError:
        return HttpResponse(
            f"{(join(settings.STATIC_ROOT, 'build'))}",
            status=501,
        )
