from .models import *
from accounts.models import *
from .serializers import *
from accounts.serializers import *
from profiles.models import *
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
import os
import re
from rest_framework.permissions import IsAuthenticated
from project.permissions import IsOwner
from django.contrib.auth.decorators import permission_required
from exif import Image
from datetime import *
import datetime as d
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings              
import pytz
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from .views_functions import *

# Create your views here.
class RespondPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 1


# Set or Get photo permissions APIs
@api_view(['PUT','GET'])
@permission_classes((IsAuthenticated,))
def set_or_get_perms(request, id):

    try:
        required_photo = get_required_photo(id)

        # Only the owner is allowed to get or set perms for his/her photo
        if (required_photo.owner != request.user):
            return Response(
                 {'stat': 'fail',
                  'message': 'User does not have permission to set'
                             ' or get perms for this photo'},
                 status=status.HTTP_403_FORBIDDEN)

        # Getting photo perms
        if request.method == 'GET':

            photo_perms = PhotoPermSerializer(required_photo).data
            return Response(
                {'stat': 'ok', 'perms': photo_perms}, status=status.HTTP_200_OK)

        # Setting photo perms
        elif request.method == 'PUT':

            photo_perms = PhotoPermSerializer(
                instance=required_photo, data=request.data)
            if photo_perms.is_valid():
                #   Ensures that is_public is a boolean value and can_comment
                #   and can_addmeta values are within the choices
                save_object(photo_perms)
                return Response(
                    {'stat': 'ok', 'photo': photo_perms.data},
                    status=status.HTTP_200_OK)
            else:
                return Response(
                    {'stat': 'fail', 'message': photo_perms.errors},
                    status=status.HTTP_400_BAD_REQUEST)

    # In case object is not found, send an error message
    except ObjectDoesNotExist:
        return Response(
            {'stat': 'fail',
             'message': 'Photo not found or invalid photo ID'},
            status=status.HTTP_404_NOT_FOUND)



