"""
Componentes de formularios para la GUI del cliente.
Proporciona formularios para los diferentes tipos de email.
"""
import logging
from typing import List, Dict, Any, Tuple, Optional, Callable
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QFormLayout, QLineEdit, QTextEdit, QComboBox, 
    QSpinBox, QCheckBox, QPushButton, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal


logger = logging.getLogger(__name__)


class CompanyForm(QGroupBox):
    """Formulario para la información de la empresa."""
    
    # Señal que se emite cuando cambia cualquier campo
    form_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Información de la Empresa", parent)
        self._setup_ui()
        
        # Conectar señales de cambio
        self.company_name.textChanged.connect(self.form_changed.emit)
        self.company_address.textChanged.connect(self.form_changed.emit)
        self.company_email.textChanged.connect(self.form_changed.emit)
        self.company_website.textChanged.connect(self.form_changed.emit)
        self.company_logo.textChanged.connect(self.form_changed.emit)
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        form_layout = QFormLayout(self)
        
        self.company_name = QLineEdit("Mi Empresa")
        self.company_address = QLineEdit("Calle Principal 123")
        self.company_email = QLineEdit("soporte@miempresa.com")
        self.company_website = QLineEdit("https://miempresa.com")
        self.company_logo = QLineEdit("https://miempresa.com/logo.png")
        
        form_layout.addRow("Nombre:", self.company_name)
        form_layout.addRow("Dirección:", self.company_address)
        form_layout.addRow("Email:", self.company_email)
        form_layout.addRow("Website:", self.company_website)
        form_layout.addRow("Logo URL:", self.company_logo)
    
    def get_company_data(self) -> Dict[str, Any]:
        """Obtiene los datos de la empresa del formulario."""
        return {
            "name": self.company_name.text(),
            "address": self.company_address.text(),
            "support_email": self.company_email.text(),
            "website": self.company_website.text(),
            "logo_url": self.company_logo.text(),
            "social_media": {
                "facebook": "https://facebook.com/miempresa",
                "twitter": "https://twitter.com/miempresa",
                "instagram": "https://instagram.com/miempresa"
            }
        }


class RecipientsField(QWidget):
    """Campo para gestionar múltiples destinatarios."""
    
    # Señal que se emite cuando cambia el campo
    field_changed = pyqtSignal()
    
    def __init__(self, placeholder="Ingrese un email por línea", parent=None):
        super().__init__(parent)
        self.recipient_names = []
        self._setup_ui(placeholder)
    
    def _setup_ui(self, placeholder):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Campo de texto para ingresar emails
        self.email_field = QTextEdit()
        self.email_field.setPlaceholderText(placeholder)
        self.email_field.setMaximumHeight(80)  # Limitar altura
        
        # Etiqueta para mostrar contador de destinatarios
        self.counter = QLabel("0 destinatarios")
        self.counter.setStyleSheet("color: gray; font-size: 10px;")
        
        # Actualizar contador cuando cambia el texto
        self.email_field.textChanged.connect(self._update_counter)
        self.email_field.textChanged.connect(self.field_changed.emit)
        
        layout.addWidget(self.email_field)
        layout.addWidget(self.counter)
    
    def _update_counter(self):
        """Actualiza el contador de destinatarios."""
        text = self.email_field.toPlainText()
        emails = [email.strip() for email in text.split('\n') if email.strip()]
        self.counter.setText(f"{len(emails)} destinatario{'s' if len(emails) != 1 else ''}")
    
    def get_emails(self) -> List[str]:
        """Obtiene la lista de emails."""
        text = self.email_field.toPlainText()
        return [email.strip() for email in text.split('\n') if email.strip()]
    
    def set_emails(self, emails: List[str], names: Optional[List[str]] = None):
        """Establece los emails y nombres en el campo."""
        text_lines = []
        for i, email in enumerate(emails):
            name = ""
            if names and i < len(names) and names[i]:
                name = names[i]
            text_lines.append(f"{email}, {name}" if name else email)
        
        self.email_field.setText("\n".join(text_lines))
        self.recipient_names = names or []
        self._update_counter()
    
    def get_recipients(self) -> List[Tuple[str, str]]:
        """Obtiene la lista de (email, nombre) del campo."""
        text = self.email_field.toPlainText()
        recipients = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Intentar separar por coma o punto y coma
            if ',' in line:
                parts = line.split(',', 1)
            elif ';' in line:
                parts = line.split(';', 1)
            else:
                # Solo email sin nombre
                parts = [line, ""]
            
            email = parts[0].strip()
            name = parts[1].strip() if len(parts) > 1 else ""
            
            if email:
                recipients.append((email, name))
        
        return recipients


