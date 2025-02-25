"""
Utilidades de validación para el sistema de emails.
"""
import re
from typing import Tuple, List, Union
import logging

logger = logging.getLogger(__name__)

# Patrón para validación de emails (RFC 5322)
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
EMAIL_REGEX = re.compile(EMAIL_PATTERN)

def validate_email(email: str) -> bool:
    """
    Valida un email según un patrón RFC 5322 simplificado.
    
    Args:
        email: Dirección de email a validar
        
    Returns:
        bool: True si el email es válido, False en caso contrario
    """
    if not email or not isinstance(email, str):
        return False
    
    return bool(EMAIL_REGEX.match(email))


def validate_emails(emails: List[str]) -> Tuple[List[str], List[str]]:
    """
    Valida una lista de emails y retorna los válidos e inválidos.
    
    Args:
        emails: Lista de direcciones de email a validar
        
    Returns:
        Tuple[List[str], List[str]]: Tupla con (emails_válidos, emails_inválidos)
    """
    valid_emails = []
    invalid_emails = []
    
    for email in emails:
        if validate_email(email):
            valid_emails.append(email)
        else:
            logger.warning(f"Email inválido: {email}")
            invalid_emails.append(email)
    
    return valid_emails, invalid_emails


def sanitize_email(email: str) -> str:
    """
    Sanitiza un email eliminando espacios y normalizando a minúsculas.
    
    Args:
        email: Dirección de email a sanitizar
        
    Returns:
        str: Email sanitizado
    """
    if not email or not isinstance(email, str):
        return ""
    
    # Eliminar espacios y convertir a minúsculas
    return email.strip().lower()


def extract_emails_from_text(text: str) -> List[str]:
    """
    Extrae emails de un texto usando expresiones regulares.
    
    Args:
        text: Texto que puede contener emails
        
    Returns:
        List[str]: Lista de emails encontrados en el texto
    """
    if not text or not isinstance(text, str):
        return []
    
    # Encontrar todos los emails en el texto
    return EMAIL_REGEX.findall(text)


def parse_emails_with_names(text: str, separators=None) -> List[Tuple[str, str]]:
    """
    Parsea un texto que contiene emails con nombres separados por delimitadores.
    
    Formato esperado: "email, nombre" o "email; nombre" por línea.
    
    Args:
        text: Texto con formato "email, nombre" por línea
        separators: Lista de separadores entre email y nombre (por defecto coma y punto y coma)
        
    Returns:
        List[Tuple[str, str]]: Lista de tuplas (email, nombre)
    """
    if not text or not isinstance(text, str):
        return []
    
    if separators is None:
        separators = [',', ';']
    
    result = []
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Buscar el primer separador en la línea
        separator_index = -1
        separator_used = None
        
        for sep in separators:
            index = line.find(sep)
            if index != -1 and (separator_index == -1 or index < separator_index):
                separator_index = index
                separator_used = sep
        
        if separator_index != -1:
            # Separar email y nombre
            email = line[:separator_index].strip()
            name = line[separator_index + len(separator_used):].strip()
        else:
            # Solo hay email, sin nombre
            email = line
            name = ""
        
        # Validar el email antes de añadirlo
        if validate_email(email):
            result.append((email, name))
    
    return result