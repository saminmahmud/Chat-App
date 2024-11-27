from django.contrib import admin
from .models import *

class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'group_name', 'groupchat_name', 'is_private']

admin.site.register(ChatGroup, ChatGroupAdmin)
admin.site.register(GroupMessage)
admin.site.register(AddFriend)
admin.site.register(FriendRequest)