class WelcomeEmailForm(QWidget):
    """Formulario para email de bienvenida."""
    
    # Señal que se emite cuando cambia cualquier campo
    form_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Información del usuario
        user_group = QGroupBox("Información del Usuario")
        user_layout = QFormLayout(user_group)
        
        self.user_name = QLineEdit("Usuario de Prueba")
        self.user_name.textChanged.connect(self.form_changed.emit)
        
        # Campo de emails
        self.user_email_container = QWidget()
        email_container_layout = QHBoxLayout(self.user_email_container)
        email_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.user_email = RecipientsField("Ingrese un email por línea")
        self.user_email.field_changed.connect(self.form_changed.emit)
        self.user_email.set_emails(["usuario@ejemplo.com"])
        
        manage_recipients_button = QPushButton("Gestionar Destinatarios")
        manage_recipients_button.clicked.connect(self._manage_recipients)
        
        email_container_layout.addWidget(self.user_email)
        email_container_layout.addWidget(manage_recipients_button)
        
        self.dashboard_url = QLineEdit("https://miempresa.com/dashboard")
        self.dashboard_url.textChanged.connect(self.form_changed.emit)
        
        user_layout.addRow("Nombre por defecto:", self.user_name)
        user_layout.addRow("Email(s):", self.user_email_container)
        user_layout.addRow("Dashboard URL:", self.dashboard_url)
        
        layout.addWidget(user_group)
        
        # Añadir espacio al final
        layout.addStretch()
    
    def _manage_recipients(self):
        """Abre diálogo para gestionar destinatarios."""
        # En una implementación completa, aquí se abriría un diálogo
        # para gestionar los destinatarios con nombres personalizados
        logger.debug("Gestionar destinatarios (no implementado)")
    
    def get_form_data(self) -> Dict[str, Any]:
        """Obtiene los datos del formulario."""
        recipients = self.user_email.get_recipients()
        emails = [email for email, _ in recipients]
        names = [name for _, name in recipients]
        
        return {
            "user": {
                "names": names,
                "emails": emails
            },
            "query": {
                "dashboard_url": self.dashboard_url.text()
            }
        }


