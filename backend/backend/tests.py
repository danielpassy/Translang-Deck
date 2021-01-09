from django.test import TestCase
from django.urls import reverse
from django.test import Client
from rest_framework.test import APITestCase
from rest_framework.test import RequestsClient
from rest_framework import status
from .models import Decks, Correction
from .serializers import DeckSerializer
from .util import get_create_uuidd
from django.core.files.uploadedfile import SimpleUploadedFile
import os
import csv
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest

# Create your tests here.
class FileInputError(APITestCase):
    def setUp(self):

        self.file_name = ["only_hebrew_words.csv", "one_word_latin.csv", "empty.csv"]

        # create the first file.
        words = ["שלום", "מצב", "להישאר", "פִּתְאוֹם"]
        with open(self.file_name[0], "w", encoding="utf-8-sig") as csvfile:
            spamwriter = csv.writer(
                csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
            )
            for word in words:
                spamwriter.writerow([word])

        self.hebrew_data = open("only_hebrew_words.csv", "rb")

        # create the second file.
        words = ["שלום", "מצב", "להישאר", "asdasds...,"]
        with open(self.file_name[1], "w", encoding="utf-8-sig") as csvfile:
            spamwriter = csv.writer(
                csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
            )
            for word in words:
                spamwriter.writerow([word])

        self.one_word_latin = open("one_word_latin.csv", "rb")

        # create the third file
        words = []
        with open(self.file_name[2], "w", encoding="utf-8-sig") as csvfile:
            spamwriter = csv.writer(
                csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
            )
            for word in words:
                spamwriter.writerow([word])
        self.empty = open("empty.csv", "rb")

    def test_empty_file(self):
        response = self.client.post(
            reverse("input", args=["file"]), {"file": self.empty}, format="multipart"
        )
        self.assertEqual(response.status_code, 200)

    def test_upload_csv_no_error(self):
        # A csv that produces no error
        response = self.client.post(
            reverse("input", args=["file"]),
            {"file": self.hebrew_data},
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)

    def test_upload_csv_1_error(self):
        # A csv that produces an error and should return the correction data
        response = self.client.post(
            reverse("input", args=["file"]),
            {"file": self.one_word_latin},
            format="multipart",
        )
        self.assertEqual(response.status_code, 200)
        data = response.data["errors"]
        self.assertEqual(data[0]["type"], "Input")

    def test_upload_csv_multiple_Error(self):
        right_words = ["שלום", "מצב", "להישאר", "פתאום"]
        wrong_words = ["asdoasjd", "as", ""]
        with open("test.csv", "w", encoding="utf-8-sig") as csvfile:
            spamwriter = csv.writer(
                csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
            )
            for word in [right_words] + [wrong_words]:
                # no reason why *2, but it's suppose to generate 4 errors.
                spamwriter.writerow(word * 2)

        with open("test.csv", "rb") as csvfile:
            response = self.client.post(
                reverse("input", args=["file"]),
                {"file": csvfile},
                format="multipart",
            )

        # this is dangerous
        os.remove("test.csv")
        self.assertEqual(response.status_code, 200)
        data = response.data["errors"]
        self.assertEqual(len(data), 4)

    def tearDown(self):
        self.hebrew_data.close()
        self.empty.close()
        self.one_word_latin.close()
        for file in self.file_name:
            os.remove(file)


class session(object):
    """
    fake sesison boject
    """

    def __init__(self, word):
        self.userID = word


class TestSession(APITestCase):
    """
    Test session for the session cookie implementation
    """

    def setUp(self):

        self.session = self.client.session
        words = ["שלום", "מצב", "להישאר", "פתאום"]
        self.request = self.client.post(
            reverse("input", args=["list"]), {"word_list": words}, format="json"
        )
        self.request.session = {}

    def test_create_id(self):
        retrieve_id = get_create_uuidd(self.request)
        self.assertTrue(type(retrieve_id) == str)

    def test_retrieve_id(self):
        # define session
        id = "123123123"
        self.session["userID"] = id
        self.session.save()
        self.request.session = self.session

        retrieve_id = get_create_uuidd(self.request)
        self.assertTrue(retrieve_id == id)


