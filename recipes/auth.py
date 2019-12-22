import hashlib
import re

from django.conf import settings
from django.contrib.auth.models import User


def get_hash(user_id, lesson_id, is_menu):
    h = hashlib.sha1()
    h.update(settings.SECRET_KEY.encode("utf-8"))
    h.update(bytes(int(user_id)))
    h.update(bytes(int(lesson_id)))
    if is_menu:
        h.update(b"menu")
    return h.hexdigest()


def get_share_key(user_id, lesson_id, is_menu=False) -> str:
    hash = get_hash(user_id, lesson_id,  is_menu)
    return f"{user_id}-{'m' if is_menu else ''}{lesson_id}-{hash}"


def check_share_key(key) -> User:
    m = re.match(r"(\d+)-(m?)(\d+)-(.*)", key)
    if not m:
        return None
    user_id, is_menu, lesson_id, hash = m.groups()
    is_menu = is_menu == "m"
    check_hash = get_hash(user_id, lesson_id, is_menu)
    if hash == check_hash:
        return User.objects.get(pk=user_id)
