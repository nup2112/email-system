"""
Modelos de datos para la aplicación de sistema de emails.
Usa Pydantic para validación y conversión de tipos.
"""
from __future__ import annotations
from pydantic import BaseModel, EmailStr, validator, HttpUrl, Field
from typing import List, Optional, Dict, Any, Union


class EmailAddress(BaseModel):
    """Modelo para una dirección de correo electrónico con nombre opcional."""
    email: EmailStr
    name: Optional[str] = None
    
    def __str__(self) -> str:
        """Formato de visualización de la dirección de email."""
        return f"{self.name} <{self.email}>" if self.name else self.email


class Company(BaseModel):
    """Información de la empresa para uso en las plantillas de email."""
    name: str
    address: str
    support_email: Union[EmailAddress, str]
    website: str
    social_media: Dict[str, str] = Field(default_factory=dict)
    logo_url: Optional[Union[HttpUrl, str]] = None
    
    @validator('support_email', pre=True)
    def parse_support_email(cls, v):
        """Convierte una cadena en objeto EmailAddress si es necesario."""
        if isinstance(v, str):
            return EmailAddress(email=v)
        return v
    
    @validator('logo_url', pre=True)
    def parse_logo_url(cls, v):
        """Permite usar cadenas para logo_url."""
        if v == "" or v is None:
            return None
        return v


class Notification(BaseModel):
    """Modelo para una notificación para enviar por email."""
    title: str
    message: str
    type: str = "info"  # 'success', 'warning', 'error', 'info'
    icon: Optional[Union[HttpUrl, str]] = None
    action_url: Optional[Union[HttpUrl, str]] = None
    action_text: Optional[str] = None
    additional_info: Optional[str] = None
    
    @validator('type')
    def validate_type(cls, v):
        """Valida que el tipo sea uno de los permitidos."""
        allowed_types = ["success", "warning", "error", "info"]
        if v not in allowed_types:
            raise ValueError(f"El tipo debe ser uno de {', '.join(allowed_types)}")
        return v


class Alert(BaseModel):
    """Modelo para una alerta para enviar por email."""
    title: str
    message: str
    type: str = "info"  # 'info', 'warning', 'error'
    steps: Optional[List[str]] = None
    action_url: Optional[Union[HttpUrl, str]] = None
    action_text: Optional[str] = None
    contact_support: bool = True
    
    @validator('type')
    def validate_type(cls, v):
        """Valida que el tipo sea uno de los permitidos."""
        allowed_types = ["info", "warning", "error"]
        if v not in allowed_types:
            raise ValueError(f"El tipo debe ser uno de {', '.join(allowed_types)}")
        return v


class OrderItem(BaseModel):
    """Modelo para un ítem de pedido."""
    name: str
    quantity: int
    price: float
    sku: Optional[str] = None
    
    @property
    def total(self) -> float:
        """Calcula el total del ítem."""
        return self.quantity * self.price


class Order(BaseModel):
    """Modelo para un pedido."""
    number: str
    items: List[OrderItem]
    shipping_address: str
    delivery_estimate: str
    
    @property
    def total(self) -> float:
        """Calcula el total del pedido."""
        return sum(item.total for item in self.items)
    
    @property
    def items_count(self) -> int:
        """Retorna el número total de ítems en el pedido."""
        return sum(item.quantity for item in self.items)