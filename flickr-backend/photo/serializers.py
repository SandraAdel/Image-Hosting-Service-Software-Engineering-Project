from rest_framework import serializers
from .models import *
from profiles.serializers import *


# Serializers define the API representation.
# Serializers define the API representation.
class PhotoPermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = [
            'id', 'is_public',
            'can_comment', 'can_addmeta']


class PhotoMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'title', 'description']


class PhotoDatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'date_taken', 'date_posted']


class PhotoCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['comment_id', 'author', 'date_created', 'comment_text']
        extra_kwargs={'author': {'read_only':True}, 'photo':{'read_only':True}}


class PhotoNoteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Note
        fields = [
            'note_id', 'author', 'left_coord', 'top_coord',
            'note_width', 'note_height', 'note_text']
        extra_kwargs={'author': {'read_only':True}, 'photo':{'read_only':True}}


class PhotoTagSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Tag
        fields = ['tag_id', 'author', 'tag_text']
        extra_kwargs={'author': {'read_only':True}, 'photo':{'read_only':True}}


class PeopleTaggingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeopleTagging
        fields = ['photo', 'person_tagged', 'added_by']


class GetPeopleTaggingSerializer(serializers.ModelSerializer):
    person_tagged = UserSerializer(read_only=True)
    added_by = UserSerializer(read_only=True)
    class Meta:
        model = PeopleTagging
        fields = ['photo', 'person_tagged', 'added_by']


class PhotoSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    photo_comments = PhotoCommentSerializer(read_only=True, many=True)
    photo_notes = PhotoNoteSerializer(read_only=True, many=True)
    photo_tags = PhotoTagSerializer(read_only=True, many=True)
    people_tagged = GetPeopleTaggingSerializer(read_only=True, many=True)
    favourites = UserSerializer(read_only=True, many=True)
    class Meta:
        model = Photo
        fields = ['id', 'owner', 'title', 'description',
                  'is_public', 'can_comment', 'can_addmeta',
                  'count_comments', 'photo_comments',
                  'count_notes', 'photo_notes',
                  'count_tags', 'photo_tags',
                  'count_people_tagged', 'people_tagged',
                  'count_favourites', 'favourites','is_faved',
                  'date_posted', 'date_taken', 'last_update',
                  'photo_height', 'photo_width', 'photo_displaypx',
                  'photo_url']


class PhotoRotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'rotated_by']

   
   
class PhotoUploadSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    class Meta:
        model = Photo
        fields = [
            'id', 'media_file', 'photo_displaypx', 'photo_height', 'photo_width',
            'is_public', 'date_taken', 'title', 'description','date_posted','owner']
        #   add tags
        extra_kwargs = {
            'photo_displaypx': {'read_only': True},
            'date_taken': {'read_only': True},
            'owner': {'read_only': True}}