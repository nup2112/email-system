"""
Cliente API para comunicarse con el backend.
"""
import logging
import json
import requests
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Excepción para errores de la API."""
    def __init__(self, status_code=None, detail=None):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Error de API: {status_code} - {detail}")


class EmailAPIClient:
    """Cliente para interactuar con la API del sistema de emails."""
    
    def __init__(self, base_url, api_key=None):
        """
        Inicializa el cliente API.
        
        Args:
            base_url: URL base de la API
            api_key: API key para autenticación
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna los headers para las peticiones HTTP."""
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        return headers
    
    def _handle_response(self, response) -> Dict[str, Any]:
        """
        Maneja la respuesta de la API y devuelve los datos o lanza una excepción.
        
        Args:
            response: Respuesta de requests
            
        Returns:
            Dict[str, Any]: Datos de la respuesta
            
        Raises:
            APIError: Si la respuesta no es exitosa
        """
        try:
            if response.status_code >= 400:
                # Intentar obtener detalles del error
                try:
                    detail = response.json().get('detail', response.text)
                except:
                    detail = response.text
                
                raise APIError(status_code=response.status_code, detail=detail)
            
            # Retornar datos para respuestas exitosas
            return response.json()
        except requests.exceptions.JSONDecodeError:
            # Si la respuesta no es JSON válido
            if response.status_code >= 400:
                raise APIError(status_code=response.status_code, detail=response.text)
            return {"message": response.text}
    
    def check_health(self) -> Dict[str, Any]:
        """
        Verifica el estado de la API.
        
        Returns:
            Dict[str, Any]: Estado de la API
            
        Raises:
            APIError: Si hay un error en la petición
        """
        try:
            url = f"{self.base_url.replace('/api', '')}/health"
            logger.debug(f"Verificando estado de la API: {url}")
            
            response = requests.get(url)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión al verificar estado: {str(e)}")
            raise APIError(detail=f"Error de conexión: {str(e)}")
    
    def send_welcome_email(
        self, 
        company: Dict[str, Any], 
        user: Dict[str, Any], 
        dashboard_url: str
    ) -> Dict[str, Any]:
        """
        Envía un email de bienvenida.
        
        Args:
            company: Datos de la empresa
            user: Datos del usuario o usuarios
            dashboard_url: URL del dashboard
            
        Returns:
            Dict[str, Any]: Respuesta de la API
            
        Raises:
            APIError: Si hay un error en la petición
        """
        url = f"{self.base_url}/emails/welcome"
        
        query = {
            "dashboard_url": dashboard_url
        }
        
        data = {
            "company": company,
            "user": user,
            "query": query
        }
        
        try:
            logger.debug(f"Enviando petición POST a {url}")
            logger.debug(f"Datos: {json.dumps(data, indent=2)}")
            
            response = requests.post(
                url,
                json=data,
                headers=self._get_headers()
            )
            
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión: {str(e)}")
            raise APIError(detail=f"Error de conexión: {str(e)}")
    
    def send_password_reset(
        self, 
        company: Dict[str, Any], 
        user: Dict[str, Any], 
        reset_url: str,
        expires_in: int = 24
    ) -> Dict[str, Any]:
        """
        Envía un email de restablecimiento de contraseña.
        
        Args:
            company: Datos de la empresa
            user: Datos del usuario o usuarios
            reset_url: URL de restablecimiento de contraseña
            expires_in: Tiempo de expiración en horas
            
        Returns:
            Dict[str, Any]: Respuesta de la API
            
        Raises:
            APIError: Si hay un error en la petición
        """
        url = f"{self.base_url}/emails/password-reset"
        
        query = {
            "reset_url": reset_url,
            "expires_in": expires_in
        }
        
        data = {
            "company": company,
            "user": user,
            "query": query
        }
        
        try:
            logger.debug(f"Enviando petición POST a {url}")
            logger.debug(f"Datos: {json.dumps(data, indent=2)}")
            
            response = requests.post(
                url,
                json=data,
                headers=self._get_headers()
            )
            
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión: {str(e)}")
            raise APIError(detail=f"Error de conexión: {str(e)}")
    
    def send_notification(
        self, 
        company: Dict[str, Any], 
        user: Dict[str, Any], 
        notification: Dict[str, Any],
        preferences_url: str = ""
    ) -> Dict[str, Any]:
        """
        Envía un email de notificación.
        
        Args:
            company: Datos de la empresa
            user: Datos del usuario o usuarios
            notification: Datos de la notificación
            preferences_url: URL de preferencias
            
        Returns:
            Dict[str, Any]: Respuesta de la API
            
        Raises:
            APIError: Si hay un error en la petición
        """
        url = f"{self.base_url}/emails/notification"
        
        query = {
            "preferences_url": preferences_url
        }
        
        data = {
            "company": company,
            "user": user,
            "notification": notification,
            "query": query
        }
        
        try:
            logger.debug(f"Enviando petición POST a {url}")
            logger.debug(f"Datos: {json.dumps(data, indent=2)}")
            
            response = requests.post(
                url,
                json=data,
                headers=self._get_headers()
            )
            
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión: {str(e)}")
            raise APIError(detail=f"Error de conexión: {str(e)}")
    
    def send_alert(
        self, 
        company: Dict[str, Any], 
        user: Dict[str, Any], 
        alert: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Envía un email de alerta.
        
        Args:
            company: Datos de la empresa
            user: Datos del usuario o usuarios
            alert: Datos de la alerta
            
        Returns:
            Dict[str, Any]: Respuesta de la API
            
        Raises:
            APIError: Si hay un error en la petición
        """
        url = f"{self.base_url}/emails/alert"
        
        data = {
            "company": company,
            "user": user,
            "alert": alert
        }
        
        try:
            logger.debug(f"Enviando petición POST a {url}")
            logger.debug(f"Datos: {json.dumps(data, indent=2)}")
            
            response = requests.post(
                url,
                json=data,
                headers=self._get_headers()
            )
            
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión: {str(e)}")
            raise APIError(detail=f"Error de conexión: {str(e)}")
    
    def send_batch_email(
        self, 
        email_type: str, 
        company: Dict[str, Any], 
        recipients: List[Dict[str, Any]], 
        query: Dict[str, Any] = None, 
        alert: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Envía emails en lote.
        
        Args:
            email_type: Tipo de email (welcome, password-reset, notification, alert)
            company: Datos de la empresa
            recipients: Lista de destinatarios
            query: Parámetros adicionales
            alert: Datos de alerta (solo para tipo alert)
            
        Returns:
            Dict[str, Any]: Respuesta de la API
            
        Raises:
            APIError: Si hay un error en la petición
        """
        url = f"{self.base_url}/emails/batch"
        
        data = {
            "email_type": email_type,
            "company": company,
            "recipients": recipients
        }
        
        if query:
            data["query"] = query
        
        if alert:
            data["alert"] = alert
        
        try:
            logger.debug(f"Enviando petición POST a {url}")
            logger.debug(f"Datos: {json.dumps(data, indent=2)}")
            
            response = requests.post(
                url,
                json=data,
                headers=self._get_headers()
            )
            
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión: {str(e)}")
            raise APIError(detail=f"Error de conexión: {str(e)}")