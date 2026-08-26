from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared limiter instance, imported by both main.py (to register it on the
# app) and routers.py (to decorate individual endpoints). Keeping it in its
# own module avoids a circular import between the two.
limiter = Limiter(key_func=get_remote_address)