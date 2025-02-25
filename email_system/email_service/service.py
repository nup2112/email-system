"""
Servicio de email mejorado con mejor manejo de errores, logging y configuración.
"""
import logging
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, Tuple
import resend
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from premailer import Premailer

from email_system.core.exceptions import EmailServiceError, TemplateNotFoundError
from email_system.core.models import EmailAddress
from email_system.email_service.types.base import BaseEmail
from email_system.core.config import settings

# Configurar logger
logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para envío de emails utilizando Resend con mejoras de manejo de errores."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_from: Optional[EmailAddress] = None,
        templates_dir: Optional[Union[str, Path]] = None,
        testing: bool = False
    ):
        """
        Inicializa el servicio de email.
        
        Args:
            api_key: Clave de API de Resend (usa la configuración global si es None)
            default_from: Dirección remitente predeterminada (usa la configuración global si es None)
            templates_dir: Directorio de plantillas (usa la configuración global si es None)
            testing: Si está en modo de pruebas (no envía emails realmente)
        """
        # Usar valores predeterminados de configuración si no se proporcionan
        self.api_key = api_key or settings.RESEND_API_KEY
        if not self.api_key and not testing:
            raise EmailServiceError("API key no configurada para el servicio de email")
        
        # Configurar Resend
        resend.api_key = self.api_key
        
        # Dirección remitente predeterminada
        if default_from is None:
            config_from = settings.get_default_from_address()
            self.default_from = EmailAddress(**config_from)
        else:
            self.default_from = default_from
            
        # Modo de pruebas
        self.testing = testing or settings.TESTING
        
        # Configurar directorio de templates
        if templates_dir is None:
            try:
                self.templates_dir = settings.get_templates_dir()
            except ValueError as e:
                raise EmailServiceError(f"Error al obtener el directorio de plantillas: {str(e)}")
        else:
            self.templates_dir = Path(templates_dir)
            if not self.templates_dir.exists() and not self.testing:
                raise EmailServiceError(f"El directorio de templates no existe: {self.templates_dir}")
        
        # Configurar el motor de plantillas Jinja2
        try:
            self.template_env = Environment(
                loader=FileSystemLoader(self.templates_dir),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
            logger.info(f"Motor de plantillas configurado con el directorio: {self.templates_dir}")
        except Exception as e:
            raise EmailServiceError(f"Error al configurar el motor de plantillas: {str(e)}")
    
    def _render_with_inline_styles(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Renderiza una plantilla y convierte sus estilos a inline.
        
        Args:
            template_name: Nombre del archivo de plantilla
            context: Datos para la plantilla
            
        Returns:
            str: HTML con estilos inlineados
            
        Raises:
            TemplateNotFoundError: Si no se encuentra la plantilla
            EmailServiceError: Si hay un error al renderizar o procesar estilos
        """
        try:
            # Obtener la plantilla
            template = self.template_env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFoundError(f"Plantilla no encontrada: {template_name}")
        except Exception as e:
            raise EmailServiceError(f"Error al cargar la plantilla {template_name}: {str(e)}")
            
        try:
            # Renderizar la plantilla
            html = template.render(**context)
        except Exception as e:
            raise EmailServiceError(f"Error al renderizar la plantilla {template_name}: {str(e)}")
        
        # Usar premailer para convertir estilos a inline
        try:
            premailer = Premailer(
                html,
                keep_style_tags=True,
                remove_classes=False,
                strip_important=False
            )
            return premailer.transform()
        except Exception as e:
            logger.warning(f"Error al convertir estilos a inline: {str(e)}")
            # Fallback al HTML original si hay error
            return html
    
    def _prepare_email_params(
        self,
        from_email: EmailAddress,
        to: List[EmailAddress],
        subject: str,
        html_content: str,
        cc: Optional[List[EmailAddress]] = None,
        bcc: Optional[List[EmailAddress]] = None
    ) -> Dict[str, Any]:
        """
        Prepara los parámetros para enviar un email.
        
        Args:
            from_email: Remitente
            to: Destinatarios
            subject: Asunto
            html_content: Contenido HTML
            cc: Destinatarios en copia
            bcc: Destinatarios en copia oculta
            
        Returns:
            dict: Parámetros para enviar el email
        """
        params = {
            "from": str(from_email),
            "to": [str(addr) for addr in to],
            "subject": subject,
            "html": html_content
        }
        
        if cc:
            params["cc"] = [str(addr) for addr in cc]
        if bcc:
            params["bcc"] = [str(addr) for addr in bcc]
            
        return params
    
    def send(
        self,
        email: BaseEmail,
        to: Union[EmailAddress, List[EmailAddress]],
        subject: str,
        from_email: Optional[EmailAddress] = None,
        cc: Optional[List[EmailAddress]] = None,
        bcc: Optional[List[EmailAddress]] = None,
        personalize: bool = False
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Envía un email utilizando Resend.
        
        Args:
            email: Instancia de BaseEmail con los datos del email
            to: Destinatario principal o lista de destinatarios
            subject: Asunto del email
            from_email: Remitente (opcional, usa default_from si no se especifica)
            cc: Lista de destinatarios en copia
            bcc: Lista de destinatarios en copia oculta
            personalize: Si es True, se generará un email personalizado para cada destinatario
            
        Returns:
            dict o List[dict]: Respuesta(s) de la API de Resend
            
        Raises:
            EmailServiceError: Si hay un error al enviar el email
        """
        try:
            # Validar los datos del email
            email.validate()
        except Exception as e:
            raise EmailServiceError(f"Error al validar los datos del email: {str(e)}")
        
        # Usar la dirección remitente predeterminada si no se especifica
        if not from_email:
            from_email = self.default_from
            
        # Convertir a lista si es un solo destinatario
        if not isinstance(to, list):
            to = [to]
            
        # Si no se requiere personalización, enviar email tradicional
        if not personalize:
            try:
                # Renderizar la plantilla con estilos inline
                html_content = self._render_with_inline_styles(
                    email.template_name, 
                    email.get_template_data()
                )
                
                # Preparar los parámetros para el email
                params = self._prepare_email_params(
                    from_email=from_email,
                    to=to,
                    subject=subject,
                    html_content=html_content,
                    cc=cc,
                    bcc=bcc
                )
                
                # En modo de pruebas, solo retornar los parámetros
                if self.testing:
                    return params
                
                # Enviar el email
                logger.info(f"Enviando email a {len(to)} destinatario(s)")
                return resend.Emails.send(params)
            except Exception as e:
                logger.error(f"Error al enviar email: {str(e)}")
                raise EmailServiceError(f"Error al enviar email: {str(e)}")
            
        # Si se requiere personalización, enviar emails separados a cada destinatario
        results = []
        
        for recipient in to:
            try:
                # Modificar los datos de la plantilla para este destinatario
                template_data = email.get_template_data()
                
                # Actualizar el usuario en los datos de la plantilla con este destinatario
                if 'user' in template_data:
                    template_data['user'] = {
                        'name': recipient.name or template_data['user'].get('name', 'Usuario'),
                        'email': recipient.email
                    }
                    
                # Renderizar con estilos inline
                html_content = self._render_with_inline_styles(
                    email.template_name,
                    template_data
                )
                
                # Preparar los parámetros para esta persona
                params = self._prepare_email_params(
                    from_email=from_email,
                    to=[recipient],
                    subject=subject,
                    html_content=html_content
                )
                
                # Enviar el email personalizado o retornar parámetros en modo de pruebas
                if self.testing:
                    results.append(params)
                else:
                    logger.info(f"Enviando email personalizado a {recipient.email}")
                    result = resend.Emails.send(params)
                    results.append(result)
            except Exception as e:
                logger.error(f"Error al enviar email personalizado a {recipient.email}: {str(e)}")
                # Registrar el error pero continuar con los demás destinatarios
                results.append({"error": str(e), "email": recipient.email})
                
        return results
    
    def send_batch(
        self,
        email: BaseEmail,
        recipients: List[Dict[str, Any]],
        subject: str,
        from_email: Optional[EmailAddress] = None
    ) -> List[Dict[str, Any]]:
        """
        Envía emails personalizados a múltiples destinatarios en un lote.
        
        Args:
            email: Instancia de BaseEmail con los datos del email
            recipients: Lista de diccionarios con datos de destinatarios
            subject: Asunto del email
            from_email: Remitente (opcional, usa default_from si no se especifica)
            
        Returns:
            List[dict]: Lista de resultados del envío
            
        Raises:
            EmailServiceError: Si hay un error en la configuración
        """
        try:
            # Validar los datos del email
            email.validate()
        except Exception as e:
            raise EmailServiceError(f"Error al validar los datos del email: {str(e)}")
        
        # Usar la dirección remitente predeterminada si no se especifica
        if not from_email:
            from_email = self.default_from
        
        # Validar que haya destinatarios
        if not recipients:
            raise EmailServiceError("No se proporcionaron destinatarios")
        
        # Enviar emails personalizados a cada destinatario
        results = []
        errors = 0
        successes = 0
        
        for recipient_data in recipients:
            try:
                # Validar que el destinatario tenga email
                if 'email' not in recipient_data:
                    logger.warning("Saltando destinatario sin email")
                    continue
                    
                # Crear objeto EmailAddress para este destinatario
                recipient = EmailAddress(
                    email=recipient_data['email'],
                    name=recipient_data.get('name', '')
                )
                
                # Obtener los datos base de la plantilla
                template_data = email.get_template_data()
                
                # Crear una copia de los datos de usuario para no modificar el original
                if 'user' in template_data:
                    # Crear una copia del usuario
                    user_data = dict(template_data['user'])
                    # Actualizar con los datos de este destinatario
                    user_data['name'] = recipient.name or user_data.get('name', 'Usuario')
                    user_data['email'] = recipient.email
                    # Reemplazar en los datos de la plantilla
                    template_data['user'] = user_data
                
                # Renderizar con estilos inline
                html_content = self._render_with_inline_styles(
                    email.template_name, 
                    template_data
                )
                
                # Preparar los parámetros para esta persona
                params = self._prepare_email_params(
                    from_email=from_email,
                    to=[recipient],
                    subject=subject,
                    html_content=html_content
                )
                
                # En modo de pruebas, solo retornar los parámetros
                if self.testing:
                    results.append(params)
                    successes += 1
                else:
                    try:
                        # Enviar el email
                        logger.info(f"Enviando email en lote a {recipient.email}")
                        result = resend.Emails.send(params)
                        results.append(result)
                        successes += 1
                    except Exception as e:
                        # Registrar el error pero continuar con los demás destinatarios
                        logger.error(f"Error enviando a {recipient.email}: {str(e)}")
                        results.append({"error": str(e), "email": recipient.email})
                        errors += 1
            except Exception as e:
                logger.error(f"Error al procesar destinatario: {str(e)}")
                results.append({"error": str(e)})
                errors += 1
        
        # Registrar estadísticas del envío en lote
        logger.info(f"Envío en lote completado: {successes} exitosos, {errors} errores")
        
        return results