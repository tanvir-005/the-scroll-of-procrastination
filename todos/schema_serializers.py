from rest_framework import serializers


class RegisteredUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()


class RegisterResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = RegisteredUserSerializer()