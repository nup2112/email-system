"""
Punto de entrada principal para el cliente GUI.
Organiza los componentes y configura la aplicación.
"""
import sys
import argparse
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QPalette, QColor

from config import ClientConfig
from components.main_window import EmailTesterMainWindow


def setup_logging(debug=False):
    """
    Configura el logging para el cliente GUI.
    
    Args:
        debug (bool): Si está en modo debug
    """
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
    )


def parse_arguments():
    """
    Parsea los argumentos de línea de comandos.
    
    Returns:
        argparse.Namespace: Argumentos parseados
    """
    parser = argparse.ArgumentParser(description="Email System Tester GUI")
    
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8000/api",
        help="URL de la API (default: http://localhost:8000/api)",
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key para autenticación",
    )
    
    parser.add_argument(
        "--templates-dir",
        type=str,
        help="Directorio de plantillas HTML",
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Habilitar modo debug",
    )
    
    return parser.parse_args()


def setup_app_style(app):
    """
    Configura el estilo de la aplicación.
    
    Args:
        app (QApplication): Aplicación Qt
    """
    # Establecer estilo base
    app.setStyle("Fusion")
    
    # Paleta de colores moderna
    palette = QPalette()
    
    # Colores principales
    primary_color = QColor(156, 39, 176)      # Morado principal
    secondary_color = QColor(103, 58, 183)    # Violeta secundario
    background_color = QColor(250, 250, 252)  # Fondo general muy claro
    surface_color = QColor(255, 255, 255)     # Superficies (como tarjetas)
    text_primary = QColor(33, 33, 33)         # Texto principal
    text_secondary = QColor(117, 117, 117)    # Texto secundario
    divider_color = QColor(238, 238, 238)     # Divisores
    
    # Configurar paleta
    palette.setColor(QPalette.Window, background_color)
    palette.setColor(QPalette.WindowText, text_primary)
    palette.setColor(QPalette.Base, surface_color)
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 250))
    palette.setColor(QPalette.ToolTipBase, surface_color)
    palette.setColor(QPalette.ToolTipText, text_primary)
    palette.setColor(QPalette.Text, text_primary)
    palette.setColor(QPalette.Button, surface_color)
    palette.setColor(QPalette.ButtonText, text_primary)
    palette.setColor(QPalette.BrightText, surface_color)
    palette.setColor(QPalette.Highlight, primary_color)
    palette.setColor(QPalette.HighlightedText, surface_color)
    palette.setColor(QPalette.Disabled, QPalette.Text, text_secondary)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, text_secondary)
    
    app.setPalette(palette)
    
    # Cargar hoja de estilos CSS
    app.setStyleSheet("""
        /* Estilos generales */
        QMainWindow, QDialog {
            background-color: #fafafc;
        }
        
        /* Barra lateral */
        QListWidget {
            background-color: #2e2e36;
            border: none;
            border-radius: 0px;
            font-size: 14px;
            padding: 8px 0px;
        }
        
        QListWidget::item {
            color: #e0e0e0;
            padding: 12px 16px;
            margin: 4px 8px;
            border-radius: 6px;
        }
        
        QListWidget::item:selected {
            background-color: #9c27b0;
            color: white;
        }
        
        QListWidget::item:hover:!selected {
            background-color: #3a3a44;
        }
        
        /* Encabezados y etiquetas */
        QLabel {
            color: #212121;
            font-size: 13px;
        }
        
        QGroupBox {
            font-size: 14px;
            font-weight: bold;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-top: 16px;
            padding-top: 16px;
            background-color: white;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 10px;
            color: #9c27b0;
            background-color: transparent;
        }
        
        /* Campos de entrada */
        QLineEdit, QTextEdit, QComboBox, QSpinBox {
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 8px;
            background-color: white;
            selection-background-color: #9c27b0;
            selection-color: white;
            min-height: 20px;
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
            border: 2px solid #9c27b0;
            padding: 7px;
        }
        
        /* Botones */
        QPushButton {
            background-color: #f5f5f5;
            color: #212121;
            border: none;
            border-radius: 6px;
            padding: 10px 16px;
            font-weight: bold;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        
        /* Scrollbars */
        QScrollBar:vertical {
            border: none;
            background: #f5f5f5;
            width: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background: #9c27b0;
            min-height: 20px;
            border-radius: 5px;
        }
    """)


def main():
    """Función principal que inicia la aplicación GUI."""
    # Parsear argumentos
    args = parse_arguments()
    
    # Configurar logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    logger.info("Iniciando Email System Tester GUI")
    
    # Crear configuración del cliente
    config = ClientConfig(
        api_url=args.api_url,
        api_key=args.api_key,
        templates_dir=args.templates_dir,
        debug=args.debug,
    )
    
    # Crear la aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Email System Tester")
    app.setApplicationVersion("1.0.0")
    # app.setWindowIcon(QIcon("path/to/icon.png"))
    
    # Configurar estilo
    setup_app_style(app)
    
    # Crear y mostrar ventana principal
    main_window = EmailTesterMainWindow(config)
    main_window.show()
    
    # Ejecutar loop de eventos
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()