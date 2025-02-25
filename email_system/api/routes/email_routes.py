"""
Rutas de API para el sistema de emails organizadas por funcionalidad.
"""
import logging
from typing import List, Dict, Any, Union, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from email_system.api.dependencies import get_api_key, get_email_service
from email_system.core.models import Company, EmailAddress, Notification, Alert
from email_system.email_service.service import EmailService
from email_system.email_service.types.templates import (
    WelcomeEmail, PasswordResetEmail, NotificationEmail, AlertEmail
)
from email_system.core.exceptions import EmailServiceError, TemplateNotFoundError
from pydantic import BaseModel, EmailStr

# Configurar logger
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/emails", tags=["emails"])

# Modelos Pydantic para la API
class CompanyBase(BaseModel):
    name: str
    address: str
    support_email: str
    website: str
    social_media: Dict[str, str] = {}
    logo_url: Optional[str] = None

class EmailAddressBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class MultiEmailAddressBase(BaseModel):
    emails: List[EmailStr]
    names: Optional[List[str]] = None
    
    def to_email_addresses(self) -> List[EmailAddress]:
        """Convierte el modelo a una lista de objetos EmailAddress"""
        result = []
        for i, email in enumerate(self.emails):
            name = None
            if self.names and i < len(self.names):
                name = self.names[i]
            result.append(EmailAddress(email=email, name=name))
        return result

class NotificationBase(BaseModel):
    title: str
    message: str
    type: str
    icon: Optional[str] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    additional_info: Optional[str] = None

class AlertBase(BaseModel):
    title: str
    message: str
    type: str = "info"
    steps: Optional[List[str]] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    contact_support: bool = True

