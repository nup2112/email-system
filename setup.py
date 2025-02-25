"""
Script de configuración para el paquete email_system.
"""
from setuptools import setup, find_packages

# Leer README para descripción larga
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Requisitos de instalación
install_requires = [
    # API
    "fastapi>=0.103.1",
    "uvicorn>=0.23.2",
    "pydantic>=2.4.2",
    "python-multipart>=0.0.6",
    "email-validator>=2.0.0",
    "jinja2>=3.1.2",
    "premailer>=3.10.0",
    "resend>=0.6.0",
    
    # Cliente
    "PyQt5>=5.15.9",
    "requests>=2.31.0",
]

# Dependencias opcionales
extras_require = {
    "dev": [
        "pytest>=7.4.2",
        "black>=23.9.1",
        "flake8>=6.1.0",
        "isort>=5.12.0",
        "mypy>=1.5.1",
        "pytest-cov>=4.1.0",
    ],
    "client": [
        "PyQt5>=5.15.9",
        "requests>=2.31.0",
    ],
}

setup(
    name="email_system",
    version="1.0.0",
    author="Tu Nombre",
    author_email="tu.email@ejemplo.com",
    description="Sistema de envío de emails con API y cliente GUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/email-system",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "email-system-api=email_system.api.main:main",
            "email-system-client=email_system.client.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "email_system": ["email_service/templates/*.html"],
    },
)