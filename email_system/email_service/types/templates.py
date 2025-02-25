"""
Implementaciones concretas de los diferentes tipos de email.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

from email_system.core.models import EmailAddress, Notification, Alert, Company, Order
from email_system.core.exceptions import ValidationError
from email_system.email_service.types.base import BaseEmail


class WelcomeEmail(BaseEmail):
    """Email de bienvenida para nuevos usuarios."""
    template_name = "welcome.html"
    
    def __init__(self, company: Company, user: EmailAddress, dashboard_url: str):
        """
        Inicializa un email de bienvenida.
        
        Args:
            company: Información de la empresa
            user: Información del usuario destinatario
            dashboard_url: URL del dashboard donde el usuario puede iniciar sesión
        """
        super().__init__(company)
        self.user = user
        self.dashboard_url = dashboard_url
    
    def get_template_data(self) -> Dict[str, Any]:
        """
        Obtiene los datos para la plantilla de bienvenida.
        
        Returns:
            Dict[str, Any]: Datos para la plantilla
        """
        data = super().get_template_data()
        data.update({
            "user": {
                "name": self.user.name or "Usuario",
                "email": self.user.email
            },
            "dashboard_url": self.dashboard_url
        })
        return data
    
    def _validate_specific_data(self) -> None:
        """
        Validaciones específicas para el email de bienvenida.
        
        Raises:
            ValidationError: Si faltan datos o son inválidos
        """
        if not self.dashboard_url:
            raise ValidationError("dashboard_url es requerido para el email de bienvenida")


class PasswordResetEmail(BaseEmail):
    """Email para restablecimiento de contraseña."""
    template_name = "password_reset.html"
    
    def __init__(
        self,
        company: Company,
        user: EmailAddress,
        reset_url: str,
        expires_in: int = 24
    ):
        """
        Inicializa un email de restablecimiento de contraseña.
        
        Args:
            company: Información de la empresa
            user: Información del usuario destinatario
            reset_url: URL para restablecer la contraseña
            expires_in: Tiempo de expiración del enlace en horas
        """
        super().__init__(company)
        self.user = user
        self.reset_url = reset_url
        self.expires_in = expires_in
    
    def get_template_data(self) -> Dict[str, Any]:
        """
        Obtiene los datos para la plantilla de restablecimiento.
        
        Returns:
            Dict[str, Any]: Datos para la plantilla
        """
        data = super().get_template_data()
        data.update({
            "user": {
                "name": self.user.name or "Usuario",
                "email": self.user.email
            },
            "reset_url": self.reset_url,
            "expires_in": self.expires_in
        })
        return data
    
    def _validate_specific_data(self) -> None:
        """
        Validaciones específicas para el email de restablecimiento.
        
        Raises:
            ValidationError: Si faltan datos o son inválidos
        """
        if not self.reset_url:
            raise ValidationError("reset_url es requerido para el email de restablecimiento")
        
        if self.expires_in <= 0:
            raise ValidationError("expires_in debe ser un número positivo de horas")


class NotificationEmail(BaseEmail):
    """Email para notificaciones generales."""
    template_name = "notification.html"
    
    def __init__(
        self,
        company: Company,
        user: EmailAddress,
        notification: Notification,
        preferences_url: str = ""
    ):
        """
        Inicializa un email de notificación.
        
        Args:
            company: Información de la empresa
            user: Información del usuario destinatario
            notification: Datos de la notificación
            preferences_url: URL para gestionar preferencias de notificación
        """
        super().__init__(company)
        self.user = user
        self.notification = notification
        self.preferences_url = preferences_url
    
    def get_template_data(self) -> Dict[str, Any]:
        """
        Obtiene los datos para la plantilla de notificación.
        
        Returns:
            Dict[str, Any]: Datos para la plantilla
        """
        data = super().get_template_data()
        data.update({
            "user": {
                "name": self.user.name or "Usuario",
                "email": self.user.email
            },
            "notification": {
                "title": self.notification.title,
                "message": self.notification.message,
                "type": self.notification.type,
                "icon": self.notification.icon,
                "action_url": self.notification.action_url,
                "action_text": self.notification.action_text,
                "additional_info": self.notification.additional_info
            },
            "preferences_url": self.preferences_url
        })
        return data
    
    def _validate_specific_data(self) -> None:
        """
        Validaciones específicas para el email de notificación.
        
        Raises:
            ValidationError: Si faltan datos o son inválidos
        """
        if not self.notification.title or not self.notification.message:
            raise ValidationError("title y message son requeridos para el email de notificación")


class AlertEmail(BaseEmail):
    """Email para alertas y advertencias."""
    template_name = "alert.html"
    
    def __init__(
        self,
        company: Company,
        user: EmailAddress,
        alert: Alert
    ):
        """
        Inicializa un email de alerta.
        
        Args:
            company: Información de la empresa
            user: Información del usuario destinatario
            alert: Datos de la alerta
        """
        super().__init__(company)
        self.user = user
        self.alert = alert
    
    def get_template_data(self) -> Dict[str, Any]:
        """
        Obtiene los datos para la plantilla de alerta.
        
        Returns:
            Dict[str, Any]: Datos para la plantilla
        """
        data = super().get_template_data()
        data.update({
            "user": {
                "name": self.user.name or "Usuario",
                "email": self.user.email
            },
            "alert": {
                "title": self.alert.title,
                "message": self.alert.message,
                "type": self.alert.type,
                "steps": self.alert.steps,
                "action_url": self.alert.action_url,
                "action_text": self.alert.action_text,
                "contact_support": self.alert.contact_support
            }
        })
        return data
    
    def _validate_specific_data(self) -> None:
        """
        Validaciones específicas para el email de alerta.
        
        Raises:
            ValidationError: Si faltan datos o son inválidos
        """
        if not self.alert.title or not self.alert.message:
            raise ValidationError("title y message son requeridos para el email de alerta")


class OrderConfirmationEmail(BaseEmail):
    """Email de confirmación de pedido."""
    template_name = "order_confirmation.html"
    
    def __init__(
        self,
        company: Company,
        customer: EmailAddress,
        order: Order
    ):
        """
        Inicializa un email de confirmación de pedido.
        
        Args:
            company: Información de la empresa
            customer: Información del cliente destinatario
            order: Datos del pedido
        """
        super().__init__(company)
        self.customer = customer
        self.order = order
    
    def get_template_data(self) -> Dict[str, Any]:
        """
        Obtiene los datos para la plantilla de confirmación de pedido.
        
        Returns:
            Dict[str, Any]: Datos para la plantilla
        """
        data = super().get_template_data()
        
        # Formatear productos para la plantilla
        products = []
        for item in self.order.items:
            products.append({
                "name": item.name,
                "sku": item.sku or "N/A",
                "quantity": item.quantity,
                "price": f"{item.price:.2f}",
                "total": f"{item.total:.2f}"
            })
        
        # Añadir información del pedido
        data.update({
            "customer": {
                "name": self.customer.name or "Cliente",
                "email": self.customer.email
            },
            "order_info": {
                "number": self.order.number,
                "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "products": products,
                "items_count": self.order.items_count,
                "total": f"{self.order.total:.2f}",
                "shipping_address": self.order.shipping_address,
                "delivery_estimate": self.order.delivery_estimate
            }
        })
        return data
    
    def _validate_specific_data(self) -> None:
        """
        Validaciones específicas para el email de confirmación de pedido.
        
        Raises:
            ValidationError: Si faltan datos o son inválidos
        """
        if not self.order.number:
            raise ValidationError("El número de pedido es requerido")
            
        if not self.order.items or len(self.order.items) == 0:
            raise ValidationError("El pedido debe tener al menos un ítem")
            
        if not self.order.shipping_address:
            raise ValidationError("La dirección de envío es requerida")