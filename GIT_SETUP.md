# 🚀 Git Setup - Push para GitHub

## Guia Completo para Publicar no GitHub

---

## 📋 Pré-requisitos

- [ ] Conta no GitHub criada
- [ ] Git instalado localmente
- [ ] Repositório criado no GitHub

---

## 🔧 Passo a Passo

### 1. Verificar Git

```bash
# Verificar se Git está instalado
git --version

# Se não estiver instalado:
# Windows: https://git-scm.com/download/win
# Mac: brew install git
# Linux: sudo apt install git
```

### 2. Configurar Git (Primeira vez)

```bash
# Configurar nome e email
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@example.com"

# Verificar configuração
git config --list
```

### 3. Inicializar Repositório Local

```bash
# Navegar para o diretório do projeto
cd projectwise-modern

# Inicializar Git (se ainda não foi feito)
git init

# Verificar status
git status
```

### 4. Adicionar Arquivos

```bash
# Adicionar todos os arquivos
git add .

# Ou adicionar seletivamente
git add backend/
git add frontend/
git add *.md
git add .gitignore

# Verificar o que será commitado
git status
```

### 5. Fazer Primeiro Commit

```bash
# Commit com mensagem descritiva
git commit -m "Initial commit: ProjectWise Modern v1.0.0

- 3 features completas (Project Management, Document Upload + AI, Dashboard KPIs)
- AI Analysis com Gemini 2.0 Flash
- Dashboard ISO 9001:2015 compliant
- Documentação completa
- Production ready"

# Verificar commit
git log
```

### 6. Criar Repositório no GitHub

1. Acesse https://github.com/new
2. Nome do repositório: `projectwise-modern`
3. Descrição: `Enterprise Document & Project Management Platform with AI`
4. Visibilidade: **Public** ou **Private**
5. **NÃO** inicialize com README, .gitignore ou license
6. Clique em **Create repository**

### 7. Conectar ao GitHub

```bash
# Adicionar remote (substitua SEU-USUARIO pelo seu username)
git remote add origin https://github.com/SEU-USUARIO/projectwise-modern.git

# Verificar remote
git remote -v

# Renomear branch para main (se necessário)
git branch -M main
```

### 8. Push para GitHub

```bash
# Push inicial
git push -u origin main

# Se pedir autenticação, use:
# Username: seu-username
# Password: seu Personal Access Token (não a senha!)
```

### 9. Criar Personal Access Token (Se necessário)

Se o GitHub pedir senha e não aceitar:

1. Acesse: https://github.com/settings/tokens
2. Clique em **Generate new token** → **Generate new token (classic)**
3. Nome: `ProjectWise Modern`
4. Selecione scopes:
   - [x] repo (todos)
   - [x] workflow
5. Clique em **Generate token**
6. **COPIE O TOKEN** (você não verá novamente!)
7. Use o token como senha no git push

### 10. Verificar no GitHub

1. Acesse: https://github.com/SEU-USUARIO/projectwise-modern
2. Verifique se todos os arquivos foram enviados
3. Verifique se o README.md está sendo exibido

---

## 📁 Estrutura que Será Enviada

```
projectwise-modern/
├── backend/                    ✅
│   ├── app/
│   ├── migrations/
│   ├── requirements.txt
│   └── .env.example           ✅ (não .env)
├── frontend/                   ✅
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── docs/                       ✅
│   ├── *.md
├── .kiro/specs/               ✅
├── .gitignore                 ✅
├── README.md                  ✅
├── DEPLOYMENT_GUIDE.md        ✅
├── PROJECT_DELIVERY.md        ✅
└── LICENSE                    ✅ (criar)
```

### ⚠️ Arquivos que NÃO serão enviados (por .gitignore):

- ❌ `node_modules/`
- ❌ `venv/`
- ❌ `.env` (contém secrets!)
- ❌ `__pycache__/`
- ❌ `dist/`
- ❌ `*.log`

---

## 🔒 Segurança - Verificar Antes do Push

### Verificar se não há secrets no código:

```bash
# Procurar por possíveis secrets
grep -r "password" --exclude-dir={node_modules,venv,.git}
grep -r "secret" --exclude-dir={node_modules,venv,.git}
grep -r "api_key" --exclude-dir={node_modules,venv,.git}
grep -r "GEMINI_API_KEY" --exclude-dir={node_modules,venv,.git}

# Verificar .env não está sendo commitado
git status | grep ".env"
```

### Criar .env.example (se não existir):

```bash
# backend/.env.example
cat > backend/.env.example << 'EOF'
# Database
DATABASE_URL=postgresql://user:password@localhost/projectwise

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# AI
GEMINI_API_KEY=your-gemini-api-key-here

# CORS
CORS_ORIGINS=["http://localhost:5173"]

# Storage
STORAGE_PATH=./uploads

# Environment
ENVIRONMENT=development
DEBUG=True
EOF
```

