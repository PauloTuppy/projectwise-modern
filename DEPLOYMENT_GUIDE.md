# 🚀 ProjectWise Modern - Guia de Deploy

## Guia Completo de Deployment para Produção

**Versão:** 1.0.0  
**Data:** 2025-11-03  
**Status:** Production Ready

---

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Configuração do Ambiente](#configuração-do-ambiente)
3. [Deploy Backend](#deploy-backend)
4. [Deploy Frontend](#deploy-frontend)
5. [Deploy Database](#deploy-database)
6. [Deploy Celery](#deploy-celery)
7. [Configuração de Domínio](#configuração-de-domínio)
8. [Monitoramento](#monitoramento)
9. [Backup e Recovery](#backup-e-recovery)
10. [Troubleshooting](#troubleshooting)

---

## 🔧 Pré-requisitos

### Servidor
- **OS:** Ubuntu 22.04 LTS ou superior
- **RAM:** Mínimo 4GB (Recomendado 8GB)
- **CPU:** 2 cores (Recomendado 4 cores)
- **Storage:** 50GB SSD
- **Network:** IP público estático

### Software
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Nginx
- Certbot (para SSL)

### Contas Necessárias
- [ ] Conta Google Cloud (para Gemini AI)
- [ ] Domínio registrado
- [ ] Servidor VPS (AWS, DigitalOcean, Vultr, etc.)

---

## ⚙️ Configuração do Ambiente

### 1. Atualizar Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instalar Dependências Base

```bash
# Python e pip
sudo apt install python3.11 python3.11-venv python3-pip -y

# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Redis
sudo apt install redis-server -y

# Nginx
sudo apt install nginx -y

# Certbot (SSL)
sudo apt install certbot python3-certbot-nginx -y

# Git
sudo apt install git -y
```

### 3. Criar Usuário de Deploy

```bash
sudo adduser projectwise
sudo usermod -aG sudo projectwise
su - projectwise
```

---

## 🗄️ Deploy Database

### 1. Configurar PostgreSQL

```bash
# Conectar como postgres
sudo -u postgres psql

# Criar database e usuário
CREATE DATABASE projectwise_prod;
CREATE USER projectwise_user WITH PASSWORD 'STRONG_PASSWORD_HERE';
ALTER ROLE projectwise_user SET client_encoding TO 'utf8';
ALTER ROLE projectwise_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE projectwise_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE projectwise_prod TO projectwise_user;

# Sair
\q
```

### 2. Configurar Acesso Remoto (Opcional)

```bash
# Editar postgresql.conf
sudo nano /etc/postgresql/15/main/postgresql.conf

# Adicionar:
listen_addresses = 'localhost'

# Editar pg_hba.conf
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Adicionar:
host    projectwise_prod    projectwise_user    127.0.0.1/32    md5

# Reiniciar
sudo systemctl restart postgresql
```

### 3. Configurar Redis

```bash
# Editar redis.conf
sudo nano /etc/redis/redis.conf

# Configurar:
bind 127.0.0.1
maxmemory 256mb
maxmemory-policy allkeys-lru

# Reiniciar
sudo systemctl restart redis
sudo systemctl enable redis
```

---

## 🔙 Deploy Backend

### 1. Clonar Repositório

```bash
cd /home/projectwise
git clone https://github.com/seu-usuario/projectwise-modern.git
cd projectwise-modern/backend
```

### 2. Criar Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 4. Configurar Variáveis de Ambiente

```bash
nano .env.production
```

```env
# Database
DATABASE_URL=postgresql://projectwise_user:STRONG_PASSWORD@localhost/projectwise_prod

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=GENERATE_STRONG_SECRET_KEY_HERE_MIN_32_CHARS
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# AI
GEMINI_API_KEY=your-gemini-api-key-here

# CORS
CORS_ORIGINS=["https://seu-dominio.com","https://www.seu-dominio.com"]

# Storage
STORAGE_PATH=/home/projectwise/uploads

# Environment
ENVIRONMENT=production
DEBUG=False
```

### 5. Executar Migrations

```bash
source venv/bin/activate
alembic upgrade head
```

### 6. Criar Diretório de Uploads

```bash
mkdir -p /home/projectwise/uploads
chmod 755 /home/projectwise/uploads
```

### 7. Configurar Gunicorn

```bash
nano /home/projectwise/projectwise-modern/backend/gunicorn.conf.py
```

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
errorlog = "/home/projectwise/logs/gunicorn-error.log"
accesslog = "/home/projectwise/logs/gunicorn-access.log"
loglevel = "info"
```

### 8. Criar Systemd Service

```bash
sudo nano /etc/systemd/system/projectwise-backend.service
```

```ini
[Unit]
Description=ProjectWise Backend
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=projectwise
Group=projectwise
WorkingDirectory=/home/projectwise/projectwise-modern/backend
Environment="PATH=/home/projectwise/projectwise-modern/backend/venv/bin"
EnvironmentFile=/home/projectwise/projectwise-modern/backend/.env.production
ExecStart=/home/projectwise/projectwise-modern/backend/venv/bin/gunicorn app.main:app -c gunicorn.conf.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 9. Iniciar Backend

```bash
# Criar diretório de logs
mkdir -p /home/projectwise/logs

# Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable projectwise-backend
sudo systemctl start projectwise-backend

# Verificar status
sudo systemctl status projectwise-backend
```

---

## 🎨 Deploy Frontend

### 1. Build Frontend

```bash
cd /home/projectwise/projectwise-modern/frontend

# Instalar dependências
npm install

# Criar .env.production
nano .env.production
```

```env
VITE_API_URL=https://api.seu-dominio.com
VITE_WS_URL=wss://api.seu-dominio.com
VITE_APP_NAME=ProjectWise Modern
```

```bash
# Build para produção
npm run build

# Resultado em: dist/
```

### 2. Copiar Build para Nginx

```bash
sudo mkdir -p /var/www/projectwise
sudo cp -r dist/* /var/www/projectwise/
sudo chown -R www-data:www-data /var/www/projectwise
```

---

## 🔄 Deploy Celery

### 1. Configurar Celery Worker

```bash
sudo nano /etc/systemd/system/projectwise-celery-worker.service
```

```ini
[Unit]
Description=ProjectWise Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=projectwise
Group=projectwise
WorkingDirectory=/home/projectwise/projectwise-modern/backend
Environment="PATH=/home/projectwise/projectwise-modern/backend/venv/bin"
EnvironmentFile=/home/projectwise/projectwise-modern/backend/.env.production
ExecStart=/home/projectwise/projectwise-modern/backend/venv/bin/celery -A app.tasks.celery_app worker --loglevel=info --logfile=/home/projectwise/logs/celery-worker.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Configurar Celery Beat

```bash
sudo nano /etc/systemd/system/projectwise-celery-beat.service
```

```ini
[Unit]
Description=ProjectWise Celery Beat
After=network.target redis.service

[Service]
Type=simple
User=projectwise
Group=projectwise
WorkingDirectory=/home/projectwise/projectwise-modern/backend
Environment="PATH=/home/projectwise/projectwise-modern/backend/venv/bin"
EnvironmentFile=/home/projectwise/projectwise-modern/backend/.env.production
ExecStart=/home/projectwise/projectwise-modern/backend/venv/bin/celery -A app.tasks.celery_app beat --loglevel=info --logfile=/home/projectwise/logs/celery-beat.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Iniciar Celery

```bash
sudo systemctl daemon-reload
sudo systemctl enable projectwise-celery-worker
sudo systemctl enable projectwise-celery-beat
sudo systemctl start projectwise-celery-worker
sudo systemctl start projectwise-celery-beat

# Verificar status
sudo systemctl status projectwise-celery-worker
sudo systemctl status projectwise-celery-beat
```

---

## 🌐 Configuração de Domínio

### 1. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/projectwise
```

```nginx
# Frontend
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;
    
    root /var/www/projectwise;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}

# Backend API
server {
    listen 80;
    server_name api.seu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Upload size
    client_max_body_size 500M;
}
```

### 2. Habilitar Site

```bash
sudo ln -s /etc/nginx/sites-available/projectwise /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. Configurar SSL (Let's Encrypt)

```bash
# Frontend
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Backend
sudo certbot --nginx -d api.seu-dominio.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## 📊 Monitoramento

### 1. Logs

```bash
# Backend logs
tail -f /home/projectwise/logs/gunicorn-error.log
tail -f /home/projectwise/logs/gunicorn-access.log

# Celery logs
tail -f /home/projectwise/logs/celery-worker.log
tail -f /home/projectwise/logs/celery-beat.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u projectwise-backend -f
sudo journalctl -u projectwise-celery-worker -f
```

### 2. Health Checks

```bash
# Backend health
curl https://api.seu-dominio.com/health

# Database
psql -U projectwise_user -d projectwise_prod -c "SELECT 1"

# Redis
redis-cli ping

# Celery
celery -A app.tasks.celery_app inspect active
```

---

## 💾 Backup e Recovery

### 1. Backup Automático do Database

```bash
# Criar script de backup
nano /home/projectwise/backup-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/projectwise/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="projectwise_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

pg_dump -U projectwise_user projectwise_prod > $BACKUP_DIR/$FILENAME

# Comprimir
gzip $BACKUP_DIR/$FILENAME

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $FILENAME.gz"
```

```bash
chmod +x /home/projectwise/backup-db.sh

# Adicionar ao crontab (diário às 2 AM)
crontab -e
```

```cron
0 2 * * * /home/projectwise/backup-db.sh >> /home/projectwise/logs/backup.log 2>&1
```

### 2. Recovery

```bash
# Restaurar backup
gunzip projectwise_backup_YYYYMMDD_HHMMSS.sql.gz
psql -U projectwise_user projectwise_prod < projectwise_backup_YYYYMMDD_HHMMSS.sql
```

---

## 🔧 Troubleshooting

### Backend não inicia

```bash
# Verificar logs
sudo journalctl -u projectwise-backend -n 50

# Verificar porta
sudo netstat -tulpn | grep 8000

# Testar manualmente
cd /home/projectwise/projectwise-modern/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Celery não processa tasks

```bash
# Verificar worker
sudo systemctl status projectwise-celery-worker

# Verificar Redis
redis-cli ping

# Verificar tasks
celery -A app.tasks.celery_app inspect active
celery -A app.tasks.celery_app inspect scheduled
```

### Database connection error

```bash
# Verificar PostgreSQL
sudo systemctl status postgresql

# Testar conexão
psql -U projectwise_user -d projectwise_prod -c "SELECT 1"

# Verificar .env
cat /home/projectwise/projectwise-modern/backend/.env.production | grep DATABASE_URL
```

### SSL certificate issues

```bash
# Renovar certificado
sudo certbot renew --dry-run
sudo certbot renew

# Verificar auto-renewal
sudo systemctl status certbot.timer
```

---

## ✅ Checklist de Deploy

- [ ] Servidor configurado e atualizado
- [ ] PostgreSQL instalado e configurado
- [ ] Redis instalado e rodando
- [ ] Backend clonado e dependências instaladas
- [ ] Migrations executadas
- [ ] Backend service rodando
- [ ] Celery worker rodando
- [ ] Celery beat rodando
- [ ] Frontend buildado
- [ ] Nginx configurado
- [ ] SSL configurado
- [ ] Domínio apontando para servidor
- [ ] Backup automático configurado
- [ ] Logs sendo gerados
- [ ] Health checks passando
- [ ] Monitoramento ativo

---

## 🎯 Próximos Passos

Após deploy bem-sucedido:

1. **Configurar Monitoring** (Sentry, New Relic, etc.)
2. **Configurar Alertas** (email, Slack, etc.)
3. **Performance Tuning** (cache, CDN, etc.)
4. **Security Hardening** (firewall, fail2ban, etc.)
5. **Load Testing** (Apache Bench, k6, etc.)

---

**Deploy Guide v1.0.0**  
**ProjectWise Modern - Production Ready** ✅

