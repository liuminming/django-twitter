from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework import exceptions

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserSerializerForTweet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class UserSerializerForLike(UserSerializerForTweet):
    pass


class UserSerializerForComment(UserSerializerForTweet):
    pass

class UserSerializerForFriendship(UserSerializerForTweet):
    pass

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def validate(self, data):
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'message': "This email address has been occupied."
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'This email address has been occupied.'
            })
        return data

    def create(self, validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']

        user = User.objects.create_user(
            username = username,
            email = email,
            password = password
        )
        # create UserProfile object
        user.profile
        return user

