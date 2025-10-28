x-ratelimit-limit: 30
x-ratelimit-remaining: 28
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'...
X-Request-ID: [UUID único]
x-process-time: [tempo de processamento]# Levitiis - Sistema de Gestão Industrial

Sistema completo de gestão industrial com monitoramento de máquinas, gestão de tickets e dashboard em tempo real.

## 🏗️ Arquitetura

### Stack Tecnológica
- **Frontend**: Vue.js 3 + Vite + Pinia + TailwindCSS
- **Backend**: FastAPI + Python 3.11
- **Banco de Dados**: PostgreSQL 15 + SQLAlchemy (ORM)
- **Cache/Session**: Redis
- **Proxy**: Nginx
- **Containerização**: Docker + Docker Compose

### Arquitetura Cliente-Servidor
```
[Agente Python] → [API REST] → [PostgreSQL] → [Dashboard React/Vue]
                      ↓
                 [Redis Cache]
                      ↓
                 [Nginx Proxy]
```

## 🚀 Funcionalidades

### Dashboard
- ✅ Estatísticas em tempo real
- ✅ Métricas de performance
- ✅ Atividades recentes
- ✅ Health check do sistema

### Autenticação e Segurança
- ✅ JWT Authentication (Access + Refresh tokens)
- ✅ Rate Limiting (30 req/min por IP)
- ✅ Input Validation e Sanitização
- ✅ Headers de Segurança (OWASP)
- ✅ CORS configurado
- ✅ Middleware de Logging

### APIs Implementadas

#### Autenticação (`/api/v1/auth/`)
- `POST /login` - Login com username/password
- `POST /refresh` - Renovar access token
- `POST /logout` - Logout

#### Dashboard (`/api/v1/dashboard/`)
- `GET /stats` - Estatísticas gerais
- `GET /metrics` - Métricas detalhadas
- `GET /recent-activity` - Atividades recentes
- `GET /health-check` - Status do sistema

#### Máquinas (`/api/v1/machines/`)
- `POST /register` - Registrar nova máquina
- `GET /status` - Status das máquinas

#### Tickets (`/api/v1/tickets/`)
- `POST /create` - Criar novo ticket

#### Alertas (`/api/v1/alerts/`)
- `POST /send` - Enviar alerta

## 🛡️ Segurança

### Middlewares Implementados
1. **Rate Limiting**: Controle de requisições por IP/usuário
2. **Input Validation**: Validação e sanitização de dados
3. **Security Headers**: Headers OWASP recomendados
4. **Request Logging**: Log de todas as requisições

### Headers de Segurança
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'...`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

## 🔧 Desenvolvimento

### Pré-requisitos
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose

### Configuração Local

1. **Clone o repositório**
```bash
git clone <repository-url>
cd levitiis-vue
```

2. **Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

3. **Frontend**
```bash
npm install
npm run dev
```

### Variáveis de Ambiente

#### Desenvolvimento (`.env`)
```env
DATABASE_URL=sqlite:///./levitiis.db
SECRET_KEY=dev-secret-key
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

#### Produção (`.env.production`)
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/levitiis_prod
SECRET_KEY=your-super-secret-key
DEBUG=false
CORS_ORIGINS=https://yourdomain.com
```

## 🚀 Deploy em Produção

### Usando Docker Compose

1. **Configurar variáveis de ambiente**
```bash
cp .env.production .env
# Editar .env com suas configurações
```

2. **Deploy com script automatizado**
```bash
chmod +x deploy.sh
./deploy.sh deploy
```

3. **Comandos úteis**
```bash
./deploy.sh health      # Verificar saúde da aplicação
./deploy.sh logs        # Ver logs
./deploy.sh backup      # Backup do banco
./deploy.sh rollback    # Rollback para versão anterior
```

### Deploy Manual

1. **Subir os serviços**
```bash
docker-compose up -d
```

2. **Verificar status**
```bash
docker-compose ps
docker-compose logs -f
```

## 📊 Monitoramento

### Health Checks
- **Backend**: `GET /health`
- **Frontend**: `GET /`
- **Database**: Verificação automática via Docker

### Logs
- **Aplicação**: `/var/log/levitiis/app.log`
- **Nginx**: `/var/log/nginx/`
- **Docker**: `docker-compose logs`

### Métricas
- Rate limiting headers: `x-ratelimit-*`
- Request tracking: `X-Request-ID`
- Process time: `x-process-time`

## 🔒 Padrões de Segurança

### TLS/SSL
- Certificados configurados no Nginx
- Redirecionamento HTTP → HTTPS
- HSTS headers

### Autenticação
- JWT com expiração configurável
- Refresh tokens para renovação
- Rate limiting em endpoints de auth

### Validação
- Sanitização de inputs
- Proteção contra XSS/SQL Injection
- Validação de tamanho de payload

## 📁 Estrutura do Projeto

```
levitiis-vue/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints da API
│   │   ├── core/           # Configurações
│   │   ├── middleware/     # Middlewares de segurança
│   │   ├── models/         # Modelos SQLAlchemy
│   │   └── services/       # Lógica de negócio
│   ├── Dockerfile
│   └── requirements.txt
├── src/                    # Frontend Vue.js
│   ├── components/         # Componentes Vue
│   ├── services/          # APIs e serviços
│   ├── stores/            # Pinia stores
│   └── views/             # Páginas
├── docker-compose.yml      # Orquestração Docker
├── nginx.conf             # Configuração Nginx
├── deploy.sh              # Script de deploy
└── README.md
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte técnico ou dúvidas:
- Email: suporte@levitiis.com
- Issues: GitHub Issues
- Documentação: [Wiki do projeto]