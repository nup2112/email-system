"""
Dependencias para la API FastAPI.
Centraliza las funciones que se usan como dependencias en los endpoints.
"""
import logging
from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader

from email_system.core.exceptions import AuthenticationError
from email_system.email_service.service import EmailService
from email_system.core.config import settings
from email_system.core.models import EmailAddress

# Configurar logger
logger = logging.getLogger(__name__)

# Configuración de seguridad
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)


async def get_api_key(api_key: str = Depends(api_key_header)):
    """
    Verifica que la API key sea válida.
    
    Args:
        api_key: API key proporcionada en el header
        
    Returns:
        str: API key si es válida
        
    Raises:
        HTTPException: Si la API key es inválida
    """
    if api_key != settings.API_KEY:
        logger.warning(f"Intento de acceso con API key inválida")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key inválida",
            headers={"WWW-Authenticate": "APIKey"},
        )
    return api_key


def get_email_service() -> EmailService:
    """
    Retorna una instancia configurada del servicio de email.
    
    Returns:
        EmailService: Instancia del servicio de email
        
    Raises:
        HTTPException: Si hay un error al crear el servicio
    """
    try:
        # Obtener la API key de la configuración
        api_key = settings.RESEND_API_KEY
        if not api_key:
            raise ValueError("RESEND_API_KEY no configurada")
        
        # Crear la dirección de email predeterminada
        default_from_data = settings.get_default_from_address()
        default_from = EmailAddress(**default_from_data)
        
        # Crear y retornar el servicio
        return EmailService(
            api_key=api_key,
            default_from=default_from,
            templates_dir=settings.get_templates_dir(),
            testing=settings.TESTING
        )
    except Exception as e:
        logger.error(f"Error al crear el servicio de email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al configurar el servicio de email: {str(e)}"
        )