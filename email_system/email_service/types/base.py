"""
Clases base para todos los tipos de email.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any

from email_system.core.models import Company
from email_system.core.exceptions import ValidationError


class BaseEmail(ABC):
    """Clase base abstracta para todos los tipos de email."""
    template_name: str
    
    def __init__(self, company: Company):
        self.company = company
        self.year = datetime.now().year
    
    @abstractmethod
    def get_template_data(self) -> Dict[str, Any]:
        """
        Retorna los datos para renderizar la plantilla.
        
        Debe ser implementado por las subclases para proporcionar 
        los datos específicos de cada tipo de email.
        
        Returns:
            Dict[str, Any]: Datos para la plantilla
        """
        # Datos base comunes a todos los emails
        return {
            "company": {
                "name": self.company.name,
                "address": self.company.address,
                "website": self.company.website,
                "support_email": str(self.company.support_email),
                "social_media": self.company.social_media,
                "logo_url": self.company.logo_url
            },
            "year": self.year
        }

    def validate(self) -> None:
        """
        Valida que todos los datos requeridos estén presentes.
        
        Raises:
            ValidationError: Si faltan datos requeridos o son inválidos
        """
        if not hasattr(self, 'template_name') or not self.template_name:
            raise ValidationError("template_name es requerido")
        
        # Validaciones adicionales que pueden ser sobrescritas por subclases
        self._validate_specific_data()
    
    def _validate_specific_data(self) -> None:
        """
        Validaciones específicas para cada tipo de email.
        
        Método para sobrescribir en subclases si se necesitan
        validaciones adicionales específicas.
        """
        pass