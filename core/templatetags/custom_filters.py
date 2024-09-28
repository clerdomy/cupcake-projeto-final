from django import template
import hashlib

register = template.Library()

@register.filter(name='generate_user_token')
def generate_user_token(username):
    return hashlib.md5(username.encode()).hexdigest()[:5]
