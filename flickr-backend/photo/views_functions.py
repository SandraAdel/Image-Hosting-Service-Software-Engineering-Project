from .models import *
from accounts.models import *
from profiles.models import *
import os


def search_in_search_place(search_place, photo_ids_list, user):

    following_list_ids = []
    following_list = user.follow_follower.all()
    for following in following_list:
        following_list_ids.append(following.id)

    if (search_place == 'user'):

        required_photos = Photo.objects.filter(is_public=True, owner_id=user.id, id__in=photo_ids_list).order_by('-date_posted')
        return required_photos

    elif (search_place == 'following'):

        required_photos = Photo.objects.filter(is_public=True, owner_id__in=following_list_ids, id__in=photo_ids_list).order_by('-date_posted')
        return required_photos

    elif (search_place == 'everyone'):

        following_list_ids.append(user.id)
        ids_list = following_list_ids
        required_photos = Photo.objects.filter(is_public=True, id__in=photo_ids_list).exclude(owner_id__in=ids_list).order_by('-date_posted')
        return required_photos

    else:
        return None


def search_according_to_all_or_tags(request_data):

    # Searching for search_text in title, description & tags OR tags only
    list = request_data['search_text'].split()
    photo_ids_list = []

    # If all_or_tags is not provided or is set to (all),
    # search for search_text in title, description & tags
    if ('all_or_tags' not in request_data) or (request_data['all_or_tags'] == 'all'):

        for text in list:
            photos = Photo.objects.filter(title__icontains=text) | Photo.objects.filter(description__icontains=text)
            for photo in photos:
                photo_ids_list.append(photo.id)
            tags = Tag.objects.filter(tag_text__icontains=text)
            for tag in tags:
                photo_ids_list.append(tag.photo_id)  

        return  photo_ids_list

   # If all_or_tags is set to (tags),
   # search for search_text in tags ONLY
    elif (request_data['all_or_tags'] == 'tags'):

        for text in list:
            tags = Tag.objects.filter(tag_text__icontains=text)
            for tag in tags:
                photo_ids_list.append(tag.photo_id)
        
        return  photo_ids_list

    else:
        return None


def limit_photos_number(photos, max_limit):

    required_photos_ids_list = []
    count = 1
    for photo in photos:
        if count <= max_limit:
            required_photos_ids_list.append(photo.id)
            count += 1

    required_photos = Photo.objects.filter(id__in=required_photos_ids_list).order_by('-date_posted')
    return required_photos


def get_required_photo(id):

    required_photo = Photo.objects.get(id=id)
    return required_photo


def get_required_comment_and_its_photo(id):

    required_comment = Comment.objects.get(comment_id=id)
    photo_id = required_comment.photo_id
    photo = Photo.objects.get(id=photo_id)
    return required_comment, photo_id, photo


def get_required_note_and_its_photo(id):

    required_note = Note.objects.get(note_id=id)
    photo_id = required_note.photo_id
    photo = Photo.objects.get(id=photo_id)
    return required_note, photo_id, photo


def get_required_tag_and_its_photo(id):

    required_tag = Tag.objects.get(tag_id=id)
    photo_id = required_tag .photo_id
    photo = Photo.objects.get(id=photo_id)
    return required_tag, photo


def get_photo_and_person_tagged(photo_id, person_id):

    photo = Photo.objects.get(id=photo_id)
    person_tagged = Account.objects.get(id=person_id)
    return photo, person_tagged


def get_note_coordinates(request_data):

    left_coord = request_data['left_coord']
    top_coord = request_data['top_coord']
    note_width = request_data['note_width']
    note_height = request_data['note_height']
    return left_coord, top_coord, note_width, note_height


def remove_photo_path_locally(photo):

    media_file = photo.media_file
    os.remove('media/' + str(media_file))


def get_photo_permission(photo, perm):

    if (perm == 'comments'):
        return photo.can_comment
    elif (perm == 'meta'):
        return photo.can_addmeta

def increment_photo_meta_counts(photo, meta):

    if (meta == 'notes'):
        photo.count_notes += 1
    elif (meta == 'comments'):
        photo.count_comments +=1
    elif (meta == 'tags'):
        photo.count_tags += 1
    elif (meta == 'people_tags'):
        photo.count_people_tagged += 1
    
    photo.save()


def decrement_photo_meta_counts(photo, meta):

    if (meta == 'notes'):
        photo.count_notes -= 1
    elif (meta == 'comments'):
        photo.count_comments -=1
    elif (meta == 'tags'):
        photo.count_tags -= 1
    elif (meta == 'people_tags'):
        photo.count_people_tagged -= 1
    
    photo.save()


def get_photo_meta_lists(id, meta):

    if (meta == 'notes'):
        photo_notes = Note.objects.filter(photo_id = id)
        return photo_notes
    elif (meta == 'comments'):
        photo_comments = Comment.objects.filter(photo_id = id)
        return photo_comments
    elif (meta == 'tags'):
        photo_tags = Tag.objects.filter(photo_id = id)
        return photo_tags
    elif (meta == 'people_tags'):
        photo = Photo.objects.get(id=id)
        people_tagged = photo.people_tagged.all()
        return photo, people_tagged


def split_tags(request_data):

    list = request_data['tag_text'].split()
    tags_text_list = []
    for tag_text in list:
        tags_text_list.append(tag_text.lower())
    return tags_text_list


def get_person_data(person):

    person_data = {'id': person.id,
                          'email': person.email,
                          'username': person.username,
                          'first_name': person.first_name,
                          'last_name': person.last_name,
                          'age': person.age,
                          'is_pro': person.is_pro,
                          'login_from': person.login_from}
    return person_data



def delete_object(object):

    object.delete()


def save_object(object):

    object.save()
