"""
Componente de vista previa de email.
"""
import logging
import tempfile
import webbrowser
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextBrowser, QFileDialog, QSplitter, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

logger = logging.getLogger(__name__)

class EmailPreviewPanel(QWidget):
    """Panel de vista previa de email con funcionalidades de guardado y apertura en navegador."""
    
    # Señal para notificar errores a la ventana principal
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.html_content = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        
        # Título para la vista previa
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        title = QLabel("Vista Previa del Email")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botones para la vista previa
        self.preview_in_browser_btn = QPushButton("Abrir en Navegador")
        self.preview_in_browser_btn.clicked.connect(self.open_in_browser)
        self.preview_in_browser_btn.setEnabled(False)  # Deshabilitado hasta que haya contenido
        header_layout.addWidget(self.preview_in_browser_btn)
        
        self.save_preview_btn = QPushButton("Guardar HTML")
        self.save_preview_btn.clicked.connect(self.save_html)
        self.save_preview_btn.setEnabled(False)  # Deshabilitado hasta que haya contenido
        header_layout.addWidget(self.save_preview_btn)
        
        layout.addWidget(header)
        
        # Visor de HTML
        self.html_viewer = QTextBrowser()
        self.html_viewer.setOpenExternalLinks(True)
        layout.addWidget(self.html_viewer)
    
    def set_html_content(self, html):
        """
        Establece el contenido HTML en la vista previa.
        
        Args:
            html (str): Contenido HTML a mostrar
        """
        if not html:
            logger.warning("Intentando establecer contenido HTML vacío")
            return
        
        self.html_content = html
        self.html_viewer.setHtml(html)
        
        # Habilitar botones
        self.preview_in_browser_btn.setEnabled(True)
        self.save_preview_btn.setEnabled(True)
        
        logger.debug("Contenido HTML establecido en la vista previa")
    
    def clear_preview(self):
        """Limpia la vista previa."""
        self.html_content = None
        self.html_viewer.setHtml("")
        
        # Deshabilitar botones
        self.preview_in_browser_btn.setEnabled(False)
        self.save_preview_btn.setEnabled(False)
        
        logger.debug("Vista previa limpiada")
    
    def open_in_browser(self):
        """Abre la vista previa actual en el navegador."""
        if not self.html_content:
            QMessageBox.warning(self, "Error", "No hay vista previa disponible.")
            return
            
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as f:
                f.write(self.html_content)
                temp_name = f.name
            
            # Abrir en navegador
            webbrowser.open('file://' + temp_name)
            logger.info(f"Vista previa abierta en navegador: {temp_name}")
        except Exception as e:
            logger.error(f"Error al abrir en navegador: {str(e)}")
            self.error_occurred.emit(f"No se pudo abrir en el navegador: {str(e)}")
    
    def save_html(self):
        """Guarda la vista previa actual como archivo HTML."""
        if not self.html_content:
            QMessageBox.warning(self, "Error", "No hay vista previa disponible.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar HTML", "", "Archivos HTML (*.html *.htm)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.html_content)
                logger.info(f"HTML guardado en: {file_path}")
                QMessageBox.information(self, "Éxito", f"HTML guardado en: {file_path}")
            except Exception as e:
                logger.error(f"Error al guardar HTML: {str(e)}")
                self.error_occurred.emit(f"No se pudo guardar el archivo: {str(e)}")


class RenderPreviewWorker:
    """
    Clase para renderizar la vista previa en un hilo separado.
    En una implementación real, esto debería ser un QThread,
    pero aquí se deja como stub para simplificar.
    """
    
    def __init__(self, template_env, template_name, template_data):
        """
        Inicializa el renderizador de vistas previas.
        
        Args:
            template_env: Entorno de plantillas Jinja2
            template_name: Nombre de la plantilla a renderizar
            template_data: Datos para la plantilla
        """
        self.template_env = template_env
        self.template_name = template_name
        self.template_data = template_data
        
        # Callbacks
        self.on_preview_ready = None
        self.on_error = None
        
    def run(self):
        """Ejecuta el renderizado de la vista previa."""
        try:
            if not self.template_env:
                if self.on_error:
                    self.on_error("El motor de plantillas no está configurado.")
                return
            
            template = self.template_env.get_template(self.template_name)
            html_content = template.render(**self.template_data)
            
            if self.on_preview_ready:
                self.on_preview_ready(html_content)
        except Exception as e:
            logger.error(f"Error al renderizar vista previa: {str(e)}")
            if self.on_error:
                self.on_error(f"Error al renderizar vista previa: {str(e)}")