# Función para manejar errores comunes del servicio de email
def handle_email_service_error(e: Exception) -> None:
    """Maneja errores comunes del servicio de email y lanza HTTPException apropiada."""
    logger.error(f"Error en el servicio de email: {str(e)}")
    
    if isinstance(e, TemplateNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Plantilla no encontrada: {str(e)}"
        )
    elif isinstance(e, EmailServiceError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el servicio de email: {str(e)}"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )


@router.post("/batch", status_code=status.HTTP_200_OK)
async def send_batch_emails(
    request_data: Dict[str, Any],
    email_service: EmailService = Depends(get_email_service),
    api_key: str = Depends(get_api_key)
):
    """
    Envía emails personalizados a múltiples destinatarios en un solo llamado.
    """
    try:
        # Extraer datos del cuerpo
        email_type = request_data.get("email_type")
        company_data = request_data.get("company")
        recipients_data = request_data.get("recipients", [])
        query_data = request_data.get("query", {})
        alert_data = request_data.get("alert")
        
        # Validar datos
        if not email_type:
            raise HTTPException(status_code=400, detail="email_type es requerido")
        if not company_data:
            raise HTTPException(status_code=400, detail="company es requerido")
        if not recipients_data:
            raise HTTPException(status_code=400, detail="recipients es requerido")
        
        # Convertir datos de diccionario a objetos
        company = Company(
            name=company_data.get("name", ""),
            address=company_data.get("address", ""),
            support_email=EmailAddress(
                email=company_data.get("support_email", ""),
                name=company_data.get("name", "")
            ),
            website=company_data.get("website", ""),
            social_media=company_data.get("social_media", {}),
            logo_url=company_data.get("logo_url")
        )
        
        # Validar que haya destinatarios
        if not recipients_data:
            raise HTTPException(status_code=400, detail="No se proporcionaron destinatarios")
        
        # Obtener el primer destinatario como referencia para la plantilla
        first_recipient = recipients_data[0]
        primary_user = EmailAddress(
            email=first_recipient.get("email", ""),
            name=first_recipient.get("name")
        )
        
        # Crear la instancia de email según el tipo
        if email_type == "welcome":
            if not query_data or 'dashboard_url' not in query_data:
                raise HTTPException(status_code=400, detail="dashboard_url es requerido")
                
            email_obj = WelcomeEmail(
                company=company,
                user=primary_user,
                dashboard_url=query_data.get("dashboard_url")
            )
            subject = f"¡Bienvenido a {company.name}!"
            
        elif email_type == "password-reset":
            if not query_data or 'reset_url' not in query_data:
                raise HTTPException(status_code=400, detail="reset_url es requerido")
                
            email_obj = PasswordResetEmail(
                company=company,
                user=primary_user,
                reset_url=query_data.get("reset_url"),
                expires_in=query_data.get("expires_in", 24)
            )
            subject = "Restablecimiento de contraseña"
            
        elif email_type == "notification":
            if not query_data:
                raise HTTPException(status_code=400, detail="Se requieren datos para la notificación")
                
            notification_obj = Notification(
                title=query_data.get("title", ""),
                message=query_data.get("message", ""),
                type=query_data.get("type", "info"),
                icon=query_data.get("icon"),
                action_url=query_data.get("action_url"),
                action_text=query_data.get("action_text"),
                additional_info=query_data.get("additional_info")
            )
            
            email_obj = NotificationEmail(
                company=company,
                user=primary_user,
                notification=notification_obj,
                preferences_url=query_data.get("preferences_url", "")
            )
            subject = notification_obj.title
            
        elif email_type == "alert":
            if not alert_data:
                raise HTTPException(status_code=400, detail="Se requieren datos para la alerta")
                
            alert_obj = Alert(
                title=alert_data.get("title", ""),
                message=alert_data.get("message", ""),
                type=alert_data.get("type", "info"),
                steps=alert_data.get("steps"),
                action_url=alert_data.get("action_url"),
                action_text=alert_data.get("action_text"),
                contact_support=alert_data.get("contact_support", True)
            )
            
            email_obj = AlertEmail(
                company=company,
                user=primary_user,
                alert=alert_obj
            )
            subject = alert_data.get("title", "Alerta")
            
        else:
            raise HTTPException(status_code=400, detail=f"Tipo de email no válido: {email_type}")
        
        # Enviar los emails personalizados en lote
        results = email_service.send_batch(
            email=email_obj,
            recipients=recipients_data,
            subject=subject
        )
        
        # Contar éxitos y errores
        success_count = sum(1 for r in results if isinstance(r, dict) and "id" in r)
        error_count = len(results) - success_count
        
        return {
            "status": "success", 
            "sent": success_count,
            "failed": error_count,
            "total": len(results)
        }
        
    except (EmailServiceError, TemplateNotFoundError) as e:
        handle_email_service_error(e)
    except Exception as e:
        logger.error(f"Error inesperado al enviar emails en lote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/welcome", status_code=status.HTTP_200_OK)
async def send_welcome_email(
    company: CompanyBase,
    user: Union[EmailAddressBase, MultiEmailAddressBase],
    query: Dict[str, Any],
    email_service: EmailService = Depends(get_email_service),
    api_key: str = Depends(get_api_key)
):
    """Envía un email de bienvenida."""
    try:
        company_obj = Company(**company.dict())
        
        # Procesar el o los destinatarios
        if isinstance(user, MultiEmailAddressBase):
            recipients = user.to_email_addresses()
            # Usamos el primer usuario para la plantilla
            primary_user = recipients[0]
        else:
            recipients = [EmailAddress(**user.dict())]
            primary_user = recipients[0]
        
        # Validar que se haya proporcionado dashboard_url
        if 'dashboard_url' not in query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="dashboard_url es requerido"
            )
        
        email = WelcomeEmail(
            company=company_obj,
            user=primary_user,
            dashboard_url=query.get('dashboard_url')
        )
        
        result = email_service.send(
            email=email,
            to=recipients,
            subject=f"¡Bienvenido a {company.name}!"
        )
        
        return {"status": "success", "message_id": result.get("id")}
    except (EmailServiceError, TemplateNotFoundError) as e:
        handle_email_service_error(e)
    except Exception as e:
        logger.error(f"Error al enviar email de bienvenida: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/password-reset", status_code=status.HTTP_200_OK)
