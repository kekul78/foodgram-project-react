from django.core.exceptions import ValidationError

import re


FORBIDDEN_LETTERS = r'^[\w.@+-]+\Z'

set_of_forbidden_letters = set()


def validate_forbidden_username(value):
    for letter in list(value):
        if re.match(FORBIDDEN_LETTERS, letter) is None:
            set_of_forbidden_letters.add(letter)
    if set_of_forbidden_letters:
        raise ValidationError(
            f'Имя пользователя не может содержать {set_of_forbidden_letters}')
    return value
