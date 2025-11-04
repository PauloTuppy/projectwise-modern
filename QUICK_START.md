# 🚀 ProjectWise Modern - Quick Start Guide

## ⚡ Start em 5 Minutos

### 1. Iniciar Backend (Terminal 1)
```bash
cd backend
python -m uvicorn app.main:app --reload
```

**Esperado:** 
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 2. Iniciar Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

**Esperado:**
```
VITE v5.4.21  ready in 500 ms
➜  Local:   http://localhost:5173/
```

### 3. Acessar Aplicação
Abra no navegador: **http://localhost:5173**

---

## 🎯 O Que Você Pode Fazer Agora

### ✅ Feature 1: Project Management
**URL:** http://localhost:5173/

**Ações:**
1. Clicar em "+ New" para criar projeto
2. Preencher nome e descrição
3. Clicar no projeto para ver detalhes
4. Clicar em "+ Invite" para adicionar membro
5. Gerenciar roles dos membros

### ✅ Feature 2: Document Upload
**URL:** http://localhost:5173/upload

**Ações:**
1. Clicar em "Select Document"
2. Escolher arquivo PDF/DOCX/DWG (max 500MB)
3. Ver validação automática
4. Clicar em "Upload & Analyze with AI"
5. Ver progress bar
6. (Análise AI aparecerá quando configurada)

---

## 🔧 Troubleshooting

### Backend não inicia
```bash
# Verificar Python
python --version  # Deve ser 3.11+

# Instalar dependências
cd backend
pip install -r requirements.txt

# Verificar .env
cat backend/.env  # Deve existir
```

### Frontend não inicia
```bash
# Verificar Node
node --version  # Deve ser 18+

# Reinstalar dependências
cd frontend
rm -rf node_modules
npm install

# Verificar .env.local
cat frontend/.env.local  # Deve existir
```

### Build com erros
```bash
cd frontend
npm run build

# Se houver erros TypeScript, verificar:
# - Imports corretos
# - Tipos definidos
# - Componentes exportados
```

---

## 📊 Status das Features

| Feature | Status | URL | Ações Disponíveis |
|---------|--------|-----|-------------------|
| Project Management | ✅ 100% | `/` | Criar, listar, convidar, gerenciar |
| Document Upload | ✅ 90% | `/upload` | Upload, validação, progress |
| Real-time Collab | 🚧 0% | - | Pendente |
| Workflows | 🚧 0% | - | Pendente |
| Versioning | 🚧 0% | - | Pendente |
| Dashboard | 🚧 0% | - | Pendente |
| Notifications | 🚧 0% | - | Pendente |

---

## 🎯 Próximos Passos

### Para Desenvolvedores

1. **Completar AI Analysis**
   ```bash
   pip install google-generativeai PyPDF2 python-docx
   # Adicionar GEMINI_API_KEY ao .env
   ```

2. **Implementar Feature 5 (Versioning)**
   - Models já existem
   - Criar UI

3. **Criar Dashboard**
   - KPIs básicos
   - Gráficos simples

### Para Testers

1. **Testar Project Management**
   - Criar 3 projetos
   - Adicionar membros
   - Testar permissões

2. **Testar Document Upload**
   - Upload PDF pequeno
   - Upload arquivo grande (próximo a 500MB)
   - Testar validação de tipo

3. **Reportar Issues**
   - Criar issue no repositório
   - Incluir screenshots
   - Descrever passos para reproduzir

---

## 📝 Comandos Úteis

### Backend
```bash
# Rodar servidor
python -m uvicorn app.main:app --reload

# Rodar com debug
python -m uvicorn app.main:app --reload --log-level debug

# Criar migração
alembic revision --autogenerate -m "description"

# Aplicar migração
alembic upgrade head
```

### Frontend
```bash
# Dev server
npm run dev

# Build
npm run build

# Preview build
npm run serve

# Lint
npm run lint

# Type check
npx tsc --noEmit
```

---

## 🐛 Problemas Comuns

### "Module not found"
```bash
cd frontend
npm install
```

### "Port already in use"
```bash
# Backend (porta 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (porta 5173)
lsof -ti:5173 | xargs kill -9
```

### "Database connection error"
```bash
# Verificar PostgreSQL rodando
# Verificar DATABASE_URL no .env
```

### "CORS error"
```bash
# Verificar CORS_ORIGINS no backend/app/config.py
# Deve incluir http://localhost:5173
```

---

## 📚 Documentação Adicional

- **Setup Completo:** `PROJECT_SETUP_REPORT.md`
- **Status Geral:** `PROJECT_STATUS_SUMMARY.md`
- **Feature 1:** `FEATURE_1_COMPLETED.md`
- **Feature 2:** `FEATURE_2_COMPLETED.md`
- **Guia de Implementação:** `IMPLEMENTATION_GUIDE.md`

---

## ✅ Checklist de Verificação

Antes de começar a desenvolver, verifique:

- [ ] Backend rodando em http://localhost:8000
- [ ] Frontend rodando em http://localhost:5173
- [ ] Consegue acessar http://localhost:5173
- [ ] Consegue criar um projeto
- [ ] Consegue fazer upload de documento
- [ ] Build do frontend funciona (`npm run build`)
- [ ] Sem erros no console do navegador

---

**Tudo funcionando?** 🎉  
**Pronto para desenvolver!** 💪

*Última atualização: 2025-11-03*
