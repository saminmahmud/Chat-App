from django.urls import path
from .views import *

urlpatterns = [
    path('base/', base, name="base"),
    path('', index, name="index"),
    path('home/', home, name="home"),
    path('chat/<str:group_name>/', chat_view, name='chat_view'),
    path('get_or_create_chatroom/<int:user_id>/', get_or_create_chatroomX, name='get_or_create_chatroomX'),
    path('create_groupchat/<str:group_name>/', create_groupchat, name='create_groupchat'),
    path('fileupload/<str:group_name>/', fileupload, name="fileupload"),
    path('add_friend/', add_friend, name="add_friend"),
    path('send_friend_request/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('handle_friend_request/<int:request_id>/<str:action>/', handle_friend_request, name='handle_friend_request'),
    path('add_group_member/<str:group_name>/<int:user_id>/', add_group_member, name="add_group_member")

]