class PasswordResetForm(QWidget):
    """Formulario para email de restablecimiento de contraseña."""
    
    # Señal que se emite cuando cambia cualquier campo
    form_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Información del usuario
        user_group = QGroupBox("Información del Usuario")
        user_layout = QFormLayout(user_group)
        
        self.user_name = QLineEdit("Usuario de Prueba")
        self.user_name.textChanged.connect(self.form_changed.emit)
        
        # Campo de emails
        self.user_email_container = QWidget()
        email_container_layout = QHBoxLayout(self.user_email_container)
        email_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.user_email = RecipientsField("Ingrese un email por línea")
        self.user_email.field_changed.connect(self.form_changed.emit)
        self.user_email.set_emails(["usuario@ejemplo.com"])
        
        manage_recipients_button = QPushButton("Gestionar Destinatarios")
        manage_recipients_button.clicked.connect(self._manage_recipients)
        
        email_container_layout.addWidget(self.user_email)
        email_container_layout.addWidget(manage_recipients_button)
        
        self.reset_url = QLineEdit("https://miempresa.com/reset-password")
        self.reset_url.textChanged.connect(self.form_changed.emit)
        
        self.expires_in = QSpinBox()
        self.expires_in.setValue(24)
        self.expires_in.setRange(1, 72)
        self.expires_in.valueChanged.connect(self.form_changed.emit)
        
        user_layout.addRow("Nombre por defecto:", self.user_name)
        user_layout.addRow("Email(s):", self.user_email_container)
        user_layout.addRow("Reset URL:", self.reset_url)
        user_layout.addRow("Expira en (horas):", self.expires_in)
        
        layout.addWidget(user_group)
        
        # Añadir espacio al final
        layout.addStretch()
    
    def _manage_recipients(self):
        """Abre diálogo para gestionar destinatarios."""
        # En una implementación completa, aquí se abriría un diálogo
        # para gestionar los destinatarios con nombres personalizados
        logger.debug("Gestionar destinatarios (no implementado)")
    
    def get_form_data(self) -> Dict[str, Any]:
        """Obtiene los datos del formulario."""
        recipients = self.user_email.get_recipients()
        emails = [email for email, _ in recipients]
        names = [name for _, name in recipients]
        
        return {
            "user": {
                "names": names,
                "emails": emails
            },
            "query": {
                "reset_url": self.reset_url.text(),
                "expires_in": self.expires_in.value()
            }
        }


class NotificationForm(QWidget):
    """Formulario para email de notificación."""
    
    # Señal que se emite cuando cambia cualquier campo
    form_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Información del usuario
        user_group = QGroupBox("Información del Usuario")
        user_layout = QFormLayout(user_group)
        
        self.user_name = QLineEdit("Usuario de Prueba")
        self.user_name.textChanged.connect(self.form_changed.emit)
        
        # Campo de emails
        self.user_email_container = QWidget()
        email_container_layout = QHBoxLayout(self.user_email_container)
        email_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.user_email = RecipientsField("Ingrese un email por línea")
        self.user_email.field_changed.connect(self.form_changed.emit)
        self.user_email.set_emails(["usuario@ejemplo.com"])
        
        manage_recipients_button = QPushButton("Gestionar Destinatarios")
        manage_recipients_button.clicked.connect(self._manage_recipients)
        
        email_container_layout.addWidget(self.user_email)
        email_container_layout.addWidget(manage_recipients_button)
        
        user_layout.addRow("Nombre por defecto:", self.user_name)
        user_layout.addRow("Email(s):", self.user_email_container)
        
        layout.addWidget(user_group)
        
        # Contenido de la notificación
        notification_group = QGroupBox("Contenido de la Notificación")
        notification_layout = QFormLayout(notification_group)
        
        self.notification_title = QLineEdit("Notificación Importante")
        self.notification_title.textChanged.connect(self.form_changed.emit)
        
        self.notification_message = QTextEdit("Este es un mensaje de notificación de prueba.")
        self.notification_message.textChanged.connect(self.form_changed.emit)
        
        self.notification_type = QComboBox()
        self.notification_type.addItems(["success", "warning", "error", "info"])
        self.notification_type.currentIndexChanged.connect(self.form_changed.emit)
        
        self.notification_icon = QLineEdit("https://miempresa.com/icons/notification.png")
        self.notification_icon.textChanged.connect(self.form_changed.emit)
        
        self.notification_action_url = QLineEdit("https://miempresa.com/action")
        self.notification_action_url.textChanged.connect(self.form_changed.emit)
        
        self.notification_action_text = QLineEdit("Ver Detalles")
        self.notification_action_text.textChanged.connect(self.form_changed.emit)
        
        self.notification_additional_info = QTextEdit("Información adicional sobre esta notificación.")
        self.notification_additional_info.textChanged.connect(self.form_changed.emit)
        
        self.notification_preferences_url = QLineEdit("https://miempresa.com/preferences")
        self.notification_preferences_url.textChanged.connect(self.form_changed.emit)
        
        notification_layout.addRow("Título:", self.notification_title)
        notification_layout.addRow("Mensaje:", self.notification_message)
        notification_layout.addRow("Tipo:", self.notification_type)
        notification_layout.addRow("Icono URL:", self.notification_icon)
        notification_layout.addRow("Action URL:", self.notification_action_url)
        notification_layout.addRow("Action Text:", self.notification_action_text)
        notification_layout.addRow("Info Adicional:", self.notification_additional_info)
        notification_layout.addRow("Preferences URL:", self.notification_preferences_url)
        
        layout.addWidget(notification_group)
        
        # Añadir espacio al final
        layout.addStretch()
    
    def _manage_recipients(self):
        """Abre diálogo para gestionar destinatarios."""
        # En una implementación completa, aquí se abriría un diálogo
        # para gestionar los destinatarios con nombres personalizados
        logger.debug("Gestionar destinatarios (no implementado)")
    
    def get_form_data(self) -> Dict[str, Any]:
        """Obtiene los datos del formulario."""
        recipients = self.user_email.get_recipients()
        emails = [email for email, _ in recipients]
        names = [name for _, name in recipients]
        
        return {
            "user": {
                "names": names,
                "emails": emails
            },
            "notification": {
                "title": self.notification_title.text(),
                "message": self.notification_message.toPlainText(),
                "type": self.notification_type.currentText(),
                "icon": self.notification_icon.text() or None,
                "action_url": self.notification_action_url.text() or None,
                "action_text": self.notification_action_text.text() or None,
                "additional_info": self.notification_additional_info.toPlainText() or None
            },
            "query": {
                "preferences_url": self.notification_preferences_url.text()
            }
        }