class ListInputError(APITestCase):
    def test_list_no_error(self):
        words = ["שלום", "מצב", "להישאר", "פתאום"]
        response = self.client.post(
            reverse("input", args=["list"]), {"word_list": words}, format="json"
        )
        self.assertEqual(response.status_code, 201)

    def test_list_1_error(self):
        words = ["שלום", "מצב", "להישאר", "פתאום", "asdasd"]
        response = self.client.post(
            reverse("input", args=["list"]), {"word_list": words}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.data["errors"]
        self.assertEqual(data[0]["type"], "Input")
        self.assertEqual(data[0]["word"], "asdasd")


class Correction(APITestCase):
    def setUp(self):
        words = ["שלום", "מצב", "להישאר", "פתאום", "asdasd"]
        wrong_word = ["asdasd"]
        self.response = self.client.post(
            reverse("input", args=["list"]), {"word_list": words}, format="json"
        )

    def test_missing_id_no_suggestion(self):
        self.client2 = Client()
        errors = self.response.data["errors"]
        errors[0]["correction"] = "שתיתי"
        self.response2 = self.client2.post(
            reverse("correct"), {"errors": errors}, format="json"
        )
        self.assertEqual(self.response2.data, "You need to specify the ID of the Deck")

    def test_missing_id_one_suggestion(self):
        """
        When attempting to correct without the ID
        When there's only 1 correction available under this session
        """
        errors = self.response.data["errors"]
        errors[0]["correction"] = "שתיתי"
        self.response2 = self.client.post(
            reverse("correct"), {"errors": errors}, format="json"
        )
        self.assertEqual(
            self.response2.data, "You need to specify the ID of the Deck, options: 1"
        )

    def test_missing_id_two_suggestion(self):
        """
        When attempting to correct without the ID
        When there's only 2 correctionS available under this session
        """

        words = ["שלום", "מצב", "להישאר", "פתאfום", "asdasd"]
        wrong_word = ["asdasd"]
        self.response2 = self.client.post(
            reverse("input", args=["list"]), {"word_list": words}, format="json"
        )

        errors = self.response.data["errors"]
        errors[0]["correction"] = "שתיתי"
        self.response3 = self.client.post(reverse("correct"), {}, format="json")
        self.assertEqual(
            self.response3.data, "You need to specify the ID of the Deck, options: 1, 2"
        )

    def test_not_the_owner(self):
        """
        When the user request a correction for a deck that is not his

        """
        self.client2 = Client()
        errors = self.response.data["errors"]
        errors[0]["correction"] = "שתיתי"
        self.response2 = self.client2.post(
            reverse("correct"), {"ID": 1, "errors": errors}, format="json"
        )
        self.assertEqual(
            self.response2.data, "You have no permission to correct this Deck"
        )

    def test_correction_dont_exist(self):
        """
        When the correction id doesnt match any
        """
        errors = self.response.data["errors"]
        errors[0]["correction"] = "שתיתי"
        self.response2 = self.client.post(
            reverse("correct"), {"ID": 3, "errors": errors}, format="json"
        )
        self.assertEqual(
            self.response2.data,
            "The Deck with 3 doesn't exist, we only keep decks for 1 hour",
        )

    def test_missing_one_correction(self):
        """
        When one correction is missing
        """
        errors = self.response.data["errors"]
        errors[0]["correction"] = []
        self.response2 = self.client.post(
            reverse("correct"), {"ID": 1, "errors": errors}, format="json"
        )
        self.assertEqual(
            self.response2.data,
            f"You must inser a correction for the word {errors[0]['word']} \
                or delete this error entry if you want to ignore it",
        )

    def test_still_needing_correction(self):
        """
        When the input still produces an error
        """
        errors = self.response.data["errors"]
        errors[0]["correction"] = "asdasd"
        self.response2 = self.client.post(
            reverse("correct"), {"ID": 1, "errors": errors}, format="json"
        )
        self.assertEqual(
            self.response2.data["errors"][0]["message"],
            "The token was not identified as Hebrew",
        )

    def test_no_errors(self):
        """
        When there's no errors dict
        """
        nothing = {}
        self.response2 = self.client.post(
            reverse("correct"), {"ID": self.response.data["id"]}, format="json"
        )
        self.assertEqual(
            self.response2.data,
            "You need to input 'errors' dict with the 'correction' and the 'word' is attempts to correct",
        )

    def test_correction_latin(self):

        # attempt to correct the word.
        errors = self.response.data["errors"]
        errors[0]["correction"] = "שתיתי"
        self.response2 = self.client.post(
            reverse("correct"),
            {"errors": errors, "ID": self.response.data["id"]},
            format="json",
        )
        self.assertEqual(self.response2.status_code, 201)

    def test_postList(self):
        pass
        # succeed
        # data = [
        #     "שד",
        #     "שדגשדג שדג ש",
        #     "שדגש שד",
        #     "גש דגשד שדג",
        #     "שדג שדג שדג",
        #     "שדגש דג שדג",
        # ]
        # response = self.client.post(reverse("input", args=["list"]), {"word_list": data})
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # # fail
        # response = self.client.post(reverse("input", args=["list"]), {"word_list": []})
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrievingMultipleFiles(self):
        pass

    def test_uploadFile(self):
        pass

    def test_retrieveFile(self):
        pass

    def test_WordList(self):
        pass

    def test_invalidWordList(self):
        pass

    # def tearDown(self):
    #     self.hebrew_data.close()
    #     self.one_word_latin.close()
    #     for file in self.file_name:
    #         os.remove(file)