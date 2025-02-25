"""
Configuración centralizada para el sistema de emails.
Carga variables de entorno y proporciona valores predeterminados.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailSystemSettings(BaseSettings):
    """Configuración global del sistema de emails."""
    # API Keys y seguridad
    API_KEY: str = Field(default="")
    RESEND_API_KEY: str = Field(default="")
    
    # Valores predeterminados para el servicio de email
    DEFAULT_FROM_EMAIL: str = Field(default="no-reply@example.com")
    DEFAULT_FROM_NAME: str = Field(default="Email System")
    
    # Rutas de directorios
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    TEMPLATES_DIR: Path = Path(__file__).parent.parent / "email_service" / "templates"
    
    # Opciones adicionales
    DEBUG: bool = Field(default=False)
    TESTING: bool = Field(default=False)
    
    # Configuración para cargar variables desde .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    @validator('DEBUG', 'TESTING', pre=True)
    def parse_boolean(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "t", "yes", "y")
        return v
        
    def get_templates_dir(self) -> Path:
        """Retorna el directorio de plantillas, asegurando que exista."""
        if not self.TEMPLATES_DIR.exists() and not self.TESTING:
            raise ValueError(f"El directorio de templates no existe: {self.TEMPLATES_DIR}")
        return self.TEMPLATES_DIR
    
    def get_default_from_address(self) -> Dict[str, str]:
        """Retorna la dirección de email predeterminada para envío."""
        return {
            "email": self.DEFAULT_FROM_EMAIL,
            "name": self.DEFAULT_FROM_NAME
        }


# Instancia de configuración para importar en otros módulos
settings = EmailSystemSettings()