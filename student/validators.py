from django.core.exceptions import ValidationError

import re

def validateUsername(username):
    pattern = r'^(u\d{8}|csshare[0-9]+)$'
    if not re.match(username, pattern):
        raise ValidationError(
            message="請輸入有效的學號!!"
        )