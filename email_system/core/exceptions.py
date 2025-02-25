"""
Excepciones personalizadas para el sistema de emails.
Centraliza todas las excepciones específicas de la aplicación.
"""


class EmailSystemError(Exception):
    """Excepción base para todas las excepciones del sistema de emails."""
    def __init__(self, message: str = "Error en el sistema de emails"):
        self.message = message
        super().__init__(self.message)


class ConfigurationError(EmailSystemError):
    """Excepción para errores de configuración."""
    def __init__(self, message: str = "Error de configuración"):
        self.message = message
        super().__init__(self.message)


class ValidationError(EmailSystemError):
    """Excepción para errores de validación."""
    def __init__(self, message: str = "Error de validación"):
        self.message = message
        super().__init__(self.message)


class EmailServiceError(EmailSystemError):
    """Excepción para errores en el servicio de email."""
    def __init__(self, message: str = "Error en el servicio de email"):
        self.message = message
        super().__init__(self.message)


class TemplateNotFoundError(EmailServiceError):
    """Excepción para cuando no se encuentra una plantilla."""
    def __init__(self, message: str = "Plantilla no encontrada"):
        self.message = message
        super().__init__(self.message)


class EmailDeliveryError(EmailServiceError):
    """Excepción para errores de entrega de email."""
    def __init__(self, message: str = "Error al entregar el email"):
        self.message = message
        super().__init__(self.message)


class APIError(EmailSystemError):
    """Excepción para errores en la API."""
    def __init__(self, message: str = "Error en la API", status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(APIError):
    """Excepción para errores de autenticación."""
    def __init__(self, message: str = "Error de autenticación"):
        super().__init__(message, status_code=401)


class AuthorizationError(APIError):
    """Excepción para errores de autorización."""
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, status_code=403)


class ResourceNotFoundError(APIError):
    """Excepción para cuando no se encuentra un recurso."""
    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message, status_code=404)


class BadRequestError(APIError):
    """Excepción para peticiones incorrectas."""
    def __init__(self, message: str = "Petición incorrecta"):
        super().__init__(message, status_code=400)