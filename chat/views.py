from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from .models import ChatRoom, ChatMessage
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from .models import ChatRoom
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect, render


class ChatRoomListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = 'chat/index.html'
    context_object_name = 'rooms'  # all chat rooms

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        subscribed_rooms = user.chat_rooms.all()  # rooms user is a member of
        other_rooms = ChatRoom.objects.exclude(pk__in=subscribed_rooms)
        context['user_chatrooms'] = subscribed_rooms
        context['other_chatrooms'] = other_rooms
        return context


class ChatRoomDetailView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = 'chat/room.html'
    pk_url_kwarg = 'room_id'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_member'] = user in self.object.members.all()
        # Pass all messages for this room, ordered by timestamp
        context['messages'] = ChatMessage.objects.filter(
            room=self.object).order_by('timestamp')
        # Pass room_id explicitly for use in template
        context['room_id'] = self.object.id
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user
        action = request.POST.get('action')

        if action == 'subscribe':
            self.object.members.add(user)
        elif action == 'unsubscribe':
            self.object.members.remove(user)

        return redirect('chat:chat_room', room_id=self.object.id)


class ChatCreateOrRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        room_name = request.GET.get('room_name', '').strip()
        if not room_name:
            return redirect('chat:chat_index')

        # Check if room exists by name
        room = ChatRoom.objects.filter(name=room_name).first()
        if room:
            # Redirect using numeric room_id for routing
            return redirect('chat:chat_room', room_id=room.id)

        # Room doesn't exist, render confirmation page to create
        return render(request, 'chat/create_confirm.html', {'room_name': room_name})


class ChatCreateConfirmView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        room_name = request.POST.get('room_name', '').strip()

        # Create or get room by name
        room, created = ChatRoom.objects.get_or_create(name=room_name)

        # Add current user as member
        room.members.add(request.user)

        # Redirect using the numeric room ID URL
        return redirect('chat:chat_room', room_id=room.id)