class AlertForm(QWidget):
    """Formulario para email de alerta."""
    
    # Señal que se emite cuando cambia cualquier campo
    form_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Información del usuario
        user_group = QGroupBox("Información del Usuario")
        user_layout = QFormLayout(user_group)
        
        self.user_name = QLineEdit("Usuario de Prueba")
        self.user_name.textChanged.connect(self.form_changed.emit)
        
        # Campo de emails
        self.user_email_container = QWidget()
        email_container_layout = QHBoxLayout(self.user_email_container)
        email_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.user_email = RecipientsField("Ingrese un email por línea")
        self.user_email.field_changed.connect(self.form_changed.emit)
        self.user_email.set_emails(["usuario@ejemplo.com"])
        
        manage_recipients_button = QPushButton("Gestionar Destinatarios")
        manage_recipients_button.clicked.connect(self._manage_recipients)
        
        email_container_layout.addWidget(self.user_email)
        email_container_layout.addWidget(manage_recipients_button)
        
        user_layout.addRow("Nombre por defecto:", self.user_name)
        user_layout.addRow("Email(s):", self.user_email_container)
        
        layout.addWidget(user_group)
        
        # Contenido de la alerta
        alert_group = QGroupBox("Contenido de la Alerta")
        alert_layout = QFormLayout(alert_group)
        
        self.alert_title = QLineEdit("Alerta de Seguridad")
        self.alert_title.textChanged.connect(self.form_changed.emit)
        
        self.alert_message = QTextEdit("Este es un mensaje de alerta de prueba.")
        self.alert_message.textChanged.connect(self.form_changed.emit)
        
        self.alert_type = QComboBox()
        self.alert_type.addItems(["info", "warning", "error"])
        self.alert_type.currentIndexChanged.connect(self.form_changed.emit)
        
        self.alert_steps = QTextEdit("Paso 1: Verificar conexión\nPaso 2: Actualizar contraseña\nPaso 3: Cerrar sesiones")
        self.alert_steps.setPlaceholderText("Un paso por línea")
        self.alert_steps.textChanged.connect(self.form_changed.emit)
        
        self.alert_action_url = QLineEdit("https://miempresa.com/action")
        self.alert_action_url.textChanged.connect(self.form_changed.emit)
        
        self.alert_action_text = QLineEdit("Resolver Ahora")
        self.alert_action_text.textChanged.connect(self.form_changed.emit)
        
        self.alert_contact_support = QCheckBox("Incluir información de soporte")
        self.alert_contact_support.setChecked(True)
        self.alert_contact_support.stateChanged.connect(self.form_changed.emit)
        
        alert_layout.addRow("Título:", self.alert_title)
        alert_layout.addRow("Mensaje:", self.alert_message)
        alert_layout.addRow("Tipo:", self.alert_type)
        alert_layout.addRow("Pasos:", self.alert_steps)
        alert_layout.addRow("Action URL:", self.alert_action_url)
        alert_layout.addRow("Action Text:", self.alert_action_text)
        alert_layout.addRow("", self.alert_contact_support)
        
        layout.addWidget(alert_group)
        
        # Añadir espacio al final
        layout.addStretch()
    
    def _manage_recipients(self):
        """Abre diálogo para gestionar destinatarios."""
        # En una implementación completa, aquí se abriría un diálogo
        # para gestionar los destinatarios con nombres personalizados
        logger.debug("Gestionar destinatarios (no implementado)")
    
    def get_form_data(self) -> Dict[str, Any]:
        """Obtiene los datos del formulario."""
        recipients = self.user_email.get_recipients()
        emails = [email for email, _ in recipients]
        names = [name for _, name in recipients]
        
        # Obtener los pasos
        steps = [
            step.strip() 
            for step in self.alert_steps.toPlainText().split("\n") 
            if step.strip()
        ]
        
        return {
            "user": {
                "names": names,
                "emails": emails
            },
            "alert": {
                "title": self.alert_title.text(),
                "message": self.alert_message.toPlainText(),
                "type": self.alert_type.currentText(),
                "steps": steps if steps else None,
                "action_url": self.alert_action_url.text() or None,
                "action_text": self.alert_action_text.text() or None,
                "contact_support": self.alert_contact_support.isChecked()
            }
        }


