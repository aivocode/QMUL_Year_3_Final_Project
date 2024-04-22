from .models import Message

def unread_messages(request):
    unread_messages = 0
    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(
            receiver=request.user, has_been_read=False
        ).count()
    return {'unread_messages': unread_messages}
