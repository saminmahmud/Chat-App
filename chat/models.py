from django.db import models
import shortuuid
import os
from PIL import Image
from django.contrib.auth import get_user_model
User = get_user_model()


class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, unique=True, blank=True, default=shortuuid.uuid)
    groupchat_name = models.CharField(max_length=128, null=True, blank=True)
    admin = models.ForeignKey(User, related_name='groupchats', blank=True, null=True, on_delete=models.SET_NULL)
    users_online = models.ManyToManyField(User, related_name='online_in_groups', blank=True)
    members = models.ManyToManyField(User, related_name='chat_groups', blank=True)
    is_private = models.BooleanField(default=False)
    
    def __str__(self):
        return self.group_name

class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=300, blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    is_image = models.BooleanField(default=False) 
    created = models.DateTimeField(auto_now_add=True)
    seen_by = models.ManyToManyField(User, related_name='seen_messages', blank=True)
    
    is_seen = models.BooleanField(default=False)

    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None

    def __str__(self):
        if self.body:
            return f'{self.group.id} --> {self.author.username} : {self.body}'
        elif self.file:
            return f'{self.group.id} --> {self.author.username} : {self.filename}'
        return "No content"
    
    class Meta:
        ordering = ['-created'] # ordering by new to old messages

    def is_image_file(self):
        try:
            # Open the file and verify if it is an image
            with Image.open(self.file) as img:
                img.verify()
            return True
        except (IOError, SyntaxError) as e:
            # If an error occurs, it means the file is not an image
            return False

    def save(self, *args, **kwargs):
        if self.file:
            self.is_image = self.is_image_file()  # Set the is_image field based on whether the file is an image
        
        super().save(*args, **kwargs)  # Call the original save method


class FriendRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"

class AddFriend(models.Model):
    author = author = models.ForeignKey(User, on_delete=models.CASCADE)
    friends = models.ManyToManyField(User, related_name='add_friend', blank=True)

    def __str__(self):
        return self.author.username
    
    def get_friends(self):
        return self.friends.all()


