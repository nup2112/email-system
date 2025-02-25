"""
Aplicación FastAPI principal para el sistema de emails.
"""
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from email_system.api.routes.email_routes import router as email_router
from email_system.core.exceptions import EmailSystemError, APIError
from email_system.core.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(
    title="Email System API",
    description="API para el sistema de envío de emails",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar según el entorno
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(email_router, prefix="/api")


# Manejador de excepciones
@app.exception_handler(EmailSystemError)
async def email_system_exception_handler(request: Request, exc: EmailSystemError):
    """Maneja excepciones de EmailSystemError."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    if isinstance(exc, APIError):
        status_code = exc.status_code
    
    logger.error(f"Error: {exc.message}")
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message},
    )


# Endpoint de estado
@app.get("/health", tags=["health"])
async def health_check():
    """Retorna el estado de la API."""
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    # Iniciar el servidor usando uvicorn
    uvicorn.run(
        "email_system.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )