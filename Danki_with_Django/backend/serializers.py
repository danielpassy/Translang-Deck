from rest_framework import serializers
from .models import Decks, Correction, Error


class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Decks
        fields = ("deck", "id")


class ErrorSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()
    correction = serializers.CharField(default="")

    class Meta:
        model = Error
        fields = ("message", "correction", "type", "id", "word")
        extra_kwargs = {
            "message": {"read_only": True},
            "correction": {"read_only": True}
        }

    def get_message(self, obj):
        if obj.type == "Input":
            return "The token was not identified as Hebrew"
        elif obj.type == "Translation":
            return "Translation not Found"
        elif obj.type == "Multiple_Translation":
            return "There multiple translation option"
        else:
            raise Exception(
                f"The type of the db Error entry with ID {obj.id} is not valid"
            )


class CorrectionSerializer(serializers.ModelSerializer):
    errors = ErrorSerializer(many=True)

    class Meta:
        model = Correction
        fields = ("fields", "userID", "id", "errors")
        extra_kwargs = {"fields": {"write_only": True}}


    def create(self, validated_data):
        errors = validated_data["errors"]
        correction = validated_data.pop('errors')
        content_hotel = Correction.objects.create(**validated_data)

        for error in errors:
            Error.objects.create(related_correction=content_hotel, **error)

        return content_hotel
