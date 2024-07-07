from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from .utils import *



# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'email', 'phone']


# User registeration and validator
class UserRegistrationSerializer(serializers.Serializer):
    userId = serializers.CharField(read_only=True)
    firstName = serializers.CharField(required=True)
    lastName = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    # If user validated
    def create(self, validated_data):
        # User instance
        user = User.objects.create(
            userId=generateUserID(),
            firstName=validated_data['firstName'],
            lastName=validated_data['lastName'],
            email=validated_data['email'],
            password=make_password(validated_data['password']),
            phone=validated_data.get('phone', None)
        )
        return user


# Organisation serializer
class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['orgId', 'name', 'description']