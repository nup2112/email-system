"""
Ventana principal de la aplicación.
"""
import logging
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QToolBar, QAction, QLineEdit, QLabel,
    QFileDialog, QMessageBox, QPushButton, QFrame,
    QStatusBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QIcon

from config import ClientConfig
from components.sidebar import EmailTypesSidebar
from components.preview import EmailPreviewPanel, RenderPreviewWorker
from components.forms import (
    CompanyForm, WelcomeEmailForm, PasswordResetForm, 
    NotificationForm, AlertForm, BatchForm
)
from utils.api_client import EmailAPIClient, APIError


logger = logging.getLogger(__name__)


class EmailTesterMainWindow(QMainWindow):
    """Ventana principal de la aplicación de prueba de emails."""
    
    def __init__(self, config: ClientConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.api_client = EmailAPIClient(
            base_url=config.api_url,
            api_key=config.api_key
        )
        
        # Atributos principales
        self.template_env = None
        self.current_email_type = None
        self.preview_update_timer = None
        
        # Configurar la ventana
        self.setWindowTitle("Email System - Tester")
        self.setMinimumSize(1200, 800)
        
        # Inicializar UI
        self._setup_ui()
        
        # Configurar motor de plantillas
        self._setup_template_engine()
        
        # Verificar conectividad con la API
        self._check_api_connection()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barra lateral
        self.sidebar = EmailTypesSidebar()
        self.sidebar.email_type_changed.connect(self._on_email_type_changed)
        main_layout.addWidget(self.sidebar)
        
        # Contenedor principal
        main_container = QWidget()
        main_container_layout = QVBoxLayout(main_container)
        main_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar para configuración
        self._create_toolbar(main_container_layout)
        
        # Splitter principal
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # Contenedor para formularios (izquierda)
        self.form_container = QWidget()
        self.form_layout = QVBoxLayout(self.form_container)
        self.form_layout.setContentsMargins(10, 10, 10, 10)
        
        # Panel de vista previa (derecha)
        self.preview_panel = EmailPreviewPanel()
        self.preview_panel.error_occurred.connect(self._show_error_message)
        
        # Añadir widgets al splitter
        self.main_splitter.addWidget(self.form_container)
        self.main_splitter.addWidget(self.preview_panel)
        self.main_splitter.setSizes([400, 800])  # Tamaños iniciales
        
        main_container_layout.addWidget(self.main_splitter)
        
        # Añadir el contenedor principal al layout
        main_layout.addWidget(main_container)
        
        # Crear formularios
        self._create_forms()
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo")
        self._initialize_default_view()

    def _initialize_default_view(self):
        """Initialize the default view with the first email type."""
        # Get the currently selected email type from sidebar (should be the first one)
        email_type = self.sidebar.get_selected_email_type()
        
        if email_type:
            # Set the current email type
            self.current_email_type = email_type
            
            # Show the corresponding form
            self._show_email_form(email_type)
            
            # Schedule preview update
            QTimer.singleShot(500, self._update_preview)
        else:
            logger.warning("No email type selected on initialization")
    
    def _create_toolbar(self, layout):
        """
        Crea una barra de herramientas para la configuración.
        
        Args:
            layout: Layout donde se agregará la barra de herramientas
        """
        toolbar_container = QWidget()
        toolbar_container.setStyleSheet("""
            background-color: white;
            border-bottom: 1px solid #e0e0e0;
            max-height: 60px;
        """)
        toolbar_layout = QHBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(15, 12, 15, 12)
        
        # API Key
        api_key_label = QLabel("API Key:")
        api_key_label.setStyleSheet("font-weight: bold;")
        toolbar_layout.addWidget(api_key_label)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setMaximumWidth(400)
        self.api_key_input.setPlaceholderText("Ingrese su API key")
        if self.config.api_key:
            self.api_key_input.setText(self.config.api_key)
        self.api_key_input.textChanged.connect(self._on_api_key_changed)
        toolbar_layout.addWidget(self.api_key_input)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setFixedWidth(2)
        separator.setStyleSheet("background-color: #e0e0e0;")
        toolbar_layout.addWidget(separator)
        
        # Directorio de plantillas
        templates_dir_label = QLabel("Plantillas:")
        templates_dir_label.setStyleSheet("font-weight: bold;")
        toolbar_layout.addWidget(templates_dir_label)
        
        self.templates_dir_input = QLineEdit()
        self.templates_dir_input.setReadOnly(True)
        self.templates_dir_input.setPlaceholderText("Seleccione el directorio de plantillas")
        if self.config.templates_dir:
            self.templates_dir_input.setText(str(self.config.templates_dir))
        toolbar_layout.addWidget(self.templates_dir_input)
        
        browse_button = QPushButton("Explorar")
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        browse_button.clicked.connect(self._browse_templates_dir)
        toolbar_layout.addWidget(browse_button)
        
        layout.addWidget(toolbar_container)
        
        # Línea separadora
        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.HLine)
        separator_line.setFrameShadow(QFrame.Sunken)
        separator_line.setFixedHeight(1)
        separator_line.setStyleSheet("background-color: #e0e0e0;")
        layout.addWidget(separator_line)
    
    def _create_forms(self):
        """Crea todos los formularios para los diferentes tipos de email."""
        # Formulario de empresa (común a todos)
        self.company_form = CompanyForm()
        self.company_form.form_changed.connect(self._schedule_preview_update)
        
        # Formularios específicos
        self.welcome_form = WelcomeEmailForm()
        self.welcome_form.form_changed.connect(self._schedule_preview_update)
        
        self.password_reset_form = PasswordResetForm()
        self.password_reset_form.form_changed.connect(self._schedule_preview_update)
        
        self.notification_form = NotificationForm()
        self.notification_form.form_changed.connect(self._schedule_preview_update)
        
        self.alert_form = AlertForm()
        self.alert_form.form_changed.connect(self._schedule_preview_update)
        
        self.batch_form = BatchForm()
        self.batch_form.form_changed.connect(self._schedule_preview_update)
    
    def _on_email_type_changed(self, email_type):
        """
        Maneja el cambio de tipo de email seleccionado.
        
        Args:
            email_type (str): Nuevo tipo de email seleccionado
        """
        self.current_email_type = email_type
        self._show_email_form(email_type)
        self._update_preview()
    
    def _show_email_form(self, email_type):
        """
        Muestra el formulario correspondiente al tipo de email seleccionado.
        
        Args:
            email_type (str): Tipo de email
        """
        # Limpiar el contenedor de formularios
        for i in reversed(range(self.form_layout.count())):
            widget = self.form_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Añadir el formulario de empresa (común a todos)
        self.form_layout.addWidget(self.company_form)
        
        # Añadir el formulario específico
        specific_form = None
        
        if email_type == "welcome":
            specific_form = self.welcome_form
        elif email_type == "password_reset":
            specific_form = self.password_reset_form
        elif email_type == "notification":
            specific_form = self.notification_form
        elif email_type == "alert":
            specific_form = self.alert_form
        elif email_type == "batch":
            specific_form = self.batch_form
        
        if specific_form:
            self.form_layout.addWidget(specific_form)
        
        # Botones de acción
        action_buttons = QWidget()
        action_layout = QHBoxLayout(action_buttons)
        
        # Añadir espacio
        action_layout.addStretch()
        
        # Botón para enviar email
        send_btn = QPushButton("Enviar Email")
        send_btn.clicked.connect(self._send_email)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        action_layout.addWidget(send_btn)
        
        self.form_layout.addWidget(action_buttons)
    
    def _on_api_key_changed(self, api_key):
        """
        Actualiza la API key en la configuración y el cliente API.
        
        Args:
            api_key (str): Nueva API key
        """
        self.config.api_key = api_key
        self.api_client.api_key = api_key
    
    def _browse_templates_dir(self):
        """Abre un diálogo para seleccionar el directorio de plantillas."""
        directory = QFileDialog.getExistingDirectory(
            self, "Seleccionar Directorio de Plantillas"
        )
        if directory:
            self.templates_dir_input.setText(directory)
            self.config.templates_dir = Path(directory)
            self._setup_template_engine(directory)
            self._update_preview()
    
    def _setup_template_engine(self, custom_dir=None):
        """
        Configura el motor de plantillas Jinja2.
        
        Args:
            custom_dir (str, optional): Directorio personalizado de plantillas
        """
        try:
            # Si se proporciona un directorio personalizado, usarlo
            if custom_dir:
                templates_dir = Path(custom_dir)
            # Si no, usar el directorio de la configuración
            elif self.config.templates_dir:
                templates_dir = self.config.templates_dir
            # Si no hay directorio en la configuración, buscar en posibles ubicaciones
            else:
                possible_paths = [
                    Path("./templates"),
                    Path("../templates"),
                    Path(__file__).parent.parent.parent.parent / "email_system" / "email_service" / "templates",
                ]
                
                templates_dir = None
                for path in possible_paths:
                    if path.exists() and path.is_dir():
                        templates_dir = path
                        self.templates_dir_input.setText(str(templates_dir))
                        self.config.templates_dir = templates_dir
                        break
                
                # Si no se encuentra un directorio, mostrar error
                if templates_dir is None:
                    logger.warning("No se encontró un directorio de plantillas válido")
                    self._show_error_message("No se encontró un directorio de plantillas válido")
                    return
            
            # Configurar el motor de plantillas
            self.template_env = Environment(
                loader=FileSystemLoader(templates_dir),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
            logger.info(f"Motor de plantillas configurado con el directorio: {templates_dir}")
            
        except Exception as e:
            logger.error(f"Error al configurar el motor de plantillas: {str(e)}")
            self._show_error_message(f"Error al configurar el motor de plantillas: {str(e)}")
    
    def _check_api_connection(self):
        """Verifica la conexión con la API."""
        try:
            result = self.api_client.check_health()
            logger.info(f"Conexión con la API establecida: {result}")
            self.status_bar.showMessage(f"API conectada - Versión: {result.get('version', 'desconocida')}")
        except APIError as e:
            logger.error(f"Error al conectar con la API: {str(e)}")
            self.status_bar.showMessage(f"Error al conectar con la API: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado al verificar conexión: {str(e)}")
            self.status_bar.showMessage(f"Error inesperado al verificar conexión: {str(e)}")
    
    def _schedule_preview_update(self):
        """Programa una actualización de la vista previa después de un retraso."""
        # Cancelar el temporizador anterior si existe
        if self.preview_update_timer:
            self.preview_update_timer.stop()
        
        # Crear nuevo temporizador para actualizar después de 500ms
        self.preview_update_timer = QTimer()
        self.preview_update_timer.setSingleShot(True)
        self.preview_update_timer.timeout.connect(self._update_preview)
        self.preview_update_timer.start(500)
    
    def _update_preview(self):
        """Actualiza la vista previa del email."""
        if not self.current_email_type or not self.template_env:
            return
        
        try:
            # Determinar la plantilla según el tipo de email actual
            if self.current_email_type == "welcome":
                template_name = "welcome.html"
                template_data = self._get_welcome_template_data()
            elif self.current_email_type == "password_reset":
                template_name = "password_reset.html"
                template_data = self._get_password_reset_template_data()
            elif self.current_email_type == "notification":
                template_name = "notification.html"
                template_data = self._get_notification_template_data()
            elif self.current_email_type == "alert":
                template_name = "alert.html"
                template_data = self._get_alert_template_data()
            elif self.current_email_type == "batch":
                # Para batch, usamos el tipo seleccionado en el formulario
                email_type = self.batch_form.email_type.currentText()
                
                if email_type == "welcome":
                    template_name = "welcome.html"
                    template_data = self._get_batch_welcome_template_data()
                elif email_type == "password-reset":
                    template_name = "password_reset.html"
                    template_data = self._get_batch_password_reset_template_data()
                elif email_type == "notification":
                    template_name = "notification.html"
                    template_data = self._get_batch_notification_template_data()
                elif email_type == "alert":
                    template_name = "alert.html"
                    template_data = self._get_batch_alert_template_data()
                else:
                    self.preview_panel.clear_preview()
                    self._show_error_message("Tipo de email no válido para el lote")
                    return
            else:
                self.preview_panel.clear_preview()
                self._show_error_message("Tipo de email no válido")
                return
            
            # Renderizar la plantilla
            # En una implementación real, esto se haría en un hilo separado
            worker = RenderPreviewWorker(self.template_env, template_name, template_data)
            worker.on_preview_ready = self.preview_panel.set_html_content
            worker.on_error = self._show_error_message
            worker.run()
            
        except Exception as e:
            logger.error(f"Error al actualizar la vista previa: {str(e)}")
            self._show_error_message(f"Error al actualizar la vista previa: {str(e)}")
    
    def _show_error_message(self, message):
        """
        Muestra un mensaje de error.
        
        Args:
            message (str): Mensaje de error
        """
        logger.error(message)
        QMessageBox.critical(self, "Error", message)
    
    def _send_email(self):
        """Envía el email según el tipo actual."""
        try:
            if not self.current_email_type:
                raise ValueError("No se ha seleccionado un tipo de email")
            
            if not self.api_client.api_key:
                raise ValueError("No se ha configurado la API key")
            
            # Obtener datos comunes
            company_data = self.company_form.get_company_data()
            
            # Enviar según el tipo
            if self.current_email_type == "welcome":
                self._send_welcome_email(company_data)
            elif self.current_email_type == "password_reset":
                self._send_password_reset(company_data)
            elif self.current_email_type == "notification":
                self._send_notification(company_data)
            elif self.current_email_type == "alert":
                self._send_alert(company_data)
            elif self.current_email_type == "batch":
                self._send_batch_email(company_data)
            else:
                raise ValueError(f"Tipo de email no soportado: {self.current_email_type}")
            
        except APIError as e:
            self._show_error_message(f"Error al enviar email: {e.detail} (código: {e.status_code})")
        except Exception as e:
            self._show_error_message(f"Error al enviar email: {str(e)}")
    
    def _send_welcome_email(self, company_data):
        """
        Envía un email de bienvenida.
        
        Args:
            company_data (dict): Datos de la empresa
        """
        form_data = self.welcome_form.get_form_data()
        
        # Preparar datos de usuario
        user_data = {
            "email": form_data["user"]["emails"][0],
            "name": form_data["user"]["names"][0] if form_data["user"]["names"] else None
        }
        
        # Si hay múltiples destinatarios, usar formato para múltiples
        if len(form_data["user"]["emails"]) > 1:
            user_data = {
                "emails": form_data["user"]["emails"],
                "names": form_data["user"]["names"]
            }
        
        # Enviar el email
        result = self.api_client.send_welcome_email(
            company=company_data,
            user=user_data,
            dashboard_url=form_data["query"]["dashboard_url"]
        )
        
        QMessageBox.information(
            self, 
            "Email Enviado", 
            f"El email de bienvenida se ha enviado correctamente. ID: {result.get('message_id')}"
        )
    
    def _send_password_reset(self, company_data):
        """
        Envía un email de restablecimiento de contraseña.
        
        Args:
            company_data (dict): Datos de la empresa
        """
        form_data = self.password_reset_form.get_form_data()
        
        # Preparar datos de usuario
        user_data = {
            "email": form_data["user"]["emails"][0],
            "name": form_data["user"]["names"][0] if form_data["user"]["names"] else None
        }
        
        # Si hay múltiples destinatarios, usar formato para múltiples
        if len(form_data["user"]["emails"]) > 1:
            user_data = {
                "emails": form_data["user"]["emails"],
                "names": form_data["user"]["names"]
            }
        
        # Enviar el email
        result = self.api_client.send_password_reset(
            company=company_data,
            user=user_data,
            reset_url=form_data["query"]["reset_url"],
            expires_in=form_data["query"]["expires_in"]
        )
        
        QMessageBox.information(
            self, 
            "Email Enviado", 
            f"El email de restablecimiento de contraseña se ha enviado correctamente. ID: {result.get('message_id')}"
        )
    
    def _send_notification(self, company_data):
        """
        Envía un email de notificación.
        
        Args:
            company_data (dict): Datos de la empresa
        """
        form_data = self.notification_form.get_form_data()
        
        # Preparar datos de usuario
        user_data = {
            "email": form_data["user"]["emails"][0],
            "name": form_data["user"]["names"][0] if form_data["user"]["names"] else None
        }
        
        # Si hay múltiples destinatarios, usar formato para múltiples
        if len(form_data["user"]["emails"]) > 1:
            user_data = {
                "emails": form_data["user"]["emails"],
                "names": form_data["user"]["names"]
            }
        
        # Enviar el email
        result = self.api_client.send_notification(
            company=company_data,
            user=user_data,
            notification=form_data["notification"],
            preferences_url=form_data["query"]["preferences_url"]
        )
        
        QMessageBox.information(
            self, 
            "Email Enviado", 
            f"El email de notificación se ha enviado correctamente. ID: {result.get('message_id')}"
        )
    
    def _send_alert(self, company_data):
        """
        Envía un email de alerta.
        
        Args:
            company_data (dict): Datos de la empresa
        """
        form_data = self.alert_form.get_form_data()
        
        # Preparar datos de usuario
        user_data = {
            "email": form_data["user"]["emails"][0],
            "name": form_data["user"]["names"][0] if form_data["user"]["names"] else None
        }
        
        # Si hay múltiples destinatarios, usar formato para múltiples
        if len(form_data["user"]["emails"]) > 1:
            user_data = {
                "emails": form_data["user"]["emails"],
                "names": form_data["user"]["names"]
            }
        
        # Enviar el email
        result = self.api_client.send_alert(
            company=company_data,
            user=user_data,
            alert=form_data["alert"]
        )
        
        QMessageBox.information(
            self, 
            "Email Enviado", 
            f"El email de alerta se ha enviado correctamente. ID: {result.get('message_id')}"
        )
    
    def _send_batch_email(self, company_data):
        """
        Envía emails en lote.
        
        Args:
            company_data (dict): Datos de la empresa
        """
        form_data = self.batch_form.get_form_data()
        
        # Validar que haya destinatarios
        if not form_data["recipients"]:
            raise ValueError("No se han proporcionado destinatarios")
        
        # Enviar el email en lote
        result = self.api_client.send_batch_email(
            email_type=form_data["email_type"],
            company=company_data,
            recipients=form_data["recipients"],
            query=form_data.get("query"),
            alert=form_data.get("alert")
        )
        
        QMessageBox.information(
            self, 
            "Emails Enviados", 
            f"Se han enviado {result.get('sent', 0)} emails correctamente.\n"
            f"Fallaron {result.get('failed', 0)} envíos.\n"
            f"Total: {result.get('total', 0)} emails."
        )
    
    # Métodos para obtener datos de plantillas (utilizados para la vista previa)
    
    def _get_welcome_template_data(self):
        """Obtiene los datos para la plantilla de bienvenida."""
        form_data = self.welcome_form.get_form_data()
        company_data = self.company_form.get_company_data()
        
        # Obtener el primer email y nombre
        email = form_data["user"]["emails"][0]
        name = form_data["user"]["names"][0] if form_data["user"]["names"] else "Usuario"
        
        return {
            "company": company_data,
            "user": {
                "name": name,
                "email": email
            },
            "dashboard_url": form_data["query"]["dashboard_url"],
            "year": 2025
        }
    
    def _get_password_reset_template_data(self):
        """Obtiene los datos para la plantilla de reset de contraseña."""
        form_data = self.password_reset_form.get_form_data()
        company_data = self.company_form.get_company_data()
        
        # Obtener el primer email y nombre
        email = form_data["user"]["emails"][0]
        name = form_data["user"]["names"][0] if form_data["user"]["names"] else "Usuario"
        
        return {
            "company": company_data,
            "user": {
                "name": name,
                "email": email
            },
            "reset_url": form_data["query"]["reset_url"],
            "expires_in": form_data["query"]["expires_in"],
            "year": 2025
        }
    
    def _get_notification_template_data(self):
        """Obtiene los datos para la plantilla de notificación."""
        form_data = self.notification_form.get_form_data()
        company_data = self.company_form.get_company_data()
        
        # Obtener el primer email y nombre
        email = form_data["user"]["emails"][0]
        name = form_data["user"]["names"][0] if form_data["user"]["names"] else "Usuario"
        
        return {
            "company": company_data,
            "user": {
                "name": name,
                "email": email
            },
            "notification": form_data["notification"],
            "preferences_url": form_data["query"]["preferences_url"],
            "year": 2025
        }
    
    def _get_alert_template_data(self):
        """Obtiene los datos para la plantilla de alerta."""
        form_data = self.alert_form.get_form_data()
        company_data = self.company_form.get_company_data()
        
        # Obtener el primer email y nombre
        email = form_data["user"]["emails"][0]
        name = form_data["user"]["names"][0] if form_data["user"]["names"] else "Usuario"
        
        return {
            "company": company_data,
            "user": {
                "name": name,
                "email": email
            },
            "alert": form_data["alert"],
            "year": 2025
        }
    
    def _get_batch_welcome_template_data(self):
        """Obtiene los datos para la plantilla de bienvenida en lote."""
        form_data = self.batch_form.get_form_data()
        company_data = self.company_form.get_company_data()
        
        # Usar el primer destinatario para la vista previa
        if form_data["recipients"]:
            recipient = form_data["recipients"][0]
            email = recipient["email"]
            name = recipient["name"] or "Usuario"
        else:
            email = "usuario@ejemplo.com"
            name = "Usuario de Prueba"
        
        query = form_data.get("query", {})
        
        return {
            "company": company_data,
            "user": {
                "name": name,
                "email": email
            },
            "dashboard_url": query.get("dashboard_url", "https://miempresa.com/dashboard"),
            "year": 2025
        }
    
    def _get_batch_password_reset_template_data(self):
        """Obtiene los datos para la plantilla de reset en lote."""
        form_data = self.batch_form.get_form_data()
        company_data = self.company_form.get_company_data()
        
        # Usar el primer destinatario para la vista previa
        if form_data["recipients"]:
            recipient = form_data["recipients"][0]
            email = recipient["email"]
            name = recipient["name"] or "Usuario"
        else:
            email = "usuario@ejemplo.com"
            name = "Usuario de Prueba"
        
        query = form_data.get("query", {})
        
        return {
            "company": company_data,
            "user": {
                "name": name,
                "email": email
            },
            "reset_url": query.get("reset_url", "https://miempresa.com/reset-password"),
            "expires_in": query.get("expires_in", 24),
            "year": 2025
        }
    
    def _get_batch_notification_template_data(self):
        """Obtiene los datos para la plantilla de notificación en lote."""
        form_data = self.batch_form.get_form_data()
        company_data = self.company_form.get_company_data()
        
        # Usar el primer destinatario para la vista previa
        if form_data["recipients"]:
            recipient = form_data["recipients"][0]
            email = recipient["email"]
            name = recipient["name"] or "Usuario"
        else:
            email = "usuario@ejemplo.com"
            name = "Usuario de Prueba"
        
        query = form_data.get("query", {})
        
        # Este es un caso especial donde la consulta contiene los datos de la notificación
        notification = {
            "title": query.get("title", "Notificación Importante"),
            "message": query.get("message", "Este es un mensaje de notificación de prueba."),
            "type": query.get("type", "info"),
            "icon": query.get("icon"),
            "action_url": query.get("action_url"),
            "action_text": query.get("action_text"),
            "additional_info": query.get("additional_info")
        }
        
        return {
            "company": company_data,
            "user": {
                "name": name,
                "email": email
            },
            "notification": notification,
            "preferences_url": query.get("preferences_url", ""),
            "year": 2025
        }
    
    def _get_batch_alert_template_data(self):
        """Obtiene los datos para la plantilla de alerta en lote."""
        form_data = self.batch_form.get_form_data()
        company_data = self.company_form.get_company_data()
        
        # Usar el primer destinatario para la vista previa
        if form_data["recipients"]:
            recipient = form_data["recipients"][0]
            email = recipient["email"]
            name = recipient["name"] or "Usuario"
        else:
            email = "usuario@ejemplo.com"
            name = "Usuario de Prueba"
        
        alert = form_data.get("alert", {
            "title": "Alerta de Seguridad",
            "message": "Este es un mensaje de alerta de prueba.",
            "type": "info",
            "steps": ["Paso 1", "Paso 2", "Paso 3"],
            "action_url": "https://miempresa.com/action",
            "action_text": "Resolver Ahora",
            "contact_support": True
        })
        
        return {
            "company": company_data,
            "user": {
                "name": name,
                "email": email
            },
            "alert": alert,
            "year": 2025
        }