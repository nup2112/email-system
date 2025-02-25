"""
Configuración para el cliente GUI.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class ClientConfig(BaseModel):
    """Configuración para el cliente GUI."""
    # URL base de la API
    api_url: str = Field(default="http://localhost:8000/api")
    
    # Directorio de plantillas
    templates_dir: Optional[Path] = None
    
    # API Key
    api_key: Optional[str] = ""
    
    # Modo depuración
    debug: bool = False
    
    def __init__(self, **data):
        """Inicializa la configuración con valores por defecto y del entorno."""
        # Cargar valores del entorno si existen
        if "api_url" not in data and os.getenv("EMAIL_SYSTEM_API_URL"):
            data["api_url"] = os.getenv("EMAIL_SYSTEM_API_URL")
            
        if "api_key" not in data and os.getenv("EMAIL_SYSTEM_API_KEY"):
            data["api_key"] = os.getenv("EMAIL_SYSTEM_API_KEY")
        
        # Si se proporciona un directorio de plantillas como string, convertirlo a Path
        if "templates_dir" in data and isinstance(data["templates_dir"], str):
            data["templates_dir"] = Path(data["templates_dir"])
            
        # Inicializar con los datos
        super().__init__(**data)
        
        # Si no se especificó un directorio de plantillas, buscar en ubicaciones posibles
        if self.templates_dir is None:
            self._find_templates_dir()
    
    def _find_templates_dir(self):
        """Busca el directorio de plantillas en ubicaciones posibles."""
        possible_paths = [
            Path("./templates"),
            Path("../templates"),
            Path(__file__).parent.parent.parent / "email_system" / "email_service" / "templates",
            Path(os.path.expanduser("~")) / ".email_system" / "templates"
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                self.templates_dir = path
                break
    
    def save_api_key(self, api_key: str):
        """Guarda la API key para uso futuro."""
        self.api_key = api_key
        
        # También se podría guardar en un archivo de configuración para persistencia
        if self.debug:
            print(f"API key guardada: {api_key[:4]}...")