# Set photo meta API
@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def set_meta(request, id):

    # Check if neither the title nor the description is provided, and send an error message in this case
    if ('title' not in request.data) and ('description' not in request.data):
        return Response(
            {'stat': 'fail',
             'message': 'At least a title or a description must be provided'},
            status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            required_photo = get_required_photo(id)

            # Only the owner is allowed to set meta for his/her photo
            if (required_photo.owner != request.user):
                return Response(
                 {'stat': 'fail',
                  'message': 'User does not have permission to set'
                             ' meta for this photo'},
                 status=status.HTTP_403_FORBIDDEN)

            # Setting photo meta
            photo_meta = PhotoMetaSerializer(
                instance=required_photo, data=request.data)
            if photo_meta.is_valid():
                #   Ensures that title field has no more than 300 characters
                #   and description no more than 2000
                save_object(photo_meta)
                return Response(
                    {'stat': 'ok', 'photo': photo_meta.data},
                    status=status.HTTP_200_OK)
            else:
                return Response(
                    {'stat': 'fail', 'message': photo_meta.errors},
                    status=status.HTTP_400_BAD_REQUEST)

        # In case object is not found, send an error message
        except ObjectDoesNotExist:
            return Response(
                {'stat': 'fail',
                 'message': 'Photo not found or invalid photo ID'},
                status=status.HTTP_404_NOT_FOUND)



# Set photo dates API
@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def set_dates(request, id):

    # Check if neither date_taken nor date_posted is provided, and send an error message in this case
    if ('date_posted' not in request.data) and ('date_taken' not in request.data):
        return Response(
            {'stat': 'fail',
             'message': 'Missing requirements.'
             'At least one date must be provided'},
            status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            required_photo = get_required_photo(id)

            # Only the owner is allowed to set dates for his/her photo
            if (required_photo.owner != request.user):
                return Response(
                 {'stat': 'fail',
                  'message': 'User does not have permission to set'
                             ' dates this photo'},
                 status=status.HTTP_403_FORBIDDEN)

            photo_dates = PhotoDatesSerializer(
                instance=required_photo, data=request.data)

            if photo_dates.is_valid():
                #   Detects whether DateTime format is invalid

                # For each date provided, check whether it is in the future or way in the past
                for date in request.data:
                    if ((request.data[date] < '1970-01-01T00:00:00-05:00') or
                       (request.data[date] > str(datetime.datetime.now()))):
                        return Response(
                            {'stat': 'fail',
                             'message': 'Date posted or date taken is '
                             'in the future or way in the past'},
                            status=status.HTTP_400_BAD_REQUEST)

                # If date_taken provided is after date_posted
                if (len(request.data) == 2 and
                   request.data['date_taken'] >= request.data['date_posted']):
                    return Response({'stat': 'fail',
                                     'message': 'Date taken should be '
                                     'before date posted'},
                                    status=status.HTTP_400_BAD_REQUEST)

            #   date_posted cannot be null
            #   beacuse it is always set at uploading
            #   Check if date_taken provided is after date_posted saved
                if (len(request.data) == 1
                    and list(request.data.keys())[0] == 'date_taken'
                   and request.data['date_taken']
                   >= str(required_photo.date_posted)):
                    return Response({'stat': 'fail',
                                     'message': 'Date taken should be '
                                     'before date posted'},
                                    status=status.HTTP_400_BAD_REQUEST)

            #   Check if date_posted provided is before date_taken saved if exists
                if (len(request.data) == 1
                    and list(request.data.keys())[0] == 'date_posted'
                   and required_photo.date_taken is not None
                   and request.data['date_posted']
                   <= str(required_photo.date_taken)):
                    return Response({'stat': 'fail',
                                     'message': 'Date taken should be '
                                     'before date posted'},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Otherwise, if date(s) is/are valid, save
                save_object(photo_dates)
                return Response({'stat': 'ok',
                                 'photo': photo_dates.data},
                                status=status.HTTP_200_OK)

            else:
                return Response({'stat': 'fail',
                                 'message': photo_dates.errors},
                                status=status.HTTP_400_BAD_REQUEST)

        # In case object is not found, send an error message
        except ObjectDoesNotExist:
            return Response({'stat': 'fail',
                             'message': 'Photo not found'
                             'or invalid photo ID'},
                            status=status.HTTP_404_NOT_FOUND)



# Edit or delete photo comment APIs
@api_view(['PUT', 'DELETE'])
@permission_classes((IsAuthenticated,))
def edit_or_delete_comment(request, id):

    try:
        required_comment, photo_id, photo = get_required_comment_and_its_photo(id)

        # Editing comment
        if request.method == 'PUT':

            # Only the author of the comment can edit it
            if (required_comment.author != request.user):
                return Response(
                    {'stat': 'fail',
                    'message': 'User does not have permission'
                                ' to edit this comment'},
                    status=status.HTTP_403_FORBIDDEN)

            # If comment_text is not provided, send error message
            if ('comment_text' not in request.data):
                return Response({'stat': 'fail',
                                 'message': 'Blank Comment'},
                                status=status.HTTP_400_BAD_REQUEST)

            edited_comment = PhotoCommentSerializer(instance=required_comment,
                                                    data=request.data)

            if edited_comment.is_valid():
                #   Ensures that comment_text field
                #   has no more than 1000 characters

                save_object(edited_comment)
                return Response({'stat': 'ok', 'photo_id': photo_id,
                                 'comment': edited_comment.data},
                                status=status.HTTP_200_OK)
            else:
                return Response({'stat': 'fail',
                                 'message': edited_comment.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        
        # Deleting comment
        elif request.method == 'DELETE':

            # Only the author of the comment and the owner of the photo can delete this comment
            if (required_comment.author == request.user) or (photo.owner == request.user):
                decrement_photo_meta_counts(photo, 'comments')
                delete_object(required_comment)
                return Response({'stat': 'ok'}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'stat': 'fail',
                     'message': 'User does not have permission'
                                ' to delete this comment'},
                    status=status.HTTP_403_FORBIDDEN)

    # In case object is not found, send an error message
    except ObjectDoesNotExist:
        return Response({'stat': 'fail',
                         'message': 'Comment not found'
                         'or invalid comment ID'},
                        status=status.HTTP_404_NOT_FOUND)



# Edit or delete photo note APIs
@api_view(['PUT', 'DELETE'])
@permission_classes((IsAuthenticated,))
def edit_or_delete_note(request, id):

    try:
        required_note, photo_id, photo = get_required_note_and_its_photo(id)

        # Editting note
        if request.method == 'PUT':

            # Only the author of the note can edit it
            if (required_note.author != request.user):
                return Response(
                    {'stat': 'fail',
                     'message': 'User does not have permission'
                                ' to edit this note'},
                    status=status.HTTP_403_FORBIDDEN)

            # Check if there are any missing requirements,
            # in this case, send an error message
            if ('left_coord' not in request.data
                or 'top_coord' not in request.data
                or 'note_width' not in request.data
                or 'note_height' not in request.data
                or 'note_text' not in request.data):

                return Response({'stat': 'fail',
                                 'message': 'Missing required arguments'},
                                status=status.HTTP_400_BAD_REQUEST)

            edited_note = PhotoNoteSerializer(instance=required_note,
                                              data=request.data)

            displaypx = photo.photo_displaypx
            left_coord, top_coord, note_width, note_height = get_note_coordinates(request.data)

            if edited_note.is_valid():
                #   Detects whether a string is inserted in an integer field
                #   or a negative integer is entered or a float is entered
                #   Ensures that note_text field has no more
                #   than 1000 characters

                # Checking if note area is beyond photo area, in this case,
                # send an error message
                if ((int(left_coord) <= int(displaypx))
                    and (int(top_coord) <= 250) and
                    (int(note_width) <= int(displaypx)-int(left_coord))
                   and (int(note_height) <= 250-int(top_coord))):
                    save_object(edited_note)
                    return Response({'stat': 'ok',
                                     'photo_id': photo_id,
                                     'note': edited_note.data},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({'stat': 'fail',
                                     'message': 'Note would exceed'
                                     ' photo dimensions'},
                                    status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'stat': 'fail',
                                 'message': edited_note.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        
        # Deleting note
        elif request.method == 'DELETE':

            # Only the author of the note and the owner of the photo can delete this note
            if (required_note.author == request.user) or (photo.owner == request.user):
                decrement_photo_meta_counts(photo, 'notes')
                delete_object(required_note)
                return Response({'stat': 'ok'}, status=status.HTTP_200_OK)

            else:
                return Response(
                    {'stat': 'fail',
                     'message': 'User does not have permission'
                                ' to delete this note'},
                    status=status.HTTP_403_FORBIDDEN)

    # In case object is not found, send an error message
    except ObjectDoesNotExist:
        return Response({'stat': 'fail',
                         'message': 'Note not found'
                         ' or invalid note ID'},
                        status=status.HTTP_404_NOT_FOUND)



# Delete photo or get photo info API
@api_view(['DELETE', 'GET'])
@permission_classes((IsAuthenticated,))
def delete_photo_or_get_photo_info(request, id):

    try:
        photo_required = get_required_photo(id)

        # Deleting photo
        if request.method == 'DELETE':

            # Only the photo owner is allowed to delete it
            if (photo_required.owner != request.user):
                return Response(
                    {'stat': 'fail',
                    'message': 'User does not have permission to delete'
                                ' this photo'},
                    status=status.HTTP_403_FORBIDDEN)

            # Removing photo path locally
            remove_photo_path_locally(photo_required)
            
            # Deleting photo
            delete_object(photo_required)
            return Response({'stat': 'ok'}, status=status.HTTP_200_OK)

        # Getting photo info
        if request.method == 'GET':

            if request.user in photo_required.favourites.all():
                photo_required.is_faved= True
            else:
                photo_required.is_faved= False
                
            photo = PhotoSerializer(photo_required).data
            return Response({'stat': 'ok',
                             'photo': photo},
                            status=status.HTTP_200_OK)

    # In case object is not found, send an error message
    except ObjectDoesNotExist:
        return Response({'stat': 'fail',
                         'message': 'Photo not found'
                         ' or invalid photo ID'},
                        status=status.HTTP_404_NOT_FOUND)



# Add a photo note or get photo notes APIs
@api_view(['POST', 'GET'])
@permission_classes((IsAuthenticated,))
def add_note_or_get_photo_notes(request, id):

    try:
        photo = get_required_photo(id)

        # Adding a new note
        if request.method == 'POST':

            # Check if there are any missing requirements,
            # in this case, send an error message
            if ('left_coord' not in request.data
            or 'top_coord' not in request.data
            or 'note_width' not in request.data
            or 'note_height' not in request.data
            or 'note_text' not in request.data):

                return Response({'stat': 'fail',
                                 'message': 'Missing required arguments'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Checking permissions
            permission = get_photo_permission(photo, 'meta')
            if (permission == 'Only The Owner') and (request.user != photo.owner):
                # Only owner is allowed
                return Response(
                    {'stat': 'fail',
                     'message': 'User does not have permission to add'
                                ' notes to this photo'},
                    status=status.HTTP_403_FORBIDDEN)
            elif (permission == 'People You Follow') and ((request.user != photo.owner) or (request.user not in photo.owner.follow_follower.all())):
                # Only users in the following list and of course the photo owner are allowed
                return Response(
                    {'stat': 'fail',
                     'message': 'User does not have permission to add'
                                ' notes to this photo'},
                    status=status.HTTP_403_FORBIDDEN)

            created_note = PhotoNoteSerializer(data=request.data)

            displaypx = photo.photo_displaypx 
            left_coord, top_coord, note_width, note_height = get_note_coordinates(request.data)

            if created_note.is_valid():
                #   Detects whether a string is inserted in an integer field
                #   or a negative integer is entered or a float is entered
                #   Ensures that note_text field has no more
                #   than 1000 characters

                # Checking if note area is beyond photo area, in this case,
                # send an error message
                if ((int(left_coord) <= int(displaypx))
                            and (int(top_coord) <= 500) and
                            (int(note_width) <= int(displaypx)-int(left_coord))
                        and (int(note_height) <= 500-int(top_coord))):
                            
                            increment_photo_meta_counts(photo, 'notes')
                            created_note.save(author=request.user, photo=photo) 
                            return Response({'stat': 'ok',
                                            'photo_id': id,
                                            'note': created_note.data},
                                            status=status.HTTP_200_OK)

                else:
                    return Response({'stat': 'fail',
                                    'message': 'Note would exceed'
                                    ' photo dimensions'},
                                    status=status.HTTP_400_BAD_REQUEST)
                        
            else:
                return Response({'stat': 'fail',
                                'message': created_note.errors},
                                status=status.HTTP_400_BAD_REQUEST)

        # Getting notes list for photo
        elif request.method == 'GET':

            photo_notes = get_photo_meta_lists(id, 'notes')
            required_notes = PhotoNoteSerializer(photo_notes, many = True).data
            return Response(
                        {'stat': 'ok',
                         'photo_id': id,
                         'count_notes': photo.count_notes,
                         'notes': required_notes},
                        status=status.HTTP_200_OK)

    # In case object is not found, send an error message
    except ObjectDoesNotExist:
        return Response({'stat': 'fail',
                         'message': 'Photo not found'
                         ' or invalid photo ID'},
                        status=status.HTTP_404_NOT_FOUND)



# Add a photo comment or get photo comments APIs
@api_view(['POST', 'GET'])
@permission_classes((IsAuthenticated,))
def add_comment_or_get_photo_comments(request, id):

    try:
        photo = get_required_photo(id)

        # Adding a new comment
        if request.method == 'POST':

            # Checking permissions
            permission = get_photo_permission(photo, 'comments')
            # Only owner is allowed
            if (permission == 'Only The Owner') and (request.user != photo.owner):
                return Response(
                    {'stat': 'fail',
                     'message': 'User does not have permission to comment'
                                ' on this photo'},
                    status=status.HTTP_403_FORBIDDEN)
            # Only users in the following list and of course the photo owner are allowed
            elif (permission == 'People You Follow') and ((request.user != photo.owner) or (request.user not in photo.owner.follow_follower.all())):
                return Response(
                    {'stat': 'fail',
                     'message': 'User does not have permission to comment'
                                ' on this photo'},
                    status=status.HTTP_403_FORBIDDEN)

            # If comment_text is not in request data, send an error message
            if ('comment_text' not in request.data):
                return Response({'stat': 'fail',
                            'message': 'Blank Comment'},
                            status=status.HTTP_400_BAD_REQUEST)

            created_comment = PhotoCommentSerializer(data=request.data)

            if created_comment.is_valid():
                #   Ensures that comment_text field has no more
                #   than 1000 characters

                increment_photo_meta_counts(photo, 'comments')
                created_comment.save(author=request.user, photo=photo, date_created=datetime.datetime.now()) 
                return Response({'stat': 'ok',
                                'photo_id': id,
                                'comment': created_comment.data},
                                status=status.HTTP_200_OK)
                        
            else:
                return Response({'stat': 'fail',
                                'message': created_comment.errors},
                                status=status.HTTP_400_BAD_REQUEST)

        # Getting comments list for a photo
        elif request.method == 'GET':

            photo_comments = get_photo_meta_lists(id, 'comments')
            required_comments = PhotoCommentSerializer(photo_comments, many = True).data
            return Response(
                        {'stat': 'ok',
                        'photo_id': id,
                        'count_comments': photo.count_comments,
                        'comments': required_comments},
                        status=status.HTTP_200_OK)

    # In case object is not found, send an error message
    except ObjectDoesNotExist:
        return Response({'stat': 'fail',
                         'message': 'Photo not found'
                         ' or invalid photo ID'},
                        status=status.HTTP_404_NOT_FOUND)



# Add or get photo tags APIs
@api_view(['POST', 'GET'])
@permission_classes((IsAuthenticated,))
def add_or_get_tags(request, id):

    try:
        photo = get_required_photo(id)

        # Adding a new tag
        if request.method == 'POST':

            # Checking permissions
            permission = get_photo_permission(photo, 'meta')
            # Only owner is allowed
            if (permission == 'Only The Owner') and (request.user != photo.owner):
                return Response(
                    {'stat': 'fail',
                     'message': 'User does not have permission to add'
                                ' tags to this photo'},
                    status=status.HTTP_403_FORBIDDEN)
            # Only users in the following list and of course the photo owner are allowed
            elif (permission == 'People You Follow') and ((request.user != photo.owner) or (request.user not in photo.owner.follow_follower.all())):
                return Response(
                    {'stat': 'fail',
                     'message': 'User does not have permission to add'
                                ' tags to this photo'},
                    status=status.HTTP_403_FORBIDDEN)

            # Checking if tag(s) contain(s) any special characters, in this case,
            # send an error message
            regex = re.compile('[@!#$%^&*()<>?/\|}{~:+=`"£¬.,;]')
            if(regex.search(request.data['tag_text']) != None):
                return Response({'stat': 'fail',
                                'messages': 'This/These tags contain(s) invalid special characters.'},
                                status=status.HTTP_400_BAD_REQUEST)

            # If the maximum limit of tags for photo, has been already reached,
            # send an error message
            if Tag.objects.filter(photo_id=id).count() == 75:
                return Response({'stat': 'fail',
                                'messages': 'Maximum number of tags for this photo has been reached.'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Splitting tag_text if more than one tag is entered
            tags_text_list = split_tags(request.data)

            tags_list = {}
            count = 0
            for tag_text in tags_text_list:
                tag_data = {'tag_text': tag_text}
                created_tag = PhotoTagSerializer(data=tag_data)

                if created_tag.is_valid():
                    
                    # For the same photo, if a tag with a similar text has already been created, do not create a new one
                    # and if the maximum number of tags has been reached, do not add anymore
                    if Tag.objects.filter(photo_id=id, tag_text=tag_text).count() == 0 and Tag.objects.filter(photo_id=id).count() < 75:
                        increment_photo_meta_counts(photo, 'tags')
                        created_tag.save(author=request.user, photo=photo) 
                        tags_list[count] = created_tag.data
                        count+=1
                            
                else:
                    return Response({'stat': 'fail',
                                    'message': created_tag.errors},
                                    status=status.HTTP_400_BAD_REQUEST)

            return Response({'stat': 'ok',
                            'photo_id': id,
                            'tags_list': tags_list},
                            status=status.HTTP_200_OK)

        # Get tags list for a photo
        elif request.method == 'GET':

            photo_tags = get_photo_meta_lists(id, 'tags')
            required_tags = PhotoTagSerializer(photo_tags, many = True).data
            return Response(
                        {'stat': 'ok',
                        'photo_id': id,
                        'count_tags': photo.count_tags,
                        'tags': required_tags},
                        status=status.HTTP_200_OK)

    # In case object is not found, send an error message
    except ObjectDoesNotExist:
        return Response({'stat': 'fail',
                         'message': 'Photo not found'
                         ' or invalid photo ID'},
                        status=status.HTTP_404_NOT_FOUND)



# Remove photo tag API
@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def remove_tag(request, id):

    try:
        required_tag, photo = get_required_tag_and_its_photo(id)

        # Only the author of the tag and the owner of the photo can delete this tag
        if (required_tag.author == request.user) or (photo.owner == request.user):
            decrement_photo_meta_counts(photo, 'tags')
            required_tag.delete()
            return Response({'stat': 'ok'}, status=status.HTTP_200_OK)
        else:
            return Response(
                {'stat': 'fail',
                 'message': 'User does not have permission to delete'
                            ' this tag'},
                status=status.HTTP_403_FORBIDDEN)

    # In case object is not found, send an error message
    except ObjectDoesNotExist:
        return Response({'stat': 'fail',
                         'message': 'Tag not found'},
                        status=status.HTTP_404_NOT_FOUND)



# Tag or untag person in photo API
@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def tag_or_untag_person(request, photo_id, person_id):

    try:
        photo, person_tagged = get_photo_and_person_tagged(photo_id, person_id)

        # Tag a person in the photo
        if request.method == 'POST':

            # Checking permissions
            permission = get_photo_permission(photo, 'meta')
            # Only owner is allowed
            if (permission == 'Only The Owner') and (request.user != photo.owner):
                return Response(
                    {'stat': 'fail',
                     'message': 'User does not have permission to tag'
                                ' people to this photo'},
                    status=status.HTTP_403_FORBIDDEN)
            # Only users in the following list and of course the photo owner are allowed
            elif (permission == 'People You Follow') and ((request.user != photo.owner) or (request.user not in photo.owner.follow_follower.all())):
                return Response(
                    {'stat': 'fail',
                     'message': 'User does not have permission to tag'
                                ' peole to this photo'},
                    status=status.HTTP_403_FORBIDDEN)

            # If the maximum limit of tags for this photo has already been reached, send an error message
            if PeopleTagging.objects.filter(photo_id=photo_id).count() == 75:
                    return Response({'stat': 'fail',
                                    'messages': 'Maximum number of people to be'
                                                ' tagged in this photo has been'
                                                ' reached.'},
                                    status=status.HTTP_400_BAD_REQUEST)

            person_tagged_data = get_person_data(person_tagged)
            added_by_data = get_person_data(request.user)

            relation_data = {'photo': photo.id, 'person_tagged': person_tagged.id, 'added_by': request.user.id}
            tagging_person = PeopleTaggingSerializer(data=relation_data)
            if tagging_person.is_valid():

                # If this person has not alreday been tagged, tag them
                if PeopleTagging.objects.filter(photo=photo, person_tagged=person_tagged).count() == 0:
                    increment_photo_meta_counts(photo, 'people_tags')
                    save_object(tagging_person)
                    return Response({'stat': 'ok',
                            'photo_id': photo_id,
                            'person_tagged': person_tagged_data,
                            'added_by': added_by_data},
                            status=status.HTTP_200_OK)
                else:
                    return Response({'stat': 'fail',
                                    'message': 'Person is already tagged in that photo.'},
                                    status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'stat': 'fail',
                                'message': tagging_person.errors},
                                status=status.HTTP_400_BAD_REQUEST)

        # Untag person from photo
        elif request.method == 'DELETE':

            required_relation = PeopleTagging.objects.get(photo=photo, person_tagged=person_tagged)

            # Only the owner of the photo, the person tagged and that person who tagged
            # can delete this tagging action
            if (photo.owner == request.user) or (required_relation.added_by == request.user) or (person_tagged == request.user):
                decrement_photo_meta_counts(photo, 'people_tags')
                delete_object(required_relation)
                return Response({'stat': 'ok'}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'stat': 'fail',
                    'message': 'User does not have permission'
                               ' to untag that person.'},
                    status=status.HTTP_403_FORBIDDEN)

    # In case object is not found, send an error message
    except ObjectDoesNotExist:
        return Response({'stat': 'fail',
                         'message': 'Photo or Person not found'
                         ' or invalid photo ID or person ID'},
                        status=status.HTTP_404_NOT_FOUND)



# Get people tag in photo API
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_people_tagged(request, id):

    try:
        photo, people_tagged = get_photo_meta_lists(id, 'people_tags')

        required_people = GetPeopleTaggingSerializer(
            people_tagged, many=True).data

        # Getting people tagged list for a photo
        return Response({'stat': 'ok',
                         'photo_id': photo.id,
                         'count_people_tagged': photo.count_people_tagged,
                         'people_tagged': required_people},
                        status=status.HTTP_200_OK)

    # In case object is not found, send an error message
    except ObjectDoesNotExist:
        return Response({'stat': 'fail',
                         'message': 'Photo not found'
                         ' or invalid photo ID'},
                        status=status.HTTP_404_NOT_FOUND)



# Get recent photos API
@api_view(['GET'])
def get_recent_photos(request):

    Paginator = PageNumberPagination()
    # Maximum number of objects per page, changed as needed
    Paginator.page_size = 20

    photos = Photo.objects.filter(is_public=True).order_by('-date_posted')
    # Maximum number of objects returned in the request, changed as needed
    required_photos = limit_photos_number(photos, 1000)

    results = Paginator.paginate_queryset(required_photos, request)

    recent_photos = PhotoSerializer(results, many=True).data
    return Paginator.get_paginated_response({'stat': 'ok',
                                             'photos': recent_photos})



# Photo search API
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def search_photos(request):

    Paginator = PageNumberPagination()
    # Maximum number of objects per page, changed as needed
    Paginator.page_size = 20

    # If search_text is missing, return an error message
    if ('search_text' not in request.data):
        return Response(
                    {'stat': 'fail',
                     'message': 'search_text is missing.'},
                    status=status.HTTP_400_BAD_REQUEST)

    photo_ids_list = search_according_to_all_or_tags(request.data)

    # In case all_or_tags is neither (all) nor (tags), send an error mesage
    if (photo_ids_list == None):
        return Response(
                    {'stat': 'fail',
                     'message': 'Invalid all_or_tags input. It should contain ( tags ) or ( all ) only.'},
                    status=status.HTTP_400_BAD_REQUEST)
    
    # If search_place is not provided, send an error message
    if ('search_place' not in request.data):
        return Response(
                    {'stat': 'fail',
                     'message': 'search_place must be provided.'},
                    status=status.HTTP_400_BAD_REQUEST)

    # Searching for photos in the search_place: user's photos,
    # photos of people he/she follows, everyone's photos
    required_photos = search_in_search_place(request.data['search_place'], photo_ids_list, request.user)

    # In case search_place is none of (user), (following) ot (everyone), send an error mesage
    if (required_photos == None):
        return Response(
                    {'stat': 'fail',
                     'message': 'Invalid search_place input. It should contain ( user ) or ( following ) or ( everyone ) only.'},
                    status=status.HTTP_400_BAD_REQUEST)

    # If both upload dates and taken dates are entered, return an error message
    if ('min_upload_date' in request.data and 'min_taken_date' in request.data
       ) or ('max_upload_date' in request.data and 'max_taken_date' in request.data
       ) or ('min_upload_date' in request.data and 'max_taken_date' in request.data
       ) or ('max_upload_date' in request.data and 'min_taken_date' in request.data):
        return Response(
                    {'stat': 'fail',
                     'message': 'Enter either upload dates or taken dates, not both.'},
                    status=status.HTTP_400_BAD_REQUEST)

    # Filtering by date posted
    elif ('min_upload_date' in request.data) or ('max_upload_date' in request.data):

        if ('min_upload_date' in request.data) and ('max_upload_date' in request.data):

            # Checking validatity of DateTime format entered
            try:
                min_upload_date = datetime.datetime.strptime(request.data['min_upload_date'], '%Y-%m-%d %H:%M:%S')
                max_upload_date = datetime.datetime.strptime(request.data['max_upload_date'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return Response(
                    {'stat': 'fail',
                     'message': 'Invalid DateTime format. Valid format is: ( %Y-%m-%d %H:%M:%S )'},
                    status=status.HTTP_400_BAD_REQUEST)

            # If min date is after max date, send an error message
            if min_upload_date >= max_upload_date:
                return Response(
                    {'stat': 'fail',
                     'message': 'Illogical dates entered.'},
                    status=status.HTTP_400_BAD_REQUEST)

            required_photos = required_photos.filter(date_posted__range=(min_upload_date, max_upload_date))

        # If only one upload date is entered, send an error message
        else:
            return Response(
                    {'stat': 'fail',
                     'message': 'Either max_upload_date or min_upload_date is missing.'},
                    status=status.HTTP_400_BAD_REQUEST)

    # Filtering by date taken
    elif ('min_taken_date' in request.data) or ('max_taken_date' in request.data):

        if ('min_taken_date' in request.data) and ('max_taken_date' in request.data):

            # Checking validatity of DateTime format entered
            try:
                min_taken_date = datetime.datetime.strptime(request.data['min_taken_date'], '%Y-%m-%d %H:%M:%S')
                max_taken_date = datetime.datetime.strptime(request.data['max_taken_date'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return Response(
                    {'stat': 'fail',
                     'message': 'Invalid DateTime format. Valid format is: ( %Y-%m-%d %H:%M:%S )'},
                    status=status.HTTP_400_BAD_REQUEST)

            # If min date is after max date, send an error message
            if min_taken_date >= max_taken_date:
                return Response(
                    {'stat': 'fail',
                     'message': 'Illogical dates entered.'},
                    status=status.HTTP_400_BAD_REQUEST)

            required_photos = required_photos.filter(date_taken__range=(min_taken_date, max_taken_date))

        # If only one taken date is entered, send an error message
        else:
            return Response(
                    {'stat': 'fail',
                     'message': 'Either max_taken_date or min_taken_date is missing.'},
                    status=status.HTTP_400_BAD_REQUEST)

    # Maximum number of objects returned in the request, changed as needed
    required_photos = limit_photos_number(required_photos, 1000)
    results = Paginator.paginate_queryset(required_photos, request)

    search_photos = PhotoSerializer(results, many=True).data
    return Paginator.get_paginated_response({'stat': 'ok',
                                             'photos': search_photos})



# Rotate photo API
@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def rotate_photo(request, id):
    
    # If angle of rotation is not provided, send an error message
    if ('rotated_by' not in request.data):
        return Response(
            {'stat': 'fail',
             'message': 'Required arguments missing.'},
            status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            required_photo = get_required_photo(id)

            # Only the owner is allowed to rotate his/her photo
            if (required_photo.owner != request.user):
                return Response(
                 {'stat': 'fail',
                  'message': 'User does not have permission to'
                             ' rotate this photo'},
                 status=status.HTTP_403_FORBIDDEN)

            rotated_photo = PhotoRotationSerializer(
                instance=required_photo, data=request.data)

            if rotated_photo.is_valid():
                #   Ensures that the angle of rotation is positive and in integer form
                save_object(rotated_photo)
                return Response(
                    {'stat': 'ok', 'photo': rotated_photo.data},
                    status=status.HTTP_200_OK)
            else:
                return Response(
                    {'stat': 'fail', 'message': rotated_photo.errors},
                    status=status.HTTP_400_BAD_REQUEST)

        # In case object is not found, send an error message
        except ObjectDoesNotExist:
            return Response(
                {'stat': 'fail',
                 'message': 'Photo not found or invalid photo ID'},
                status=status.HTTP_404_NOT_FOUND)






# Favourites
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def faves_list(request):
    # get the favourites photos list for the requested user
    # GET
    user = request.user
    faves_list = user.post_favourite.all()
    serializer = PhotoMetaSerializer(
        faves_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def photo_faves(request, id):
    # get list of the users who faved a specific photo given the photo id
    try:
        photo_obj = Photo.objects.get(id=id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    users = photo_obj.favourites.all()
    serializer = OwnerSerializer(
        users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def fav_photo(request, id):
    # add or remove a specific photo to the favourites photos
    # given the photo id
    try:
        photo_obj = Photo.objects.get(id=id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        if(photo_obj.owner == request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        if request.user not in photo_obj.favourites.all():
            photo_obj.favourites.add(request.user)
            # increment the count of the users who faved this photo by 1
            photo_obj.count_favourites += 1
            photo_obj.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if request.user in photo_obj.favourites.all():
            photo_obj.favourites.remove(request.user)
            # decrement the count of the users who faved this photo by 1
            photo_obj.count_favourites -= 1
            photo_obj.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def upload_media(request):
    #upload photo one at a time
    if request.method == 'POST':
        parser_classes = (MultiPartParser, FormParser)
        serializer = PhotoUploadSerializer(data=request.data)
        user = request.user
        profile_obj = Profile.objects.get(owner=user)
        if serializer.is_valid():
            file_field = request.FILES['media_file']

            # get the type of the file from the extension
            content_type = file_field.content_type.split('/')[0]
            # check if its type is image
            if content_type in settings.IMAGE_TYPE:
                # make limitations for the free user to have less than or equal 1000 media and 200mb as a max size of the photo
                if user.is_pro is not True:
                    if profile_obj.total_media >= 1000 and file_field.size > settings.MAX_IMAGE_SIZE:
                        return Response(status=status.HTTP_400_BAD_REQUEST)

                # calculate the display pixels
                height = request.data['photo_height']
                width = request.data['photo_width']
                # pixels = (250*width)/height
                image = Image(file_field)

                # check if the image has exif to etxraxt the date taken from it  
                if(image.has_exif):

                    try:
                        datetime_str = image.datetime_original
                        # convert the string date to the needed format (UTC)
                        naive_datetime = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                        local_time = pytz.timezone("America/New_York")
                        local_datetime = local_time.localize(
                            naive_datetime, is_dst=None)
                        date_taken = local_datetime.astimezone(pytz.utc)
                    # if it doesn't have the exif or date taken set it to be null    
                    except: 
                        date_taken = None
    
                else:
                    date_taken = None
            else:
                raise ValidationError(_('File type is not supported'))

            serializer.save(photo_displaypx=0, date_taken=date_taken, owner=request.user)
            # increment the count of media 
            # profile_obj.total_media += 1
            # profile_obj.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
# Get public photos of a given user
def get_public(request, id):
    try:
        user=Account.objects.get(id=id)
        get_list = Photo.objects.filter(owner=user,is_public=True).order_by('-date_posted')
        
    except ObjectDoesNotExist:
        
        return Response(status=status.HTTP_404_NOT_FOUND)

    #  for pagination
    Paginator = RespondPagination()
    results = Paginator.paginate_queryset(get_list, request)
    photos = PhotoPermSerializer(results, many=True).data
    return Paginator.get_paginated_response({'photos': photos})


@api_view(['GET'])
#  Get public photos of loggedin user
@permission_classes((IsAuthenticated,))
def get_public_logged(request):
    try:

        get_list = Photo.objects.filter(owner=request.user,is_public=True).order_by('-date_posted')
        
        
    except ObjectDoesNotExist:
        
        return Response(status=status.HTTP_404_NOT_FOUND)

    #  for pagination
    Paginator = RespondPagination()
    results = Paginator.paginate_queryset(get_list, request)
    photos = PhotoPermSerializer(results, many=True).data
    return Paginator.get_paginated_response({'photos': photos})

@api_view(['GET'])
 #  Get all photos of loggedin user
@permission_classes((IsAuthenticated,))
def get_photos_logged(request):
    try:

        get_list = Photo.objects.filter(owner=request.user).order_by('-date_posted')
        
        
    except ObjectDoesNotExist:
        
        return Response(status=status.HTTP_404_NOT_FOUND)

    #  for pagination
    Paginator = RespondPagination()
    results = Paginator.paginate_queryset(get_list, request)
    photos = PhotoPermSerializer(results, many=True).data
    return Paginator.get_paginated_response({'photos': photos})