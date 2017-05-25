import sys

from django.conf import settings

PY2 = sys.version_info.major == 2

if PY2:
    binary_type = str
    text_type = unicode
else:
    binary_type = bytes
    text_type = str


user_model_label = getattr(settings, 'AUTH_USER_MODEL', 'auth.USER')