---

## 📝 Criar LICENSE

```bash
# Criar arquivo LICENSE (MIT)
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 ProjectWise Modern

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# Adicionar ao git
git add LICENSE
git commit -m "Add MIT License"
git push
```

---

## 🎨 Melhorar README do GitHub

O README.md já está ótimo, mas você pode adicionar badges:

```markdown
# 🚀 ProjectWise Modern

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Progress](https://img.shields.io/badge/progress-80%25-blue)]()
[![ISO](https://img.shields.io/badge/ISO%209001%3A2015-compliant-green)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![Node](https://img.shields.io/badge/node-18+-green)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal)]()
[![React](https://img.shields.io/badge/React-18-blue)]()
```

---

## 🔄 Comandos Git Úteis

### Adicionar mais arquivos depois:

```bash
# Adicionar novos arquivos
git add .
git commit -m "Add new feature"
git push
```

### Ver histórico:

```bash
git log --oneline
git log --graph --oneline --all
```

### Desfazer mudanças:

```bash
# Desfazer mudanças não commitadas
git checkout -- arquivo.txt

# Desfazer último commit (mantém mudanças)
git reset --soft HEAD~1

# Desfazer último commit (descarta mudanças)
git reset --hard HEAD~1
```

### Branches:

```bash
# Criar nova branch
git checkout -b feature/nova-feature

# Listar branches
git branch

# Mudar de branch
git checkout main

# Merge branch
git merge feature/nova-feature
```

---

## 📊 Configurar GitHub Pages (Opcional)

Para hospedar documentação:

1. Acesse: Settings → Pages
2. Source: Deploy from a branch
3. Branch: main → /docs
4. Save

Sua documentação estará em:
`https://SEU-USUARIO.github.io/projectwise-modern/`

---

## 🏷️ Criar Release

Após o push inicial:

1. Acesse: Releases → Create a new release
2. Tag: `v1.0.0`
3. Title: `ProjectWise Modern v1.0.0 - Production Ready`
4. Description:
```markdown
## 🎉 First Release - Production Ready

### Features Completas (80%)
- ✅ Project Management
- ✅ Document Upload + AI Analysis (Gemini 2.0)
- ✅ Dashboard KPIs (ISO 9001:2015)
- 🔨 Workflow Automation (80%)

### Highlights
- ~5,000 linhas de código
- Documentação completa
- Deployment guide
- Production ready

### Quick Start
See [README.md](README.md) for installation instructions.

### Documentation
- [Quick Start Guide](QUICK_START.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Project Delivery](PROJECT_DELIVERY.md)
```
5. Clique em **Publish release**

---

## ✅ Checklist Final

Antes de fazer público:

- [ ] .gitignore configurado
- [ ] .env não está no repositório
- [ ] .env.example criado
- [ ] README.md completo
- [ ] LICENSE adicionado
- [ ] Secrets removidos do código
- [ ] Documentação revisada
- [ ] Links atualizados (substitua SEU-USUARIO)
- [ ] Build funcionando
- [ ] Testes passando (se houver)

---

## 🎯 Comandos Resumidos

```bash
# Setup inicial
git init
git add .
git commit -m "Initial commit: ProjectWise Modern v1.0.0"

# Conectar ao GitHub
git remote add origin https://github.com/SEU-USUARIO/projectwise-modern.git
git branch -M main

# Push
git push -u origin main

# Verificar
git status
git log
```

---

## 🆘 Troubleshooting

### Erro: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/SEU-USUARIO/projectwise-modern.git
```

### Erro: "failed to push some refs"
```bash
# Pull primeiro
git pull origin main --rebase
git push origin main
```

### Erro: "Authentication failed"
```bash
# Use Personal Access Token, não senha
# Gere em: https://github.com/settings/tokens
```

### Arquivo grande demais
```bash
# GitHub tem limite de 100MB por arquivo
# Use Git LFS para arquivos grandes
git lfs install
git lfs track "*.pdf"
git add .gitattributes
```

---

## 🎉 Pronto!

Seu código está no GitHub! 🚀

**URL:** https://github.com/SEU-USUARIO/projectwise-modern

**Próximos passos:**
1. Adicionar colaboradores (Settings → Collaborators)
2. Configurar branch protection (Settings → Branches)
3. Adicionar GitHub Actions (CI/CD)
4. Configurar Issues e Projects
5. Adicionar Topics (tags) ao repositório

---

**Criado em:** 2025-11-03  
**Versão:** 1.0.0

