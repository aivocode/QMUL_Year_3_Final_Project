from ..models import *
from django import template


register = template.Library()


@register.filter(name='is_employer')
def is_employer(request_user):
    return EmployerProfile.objects.filter(user_id=request_user.id).exists()

@register.filter(name='is_candidate')
def is_candidate(request_user):
    return CandidateProfile.objects.filter(user_id=request_user.id).exists()


@register.simple_tag
def new_messages_count(receiver, sender):
    return Message.objects.filter(receiver=receiver, sender=sender, has_been_read=False).count()
