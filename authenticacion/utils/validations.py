from django.core.exceptions import ValidationError
import re

def validate_password_strength(password):
    """Valida la fortaleza de la contraseña."""
    if len(password) < 8:
        raise ValidationError(
            'La contraseña debe tener al menos 8 caracteres.'
        )
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError(
            'La contraseña debe contener al menos una letra mayúscula.'
        )
    
    if not re.search(r'[a-z]', password):
        raise ValidationError(
            'La contraseña debe contener al menos una letra minúscula.'
        )
    
    if not re.search(r'[0-9]', password):
        raise ValidationError(
            'La contraseña debe contener al menos un número.'
        )

def validate_phone_number(phone):
    """Valida el formato del número de teléfono."""
    pattern = r'^\+?1?\d{9,15}$'
    if not re.match(pattern, phone):
        raise ValidationError(
            'Número de teléfono inválido. Debe contener entre 9 y 15 dígitos.'
        )