class BatchForm(QWidget):
    """Formulario para envío en lote."""
    
    # Señal que se emite cuando cambia cualquier campo
    form_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tipo de email a enviar
        type_group = QGroupBox("Tipo de Email a Enviar")
        type_layout = QFormLayout(type_group)
        
        self.email_type = QComboBox()
        self.email_type.addItems(["welcome", "password-reset", "notification", "alert"])
        self.email_type.currentIndexChanged.connect(self._update_params)
        
        type_layout.addRow("Tipo:", self.email_type)
        
        layout.addWidget(type_group)
        
        # Destinatarios
        recipients_group = QGroupBox("Destinatarios")
        recipients_layout = QVBoxLayout(recipients_group)
        
        # Editor de texto para los destinatarios
        self.recipients_text = QTextEdit()
        self.recipients_text.setPlaceholderText("usuario1@ejemplo.com, Nombre 1\nusuario2@ejemplo.com, Nombre 2\n...")
        self.recipients_text.textChanged.connect(self.form_changed.emit)
        
        recipients_layout.addWidget(self.recipients_text)
        
        # Botones para gestionar los destinatarios
        recipients_buttons = QHBoxLayout()
        
        add_recipients_btn = QPushButton("Añadir Destinatarios")
        add_recipients_btn.clicked.connect(self._manage_recipients)
        recipients_buttons.addWidget(add_recipients_btn)
        
        clear_recipients_btn = QPushButton("Limpiar")
        clear_recipients_btn.clicked.connect(lambda: self.recipients_text.clear())
        recipients_buttons.addWidget(clear_recipients_btn)
        
        recipients_layout.addLayout(recipients_buttons)
        
        layout.addWidget(recipients_group)
        
        # Parámetros adicionales (depende del tipo de email)
        self.params_container = QWidget()
        self.params_layout = QVBoxLayout(self.params_container)
        layout.addWidget(self.params_container)
        
        # Actualizar los parámetros según el tipo seleccionado
        self._update_params()
        
        # Añadir espacio al final
        layout.addStretch()
    
    def _update_params(self):
        """Actualiza los parámetros según el tipo de email seleccionado."""
        # Limpiar el contenedor de parámetros
        for i in reversed(range(self.params_layout.count())):
            widget = self.params_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Obtener el tipo de email seleccionado
        email_type = self.email_type.currentText()
        
        if email_type == "welcome":
            # Parámetros para email de bienvenida
            params_group = QGroupBox("Parámetros de Bienvenida")
            params_layout = QFormLayout(params_group)
            
            self.dashboard_url = QLineEdit("https://miempresa.com/dashboard")
            self.dashboard_url.textChanged.connect(self.form_changed.emit)
            params_layout.addRow("Dashboard URL:", self.dashboard_url)
            
            self.params_layout.addWidget(params_group)
            
        elif email_type == "password-reset":
            # Parámetros para reset de contraseña
            params_group = QGroupBox("Parámetros de Reset")
            params_layout = QFormLayout(params_group)
            
            self.reset_url = QLineEdit("https://miempresa.com/reset-password")
            self.reset_url.textChanged.connect(self.form_changed.emit)
            params_layout.addRow("Reset URL:", self.reset_url)
            
            self.expires_in = QSpinBox()
            self.expires_in.setValue(24)
            self.expires_in.setRange(1, 72)
            self.expires_in.valueChanged.connect(self.form_changed.emit)
            params_layout.addRow("Expira en (horas):", self.expires_in)
            
            self.params_layout.addWidget(params_group)
            
        elif email_type == "notification":
            # Parámetros para notificación
            params_group = QGroupBox("Parámetros de Notificación")
            params_layout = QFormLayout(params_group)
            
            self.notification_title = QLineEdit("Notificación Importante")
            self.notification_title.textChanged.connect(self.form_changed.emit)
            params_layout.addRow("Título:", self.notification_title)
            
            self.notification_message = QTextEdit("Este es un mensaje de notificación de prueba.")
            self.notification_message.textChanged.connect(self.form_changed.emit)
            params_layout.addRow("Mensaje:", self.notification_message)
            
            self.notification_type = QComboBox()
            self.notification_type.addItems(["success", "warning", "error", "info"])
            self.notification_type.currentIndexChanged.connect(self.form_changed.emit)
            params_layout.addRow("Tipo:", self.notification_type)
            
            self.notification_icon = QLineEdit("https://miempresa.com/icons/notification.png")
            self.notification_icon.textChanged.connect(self.form_changed.emit)
            params_layout.addRow("Icono URL:", self.notification_icon)
            
            self.notification_action_url = QLineEdit("https://miempresa.com/action")
            self.notification_action_url.textChanged.connect(self.form_changed.emit)
            params_layout.addRow("Action URL:", self.notification_action_url)
            
            self.notification_action_text = QLineEdit("Ver Detalles")
            self.notification_action_text.textChanged.connect(self.form_changed.emit)
            params_layout.addRow("Action Text:", self.notification_action_text)
            
            self.notification_additional_info = QTextEdit("Información adicional sobre esta notificación.")
            self.notification_additional_info.textChanged.connect(self.form_changed.emit)
            params_layout.addRow("Info Adicional:", self.notification_additional_info)
            
            self.notification_preferences_url = QLineEdit("https://miempresa.com/preferences")
            self.notification_preferences_url.textChanged.connect(self.form_changed.emit)
            params_layout.addRow("Preferences URL:", self.notification_preferences_url)
            
            self.params_layout.addWidget(params_group)
            
        elif email_type == "alert":
            # Parámetros para alerta
            params_group = QGroupBox("Parámetros de Alerta")
            params_layout = QFormLayout(params_group)
            
            self.alert_title = QLineEdit("Alerta de Seguridad")
            self.alert_title.textChanged.connect(self.form_changed.emit)
            params_layout.addRow("Título:", self.alert_title)
            
            self.alert_message = QTextEdit("Este es un mensaje de alerta de prueba.")
            self.alert_message.textChanged.connect(self.form_changed.emit)
            params_layout.addRow("Mensaje:", self.alert_message)
            
            self.alert_type = QComboBox()
            self.alert_type.addItems(["info", "warning", "error"])
            self.alert_type.currentIndexChanged.connect(self.form_changed.emit)
            params_layout.addRow("Tipo:", self.alert_type)
            
            self.alert_steps = QTextEdit("Paso 1: Verificar conexión\nPaso 2: Actualizar contraseña\nPaso 3: Cerrar sesiones")
            self.alert_steps.setPlaceholderText("Un paso por línea")
            self.alert_steps.textChanged.connect(self.form_changed.emit)
            params_layout.addRow("Pasos:", self.alert_steps)
            
            self.alert_action_url = QLineEdit("https://miempresa.com/action")
            self.alert_action_url.textChanged.connect(self.form_changed.emit)
            params_layout.addRow("Action URL:", self.alert_action_url)
            
            self.alert_action_text = QLineEdit("Resolver Ahora")
            self.alert_action_text.textChanged.connect(self.form_changed.emit)
            params_layout.addRow("Action Text:", self.alert_action_text)
            
            self.alert_contact_support = QCheckBox("Incluir información de soporte")
            self.alert_contact_support.setChecked(True)
            self.alert_contact_support.stateChanged.connect(self.form_changed.emit)
            params_layout.addRow("", self.alert_contact_support)
            
            self.params_layout.addWidget(params_group)
        
        # Emitir señal de cambio
        self.form_changed.emit()
    
    def _manage_recipients(self):
        """Abre diálogo para gestionar destinatarios."""
        # En una implementación completa, aquí se abriría un diálogo
        # para gestionar los destinatarios con nombres personalizados
        logger.debug("Gestionar destinatarios (no implementado)")
    
    def get_recipients(self) -> List[Dict[str, str]]:
        """Obtiene la lista de destinatarios como diccionarios."""
        text = self.recipients_text.toPlainText()
        recipients = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Intentar separar por coma o punto y coma
            if ',' in line:
                parts = line.split(',', 1)
            elif ';' in line:
                parts = line.split(';', 1)
            else:
                # Solo email sin nombre
                parts = [line, ""]
            
            email = parts[0].strip()
            name = parts[1].strip() if len(parts) > 1 else ""
            
            if email:
                recipients.append({
                    "email": email,
                    "name": name
                })
        
        return recipients
    
    def get_form_data(self) -> Dict[str, Any]:
        """Obtiene los datos del formulario."""
        # Datos base
        data = {
            "email_type": self.email_type.currentText(),
            "recipients": self.get_recipients()
        }
        
        # Añadir parámetros según el tipo
        email_type = self.email_type.currentText()
        
        if email_type == "welcome":
            data["query"] = {
                "dashboard_url": self.dashboard_url.text()
            }
        elif email_type == "password-reset":
            data["query"] = {
                "reset_url": self.reset_url.text(),
                "expires_in": self.expires_in.value()
            }
        elif email_type == "notification":
            data["query"] = {
                "title": self.notification_title.text(),
                "message": self.notification_message.toPlainText(),
                "type": self.notification_type.currentText(),
                "icon": self.notification_icon.text() or None,
                "action_url": self.notification_action_url.text() or None,
                "action_text": self.notification_action_text.text() or None,
                "additional_info": self.notification_additional_info.toPlainText() or None,
                "preferences_url": self.notification_preferences_url.text()
            }
        elif email_type == "alert":
            # Obtener los pasos
            steps = [
                step.strip() 
                for step in self.alert_steps.toPlainText().split("\n") 
                if step.strip()
            ]
            
            data["alert"] = {
                "title": self.alert_title.text(),
                "message": self.alert_message.toPlainText(),
                "type": self.alert_type.currentText(),
                "steps": steps if steps else None,
                "action_url": self.alert_action_url.text() or None,
                "action_text": self.alert_action_text.text() or None,
                "contact_support": self.alert_contact_support.isChecked()
            }
        
        return data