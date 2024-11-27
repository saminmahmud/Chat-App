from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
import json
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
User = get_user_model()

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        print("Websocket Connectied...")
        
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name) # group_name
        
        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name,
            self.channel_name
        )

        self.seen_message() #seen message

        # update online user (add)
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
        
        self.update_online_count()

        self.accept()

    def disconnect(self, close_code):
        print("Disconnect...", close_code)
        
        # update online user (remove)
        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
        
        self.update_online_count()
        
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name,
            self.channel_name
        )


    def receive(self, text_data):
        # print("Message Recieved...", text_data)
        
        # text_data is now json format, so first convert it into python object
        text_data_json = json.loads(text_data)

        if 'body' in text_data_json:
            body = text_data_json['body']
        else:
            body = None

        # now store the message into the database
        message = GroupMessage.objects.create(
            body = body,
            author = self.user,
            group = self.chatroom
        )
        message.seen_by.add(self.user)

        event = {
            'type': 'message_handler',
            'message_id': message.id
        }
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name,
            event
        )
        
        # Notify the notification consumer to update notifications
        notification_event = {
            'type': 'update_notifications',
            'task': 'notificationformessage'
        }
        async_to_sync(self.channel_layer.group_send)(
            'notifications_group',
            notification_event
        )

    def message_handler(self, event):
        message_id = event['message_id']
        message = GroupMessage.objects.get(id=message_id)

        # Prepare the message data to send
        message_data = {
            'author': message.author.username,  # or other fields if necessary
            'profile_picture': message.author.profile_picture.url,
            'body': message.body,
            'created': message.created.strftime('%b. %d, %Y, %I:%M %p'),

            'filename': message.filename,
            'file_url': message.file.url if message.file else None,
            'is_image': message.is_image
        }

        # Send the message data as JSON
        self.send(text_data=json.dumps(message_data))
        self.seen_message()


    def update_online_count(self):
        online_count = self.chatroom.users_online.count()-1

        event = {
            'type': 'online_count_handler',
            'online_count': online_count
        }

        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name,
            event
        )

    def online_count_handler(self, event):
        online_count = event['online_count']
        
        online_count ={
            'online_count':online_count
        }

        self.send(text_data=json.dumps(online_count))

    def seen_message(self):
        #seen all messages

        messages = self.chatroom.chat_messages.all()
        for message in messages:
            if self.user not in message.seen_by.all():
                message.seen_by.add(self.user)
                message.save()


class MessageNotificationConsumer(WebsocketConsumer):
    def connect(self):
        print("Websocket Notification Connectied...")
        self.user = self.scope['user']
        self.notification_group = f'notifications_{self.user.id}'

        async_to_sync(self.channel_layer.group_add)(
            'notifications_group',
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        print("Disconnect Notification...", close_code)

        async_to_sync(self.channel_layer.group_discard)(
            'notifications_group',
            self.channel_name
        )

    def receive(self, text_data):
        # print("Message Received Notification...", text_data)

        notification_event = {
            'type': 'update_notifications',
            'task': 'notificationformessage'
        }
        async_to_sync(self.channel_layer.group_send)(
            'notifications_group',
            notification_event
        )

    def update_notifications(self, event):
        # print("Message Update Notification...", event)

        chat_groups = ChatGroup.objects.filter(members = self.user)
        data = []

        for group in chat_groups:
            last_message = group.chat_messages.order_by('-created').first()
            last_message_data = {
                'body': last_message.body if last_message else '',
                'is_image': last_message.is_image if last_message else False,
                'file': last_message.filename if (last_message and last_message.is_image) else None,
                'author': last_message.author.username if last_message else 'Unknown',
                'created_at': last_message.created.strftime('%b. %d, %Y, %I:%M %p') if last_message else None
            }

            if last_message:
                not_seen = group.chat_messages.exclude(seen_by=self.user).count()
            else:
                not_seen = 0
        
            profile_picture = None
            for member in group.members.all():
                if group.is_private:
                    if member != self.user and group.is_private == True :
                        profile_picture = member.profile_picture.url
                else:
                    profile_picture = '/media/profile_pictures/group-pic.jpg'

            group_data = {
                'group_name': group.group_name,
                'is_private': group.is_private,
                'groupchat_name': group.groupchat_name,
                'members': [member.username for member in group.members.all()],
                'last_message_data':last_message_data,
                'not_seen': not_seen,
                'profile_picture': profile_picture
            }
            data.append(group_data)

        self.send(text_data=json.dumps(data))


