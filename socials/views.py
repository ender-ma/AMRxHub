from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages

from .models import ChatRoom, ChatMessage, ResearchGroup, FeaturedResearcher
from authentication.utils import email_verified_required

@login_required
@email_verified_required
def social_hub(request):
    """Main view for the social hub page"""
    # Get chat rooms accessible to the user
    public_rooms = ChatRoom.objects.filter(is_private=False)
    private_rooms = ChatRoom.objects.filter(is_private=True, allowed_users=request.user)
    
    # Get or create global chat room
    global_chat, created = ChatRoom.objects.get_or_create(
        name="Global Chat",
        is_private=False,
    )
    
    # Get latest messages for global chat
    latest_messages = ChatMessage.objects.filter(room=global_chat).order_by('-timestamp')[:50]
    latest_messages = reversed(list(latest_messages))  # Reverse to show oldest first
    
    # Get research groups
    research_groups = ResearchGroup.objects.annotate(member_count=Count('members'))
    user_groups = request.user.research_groups.all()
    
    # Get featured researchers
    today = timezone.now().date()
    featured_researchers = FeaturedResearcher.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).select_related('user')
    
    context = {
        'public_rooms': public_rooms,
        'private_rooms': private_rooms,
        'global_chat': global_chat,
        'latest_messages': latest_messages,
        'research_groups': research_groups,
        'user_groups': user_groups,
        'featured_researchers': featured_researchers,
    }
    
    return render(request, 'socials/social_hub.html', context)

@login_required
@email_verified_required
def chat_room(request, room_name):
    """View for a specific chat room"""
    room = get_object_or_404(ChatRoom, name=room_name)
    
    # Check if user has access to this room
    if room.is_private and not room.allowed_users.filter(id=request.user.id).exists():
        messages.error(request, "You don't have access to this chat room.")
        return redirect('socials:social_hub')
    
    # Get latest messages
    latest_messages = ChatMessage.objects.filter(room=room).order_by('-timestamp')[:50]
    latest_messages = reversed(list(latest_messages))  # Reverse to show oldest first
    
    context = {
        'room': room,
        'latest_messages': latest_messages,
    }
    
    return render(request, 'socials/chat_room.html', context)

@login_required
@email_verified_required
def join_group(request, group_id):
    """Handle joining a research group"""
    if request.method == 'POST':
        group = get_object_or_404(ResearchGroup, id=group_id)
        group.members.add(request.user)
        messages.success(request, f"You have joined the {group.name} group!")
        
    return redirect('socials:social_hub')

@login_required
@email_verified_required
def leave_group(request, group_id):
    """Handle leaving a research group"""
    if request.method == 'POST':
        group = get_object_or_404(ResearchGroup, id=group_id)
        group.members.remove(request.user)
        messages.success(request, f"You have left the {group.name} group.")
        
    return redirect('socials:social_hub')