async def send_password_reset(
    company: CompanyBase,
    user: Union[EmailAddressBase, MultiEmailAddressBase],
    query: Dict[str, Any],
    email_service: EmailService = Depends(get_email_service),
    api_key: str = Depends(get_api_key)
):
    """Envía un email de restablecimiento de contraseña."""
    try:
        company_obj = Company(**company.dict())
        
        # Procesar el o los destinatarios
        if isinstance(user, MultiEmailAddressBase):
            recipients = user.to_email_addresses()
            # Usamos el primer usuario para la plantilla
            primary_user = recipients[0]
        else:
            recipients = [EmailAddress(**user.dict())]
            primary_user = recipients[0]
        
        # Validar que se haya proporcionado reset_url
        if 'reset_url' not in query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="reset_url es requerido"
            )
        
        email = PasswordResetEmail(
            company=company_obj,
            user=primary_user,
            reset_url=query.get('reset_url'),
            expires_in=query.get('expires_in', 24)
        )
        
        result = email_service.send(
            email=email,
            to=recipients,
            subject="Restablecimiento de contraseña"
        )
        
        return {"status": "success", "message_id": result.get("id")}
    except (EmailServiceError, TemplateNotFoundError) as e:
        handle_email_service_error(e)
    except Exception as e:
        logger.error(f"Error al enviar email de restablecimiento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notification", status_code=status.HTTP_200_OK)
async def send_notification(
    company: CompanyBase,
    user: Union[EmailAddressBase, MultiEmailAddressBase],
    notification: NotificationBase,
    query: Dict[str, Any],
    email_service: EmailService = Depends(get_email_service),
    api_key: str = Depends(get_api_key)
):
    """Envía un email de notificación."""
    try:
        company_obj = Company(**company.dict())
        notification_obj = Notification(**notification.dict())
        
        # Procesar el o los destinatarios
        if isinstance(user, MultiEmailAddressBase):
            recipients = user.to_email_addresses()
            # Usamos el primer usuario para la plantilla
            primary_user = recipients[0]
        else:
            recipients = [EmailAddress(**user.dict())]
            primary_user = recipients[0]
        
        email = NotificationEmail(
            company=company_obj,
            user=primary_user,
            notification=notification_obj,
            preferences_url=query.get('preferences_url', '')
        )
        
        result = email_service.send(
            email=email,
            to=recipients,
            subject=notification_obj.title
        )
        
        return {"status": "success", "message_id": result.get("id")}
    except (EmailServiceError, TemplateNotFoundError) as e:
        handle_email_service_error(e)
    except Exception as e:
        logger.error(f"Error al enviar email de notificación: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alert", status_code=status.HTTP_200_OK)
async def send_alert(
    company: CompanyBase,
    user: Union[EmailAddressBase, MultiEmailAddressBase],
    alert: AlertBase,
    email_service: EmailService = Depends(get_email_service),
    api_key: str = Depends(get_api_key)
):
    """Envía un email de alerta."""
    try:
        company_obj = Company(**company.dict())
        alert_obj = Alert(**alert.dict())
        
        # Procesar el o los destinatarios
        if isinstance(user, MultiEmailAddressBase):
            recipients = user.to_email_addresses()
            # Usamos el primer usuario para la plantilla
            primary_user = recipients[0]
        else:
            recipients = [EmailAddress(**user.dict())]
            primary_user = recipients[0]
        
        email = AlertEmail(
            company=company_obj,
            user=primary_user,
            alert=alert_obj
        )
        
        result = email_service.send(
            email=email,
            to=recipients,
            subject=alert.title
        )
        
        return {"status": "success", "message_id": result.get("id")}
    except (EmailServiceError, TemplateNotFoundError) as e:
        handle_email_service_error(e)
    except Exception as e:
        logger.error(f"Error al enviar email de alerta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))