from django.core.exceptions import ValidationError


def validate_zero(value):
    if value < 1:
        raise ValidationError('Введите значение больше 0!')
