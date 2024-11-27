from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import *
from django.http import JsonResponse
from django.http import Http404
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.contrib.auth import get_user_model
User = get_user_model()



def base(request):
    user = User.objects.get(id=request.user.id)  
    return render(request, 'base.html', {'user': user})


def index(request):
    if request.user.is_authenticated:
        return redirect('home') 
    return render(request, 'index.html')


@login_required
def home(request):
    try:
        add_friend = AddFriend.objects.get(author=request.user)
        friends = add_friend.get_friends()
    except AddFriend.DoesNotExist:
        friends = User.objects.none()

    chat_groups = ChatGroup.objects.filter(members = request.user)

    return render(request, 'home.html', {
        'friends': friends, 
        'chat_groups':chat_groups, 
    })


@login_required
def chat_view(request, group_name):
    form = ChatmessageCreateForm()
    chat_group = get_object_or_404(ChatGroup, group_name=group_name)

    other_user = []

    # for private chat
    if chat_group.is_private:
        other_user = [member for member in chat_group.members.all() if member != request.user]
    
    # for group chat (public chat)
    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            chat_group.members.add(request.user)

        other_user = [member for member in chat_group.members.all()]

    chat_message = chat_group.chat_messages.all()[:30]

    add_friend = AddFriend.objects.filter(author=request.user).first()
    friends = add_friend.get_friends() if add_friend else []

    # Filter friends who are not in the chat group
    friends_to_add = [friend for friend in friends if friend not in other_user]

    return render(request, 'chat_room.html', {
        'group_name': chat_group.group_name,
        'group_chat_name': chat_group.groupchat_name,
        'chat_message': chat_message,
        'other_user':other_user,
        'add_friend_to_group': friends_to_add,
        'form': form
    })


@login_required
def get_or_create_chatroomX(request, user_id):
    # Redirect if trying to start a chat with self
    if request.user.id == user_id:
        return redirect('home')

    try:
        other_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Http404("User does not exist")

    # Fetch private chatrooms where the current user is a member
    my_chatrooms = request.user.chat_groups.filter(is_private=True)

    # Try to find an existing chatroom with the other_user
    chatroom = None
    for room in my_chatrooms:
        if other_user in room.members.all():
            chatroom = room
            break

    # If no existing chatroom, create a new one
    if not chatroom:
        chatroom = ChatGroup.objects.create(is_private=True)
        chatroom.members.add(other_user, request.user)
        chatroom.save()
    
    return redirect('chat_view', group_name=chatroom.group_name)


@login_required
def create_groupchat(request, group_name):
    try:
        chat_group = ChatGroup.objects.get(group_name= group_name)

    except:
        chat_group = ChatGroup.objects.create(
            groupchat_name = group_name,
            admin = request.user,
        )
        chat_group.members.add(request.user)
    
    return redirect('chat_view', group_name=chat_group)


@login_required
@csrf_exempt
def fileupload(request, group_name):
    chat_group = get_object_or_404(ChatGroup, group_name=group_name)

    if request.method == 'POST' and request.FILES:
        file = request.FILES['file']
        
        # Check if the file is an image
        is_image = file.content_type.startswith('image/')
        
        # Create a GroupMessage with the file and is_image flag
        message = GroupMessage.objects.create(
            file=file,
            author=request.user,
            group=chat_group,
            is_image=is_image  # Set whether the file is an image
        )

        # Notify other clients via WebSocket (broadcast message ID)
        channel_layer = get_channel_layer()
        event = {
            'type': 'message_handler',
            'message_id': message.id,  # Include the message ID in the event
        }
        async_to_sync(channel_layer.group_send)(
            chat_group.group_name,  # Ensure this is the correct channel group name
            event
        )

        return JsonResponse({'status': 'success', 'file_url': message.file.url, 'is_image': is_image, 'filename': message.filename}, status=200)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def add_friend(request):
    users = User.objects.exclude(id=request.user.id)
    try:
        add_friend = AddFriend.objects.get(author=request.user)
        friends = add_friend.get_friends()
        # Exclude users who are friends
        friends_ids = friends.values_list('id', flat=True)
        users = users.exclude(id__in=friends_ids)
    except AddFriend.DoesNotExist:
        # If AddFriend instance does not exist, use an empty QuerySet for friends
        pass

    sent_requests = FriendRequest.objects.filter(sender=request.user, accepted=False)
    sent_request_ids = sent_requests.values_list('receiver_id', flat=True)

    received_requests = FriendRequest.objects.filter(receiver=request.user, accepted=False)
    received_request_ids = received_requests.values_list('sender_id', flat=True)

    all_request_ids = list(sent_request_ids) + list(received_request_ids)
    users = users.exclude(id__in=all_request_ids)

    friend_requests = FriendRequest.objects.filter(receiver=request.user, accepted=False)
    
    return render(request, 'add_friend.html', {
        'users': users, 
        'friend_requests': friend_requests
    })


@login_required
def send_friend_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    if receiver != request.user:
        FriendRequest.objects.get_or_create(sender=request.user, receiver=receiver)
        messages.success(request, f'You have successfully send request to {receiver} as a friend!')
    return redirect('add_friend')


@login_required
def handle_friend_request(request, request_id, action):
    friend_request = get_object_or_404(FriendRequest, sender=request_id, receiver=request.user)
    if action == 'accept':
        friend_request.accepted = True
        friend_request.save()

        # Add to AddFriend 
        sender_profile, _ = AddFriend.objects.get_or_create(author=friend_request.sender)
        receiver_profile, _ = AddFriend.objects.get_or_create(author=request.user)
        sender_profile.friends.add(request.user)
        receiver_profile.friends.add(friend_request.sender)
        messages.success(request, f'Friend request accepted.')

        # now create chat for two users

        other_user = friend_request.sender
        chatroom = ChatGroup.objects.create(is_private=True)
        chatroom.members.add(other_user, request.user)
        chatroom.save()

    elif action == 'reject':
        # delete request # delete to this AddFriend 
        friend_request.delete()
        messages.success(request, f'Friend request deleted successfully.')
    
    return redirect('add_friend')


@login_required
def add_group_member(request, group_name, user_id): 
    chat_group = ChatGroup.objects.get(group_name=group_name)
    if user_id not in chat_group.members.all():
        chat_group.members.add(user_id)
    return redirect('chat_view', group_name=group_name)
    

    
