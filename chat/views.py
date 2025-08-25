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
    slug_field = 'name'
    slug_url_kwarg = 'room_name'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_member'] = user in self.object.members.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user
        action = request.POST.get('action')

        if action == 'subscribe':
            self.object.members.add(user)
        elif action == 'unsubscribe':
            self.object.members.remove(user)

        return redirect('chat:chat_room', room_name=self.object.name)


class ChatCreateOrRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        room_name = request.GET.get('room_name', '').strip()
        if not room_name:
            return redirect('chat:chat_index')

        # Check if room exists
        room = ChatRoom.objects.filter(name=room_name).first()
        if room:
            return redirect('chat:chat_room', room_name=room_name)

        # Room doesn't exist, render confirmation page to create
        return render(request, 'chat/create_confirm.html', {'room_name': room_name})


class ChatCreateConfirmView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        room_name = request.POST.get('room_name').strip()
        # Create the room
        room, created = ChatRoom.objects.get_or_create(name=room_name)
        room.members.add(request.user)
        return redirect('chat:chat_room', room_name=room_name)
