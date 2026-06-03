from django.core.management.base import BaseCommand
from socials.models import ChatRoom, ChatMessage
from django.utils import timezone
from django.db.models import Count

class Command(BaseCommand):
    help = 'Cleans old messages from global chat room'

    def handle(self, *args, **options):
        try:
            global_room = ChatRoom.objects.get(name="Global Chat", is_private=False)
            
            messages_count = ChatMessage.objects.filter(room=global_room).count()
            self.stdout.write(f"Found {messages_count} messages in Global Chat")
            
            if messages_count > 1000:
                # Get IDs of oldest messages that exceed the limit
                old_message_ids = ChatMessage.objects.filter(room=global_room).order_by('timestamp').values_list('id', flat=True)[:messages_count-1000]
                # Delete them
                deleted_count = ChatMessage.objects.filter(id__in=old_message_ids).delete()[0]
                
                self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count} old messages"))
            else:
                self.stdout.write(self.style.SUCCESS("No messages to delete"))
                
        except ChatRoom.DoesNotExist:
            self.stdout.write(self.style.ERROR("Global Chat room not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))