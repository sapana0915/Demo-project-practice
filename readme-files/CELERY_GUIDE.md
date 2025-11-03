# Celery Task Queue Guide

This comprehensive guide covers Celery setup with RabbitMQ broker, container architecture, task creation, and scheduling using the AtomicLoops Django boilerplate patterns.

## 📋 Table of Contents

- [What is Celery?](#what-is-celery)
- [RabbitMQ Broker Setup](#rabbitmq-broker-setup)
- [Celery App Configuration](#celery-app-configuration)
- [Container Architecture](#container-architecture)
- [Creating Tasks](#creating-tasks)
- [Task Scheduling with Beat](#task-scheduling-with-beat)
- [Production Deployment](#production-deployment)
- [Monitoring & Debugging](#monitoring--debugging)
- [Best Practices](#best-practices)

---

## 🔄 What is Celery?

**Celery** is a distributed task queue system that allows you to:

- **🚀 Asynchronous Processing**: Run time-consuming tasks in the background
- **📊 Distributed Computing**: Scale across multiple workers and machines
- **⏰ Task Scheduling**: Execute periodic tasks with Celery Beat
- **🔄 Retry Logic**: Automatic retries for failed tasks
- **📈 Monitoring**: Real-time monitoring with Flower

### **Key Components:**
- **Celery Workers**: Execute background tasks
- **Message Broker**: RabbitMQ (routes tasks between producers and workers)
- **Celery Beat**: Scheduler for periodic tasks
- **Result Backend**: Stores task results (optional)

---

## 🐰 RabbitMQ Broker Setup

### **What is RabbitMQ?**

RabbitMQ is a message broker that acts as an intermediary for task messages between your Django application and Celery workers.

```
[Django App] → [RabbitMQ] → [Celery Workers]
     ↓              ↓              ↓
  Create Task   Queue Task    Execute Task
```

### **Docker Configuration**

**In docker-compose.yml:**
```yaml
services:
  rabbit-mq:
    image: rabbitmq:3.7-management
    restart: always
    container_name: 'demo-rabbit-mq'
    environment:
      - RABBITMQ_DEFAULT_USER=admin
      - RABBITMQ_DEFAULT_PASS=admin
    ports:
      - '5672:5672'      # AMQP port
      - '15672:15672'    # Management UI port
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq

volumes:
  rabbitmq_data:
```

### **RabbitMQ Management Interface**

Access the management UI at: **http://localhost:15672**
- **Username**: `admin`
- **Password**: `admin`

**Features available:**
- Queue monitoring
- Exchange management
- Connection tracking
- Message statistics

### **Connection Configuration**

**In src/settings/base.py:**
```python
# RabbitMQ Broker Configuration
CELERY_BROKER_URL = 'amqp://admin:admin@demo-rabbit-mq:5672//'

# For development (local RabbitMQ)
# CELERY_BROKER_URL = 'amqp://admin:admin@localhost:5672//'

# Alternative Redis broker (if needed)
# CELERY_BROKER_URL = 'redis://localhost:6379/0'
```

**Environment-specific configuration:**
```python
# In vault.py
credentials = {
    "dev": {
        "CELERY_BROKER_URL": "amqp://admin:admin@localhost:5672//",
        "CELERY_RESULT_BACKEND": "redis://localhost:6379/1",
    },
    "prod": {
        "CELERY_BROKER_URL": "amqp://admin:admin@prod-rabbitmq:5672//",
        "CELERY_RESULT_BACKEND": "redis://prod-redis:6379/1",
    }
}
```

---

## ⚙️ Celery App Configuration

### **Celery App Setup (src/celery.py)**

```python
import os
from celery import Celery
from celery import shared_task
from django.conf import settings

# Set the default Django settings module for the 'celery' program
ENV = os.getenv('ENV', None)
if ENV is not None and ENV == "prod":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.prod')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.dev')

# Create the Celery app instance
app = Celery('src')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps
app.autodiscover_tasks()

# Celery configuration
app.conf.update(
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'myapp.tasks.heavy_task': {'queue': 'heavy'},
        'myapp.tasks.quick_task': {'queue': 'quick'},
    },
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    
    # Task result settings
    result_expires=3600,  # 1 hour
)

# Debug task (example)
@shared_task
def debug_task():
    """Simple debug task for testing Celery setup"""
    print("Celery is working!")
    return "Debug task completed successfully"
```

### **Django Settings Configuration**

**In src/settings/base.py:**
```python
from celery.schedules import crontab
from vault import vault

# Celery Configuration
CELERY_BROKER_URL = vault.get('CELERY_BROKER_URL', 'amqp://admin:admin@demo-rabbit-mq:5672//')
CELERY_RESULT_BACKEND = vault.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

# Celery Task Settings
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_ENABLE_UTC = True

# Worker Settings
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Task Result Settings
CELERY_RESULT_EXPIRES = 3600  # 1 hour

# Task Routing (Optional)
CELERY_TASK_ROUTES = {
    'users.tasks.send_email': {'queue': 'email'},
    'users.tasks.generate_report': {'queue': 'heavy'},
    'users.tasks.quick_notification': {'queue': 'quick'},
}

# Beat Schedule (Periodic Tasks)
CELERY_BEAT_SCHEDULE = {
    'demo-task': {
        'task': 'src.celery.debug_task',
        'schedule': crontab(hour="*/12"),  # Every 12 hours
    },
    'daily-cleanup': {
        'task': 'users.tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2:00 AM
    },
    'send-weekly-report': {
        'task': 'users.tasks.generate_weekly_report',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),  # Monday 9:00 AM
    },
}

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
```

---

## 🐳 Container Architecture

### **Docker Compose Services**

Your project uses **4 Celery-related containers**:

#### **1. Backend Service (Django + Celery Producer)**
```yaml
backend:
  build: .
  container_name: 'django-backend'
  command: uv run gunicorn --bind 0.0.0.0:8000 -w 2 src.wsgi --reload
  volumes:
    - .:/opt/:Z
  ports:
    - 8000:8000
  depends_on:
    - rabbit-mq
```

#### **2. Celery Worker Container**
```yaml
celery:
  container_name: 'celery-worker'
  build: .
  command: uv run celery -A src worker -l INFO -E -f /opt/logs/celery/worker.logs
  volumes:
    - .:/opt/
  depends_on:
    - rabbit-mq
    - backend
  environment:
    - DJANGO_SETTINGS_MODULE=src.settings.dev
```

#### **3. Celery Beat Container (Scheduler)**
```yaml
celery-beat:
  container_name: 'celery-beat'
  build: .
  command: uv run celery -A src beat -l INFO -f /opt/logs/celery/beat.logs
  volumes:
    - .:/opt/
  depends_on:
    - rabbit-mq
    - backend
  environment:
    - DJANGO_SETTINGS_MODULE=src.settings.dev
```

#### **4. Flower Monitoring Container**
```yaml
flower:
  container_name: 'celery-flower'
  build: .
  command: uv run celery -A src flower --port=5555
  ports:
    - 5555:5555
  volumes:
    - .:/opt/
  depends_on:
    - backend
    - celery
    - rabbit-mq
```

#### **5. RabbitMQ Broker Container**
```yaml
rabbit-mq:
  image: rabbitmq:3.7-management
  restart: always
  container_name: 'demo-rabbit-mq'
  environment:
    - RABBITMQ_DEFAULT_USER=admin
    - RABBITMQ_DEFAULT_PASS=admin
  ports:
    - '5672:5672'    # AMQP
    - '15672:15672'  # Management UI
```

### **Container Communication Flow**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django App    │ -> │    RabbitMQ     │ -> │ Celery Worker   │
│   (Producer)    │    │    (Broker)     │    │  (Consumer)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         v                       v                       v
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Celery Beat    │    │     Flower      │    │     Redis       │
│  (Scheduler)    │    │  (Monitoring)   │    │ (Result Store)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Starting the Stack**

```bash
# Development
docker-compose -f docker-compose-dev.yml up -d

# Production
docker-compose up -d

# Check container status
docker-compose ps

# View logs
docker-compose logs celery
docker-compose logs celery-beat
docker-compose logs flower
```

---

## 🔧 Creating Tasks

### **Task Creation Patterns**

#### **1. Using app.task with bind=True (Recommended)**

```python
# users/tasks.py
from celery import current_app
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from django.contrib.auth.models import User
import time

# Get logger
logger = get_task_logger(__name__)

@current_app.task(bind=True, retry_kwargs={'max_retries': 3, 'countdown': 60})
def send_welcome_email(self, user_id):
    """
    Send welcome email to user with retry logic
    """
    try:
        # Get user
        user = User.objects.get(id=user_id)
        
        # Simulate email sending
        logger.info(f"Sending welcome email to {user.email}")
        
        send_mail(
            subject="Welcome to Our Platform!",
            message=f"Hello {user.first_name}, welcome to our platform!",
            from_email="noreply@yourapp.com",
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent successfully to {user.email}")
        return f"Email sent to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        raise self.retry(countdown=60, max_retries=3)
        
    except Exception as exc:
        logger.error(f"Failed to send email: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))

@current_app.task(bind=True)
def process_user_data(self, user_id, operation_type):
    """
    Process user data with progress tracking
    """
    try:
        user = User.objects.get(id=user_id)
        total_steps = 5
        
        for i in range(total_steps):
            # Update task progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i + 1,
                    'total': total_steps,
                    'status': f'Processing step {i + 1}...'
                }
            )
            
            # Simulate processing
            time.sleep(2)
            logger.info(f"Completed step {i + 1} for user {user.email}")
        
        return {
            'status': 'COMPLETED',
            'result': f'Successfully processed {operation_type} for {user.email}',
            'user_id': user_id
        }
        
    except Exception as exc:
        logger.error(f"Error processing user data: {str(exc)}")
        return {
            'status': 'FAILED',
            'error': str(exc),
            'user_id': user_id
        }

@current_app.task(bind=True)
def generate_report(self, report_type, user_id, filters=None):
    """
    Generate reports with file creation
    """
    try:
        import pandas as pd
        from datetime import datetime
        
        logger.info(f"Generating {report_type} report for user {user_id}")
        
        # Simulate data processing
        self.update_state(state='PROGRESS', meta={'status': 'Fetching data...'})
        time.sleep(3)
        
        self.update_state(state='PROGRESS', meta={'status': 'Processing data...'})
        time.sleep(5)
        
        self.update_state(state='PROGRESS', meta={'status': 'Creating file...'})
        
        # Create sample report
        filename = f"report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = f"/opt/reports/{filename}"
        
        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Create sample data
        data = {
            'id': range(1, 101),
            'value': [i * 10 for i in range(1, 101)],
            'timestamp': [datetime.now() for _ in range(100)]
        }
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        logger.info(f"Report generated: {filepath}")
        
        return {
            'status': 'COMPLETED',
            'filename': filename,
            'filepath': filepath,
            'rows': len(df)
        }
        
    except Exception as exc:
        logger.error(f"Report generation failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=120, max_retries=2)
```

#### **2. Task with Custom Options**

```python
@current_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5, 'countdown': 60},
    retry_backoff=True,
    retry_jitter=False
)
def heavy_computation_task(self, data_payload):
    """
    Heavy computation task with automatic retry
    """
    try:
        # Simulate heavy computation
        import json
        import hashlib
        
        logger.info("Starting heavy computation...")
        
        # Process data
        processed_data = []
        total_items = len(data_payload.get('items', []))
        
        for idx, item in enumerate(data_payload.get('items', [])):
            # Update progress
            progress = int((idx / total_items) * 100)
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': idx,
                    'total': total_items,
                    'progress': progress,
                    'status': f'Processing item {idx + 1}/{total_items}'
                }
            )
            
            # Simulate computation
            result = hashlib.md5(json.dumps(item).encode()).hexdigest()
            processed_data.append({
                'original': item,
                'hash': result,
                'processed_at': time.time()
            })
            
            time.sleep(0.1)  # Simulate work
        
        return {
            'status': 'SUCCESS',
            'processed_count': len(processed_data),
            'results': processed_data[:10],  # Return first 10 for brevity
            'total_items': total_items
        }
        
    except Exception as exc:
        logger.error(f"Heavy computation failed: {str(exc)}")
        raise
```

### **Invoking Tasks Asynchronously**

#### **1. Using apply_async() (Recommended)**

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from users.tasks import send_welcome_email, process_user_data, generate_report
import json

@require_http_methods(["POST"])
def trigger_welcome_email(request):
    """Trigger welcome email task"""
    data = json.loads(request.body)
    user_id = data.get('user_id')
    
    if not user_id:
        return JsonResponse({'error': 'user_id required'}, status=400)
    
    # Execute task asynchronously
    task = send_welcome_email.apply_async(
        args=[user_id],
        countdown=10,  # Delay execution by 10 seconds
        expires=3600   # Task expires in 1 hour
    )
    
    return JsonResponse({
        'message': 'Welcome email task queued',
        'task_id': task.id,
        'status': 'PENDING'
    })

@require_http_methods(["POST"])
def trigger_data_processing(request):
    """Trigger data processing task"""
    data = json.loads(request.body)
    user_id = data.get('user_id')
    operation_type = data.get('operation_type', 'default')
    
    # Execute with custom queue and priority
    task = process_user_data.apply_async(
        args=[user_id, operation_type],
        queue='heavy',     # Use specific queue
        priority=5,        # Higher priority
        retry=True,
        retry_policy={
            'max_retries': 3,
            'interval_start': 0,
            'interval_step': 0.2,
            'interval_max': 0.2,
        }
    )
    
    return JsonResponse({
        'message': 'Data processing task started',
        'task_id': task.id,
        'queue': 'heavy'
    })

@require_http_methods(["POST"])
def trigger_report_generation(request):
    """Trigger report generation"""
    data = json.loads(request.body)
    
    task = generate_report.apply_async(
        args=[
            data.get('report_type', 'default'),
            data.get('user_id'),
            data.get('filters', {})
        ],
        countdown=0,  # Execute immediately
        expires=7200  # 2 hours expiry
    )
    
    return JsonResponse({
        'message': 'Report generation started',
        'task_id': task.id,
        'estimated_time': '5-10 minutes'
    })
```

#### **2. Task Status Checking**

```python
from celery.result import AsyncResult
from django.http import JsonResponse

def check_task_status(request, task_id):
    """Check the status of a Celery task"""
    try:
        task_result = AsyncResult(task_id)
        
        response_data = {
            'task_id': task_id,
            'status': task_result.status,
            'ready': task_result.ready(),
            'successful': task_result.successful() if task_result.ready() else None,
        }
        
        if task_result.status == 'PROGRESS':
            response_data['progress'] = task_result.info
        elif task_result.status == 'SUCCESS':
            response_data['result'] = task_result.result
        elif task_result.status == 'FAILURE':
            response_data['error'] = str(task_result.info)
            response_data['traceback'] = task_result.traceback
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to get task status: {str(e)}'
        }, status=500)

def cancel_task(request, task_id):
    """Cancel a running task"""
    try:
        task_result = AsyncResult(task_id)
        task_result.revoke(terminate=True)
        
        return JsonResponse({
            'message': f'Task {task_id} has been cancelled',
            'status': 'REVOKED'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to cancel task: {str(e)}'
        }, status=500)
```

#### **3. Batch Task Processing**

```python
from celery import group, chain, chord

# Group: Execute tasks in parallel
def process_multiple_users(user_ids):
    """Process multiple users in parallel"""
    job = group(send_welcome_email.s(user_id) for user_id in user_ids)
    result = job.apply_async()
    
    return {
        'group_id': result.id,
        'task_count': len(user_ids),
        'message': 'Batch processing started'
    }

# Chain: Execute tasks sequentially
def process_user_workflow(user_id):
    """Execute a workflow of tasks in sequence"""
    workflow = chain(
        send_welcome_email.s(user_id),
        process_user_data.s('welcome'),
        generate_report.s('user_activity', user_id)
    )
    
    result = workflow.apply_async()
    return {
        'workflow_id': result.id,
        'message': 'User workflow started'
    }

# Chord: Execute tasks in parallel, then run callback
def generate_batch_report(user_ids):
    """Generate individual reports, then create summary"""
    
    # Parallel report generation
    parallel_tasks = group(
        generate_report.s('individual', user_id) 
        for user_id in user_ids
    )
    
    # Summary task after all complete
    summary_task = create_summary_report.s()
    
    # Combine with chord
    workflow = chord(parallel_tasks)(summary_task)
    
    return {
        'chord_id': workflow.id,
        'message': 'Batch report generation started'
    }

@current_app.task(bind=True)
def create_summary_report(self, individual_results):
    """Create summary from individual report results"""
    logger.info(f"Creating summary from {len(individual_results)} reports")
    
    # Process individual results
    summary_data = {
        'total_reports': len(individual_results),
        'successful': sum(1 for r in individual_results if r.get('status') == 'COMPLETED'),
        'failed': sum(1 for r in individual_results if r.get('status') == 'FAILED'),
        'timestamp': time.time()
    }
    
    return summary_data
```

---

## ⏰ Task Scheduling with Beat

### **Celery Beat Configuration**

Celery Beat is the scheduler that triggers periodic tasks. It reads the schedule and sends tasks to workers at the specified times.

#### **1. Schedule Definition in Settings**

```python
# src/settings/base.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Debug task every 12 hours
    'demo-task': {
        'task': 'src.celery.debug_task',
        'schedule': crontab(hour="*/12"),  # Every 12 hours
    },
    
    # Daily cleanup at 2 AM
    'daily-cleanup': {
        'task': 'users.tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2:00 AM
        'options': {'queue': 'maintenance'}
    },
    
    # Weekly report on Mondays at 9 AM
    'weekly-report': {
        'task': 'users.tasks.generate_weekly_report',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),  # Monday 9:00 AM
        'kwargs': {'report_type': 'weekly_summary'}
    },
    
    # Every 5 minutes during business hours
    'check-system-health': {
        'task': 'monitoring.tasks.health_check',
        'schedule': crontab(minute='*/5', hour='9-18'),  # Every 5 min, 9 AM - 6 PM
    },
    
    # Monthly report on 1st at midnight
    'monthly-report': {
        'task': 'users.tasks.generate_monthly_report',
        'schedule': crontab(minute=0, hour=0, day_of_month=1),  # 1st of month at midnight
    },
    
    # Custom interval (every 30 seconds)
    'frequent-task': {
        'task': 'monitoring.tasks.quick_check',
        'schedule': 30.0,  # Every 30 seconds
    },
}

# Beat scheduler backend
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
```

#### **2. Scheduled Task Examples**

```python
# users/tasks.py
from celery import current_app
from celery.utils.log import get_task_logger
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import os

logger = get_task_logger(__name__)

@current_app.task(bind=True)
def cleanup_old_data(self):
    """Clean up old data daily"""
    try:
        cutoff_date = timezone.now() - timedelta(days=30)
        
        # Clean up old user sessions
        from django.contrib.sessions.models import Session
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
        deleted_sessions = expired_sessions.count()
        expired_sessions.delete()
        
        # Clean up old log files
        log_dir = '/opt/logs'
        cleaned_files = 0
        
        for root, dirs, files in os.walk(log_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_time = timezone.datetime.fromtimestamp(
                    os.path.getctime(file_path)
                ).replace(tzinfo=timezone.utc)
                
                if file_time < cutoff_date and file.endswith('.log'):
                    try:
                        os.remove(file_path)
                        cleaned_files += 1
                    except OSError:
                        pass
        
        logger.info(f"Cleanup completed: {deleted_sessions} sessions, {cleaned_files} log files")
        
        return {
            'status': 'COMPLETED',
            'deleted_sessions': deleted_sessions,
            'cleaned_files': cleaned_files,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Cleanup failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=300, max_retries=3)

@current_app.task(bind=True)
def generate_weekly_report(self, report_type='weekly_summary'):
    """Generate weekly reports"""
    try:
        from datetime import datetime
        import json
        
        logger.info(f"Generating weekly report: {report_type}")
        
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        
        # Gather statistics
        new_users = User.objects.filter(
            date_joined__gte=start_date,
            date_joined__lt=end_date
        ).count()
        
        active_users = User.objects.filter(
            last_login__gte=start_date,
            last_login__lt=end_date
        ).count()
        
        # Create report data
        report_data = {
            'report_type': report_type,
            'week_start': start_date.isoformat(),
            'week_end': end_date.isoformat(),
            'new_users': new_users,
            'active_users': active_users,
            'generated_at': timezone.now().isoformat()
        }
        
        # Save report (example - save to file)
        report_filename = f"weekly_report_{start_date.strftime('%Y%m%d')}.json"
        report_path = f"/opt/reports/{report_filename}"
        
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Weekly report saved: {report_path}")
        
        # Optionally send email notification
        send_report_notification.apply_async(
            args=[report_path, 'weekly'],
            countdown=60
        )
        
        return report_data
        
    except Exception as exc:
        logger.error(f"Weekly report generation failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=600, max_retries=2)

@current_app.task(bind=True)
def send_report_notification(self, report_path, report_type):
    """Send report notification email"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        # Read report data
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        # Compose email
        subject = f"Weekly Report - {report_data.get('week_start', 'N/A')}"
        message = f"""
        Weekly Report Generated
        
        Period: {report_data.get('week_start')} to {report_data.get('week_end')}
        New Users: {report_data.get('new_users', 0)}
        Active Users: {report_data.get('active_users', 0)}
        
        Report file: {report_path}
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['admin@yourapp.com'],
            fail_silently=False,
        )
        
        logger.info(f"Report notification sent for {report_type}")
        return f"Notification sent for {report_type} report"
        
    except Exception as exc:
        logger.error(f"Failed to send report notification: {str(exc)}")
        raise self.retry(exc=exc, countdown=300, max_retries=3)

@current_app.task(bind=True)
def health_check(self):
    """System health check task"""
    try:
        import psutil
        from django.db import connection
        
        # Check database connection
        db_status = 'OK'
        try:
            connection.ensure_connection()
        except Exception:
            db_status = 'FAILED'
        
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        health_data = {
            'timestamp': timezone.now().isoformat(),
            'database': db_status,
            'cpu_usage': cpu_percent,
            'memory_usage': memory_percent,
            'disk_usage': disk_percent,
            'status': 'HEALTHY' if all([
                db_status == 'OK',
                cpu_percent < 80,
                memory_percent < 80,
                disk_percent < 80
            ]) else 'WARNING'
        }
        
        # Log health status
        if health_data['status'] == 'WARNING':
            logger.warning(f"Health check warning: {health_data}")
        else:
            logger.info(f"Health check passed: {health_data}")
        
        return health_data
        
    except Exception as exc:
        logger.error(f"Health check failed: {str(exc)}")
        return {
            'status': 'ERROR',
            'error': str(exc),
            'timestamp': timezone.now().isoformat()
        }
```

#### **3. Managing Beat Schedule**

```bash
# Start Celery Beat (scheduler)
uv run celery -A src beat -l INFO

# Start Beat with custom schedule file
uv run celery -A src beat -s /opt/celerybeat-schedule -l INFO

# List scheduled tasks
uv run celery -A src inspect scheduled

# Check active tasks
uv run celery -A src inspect active

# Monitor Beat in real-time
uv run celery -A src events --camera=events.state
```

#### **4. Dynamic Schedule Management**

```python
# Add periodic task dynamically
from django_celery_beat.models import PeriodicTask, CrontabSchedule

# Create schedule
schedule, created = CrontabSchedule.objects.get_or_create(
    minute='*/10',  # Every 10 minutes
    hour='*',
    day_of_week='*',
    day_of_month='*',
    month_of_year='*',
)

# Create periodic task
PeriodicTask.objects.create(
    crontab=schedule,
    name='Dynamic Task',
    task='users.tasks.dynamic_task',
    args=json.dumps(['arg1', 'arg2']),
    kwargs=json.dumps({'key': 'value'}),
    enabled=True,
)
```

---

## 🚀 Production Deployment

### **Production Docker Configuration**

```yaml
# docker-compose.yml (Production)
version: '3.8'

services:
  # RabbitMQ Cluster for High Availability
  rabbitmq:
    image: rabbitmq:3.9-management
    hostname: rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASS}
      RABBITMQ_DEFAULT_VHOST: /
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    deploy:
      replicas: 1
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  # Multiple Celery Workers
  celery-worker:
    build: .
    command: >
      uv run celery -A src worker 
      --loglevel=info 
      --concurrency=4 
      --prefetch-multiplier=1
      --max-tasks-per-child=1000
    environment:
      - ENV=prod
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
      - CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
    volumes:
      - ./logs:/opt/logs
      - ./reports:/opt/reports
    depends_on:
      - rabbitmq
      - redis
    deploy:
      replicas: 3  # Multiple worker instances
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  # Celery Beat (Single Instance)
  celery-beat:
    build: .
    command: >
      uv run celery -A src beat 
      --loglevel=info 
      --pidfile=/tmp/celerybeat.pid
    environment:
      - ENV=prod
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
    volumes:
      - ./logs:/opt/logs
      - beat_schedule:/opt/schedule
    depends_on:
      - rabbitmq
      - postgres
    deploy:
      replicas: 1  # Only one beat instance
      resources:
        limits:
          memory: 256M

  # Flower Monitoring
  flower:
    build: .
    command: >
      uv run celery -A src flower 
      --port=5555 
      --basic_auth=${FLOWER_USER}:${FLOWER_PASS}
    ports:
      - "5555:5555"
    environment:
      - ENV=prod
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
    depends_on:
      - rabbitmq
    deploy:
      resources:
        limits:
          memory: 256M

volumes:
  rabbitmq_data:
  beat_schedule:
```

### **Environment Variables (.env)**

```bash
# Production Environment Variables
ENV=prod

# RabbitMQ Configuration
RABBITMQ_USER=admin
RABBITMQ_PASS=secure_password_123
CELERY_BROKER_URL=amqp://admin:secure_password_123@rabbitmq:5672//

# Redis Result Backend
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password_123
CELERY_RESULT_BACKEND=redis://:redis_password_123@redis:6379/1

# Flower Monitoring
FLOWER_USER=admin
FLOWER_PASS=flower_password_123

# Database
POSTGRES_DB=myapp_prod
POSTGRES_USER=myapp_user
POSTGRES_PASSWORD=db_password_123
```

### **Production Settings**

```python
# src/settings/prod.py
from .base import *
from vault import vault

# Celery Production Configuration
CELERY_BROKER_URL = vault.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = vault.get('CELERY_RESULT_BACKEND')

# Worker Configuration
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_WORKER_DISABLE_RATE_LIMITS = True

# Task Settings
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_IGNORE_RESULT = False

# Result Backend Settings
CELERY_RESULT_EXPIRES = 3600  # 1 hour
CELERY_RESULT_PERSISTENT = True

# Monitoring
CELERY_SEND_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True

# Security
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Logging
CELERY_WORKER_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
CELERY_WORKER_TASK_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# Queue Configuration
CELERY_TASK_ROUTES = {
    'users.tasks.send_email': {'queue': 'email'},
    'users.tasks.generate_report': {'queue': 'reports'},
    'users.tasks.heavy_computation': {'queue': 'compute'},
    'monitoring.tasks.*': {'queue': 'monitoring'},
}

# Queue Priorities
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_QUEUES = {
    'default': {'routing_key': 'default'},
    'email': {'routing_key': 'email'},
    'reports': {'routing_key': 'reports'},
    'compute': {'routing_key': 'compute'},
    'monitoring': {'routing_key': 'monitoring'},
}
```

---

## 📊 Monitoring & Debugging

### **1. Flower Monitoring**

Access Flower at: **http://localhost:5555**

**Features:**
- Real-time task monitoring
- Worker status and statistics
- Task history and results
- Queue management
- Performance metrics

```bash
# Start Flower with authentication
uv run celery -A src flower --basic_auth=admin:password --port=5555

# Flower with custom configuration
uv run celery -A src flower --conf=flower_config.py
```

### **2. Command Line Monitoring**

```bash
# Check worker status
uv run celery -A src inspect stats

# List active tasks
uv run celery -A src inspect active

# List scheduled tasks
uv run celery -A src inspect scheduled

# List registered tasks
uv run celery -A src inspect registered

# Check worker queues
uv run celery -A src inspect active_queues

# Monitor events in real-time
uv run celery -A src events

# Check reserved tasks
uv run celery -A src inspect reserved

# Worker control commands
uv run celery -A src control enable_events
uv run celery -A src control disable_events
uv run celery -A src control pool_restart
```

### **3. RabbitMQ Monitoring**

**Management UI**: http://localhost:15672
- Username: `admin`
- Password: `admin`

**Command line tools:**
```bash
# Check queue status
docker exec demo-rabbit-mq rabbitmqctl list_queues

# Check connections
docker exec demo-rabbit-mq rabbitmqctl list_connections

# Check exchanges
docker exec demo-rabbit-mq rabbitmqctl list_exchanges

# Queue statistics
docker exec demo-rabbit-mq rabbitmqctl list_queues name messages consumers
```

### **4. Logging and Debugging**

```python
# Enhanced logging setup
import logging
from celery.utils.log import get_task_logger

# Task-specific logger
logger = get_task_logger(__name__)

@current_app.task(bind=True)
def debug_task_with_logging(self):
    """Task with comprehensive logging"""
    
    # Log task start
    logger.info(f"Task {self.request.id} started")
    logger.info(f"Task args: {self.request.args}")
    logger.info(f"Task kwargs: {self.request.kwargs}")
    logger.info(f"Worker: {self.request.hostname}")
    
    try:
        # Your task logic here
        result = "Task completed successfully"
        
        # Log success
        logger.info(f"Task {self.request.id} completed: {result}")
        return result
        
    except Exception as exc:
        # Log error with full context
        logger.error(f"Task {self.request.id} failed: {str(exc)}")
        logger.error(f"Error type: {type(exc).__name__}")
        logger.error(f"Error args: {exc.args}")
        
        # Include task context in error
        error_context = {
            'task_id': self.request.id,
            'task_name': self.name,
            'args': self.request.args,
            'kwargs': self.request.kwargs,
            'retries': self.request.retries,
            'hostname': self.request.hostname
        }
        logger.error(f"Error context: {error_context}")
        
        raise
```

### **5. Performance Monitoring**

```python
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor task performance"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        
        # Log task start
        logger.info(f"Starting task {func.__name__} with ID {self.request.id}")
        
        try:
            result = func(self, *args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log success with timing
            logger.info(f"Task {func.__name__} completed in {execution_time:.2f}s")
            
            return result
            
        except Exception as exc:
            execution_time = time.time() - start_time
            logger.error(f"Task {func.__name__} failed after {execution_time:.2f}s: {str(exc)}")
            raise
            
    return wrapper

@current_app.task(bind=True)
@monitor_performance
def monitored_task(self, data):
    """Task with performance monitoring"""
    # Task implementation
    time.sleep(5)  # Simulate work
    return "Task completed"
```

---

## 💡 Best Practices

### **1. Task Design**

```python
# ✅ Good: Idempotent task
@current_app.task(bind=True)
def send_notification(self, user_id, message_type):
    """Send notification - can be safely retried"""
    try:
        # Check if notification already sent
        if NotificationLog.objects.filter(
            user_id=user_id, 
            message_type=message_type,
            status='sent'
        ).exists():
            logger.info(f"Notification already sent to user {user_id}")
            return "Already sent"
        
        # Send notification
        send_actual_notification(user_id, message_type)
        
        # Log success
        NotificationLog.objects.create(
            user_id=user_id,
            message_type=message_type,
            status='sent'
        )
        
        return "Notification sent"
        
    except Exception as exc:
        logger.error(f"Failed to send notification: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)

# ❌ Bad: Non-idempotent task
@current_app.task
def bad_increment_counter():
    """Bad: This task is not idempotent"""
    counter = Counter.objects.get(id=1)
    counter.value += 1  # This will increment multiple times if retried
    counter.save()
```

### **2. Error Handling**

```python
@current_app.task(bind=True, autoretry_for=(ConnectionError, TimeoutError))
def robust_task(self, data):
    """Task with robust error handling"""
    try:
        # Task implementation
        return process_data(data)
        
    except ValidationError as exc:
        # Don't retry for validation errors
        logger.error(f"Validation error: {str(exc)}")
        raise
        
    except (ConnectionError, TimeoutError) as exc:
        # Automatic retry for connection issues
        logger.warning(f"Connection issue, will retry: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=5)
        
    except Exception as exc:
        # Manual retry for other exceptions
        logger.error(f"Unexpected error: {str(exc)}")
        if self.request.retries < 3:
            raise self.retry(exc=exc, countdown=120)
        else:
            # Final failure - notify admin
            notify_admin_of_failure(self.request.id, str(exc))
            raise
```

### **3. Resource Management**

```python
@current_app.task(bind=True)
def memory_conscious_task(self, large_dataset_id):
    """Task that handles large data efficiently"""
    try:
        # Process data in chunks to avoid memory issues
        chunk_size = 1000
        total_processed = 0
        
        for chunk in get_data_chunks(large_dataset_id, chunk_size):
            # Process chunk
            process_chunk(chunk)
            total_processed += len(chunk)
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'processed': total_processed}
            )
            
            # Clear memory
            del chunk
            
        return f"Processed {total_processed} items"
        
    except MemoryError:
        logger.error("Out of memory - reducing chunk size")
        # Could trigger a new task with smaller chunk size
        raise self.retry(countdown=300, max_retries=1)
```

### **4. Task Organization**

```python
# tasks/email.py - Email related tasks
@current_app.task(bind=True, queue='email')
def send_welcome_email(self, user_id):
    """Send welcome email"""
    pass

# tasks/reports.py - Report generation tasks  
@current_app.task(bind=True, queue='reports')
def generate_monthly_report(self, month, year):
    """Generate monthly report"""
    pass

# tasks/maintenance.py - Maintenance tasks
@current_app.task(bind=True, queue='maintenance')
def cleanup_old_files(self):
    """Clean up old files"""
    pass
```

### **5. Configuration Best Practices**

```python
# Production settings
CELERY_TASK_ALWAYS_EAGER = False  # Never True in production
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_IGNORE_RESULT = False  # Set to True if you don't need results
CELERY_RESULT_EXPIRES = 3600  # Clean up results after 1 hour

# Worker settings
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Important for fair task distribution
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # Restart workers to prevent memory leaks

# Monitoring
CELERY_SEND_EVENTS = True  # Enable for monitoring
CELERY_TASK_SEND_SENT_EVENT = True
```

---

## 📚 Quick Reference

### **Common Commands**
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs celery
docker-compose logs celery-beat
docker-compose logs flower

# Worker management
uv run celery -A src worker --loglevel=info
uv run celery -A src beat --loglevel=info
uv run celery -A src flower

# Monitoring
uv run celery -A src inspect stats
uv run celery -A src inspect active
uv run celery -A src events

# Task management
uv run celery -A src control revoke <task_id>
uv run celery -A src purge  # Clear all tasks
```

### **Task Patterns**
```python
# Basic task
@current_app.task(bind=True)
def my_task(self, arg):
    return "Result"

# Invoke asynchronously
task = my_task.apply_async(args=[arg], countdown=60)

# Check status
from celery.result import AsyncResult
result = AsyncResult(task.id)
print(result.status)
```

### **Scheduled Tasks**
```python
# In settings
CELERY_BEAT_SCHEDULE = {
    'task-name': {
        'task': 'app.tasks.my_task',
        'schedule': crontab(minute=0, hour=0),  # Daily at midnight
    },
}
```

---

**🎉 Your Celery setup is now complete with RabbitMQ broker, container architecture, and comprehensive task patterns!**
