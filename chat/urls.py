from django.urls import path
from .views import (ChatRoomDetailView,
                    ChatRoomListView,
                    ChatCreateOrRedirectView,
                    ChatCreateConfirmView)

app_name = 'chat'

urlpatterns = [
    path('', ChatRoomListView.as_view(), name='chat_index'),
    path('<int:room_id>/', ChatRoomDetailView.as_view(), name='chat_room'),
    path('create-or-redirect/', ChatCreateOrRedirectView.as_view(),
         name='create_or_redirect'),
    path('create-confirm/<int:room_id>/',
         ChatCreateConfirmView.as_view(), name='create_confirm'),
]
