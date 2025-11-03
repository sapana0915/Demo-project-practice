# Vault Management Guide

This guide covers the complete vault system for managing sensitive configuration data, environment variables, and secrets across development and production environments.

## 📋 Table of Contents

- [What is Vault?](#what-is-vault)
- [Vault File Structure](#vault-file-structure)
- [Initial Setup](#initial-setup)
- [Adding Keys to Vault](#adding-keys-to-vault)
- [Development Environment](#development-environment)
- [Production Environment](#production-environment)
- [Deployment Process](#deployment-process)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## 🔐 What is Vault?

The vault system is AtomicLoops' centralized configuration management solution that:

- **🔒 Secures sensitive data**: API keys, database credentials, secrets
- **🌍 Environment separation**: Different configs for dev/staging/prod
- **🔄 Version control**: Track configuration changes
- **📦 Easy deployment**: Automated config distribution
- **👥 Team collaboration**: Shared configuration management

---

## 📁 Vault File Structure

### **vault.py Structure**
```python
# src/vault.py
# AtomicLoops Vault Configuration System

# Dictionary-based configuration for different environments
credentials = {
    "dev": {
        # Email Configuration
        "EMAIL": "your-dev-email@gmail.com",
        "PASSWORD": "your-app-password",
        
        # AWS Configuration
        "S3_BUCKET": "your-dev-s3-bucket",
        "AWS_ACCESS_KEY_ID": "your-dev-aws-access-key",
        "AWS_SECRET_ACCESS_KEY": "your-dev-aws-secret-key",
        "REGION": "ap-south-1",
        "AWS_URL": "https://s3.ap-south-1.amazonaws.com",
        
        # Database Configuration
        "DB_ENGINE": "django.db.backends.postgresql",
        "DB_NAME": "myapp_dev",
        "DB_USER": "postgres",
        "DB_PASSWORD": "postgres",
        "DB_HOST": "localhost",  # or "test-db" for Docker
        "DB_PORT": 5432,
        
        # Frontend URLs
        "FRONTEND_BASE_URL": "http://localhost:3000",
        "ADMIN_FRONTEND_BASE_URL": "http://localhost:3001",
        
        # Additional Development Settings
        "DEBUG": True,
        "SECRET_KEY": "dev-secret-key-change-in-production",
        "ALLOWED_HOSTS": "localhost,127.0.0.1,0.0.0.0",
        
        # Redis Configuration
        "REDIS_HOST": "localhost",
        "REDIS_PORT": 6379,
        "REDIS_PASSWORD": "",
        
        # Third-party API Keys (Development)
        "GOOGLE_MAPS_API_KEY": "your-dev-google-maps-key",
        "STRIPE_PUBLIC_KEY": "pk_test_dev_key",
        "STRIPE_SECRET_KEY": "sk_test_dev_key",
        "FIREBASE_PRIVATE_KEY": "your-dev-firebase-key",
    },
    
    "staging": {
        # Email Configuration
        "EMAIL": "staging@yourcompany.com",
        "PASSWORD": "staging-email-password",
        
        # AWS Configuration
        "S3_BUCKET": "your-staging-s3-bucket",
        "AWS_ACCESS_KEY_ID": "your-staging-aws-access-key",
        "AWS_SECRET_ACCESS_KEY": "your-staging-aws-secret-key",
        "REGION": "ap-south-1",
        "AWS_URL": "https://s3.ap-south-1.amazonaws.com",
        
        # Database Configuration
        "DB_ENGINE": "django.db.backends.postgresql",
        "DB_NAME": "myapp_staging",
        "DB_USER": "myapp_staging_user",
        "DB_PASSWORD": "staging-db-password",
        "DB_HOST": "staging-db.yourcompany.com",
        "DB_PORT": 5432,
        
        # Frontend URLs
        "FRONTEND_BASE_URL": "https://staging.yourapp.com",
        "ADMIN_FRONTEND_BASE_URL": "https://admin-staging.yourapp.com",
        
        # Staging Settings
        "DEBUG": False,
        "SECRET_KEY": "staging-secret-key-different-from-prod",
        "ALLOWED_HOSTS": "staging.yourapp.com,admin-staging.yourapp.com",
        
        # Redis Configuration
        "REDIS_HOST": "staging-redis.yourcompany.com",
        "REDIS_PORT": 6379,
        "REDIS_PASSWORD": "staging-redis-password",
        
        # Third-party API Keys (Staging)
        "GOOGLE_MAPS_API_KEY": "your-staging-google-maps-key",
        "STRIPE_PUBLIC_KEY": "pk_test_staging_key",
        "STRIPE_SECRET_KEY": "sk_test_staging_key",
        "FIREBASE_PRIVATE_KEY": "your-staging-firebase-key",
    },
    
    "prod": {
        # Email Configuration
        "EMAIL": "noreply@yourcompany.com",
        "PASSWORD": "production-email-password",
        
        # AWS Configuration
        "S3_BUCKET": "your-production-s3-bucket",
        "AWS_ACCESS_KEY_ID": "your-production-aws-access-key",
        "AWS_SECRET_ACCESS_KEY": "your-production-aws-secret-key",
        "REGION": "ap-south-1",
        "AWS_URL": "https://s3.ap-south-1.amazonaws.com",
        
        # Database Configuration
        "DB_ENGINE": "django.db.backends.postgresql",
        "DB_NAME": "myapp_production",
        "DB_USER": "myapp_prod_user",
        "DB_PASSWORD": "super-secure-production-password",
        "DB_HOST": "prod-db.yourcompany.com",
        "DB_PORT": 5432,
        
        # Frontend URLs
        "FRONTEND_BASE_URL": "https://yourapp.com",
        "ADMIN_FRONTEND_BASE_URL": "https://admin.yourapp.com",
        
        # Production Settings
        "DEBUG": False,
        "SECRET_KEY": "production-secret-key-very-secure",
        "ALLOWED_HOSTS": "yourapp.com,www.yourapp.com,admin.yourapp.com,api.yourapp.com",
        
        # Redis Configuration
        "REDIS_HOST": "prod-redis.yourcompany.com",
        "REDIS_PORT": 6379,
        "REDIS_PASSWORD": "production-redis-password",
        
        # Third-party API Keys (Production)
        "GOOGLE_MAPS_API_KEY": "your-production-google-maps-key",
        "STRIPE_PUBLIC_KEY": "pk_live_production_key",
        "STRIPE_SECRET_KEY": "sk_live_production_key",
        "FIREBASE_PRIVATE_KEY": "your-production-firebase-key",
    },
}

# Helper function to get current environment credentials
import os

def get_credentials(env=None):
    """
    Get credentials for specified environment.
    If no environment specified, use ENV environment variable or default to 'dev'
    """
    if env is None:
        env = os.getenv('ENV', 'dev')
    
    if env not in credentials:
        raise ValueError(f"Environment '{env}' not found in vault. Available: {list(credentials.keys())}")
    
    return credentials[env]

# Global access to current environment credentials
current_env = os.getenv('ENV', 'dev')
vault = get_credentials(current_env)
```

---

## 🚀 Initial Setup

### **1. Download Initial Vault File**

**Linux/macOS:**
```bash
# Download initial vault template
wget -O src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py

# Or download latest version
wget -O src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```

**Windows:**
```powershell
# Download initial vault template
curl -o src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py

# Or download latest version
curl -o src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```



### **2. Verify Download**
```bash
# Check if vault file exists
ls -la src/vault.py

# Check file size (should not be empty)
wc -l src/vault.py
```

---

## 🔧 Adding Keys to Vault

### **1. Edit vault.py Directly**

**Add new configuration keys to all environments:**
```python
# In src/vault.py
credentials = {
    "dev": {
        # ... existing fields ...
        
        # Add your new configuration keys
        "NEW_API_KEY": "dev-api-key-12345",
        "NEW_SERVICE_URL": "https://dev-api.example.com",
        "NEW_FEATURE_ENABLED": True,
        "PAYMENT_GATEWAY_URL": "https://sandbox-payments.example.com",
        "MAX_FILE_SIZE": 10485760,  # 10MB for development
    },
    
    "staging": {
        # ... existing fields ...
        
        # Add staging values
        "NEW_API_KEY": "staging-api-key-67890",
        "NEW_SERVICE_URL": "https://staging-api.example.com",
        "NEW_FEATURE_ENABLED": True,
        "PAYMENT_GATEWAY_URL": "https://staging-payments.example.com",
        "MAX_FILE_SIZE": 52428800,  # 50MB for staging
    },
    
    "prod": {
        # ... existing fields ...
        
        # Add production values
        "NEW_API_KEY": "prod-api-key-secure-12345",
        "NEW_SERVICE_URL": "https://api.example.com",
        "NEW_FEATURE_ENABLED": False,  # Feature flag disabled in prod initially
        "PAYMENT_GATEWAY_URL": "https://payments.example.com",
        "MAX_FILE_SIZE": 104857600,  # 100MB for production
    },
}
```

**Alternative: Environment Variable Override (Production)**
```python
# For production, you can override with environment variables
credentials = {
    "prod": {
        # Use environment variables for sensitive production data
        "NEW_API_KEY": os.getenv("NEW_API_KEY", "fallback-key"),
        "NEW_SERVICE_URL": os.getenv("NEW_SERVICE_URL", "https://api.example.com"),
        "NEW_FEATURE_ENABLED": os.getenv("NEW_FEATURE_ENABLED", "false").lower() == "true",
        # ... other configs
    }
}
```

### **2. Use in Django Settings**

**In settings/base.py:**
```python
from vault import vault

# Use vault configuration (dictionary access)
SECRET_KEY = vault.get("SECRET_KEY", "fallback-secret-key")
DEBUG = vault.get("DEBUG", False)
ALLOWED_HOSTS = vault.get("ALLOWED_HOSTS", "localhost").split(",")

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': vault.get("DB_ENGINE", "django.db.backends.postgresql"),
        'NAME': vault.get("DB_NAME"),
        'USER': vault.get("DB_USER"),
        'PASSWORD': vault.get("DB_PASSWORD"),
        'HOST': vault.get("DB_HOST"),
        'PORT': vault.get("DB_PORT", 5432),
    }
}

# Email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = vault.get("EMAIL")
EMAIL_HOST_PASSWORD = vault.get("PASSWORD")
EMAIL_USE_TLS = True

# AWS configuration
AWS_ACCESS_KEY_ID = vault.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = vault.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = vault.get("S3_BUCKET")
AWS_S3_REGION_NAME = vault.get("REGION", "ap-south-1")
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

# Frontend URLs
FRONTEND_BASE_URL = vault.get("FRONTEND_BASE_URL", "http://localhost:3000")
ADMIN_FRONTEND_BASE_URL = vault.get("ADMIN_FRONTEND_BASE_URL", "http://localhost:3001")

# Redis configuration
REDIS_HOST = vault.get("REDIS_HOST", "localhost")
REDIS_PORT = vault.get("REDIS_PORT", 6379)
REDIS_PASSWORD = vault.get("REDIS_PASSWORD", "")

# Custom settings
YOUR_NEW_API_KEY = vault.get("NEW_API_KEY")
YOUR_SERVICE_URL = vault.get("NEW_SERVICE_URL")
PAYMENT_GATEWAY_URL = vault.get("PAYMENT_GATEWAY_URL")
MAX_FILE_SIZE = vault.get("MAX_FILE_SIZE", 10485760)  # Default 10MB
```

**Alternative: Direct import with environment check:**
```python
import os
from vault import get_credentials

# Get environment-specific credentials
env = os.getenv('ENV', 'dev')
credentials = get_credentials(env)

# Use credentials
SECRET_KEY = credentials["SECRET_KEY"]
DEBUG = credentials["DEBUG"]
DATABASES = {
    'default': {
        'ENGINE': credentials["DB_ENGINE"],
        'NAME': credentials["DB_NAME"],
        'USER': credentials["DB_USER"],
        'PASSWORD': credentials["DB_PASSWORD"],
        'HOST': credentials["DB_HOST"],
        'PORT': credentials["DB_PORT"],
    }
}
```

### **3. Common Configuration Examples**

#### **Database Credentials**
```python
# PostgreSQL Configuration
"DB_ENGINE": "django.db.backends.postgresql",
"DB_NAME": "myapp_prod",
"DB_USER": "myapp_user", 
"DB_PASSWORD": "secure_password_123",
"DB_HOST": "db.example.com",
"DB_PORT": 5432,

# MongoDB Configuration
"MONGO_URI": "mongodb://user:pass@localhost:27017/myapp",
"MONGO_DB_NAME": "myapp_production",

# SQLite (for development only)
"DB_ENGINE": "django.db.backends.sqlite3",
"DB_NAME": "db.sqlite3",
```

#### **Email Settings**
```python
# Gmail SMTP
"EMAIL": "noreply@mycompany.com",
"PASSWORD": "app_specific_password",
"EMAIL_HOST": "smtp.gmail.com",
"EMAIL_PORT": 587,
"EMAIL_USE_TLS": True,

# SendGrid
"SENDGRID_API_KEY": "SG.xxxxxxxxxxxxxxxxxxxx",
"EMAIL_BACKEND": "sendgrid_backend.SendgridBackend",

# Development (Console backend)
"EMAIL_BACKEND": "django.core.mail.backends.console.EmailBackend",
```

#### **Third-party APIs**
```python
# Social Authentication
"GOOGLE_OAUTH_CLIENT_ID": "your-google-client-id",
"GOOGLE_OAUTH_SECRET": "your-google-secret",
"FACEBOOK_APP_ID": "your-facebook-app-id",
"FACEBOOK_APP_SECRET": "your-facebook-secret",

# Payment Gateways
"STRIPE_PUBLIC_KEY": "pk_test_xxxxxxxxxxxx",
"STRIPE_SECRET_KEY": "sk_test_xxxxxxxxxxxx",
"RAZORPAY_KEY_ID": "rzp_test_xxxxxxxxxxxx",
"RAZORPAY_KEY_SECRET": "your-razorpay-secret",

# Cloud Services
"CLOUDINARY_NAME": "your-cloud-name",
"CLOUDINARY_API_KEY": "123456789012345",
"CLOUDINARY_API_SECRET": "your-cloudinary-secret",

# Google Services
"GOOGLE_MAPS_API_KEY": "your-google-maps-key",
"GOOGLE_ANALYTICS_ID": "GA-XXXXXXXXX-X",

# Firebase
"FIREBASE_PROJECT_ID": "your-firebase-project",
"FIREBASE_PRIVATE_KEY": "your-firebase-private-key",
"FIREBASE_CLIENT_EMAIL": "firebase-adminsdk@your-project.iam.gserviceaccount.com",
```

---

## 🛠️ Development Environment

### **1. Development Setup**
```bash
# Set development environment
export ENV=dev

# Or create .env file
echo "ENV=dev" > .env

# Run development server
uv run python manage.py runserver
```

### **2. Development Configuration**
- **Database**: Local PostgreSQL or SQLite
- **Email**: Console backend or development SMTP
- **Storage**: Local file system
- **Cache**: Local Redis or dummy cache
- **Debug**: Enabled with detailed error pages
- **Logging**: Verbose logging to console

### **3. Development Vault Values**
```python
# Development configuration in credentials["dev"]
"dev": {
    # Safe development values
    "SECRET_KEY": "dev-secret-key-not-for-production",
    "DEBUG": True,
    "ALLOWED_HOSTS": "localhost,127.0.0.1,0.0.0.0,*",  # Allow all hosts in dev
    
    # Local services
    "DB_HOST": "localhost",  # or "test-db" for Docker
    "DB_NAME": "myapp_dev",
    "DB_USER": "postgres",
    "DB_PASSWORD": "postgres",
    
    "REDIS_HOST": "localhost",
    "REDIS_PORT": 6379,
    "REDIS_PASSWORD": "",  # No password for local Redis
    
    # Development API keys (limited scope)
    "GOOGLE_MAPS_API_KEY": "dev-maps-key-restricted",
    "STRIPE_SECRET_KEY": "sk_test_dev_key_12345",
    "STRIPE_PUBLIC_KEY": "pk_test_dev_key_12345",
    
    # Development AWS (separate dev bucket)
    "AWS_ACCESS_KEY_ID": "dev-aws-access-key",
    "AWS_SECRET_ACCESS_KEY": "dev-aws-secret-key",
    "S3_BUCKET": "myapp-dev-media",
    
    # Frontend URLs (local development)
    "FRONTEND_BASE_URL": "http://localhost:3000",
    "ADMIN_FRONTEND_BASE_URL": "http://localhost:3001",
    
    # Email (console backend for development)
    "EMAIL": "dev@localhost.com",
    "PASSWORD": "dev-password-123",
    "EMAIL_BACKEND": "django.core.mail.backends.console.EmailBackend",
}
```

### **4. Development Commands**
```bash
# Run with development settings
uv run python manage.py runserver --settings=src.settings.dev

# Run migrations in development
uv run python manage.py migrate --settings=src.settings.dev

# Create development superuser
uv run python manage.py createsuperuser --settings=src.settings.dev

# Load development fixtures
uv run python manage.py loaddata dev_data.json
```

---

## 🚀 Production Environment

### **1. Production Environment Variables**

**Set on server/container:**
```bash
# Core Django
export DJANGO_SECRET_KEY="production-secret-key-very-secure"
export ALLOWED_HOSTS="myapp.com,www.myapp.com,api.myapp.com"

# Database
export PROD_DB_NAME="myapp_production"
export PROD_DB_USER="myapp_prod_user"
export PROD_DB_PASSWORD="super_secure_password_123"
export PROD_DB_HOST="prod-db.example.com"
export PROD_DB_PORT="5432"

# Email
export EMAIL_HOST="smtp.sendgrid.net"
export EMAIL_USER="apikey"
export EMAIL_PASSWORD="SG.your-sendgrid-api-key"

# AWS
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="your-aws-secret"
export AWS_STORAGE_BUCKET_NAME="myapp-prod-media"

# Redis
export REDIS_HOST="prod-redis.example.com"
export REDIS_PASSWORD="redis_password_123"

# API Keys
export GOOGLE_MAPS_API_KEY="your-production-maps-key"
export STRIPE_SECRET_KEY="sk_live_production_key"
```

### **2. Docker Production Environment**
```dockerfile
# In Dockerfile
ENV ENV=prod

# Environment variables passed via docker-compose
```

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      ENV: prod
      DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY}
      PROD_DB_HOST: ${PROD_DB_HOST}
      # ... other production env vars
```

### **3. Production Configuration**
```python
def get_production_config() -> VaultConfig:
    return VaultConfig(
        # Secure production values from environment
        SECRET_KEY=os.getenv("DJANGO_SECRET_KEY"),
        DEBUG=False,  # Always False in production
        ALLOWED_HOSTS=os.getenv("ALLOWED_HOSTS", "").split(","),
        
        # Production database
        DB_HOST=os.getenv("PROD_DB_HOST"),
        DB_PASSWORD=os.getenv("PROD_DB_PASSWORD"),
        
        # Production Redis with password
        REDIS_HOST=os.getenv("REDIS_HOST"),
        REDIS_PASSWORD=os.getenv("REDIS_PASSWORD"),
        
        # Production API keys
        STRIPE_SECRET_KEY=os.getenv("STRIPE_SECRET_KEY"),
    )
```

---

## 🚀 Deployment Process

### **1. Sync Vault to Production**

**Using Management Command:**
```bash
# Sync vault configuration to production
uv run python manage.py sync-vault

# Or using bash script
./run.sh sync-vault
```

### **2. Manual Deployment Steps**

#### **Step 1: Update Production Vault**
```bash
# Upload updated vault to S3
aws s3 cp src/vault.py s3://atomicloops-prod/vault.py

# Create versioned backup
aws s3 cp src/vault.py s3://atomicloops-prod/vault-$(date +%Y%m%d-%H%M%S).py
```

#### **Step 2: Deploy to Production Server**
```bash
# Download latest vault on production server
ssh production-server "
  cd /opt/myapp &&
  wget -O src/vault.py https://atomicloops-prod.s3.ap-south-1.amazonaws.com/vault.py &&
  systemctl restart myapp-django
"
```

#### **Step 3: Update Docker Deployment**
```bash
# Build new Docker image with updated vault
docker build -t myapp:latest .

# Push to registry
docker push myapp:latest

# Deploy to production
docker-compose pull && docker-compose up -d
```

### **3. Automated Deployment (CI/CD)**

**GitHub Actions Example:**
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Download Production Vault
        run: |
          curl -o src/vault.py ${{ secrets.VAULT_PRODUCTION_URL }}
      
      - name: Build Docker Image
        run: |
          docker build -t myapp:${{ github.sha }} .
      
      - name: Deploy to Production
        run: |
          # Deploy using your preferred method
          kubectl set image deployment/myapp myapp=myapp:${{ github.sha }}
```

### **4. Create Production URLs**

#### **Generate Production Vault URL**
```bash
# Upload to S3 with public access
aws s3 cp src/vault.py s3://your-production-bucket/vault.py \
  --acl public-read

# Get the URL
echo "Production vault URL: https://your-production-bucket.s3.region.amazonaws.com/vault.py"
```

#### **Create Environment-Specific URLs**
```bash
# Development
https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py

# Staging  
https://atomicloops-staging.s3.ap-south-1.amazonaws.com/vault.py

# Production
https://atomicloops-prod.s3.ap-south-1.amazonaws.com/vault.py
```

---

## 📝 Best Practices

### **1. Security Guidelines**

#### **Never Commit Secrets**
```bash
# Add vault.py to .gitignore
echo "src/vault.py" >> .gitignore

# Use environment variables in production
# Hard-code only non-sensitive development values
```

#### **Use Strong Secrets**
```python
# Generate secure secret key
import secrets
SECRET_KEY = secrets.token_urlsafe(50)

# Use environment variables for production
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-for-dev-only")
```

#### **Separate Environment Configs**
```python
# Different databases for different environments
def get_development_config():
    return VaultConfig(DB_NAME="myapp_dev", ...)

def get_staging_config():
    return VaultConfig(DB_NAME="myapp_staging", ...)

def get_production_config():
    return VaultConfig(DB_NAME="myapp_prod", ...)
```

### **2. Configuration Management**

#### **Use Type Hints**
```python
@dataclass
class VaultConfig:
    API_TIMEOUT: int  # Always specify types
    FEATURE_ENABLED: bool
    API_URL: str
    MAX_RETRIES: Optional[int] = None
```

#### **Validate Configuration**
```python
def get_vault_config() -> VaultConfig:
    config = get_environment_config()
    
    # Validate critical settings
    if not config.SECRET_KEY:
        raise ValueError("SECRET_KEY must be set")
    
    if config.DEBUG and config.ENVIRONMENT == "production":
        raise ValueError("DEBUG cannot be True in production")
    
    return config
```

#### **Environment Detection**
```python
def get_environment() -> str:
    # Check environment variable
    env = os.getenv('ENV', '').lower()
    
    # Fallback to Django settings
    if not env:
        from django.conf import settings
        env = 'prod' if not settings.DEBUG else 'dev'
    
    return env
```

### **3. Team Collaboration**

#### **Document Configuration Changes**
```python
# Always document new configuration keys
@dataclass
class VaultConfig:
    # Added 2024-01-15: New payment gateway integration
    PAYMENT_API_KEY: str
    
    # Added 2024-01-20: Feature flag for new dashboard
    NEW_DASHBOARD_ENABLED: bool = False
```

#### **Use Configuration Schema**
```python
from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class EmailConfig:
    host: str
    port: int
    username: str
    password: str
    use_tls: bool = True

@dataclass  
class VaultConfig:
    email: EmailConfig
    allowed_hosts: List[str] = field(default_factory=list)
    feature_flags: dict = field(default_factory=dict)
```

---

## 🆘 Troubleshooting

### **Common Issues**

#### **Vault File Not Found**
```bash
# Check if file exists
ls -la src/vault.py

# Re-download if missing
wget -O src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py

# Check file permissions
chmod 644 src/vault.py
```

#### **Import Error**
```python
# Make sure src is in Python path
import sys
sys.path.append('src')
from vault import vault

# Or use relative import
from .vault import vault
```

#### **Environment Variable Not Set**
```python
# Add default values for development
DB_PASSWORD = os.getenv("DB_PASSWORD", "dev_password_123")

# Or raise clear error for required variables
if not os.getenv("REQUIRED_API_KEY"):
    raise ValueError("REQUIRED_API_KEY environment variable must be set")
```

#### **Configuration Conflicts**
```python
# Check current environment
import os
from vault import vault, get_credentials

print(f"Current environment: {os.getenv('ENV', 'not set')}")
print(f"Debug mode: {vault.get('DEBUG', 'not set')}")
print(f"Database host: {vault.get('DB_HOST', 'not set')}")
print(f"Available keys: {list(vault.keys())}")

# Validate environment consistency
current_env = os.getenv('ENV', 'dev')
if current_env == "prod" and vault.get("DEBUG", False):
    raise ValueError("Production environment cannot have DEBUG=True")

# Check if all required keys exist
required_keys = ["DB_HOST", "DB_NAME", "DB_USER", "SECRET_KEY"]
missing_keys = [key for key in required_keys if key not in vault]
if missing_keys:
    raise ValueError(f"Missing required keys in vault: {missing_keys}")
```

### **Debugging Commands**

```bash
# Check environment variables
env | grep -E "(ENV|DB_|EMAIL_|AWS_)"

# Test vault configuration
uv run python -c "
import os
from src.vault import vault, get_credentials

current_env = os.getenv('ENV', 'dev')
print(f'Current environment: {current_env}')
print(f'Debug mode: {vault.get(\"DEBUG\", \"Not set\")}')
print(f'Database host: {vault.get(\"DB_HOST\", \"Not set\")}')
print(f'Database name: {vault.get(\"DB_NAME\", \"Not set\")}')
print(f'Frontend URL: {vault.get(\"FRONTEND_BASE_URL\", \"Not set\")}')
print(f'Available vault keys: {list(vault.keys())}')
print('Vault loaded successfully!')
"

# Test specific environment
uv run python -c "
from src.vault import get_credentials
try:
    dev_creds = get_credentials('dev')
    print('Dev credentials loaded:', 'DB_HOST' in dev_creds)
    
    prod_creds = get_credentials('prod') 
    print('Prod credentials loaded:', 'DB_HOST' in prod_creds)
except Exception as e:
    print('Error loading credentials:', e)
"

# Validate Django settings
uv run python manage.py check

# Test database connection
uv run python manage.py dbshell

# Test with specific environment
ENV=prod uv run python manage.py check
ENV=dev uv run python manage.py check
```

### **Recovery Procedures**

#### **Reset Vault Configuration**
```bash
# Backup current vault
cp src/vault.py src/vault.py.backup

# Download fresh vault
wget -O src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py

# Restore custom changes
# (manually merge your custom configurations)
```

#### **Emergency Production Access**
```bash
# Use environment variables override
export DJANGO_SETTINGS_MODULE=src.settings.base
export SECRET_KEY=emergency-secret-key
export DEBUG=False

# Start server with minimal configuration
uv run python manage.py runserver --noreload
```

---

## 📚 Quick Reference

### **Common Commands**
```bash
# Download vault
wget -O src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py

# Sync vault to production
./run.sh sync-vault
# Or with UV
uv run python manage.py sync-vault

# Check vault configuration
uv run python -c "
import os
from src.vault import vault
print(f'Environment: {os.getenv(\"ENV\", \"dev\")}')
print(f'Database: {vault.get(\"DB_HOST\", \"Not configured\")}')
print(f'Debug: {vault.get(\"DEBUG\", False)}')
"

# Run with specific environment
ENV=prod uv run python manage.py runserver
ENV=dev uv run python manage.py runserver
ENV=staging uv run python manage.py runserver

# Test different environments
ENV=dev uv run python -c "from src.vault import vault; print('Dev DB:', vault.get('DB_HOST'))"
ENV=prod uv run python -c "from src.vault import vault; print('Prod DB:', vault.get('DB_HOST'))"
```

### **File Locations**
- **Vault file**: `src/vault.py`
- **Settings**: `src/settings/`
- **Environment file**: `.env` (optional)
- **Docker env**: `docker-compose.yml`

### **Environment Variables**
- **`ENV`**: Environment name (dev/staging/prod)
- **`DJANGO_SECRET_KEY`**: Production secret key
- **`PROD_DB_*`**: Production database credentials
- **`EMAIL_*`**: Email configuration
- **`AWS_*`**: AWS credentials

---

**🔐 Your vault is now properly configured for secure, scalable configuration management across all environments!**
