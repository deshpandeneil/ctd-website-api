from django.db.models import fields
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class AccountSerializer(serializers.ModelSerializer):
    class ProfileSerializer(serializers.ModelSerializer):
        senior = serializers.NullBooleanField()

        class Meta:
            model = Profile
            fields = ['reg_no', 'country_code', 'phone_no', 'senior']

    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'profile']

    @staticmethod
    def create(validated_data):
        profile_data = validated_data.pop('profile')
        user_instance = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user_instance, **profile_data)
        return user_instance


class EventLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLine
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ['event_password']


# class MultipleEventsOrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MultipleEventsOrder
#         fields = '__all__'
