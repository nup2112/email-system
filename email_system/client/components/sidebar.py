"""
Componente de barra lateral para la aplicación.
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal

logger = logging.getLogger(__name__)

class EmailTypesSidebar(QWidget):
    """Barra lateral con los tipos de emails disponibles."""
    
    # Señal que se emite cuando cambia la selección
    email_type_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(250)
        self.setMinimumWidth(200)
        self.setStyleSheet("""
            background-color: #2e2e36;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
        """)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Título de la barra lateral
        header = QLabel("Email System")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 20px 15px;
            color: white;
            background-color: #232329;
        """)
        layout.addWidget(header)
        
        # Subtítulo
        subtitle = QLabel("TIPOS DE EMAIL")
        subtitle.setAlignment(Qt.AlignLeft)
        subtitle.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            padding: 15px 20px 10px 20px;
            color: #9e9e9e;
            background-color: #232329;
        """)
        layout.addWidget(subtitle)
        
        # Lista de tipos de email
        self.email_types_list = QListWidget()
        self.email_types_list.setStyleSheet("""
            border: none;
            outline: none;
            min-height: 800px;
            background-color: #232329;                                            
        """)
        
        # Añadir los tipos de email
        self._add_email_types()
        
        # Conectar señal de cambio de selección
        self.email_types_list.currentItemChanged.connect(self._on_item_changed)
        
        layout.addWidget(self.email_types_list)
        
        # Añadir espacio
        layout.addStretch()
        
        # Footer
        footer = QLabel("© 2025 Email System")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("""
            font-size: 12px;
            padding: 15px;
            color: #9e9e9e;
            background-color: #232329;
        """)
        layout.addWidget(footer)
    
    def _add_email_types(self):
        """Añade los tipos de email a la lista."""
        email_types = [
            ("welcome", "Bienvenida", "👋"),
            ("password_reset", "Reset Contraseña", "🔒"),
            ("notification", "Notificación", "🔔"),
            ("alert", "Alerta", "⚠️"),
            ("batch", "Envío en Lote", "📧")
        ]
        
        for email_type, display_name, icon in email_types:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, email_type)
            item.setText(f"{icon}  {display_name}")
            self.email_types_list.addItem(item)
        
        # Seleccionar el primer elemento por defecto
        if self.email_types_list.count() > 0:
            self.email_types_list.setCurrentRow(0)
    
    def _on_item_changed(self, current, previous):
        """Maneja el cambio de selección en la lista."""
        if current:
            email_type = current.data(Qt.UserRole)
            logger.debug(f"Tipo de email seleccionado: {email_type}")
            self.email_type_changed.emit(email_type)
    
    def select_email_type(self, email_type):
        """
        Selecciona un tipo de email programáticamente.
        
        Args:
            email_type (str): Tipo de email a seleccionar
        """
        for i in range(self.email_types_list.count()):
            item = self.email_types_list.item(i)
            if item.data(Qt.UserRole) == email_type:
                self.email_types_list.setCurrentItem(item)
                break
    
    def get_selected_email_type(self):
        """
        Obtiene el tipo de email seleccionado actualmente.
        
        Returns:
            str: Tipo de email seleccionado o None si no hay selección
        """
        current_item = self.email_types_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None