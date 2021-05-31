from .models import *
from .serializers import *
from photo.serializers import *
from photo.models import Photo
from accounts.models import Account
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from project.permissions import IsOwner
from django.contrib.auth.decorators import permission_required
from django.db.models import Count, F, Q
# from notifications.models import Notification

# Create your views here.

# group


# get specific group
@api_view(['GET'])
def group_info(request, id):

    try:
        group_obj = group.objects.get(id=id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = GroupSerializer(group_obj)
    return Response(serializer.data, status=status.HTTP_200_OK)


# join or leave group APIs
@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def join_leave_group(request, id):

    try:
        group_obj = group.objects.get(id=id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Join group
    if request.method == 'POST':
        Members.objects.create(group=group_obj,
                               member=request.user,
                               member_type=1)
        group_obj.member_count += 1
        group_obj.save()
        return Response(status=status.HTTP_200_OK)

    # Leave group
    elif request.method == 'DELETE':
        group_member_obj = Members.objects.get(group=group_obj,
                                               member=request.user)
        group_members = Members.objects.all().filter(group=group_obj)
        number = group_members.filter(member_type__exact=2).count()

        # if the last member want to leave the group, delete the group
        if group_obj.member_count == 1:
            operation = group_obj.delete()

        # if the last admin in the group want to leave,
        # promote the oldest member to be admin
        elif group_member_obj.member_type == 2 and number == 1:
            group_member_obj1 = Members.objects.all(
                ).filter(group=group_obj,
                         member=request.user)
            operation = group_member_obj1.delete()
            group_obj.member_count -= 1
            group_obj.save()
            group_member1 = Members.objects.all().filter(group=group_obj)
            first_member = group_member1.first()
            Members.objects.filter(group=group_obj,
                                   member=first_member.member).update(
                                       member_type=2)

        else:  # member leave
            group_member_obj2 = Members.objects.all(
                ).filter(group=group_obj,
                         member=request.user)
            operation = group_member_obj2.delete()
            group_obj.member_count -= 1
            group_obj.save()

        data = {}
        operation = True
        if operation:
            data["stat"] = "ok"
        else:
            data["stat"] = "fail"
        return Response(data=data)


# get public groups user is a member of
@api_view(['GET'])
def group_list(request, id):

    paginator = PageNumberPagination()
    paginator.page_size = 10

    try:
        user_obj = Account.objects.get(id=id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    groups = user_obj.group_member.all().filter(
        Q(privacy=3) | Q(privacy=2))
    result_page = paginator.paginate_queryset(groups, request)
    serializer = GroupSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# get member list of a group
@api_view(['GET'])
def member_list(request, id):

    paginator = PageNumberPagination()
    paginator.page_size = 10

    try:
        group_obj = group.objects.get(id=id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    members = Members.objects.all().filter(group=group_obj)
    result_page = paginator.paginate_queryset(members, request)
    serializer = GroupMemberSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# By group admin only
@api_view(['PUT', 'DELETE'])
@permission_classes((IsAuthenticated,))
def member_manage(request, group_id, member_id):

    try:
        group_obj = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        member_obj = Account.objects.get(id=member_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Promote member to be admin by admin only
    if request.method == 'PUT':
        serializer = GroupMemberSerializer(data=request.data)
        if serializer.is_valid():
            Members.objects.filter(group=group_obj,
                                   member=member_obj).update(
                                       member_type=request.data['member_type'])
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete member by admin
    if request.method == 'DELETE':
        group_member_obj = Members.objects.all(
                ).filter(group=group_obj,
                         member=member_obj)
        operation = group_member_obj.delete()
        group_obj.member_count -= 1
        group_obj.save()
        data = {}
        operation = True
        if operation:
            data["stat"] = "ok"
        else:
            data["stat"] = "fail"
        return Response(data=data)


# edit group rules by group admin only
@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def edit_group_rules(request, group_id):
    try:
        group_obj = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = GroupRulesSerializer(group_obj, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# edit group name and discription by group admin only
@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def edit_group_name(request, group_id):
    try:
        group_obj = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = GroupNameSerializer(group_obj, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# edit group roles by group admin only
@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def edit_group_roles(request, group_id):
    try:
        group_obj = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = GroupRoleSerializer(group_obj, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# edit group privacy by group admin only
@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def edit_group_privacy(request, group_id):
    try:
        group_obj = group.objects.filter(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    group_obj_test = group.objects.get(id=group_id)
    serializer = GroupPrivacySerializer(data=request.data)

    if serializer.is_valid():

        if group_obj_test.privacy == 2 and (serializer.validated_data['privacy'] == 1 or serializer.validated_data['privacy'] == 3):
            group_obj.update(privacy=request.data['privacy'],
                             invitation_only=False)

        elif group_obj_test.privacy == 1 and (serializer.validated_data['privacy'] == 2 or serializer.validated_data['privacy'] == 3):
            return Response(
                 {'stat': 'fail',
                  'message': 'Private groups can not be made public.'},
                 status=status.HTTP_403_FORBIDDEN)

        elif serializer.validated_data['privacy'] == 1 or serializer.validated_data['privacy'] == 3:
            group_obj.update(privacy=request.data['privacy'],
                             invitation_only=False)

        else:
            group_obj.update(privacy=request.data['privacy'],
                             invitation_only=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def edit_group_18plus(request, group_id):
    try:
        group_obj = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = GroupSafetyLevelSerializer(group_obj, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# create group or get groups user is a member of
@api_view(['POST', 'GET'])
@permission_classes((IsAuthenticated,))
def group_get_create(request):

    if request.method == 'GET':
        user_obj = request.user
        groups = user_obj.group_member.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['privacy'] == 2:
                new_group = group.objects.create(
                    name=request.data["name"],
                    privacy=request.data['privacy'],
                    eighteenplus=request.data['eighteenplus'])
                user_obj = request.user
                new_group.invitation_only = True
                new_group.save()
                Members.objects.create(group=new_group,
                                       member=user_obj,
                                       member_type=2)
            else:
                new_group = group.objects.create(
                    name=request.data["name"],
                    privacy=request.data['privacy'],
                    eighteenplus=request.data['eighteenplus'])
                user_obj = request.user
                new_group.save()
                Members.objects.create(group=new_group,
                                       member=user_obj,
                                       member_type=2)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def find_groups(request):
    # search for a group by its title ordered from the oldest

    paginator = PageNumberPagination()
    paginator.page_size = 10

    value = request.query_params.get("name")
    groups = group.objects.filter(name__icontains=value)\
        .order_by('-date_create')
    result_page = paginator.paginate_queryset(groups, request)
    serializer = GroupSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def find_my_groups(request):
    # search for a group by its title ordered from the oldest
    # group user is a member of

    paginator = PageNumberPagination()
    paginator.page_size = 10

    user_obj = request.user
    value = request.query_params.get("name")
    groups = user_obj.group_member.all().filter(name__icontains=value)\
        .order_by('-date_create')
    result_page = paginator.paginate_queryset(groups, request)
    serializer = GroupSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Join request
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def group_join_request(request, id):

    # Check if group exists
    try:
        group_obj = group.objects.get(id=id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Get list of pending members in group
    if request.method == 'GET':
        pending_members = PendingMembers.objects.all().filter(group=group_obj)
        serializer = GroupPendingMemberSerializer(pending_members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Join group request
    elif request.method == 'POST':
        serializer = GroupPendingMemberSerializer(data=request.data)
        if serializer.is_valid():
            PendingMembers.objects.create(group=group_obj,
                                          pending_member=request.user,
                                          message=request.data['message'])
            group_obj.pending_members_count += 1
            group_obj.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete join group request
    elif request.method == 'DELETE':
        group_member_obj = PendingMembers.objects.all().filter(
            group=group_obj, pending_member=request.user)
        operation = group_member_obj.delete()
        group_obj.pending_members_count -= 1
        group_obj.save()
        data = {}
        operation = True
        if operation:
            data["stat"] = "ok"
        else:
            data["stat"] = "fail"
        return Response(data=data)


# Accept or decline join request of pending members (By admins only)
@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def group_join_request_respond(request, group_id, pending_id):

    try:
        group_obj = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        pending_member_obj = Account.objects.get(id=pending_id)
        print(pending_member_obj)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    group_member_obj = PendingMembers.objects.filter(
            group=group_obj, pending_member=pending_member_obj)

    # Accept group join request of pending member
    if request.method == 'POST':

        if not group_member_obj:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Pending member join group
        Members.objects.create(group=group_obj,
                               member=pending_member_obj,
                               member_type=1)
        group_obj.member_count += 1
        group_obj.save()

        # Delete pending member
        operation = group_member_obj.delete()
        group_obj.pending_members_count -= 1
        group_obj.save()
        data = {}
        operation = True
        if operation:
            data["stat"] = "ok"
        else:
            data["stat"] = "fail"
        return Response(data=data)

    # Delete join group request
    elif request.method == 'DELETE':
        if not group_member_obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        operation = group_member_obj.delete()
        group_obj.pending_members_count -= 1
        group_obj.save()
        data = {}
        operation = True
        if operation:
            data["stat"] = "ok"
        else:
            data["stat"] = "fail"
        return Response(data=data)


# Topic
# create topic
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def create_topic(request, group_id):

    try:
        group_obj = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = TopicSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(group=group_obj,
                        owner=request.user)
        group_obj.topic_count += 1
        group_obj.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# get list of topics in specific group
@api_view(['GET'])
def topic_list(request, group_id):

    try:
        group_obj = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    paginator = PageNumberPagination()
    paginator.page_size = 10

    group_topic = group_obj.group_topic.all()
    result_page = paginator.paginate_queryset(group_topic, request)
    serializer = TopicSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# get topic info
@api_view(['GET'])
def topic_info(request, group_id, topic_id):

    try:
        group_obj = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        group_topic = group_obj.group_topic.get(id=topic_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = TopicSerializer(group_topic)
    return Response(serializer.data)


# edit or delete topic
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticated,))
def edit_delete_topic(request, group_id, topic_id):

    try:
        group_obj = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        group_topic = group_obj.group_topic.get(id=topic_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        if (group_topic.owner != request.user):
            return Response(
                 {'stat': 'fail',
                  'message': 'User does not have permission to edit'
                             '  this topic'},
                 status=status.HTTP_403_FORBIDDEN)
        serializer = TopicSerializer(group_topic, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if (group_topic.owner != request.user):
            return Response(
                 {'stat': 'fail',
                  'message': 'User does not have permission to delete'
                             '  this topic'},
                 status=status.HTTP_403_FORBIDDEN)
        operation = group_topic.delete()
        group_obj.topic_count -= 1
        group_obj.save()
        data = {}
        if operation:
            data["stat"] = "ok"
        else:
            data["stat"] = "fail"
        return Response(data=data)


# replies
# create new reply
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def create_reply(request, group_id, topic_id):

    try:
        group_detail = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        group_topic = group_detail.group_topic.get(id=topic_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ReplySerializer(data=request.data)
    if serializer.is_valid():
        topic_obj2 = group.objects.filter(id=topic_id)
        reply_obj = reply.objects.create(
            message=request.data['message'],
            topic=group_topic,
            owner=request.user
        )
        group_topic.last_reply = request.user 
        group_topic.count_replies += 1
        group_topic.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# get list of replies in specific topic
@api_view(['GET'])
def reply_list(request, group_id, topic_id):

    try:
        group_detail = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        group_topic = group_detail.group_topic.get(id=topic_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    paginator = PageNumberPagination()
    paginator.page_size = 10
    group_topic_reply = group_topic.group_topic_reply.all()
    result_page = paginator.paginate_queryset(group_topic_reply, request)
    serializer = ReplySerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# get reply info
@api_view(['GET'])
def reply_info(request, group_id, topic_id, reply_id):

    try:
        group_detail = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        group_topic = group_detail.group_topic.get(id=topic_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        group_topic_reply = group_topic.group_topic_reply.get(id=reply_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ReplySerializer(group_topic_reply)
    return Response(serializer.data)

@api_view(['GET'])
def find_topic(request,group_id):
    # search for a topic by its message ordered from the oldest
    try:
        group_detail = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    value = request.query_params.get("message")
    try: 
        topics = topic.objects.filter(message__icontains=value, group=group_detail)\
        .order_by('-date_create')
    except:
       return Response(status=status.HTTP_404_NOT_FOUND)
            
    serializer = TopicSerializer(topics, many=True)
    return Response(serializer.data)

# @api_view(['GET'])
# def find_pools(request,group_id):
#     # search for a topic by its message ordered from the oldest
#     try:
#         group_detail = group.objects.get(id=group_id)
#     except ObjectDoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     value = request.query_params.get("message")
#     try: 
#         topics = topic.objects.filter(message__icontains=value, group=group_detail)\
#         .order_by('-date_create')
#     except:
#        return Response(status=status.HTTP_404_NOT_FOUND)
            
#     serializer = TopicSerializer(topics, many=True)
#     return Response(serializer.data)



# edit or delete reply
@api_view(['PUT', 'DELETE'])
@permission_classes((IsAuthenticated,))
def edit_delete_reply(request, group_id, topic_id, reply_id):

    try:
        group_detail = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        group_topic = group_detail.group_topic.get(id=topic_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        group_topic_reply = group_topic.group_topic_reply.get(id=reply_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        if (group_topic_reply.owner != request.user):
            return Response(
                 {'stat': 'fail',
                  'message': 'User does not have permission to edit'
                             '  this reply'},
                 status=status.HTTP_403_FORBIDDEN)
        serializer = ReplySerializer(group_topic_reply, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if (group_topic_reply.owner != request.user):
            return Response(
                 {'stat': 'fail',
                  'message': 'User does not have permission to delete'
                             '  this reply'},
                 status=status.HTTP_403_FORBIDDEN)
        operation = group_topic_reply.delete()
        group_topic.count_replies -= 1
        group_topic.save()
        data = {}
        if operation:
            data["stat"] = "ok"
        else:
            data["stat"] = "fail"
        return Response(data=data)


# pools
# get list of photos in a specific group given the group id
@api_view(['GET'])
def group_photos(request, group_id):
    try:
        group_obj = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    # GET
    photos = group_obj.photos.all()
    serializer = PhotoMetaSerializer(photos, many=True)
    return Response(serializer.data)


# add or remove a specific photo in a specific gallery given their ids
@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def group_photo(request,  group_id,  photo_id):
    try:
        group_obj = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    try:
        photo_obj = Photo.objects.get(id=photo_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # put a flag to see whether the photo is already in the group or not
    photos = group_obj.photos.all()
    if photo_obj in photos:
        exist = True
    else:
        exist = False
    user_obj = request.user

    # no of groups a photo is added to (differ if member is pro or no-pro)
    if user_obj.is_pro:
        photo_group_limit = 60
    else:
        photo_group_limit = 30

    # 2 options:
    if request.method == 'POST':
        # 1) add his own photo to a group he is a member of
        # checks: photo does not exist in the group and
        #  limitation to user type
        if ((photo_obj.owner == request.user) and (not exist) and
                ((photo_obj.group_count) <= photo_group_limit)):

            photo_obj.group_photos.add(group_obj)

            # increment the count of photos in that group by 1 and save
            group_obj.pool_count += 1
            group_obj.save()

            # increment the number of groups a photo is added to by 1 and save
            photo_obj.group_count += 1
            photo_obj.save()

            return Response(status=status.HTTP_201_CREATED)

        # 2) add someone's photo to a group you're a member of 
        # (pending request: owner should accept first)
        # elif ((photo_obj.owner != request.user) and (not exist) and
        #         ((photo_obj.group_count) <= photo_group_limit)):
        #     Notification.objects.create(sender=user_obj, user=photo_obj.owner,
        #                                 photo=photo_obj, group=group_obj,
        #                                 notification_type=6)
        #     return Response(status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    #   DELETE
    elif request.method == 'DELETE':
        if exist:
            photo_obj.group_photos.remove(group_obj)
            # decrement the count of photos in that group by 1 and save
            group_obj.pool_count -= 1
            group_obj.save()
            # decrement the number of groups a photo is added to by 1 and save
            photo_obj.group_count += 1
            photo_obj.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


# get list of groups you can add someone's photos to
# you need permission from photo's owner
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def group_photo_list(request):
    user_obj = request.user
    member_obj = Members.objects.all().filter(member=user_obj, member_type=2)
    serializer = GroupMemberListSerializer(member_obj, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Accept or decline invite request to add photo to a group (By photo owner)
@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def group_photo_request_respond(request, group_id, photo_id, sender_id):

    try:
        group_obj = group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        photo_obj = Photo.objects.get(id=photo_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        sender_obj = Account.objects.get(id=sender_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Accept group join request of pending member

    # put a flag to see whether the photo is already in the group or not
    photos = group_obj.photos.all()
    if photo_obj in photos:
        exist = True
    else:
        exist = False
    user_obj = request.user

    # number of groups a photo is added to (differ if member is pro or no-pro)
    if user_obj.is_pro:
        photo_group_limit = 60
    else:
        photo_group_limit = 30

    if request.method == 'POST':

        if ((not exist) and ((photo_obj.group_count) <= photo_group_limit)):

            photo_obj.group_photos.add(group_obj)

            # increment the count of photos in that group by 1 and save
            group_obj.pool_count += 1
            group_obj.save()

            # increment the number of groups a photo is added to by 1 and save
            photo_obj.group_count += 1
            photo_obj.save()

            # delete notification
            # notify = Notification.objects.filter(photo=photo_obj,
            #                                      sender=sender_obj,
            #                                      user=photo_obj.owner,
            #                                      notification_type=6)
            # notify.delete()
            return Response(
                 {'stat': 'ok',
                  'message': 'photo owner accept invite request and photo added to group'},
                 status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        # delete notification
        # notify = Notification.objects.filter(photo=photo_obj,
        #                                      sender=sender_obj,
        #                                      user=photo_obj.owner,
        #                                      notification_type=6)
        # notify.delete()
        return Response(
            {'stat': 'ok',
             'message': 'photo owner decline invite request'},
            status=status.HTTP_200_OK)
