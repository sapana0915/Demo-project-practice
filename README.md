## Atomicloops Django Setup

### Project-Name : <>

### 1. Clone the repository

```
git clone <url>
cd <repo-name>
git checkout -b dev
```

### 2. Install AWS CLI and configurations as per your os

- [Install AWSCLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Install & Configure AWSCLI](https://medium.com/analytics-vidhya/configure-aws-cli-and-execute-commands-fc16a17b0aa2)

### 3. Create a new virtualenv and install requirements (Soon will be deprecated)

- [How to install virtualenv](./docs/Install%20Virtaulenv.pdf)

<details>
<summary>Click to expand legacy pip instructions</summary>

#### Windows

```
virtualenv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install "drf-yasg[validation]"
pip install git+https://github.com/atomic-loops/atomicloops-django-logger
```

#### Linux and Mac OS

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
pip install "drf-yasg[validation]"
pip install git+https://github.com/atomic-loops/atomicloops-django-logger
```

</details>

### 4. 🔐 **Vault Configuration Management**

This project uses AtomicLoops' vault system for secure configuration management across environments.

**📖 [Complete Vault Management Guide](./readme-files/VAULT_MANAGEMENT.md)** - Comprehensive guide for vault setup and management

#### Quick Vault Setup:

**Download Initial Vault:**
```bash
# Linux/macOS
wget -O src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py

# Windows
curl -o src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```

**📋 What the vault manages:**
- 🔒 **Database credentials** (PostgreSQL, MongoDB)
- 📧 **Email configuration** (SMTP, SendGrid)  
- ☁️ **Cloud services** (AWS, Firebase)
- 🔑 **API keys** (Google Maps, Stripe, etc.)
- 🎛️ **Environment settings** (Debug, allowed hosts)

**🔧 Environment-specific configuration:**
- **Development**: Local services, test credentials
- **Staging**: Pre-production environment  
- **Production**: Secure environment variables

<details>
<summary>Legacy vault download instructions</summary>

**A. Initial**
```
wget -O src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```

**Windows**
```
curl -o src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```

**B. Latest**
```
wget -O src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```

**Windows**
```
curl -o src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```

Note: Update the URLs for Latest Section when you sync the vault file.

</details>

### 5. Initialize Project Setup

[Setup Email Password](http://165.232.181.62/books/backend-development/page/generate-password-for-automated-e-mail)

[Atomicloops Django Setup](./docs/ProjectSetup.pdf)

[Atomicloops Custom Commands with Bash](http://165.232.181.62/books/backend-development/page/django-atomicloops-commands-bash)

[Atomicloops Custom Commands python](https://drive.google.com/file/d/1dKK_Eo-7OAAFYTrEtS_N5pQGDLK06Y-a/view?usp=share_link)

#### Update container names and add them to `src/vault.py`

After renaming the project, update the `container_name` entries in your Compose files so they follow the convention `<project-name>-<service>`.

- Edit `docker-compose.yml` and `docker-compose-dev.yml` and set `container_name` for each service you rely on (backend, db, redis, rabbit-mq, celery, flower).
- Add the corresponding container/service names to `src/vault.py` under the `dev` block so setup checks and automation can validate them.

Example `docker-compose-dev.yml` snippet:

```yaml
services:
  backend:
    container_name: myproject-backend
    # ...
  db:
    container_name: myproject-db
    # ...
  redis:
    container_name: myproject-redis
    # ...
  rabbit-mq:
    container_name: myproject-rabbit-mq
    # ...
  celery:
    container_name: myproject-celery
    # ...
```

Add matching entries to `src/vault.py` (dev block):

```python
credentials = {
    'dev': {
        # database
        'DB_NAME': 'my_local_db',
        'DB_USER': 'my_local_user',
        'DB_PASSWORD': 'my_local_password',
        'DB_HOST': 'db',                  # service name used by Compose
        'DB_CONTAINER_NAME': 'myproject-db',
        'DB_VOLUME_NAME': 'myproject-db-data',
        # other dev keys...
    },
    'prod': {
        # production config
    }
}
```

Notes:

- Use the Compose **service key** (e.g., `db`) as the `DB_HOST` value so containers resolve each other using the Compose network.
- Never commit real secrets. Keep `src/vault.py` out of git for production secrets and use CI vaults for deployment.

Update volume names to include project name

- When you change `container_name` and service names, also update any named volumes so they follow the `<project-name>-<purpose>` convention. This avoids collisions and makes volumes easier to identify.

Example - update the DB volume mapping in the Compose service and the top-level `volumes` block:

```yaml
services:
  db:
    container_name: myproject-db
    image: postgres:15
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: mydb
    volumes:
      - myproject-db-data:/var/lib/postgresql/data

volumes:
  myproject-db-data:
```

Also add the named volume entry to `src/vault.py` (dev block) so `check-setup` can validate it:

```python
    'DB_VOLUME_NAME': 'myproject-db-data',
```


### 6. Makemigrations and Create Table

```bash
./run.sh start-dev
./run.sh interactive-dev
python manage.py makemigrations
python manage.py migrate
```

### 7. Start Server

```sh
./run.sh start-dev
```

### 8. 🔄 **Vault Management & Sync**

**📖 [See VAULT_MANAGEMENT.md for complete vault operations](./readme-files/VAULT_MANAGEMENT.md)**

#### Quick Vault Operations:
```
./run.sh sync-vault
```

### 9. How to add new libraries
**Bash scripts:**
```
./run.sh interactive-dev
pip install <package_name>
pip freeze > requirements.txt
exit
./run.sh start-dev
```

**Python scripts:**
```
source venv/bin/activate
pip install <package_name>
pip freeze > requirements.txt
python manage.py run --mode start-dev
```

---

---

## 🚀 Modern Development Stack

This AtomicLoops Django boilerplate has been upgraded with modern development tools and practices:


**📖 [Complete UV Setup Guide](./readme-files/UV_SETUP.md)** - Installation, usage, and best practices

### **🔐 Vault Configuration Management**
- **Environment-specific configs** (dev/staging/prod)
- **Secure secret management** 
- **Automated deployment** and sync
- **Team collaboration** tools

**📖 [Complete Vault Management Guide](./readme-files/VAULT_MANAGEMENT.md)** - Configuration, deployment, and best practices

### **🐳 Docker Optimization**
- **UV-optimized containers** for faster builds
- **Multi-stage builds** for production efficiency
- **Separated dev/prod Dockerfiles**
- **Environment-aware deployments**

### **📚 Comprehensive Documentation**
- **Step-by-step guides** for all tools
- **Best practices** and troubleshooting
- **Quick reference** commands
- **Migration guides** from legacy setups

### **🔄 Celery Task Queue System**
- **Asynchronous task processing** with RabbitMQ broker
- **Scheduled tasks** with Celery Beat
- **Container architecture** for scalable deployment
- **Monitoring and debugging** with Flower

**📖 [Complete Celery Guide](./readme-files/CELERY_GUIDE.md)** - Task queues, scheduling, and production deployment


TODO:
Create atomicloops package
