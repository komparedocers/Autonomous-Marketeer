# Autonomous Marketeer

> **AI-Powered Marketing Automation Platform**

A comprehensive, agentic AI SaaS application for marketing automation that creates, publishes, and optimizes ads across multiple channels using autonomous AI agents. Track conversions, analyze attribution, and let AI handle your marketing campaigns.

---

## 🚀 Features

### Core Capabilities

- **🤖 AI Agents**: Six specialized agents for marketing automation
  - **CreativeAgent**: Generate multi-variant ad copy using LLM
  - **ComplianceAgent**: Check content for platform policy violations
  - **ChannelPlanner**: Create optimal campaign strategies
  - **BudgetPacer**: Monitor and optimize budget allocation
  - **Optimizer**: Multi-armed bandit optimization (Thompson Sampling)
  - **AnalystAgent**: Generate insights and weekly reports

- **📊 Multi-Channel Publishing**: Support for:
  - Google Ads
  - Meta (Facebook/Instagram)
  - LinkedIn
  - TikTok
  - X (Twitter)
  - YouTube
  - Reddit
  - Email

- **📈 Attribution & Analytics**:
  - First-party tracking pixel
  - Server-side events
  - Multiple attribution models (last-touch, first-touch, linear, position-based)
  - Real-time analytics dashboard
  - Conversion funnel analysis

- **🎯 Dashboard Features**:
  - Campaign management (CRUD operations)
  - Agent monitoring and configuration
  - Performance analytics with charts
  - LLM provider configuration (OpenAI/Local toggle)
  - Real-time metrics

### Technical Stack

**Backend:**
- Python 3.11
- FastAPI (API Gateway)
- SQLAlchemy + PostgreSQL (OLTP)
- ClickHouse (Analytics)
- Redis (Cache & Queue)
- Celery (Task Queue)
- MinIO (S3-compatible storage)

**AI/LLM:**
- **Local LLM**: Hugging Face Transformers (Mistral-7B default)
- **OpenAI**: GPT-4 Turbo (optional)
- Configurable via dashboard and environment variables

**Frontend:**
- React 18
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query
- Recharts

**Infrastructure:**
- Docker Compose
- Prometheus (Metrics)
- Grafana (Dashboards)

---

## 📋 Prerequisites

- **Docker** and **Docker Compose** (v2.0+)
- **8GB RAM minimum** (16GB recommended for local LLM)
- **10GB disk space**
- **Optional**: NVIDIA GPU for local LLM acceleration

---

## 🏃 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/komparedocers/Autonomous-Marketeer.git
cd Autonomous-Marketeer
```

### 2. Run Setup Script

**Linux/macOS:**
```bash
bash setup.sh
```

**Windows:**
```cmd
setup.bat
```

**Manual alternative (if script fails):**
```bash
cp .env.example .env
```

This will:
- ✅ Create `.env` file from `.env.example`
- ✅ Display configuration summary
- ✅ Show you next steps

### 3. (Optional) Configure Environment

The `.env` file is created with sensible defaults. To enable OpenAI or customize:

```bash
# Edit .env file
nano .env  # or use your preferred editor

# Key configurations:
LLM_PROVIDER=local              # or 'openai' or 'both'
OPENAI_ENABLED=false            # Set to true to enable OpenAI
OPENAI_API_KEY=sk-...           # Add your OpenAI API key here
LOCAL_LLM_ENABLED=true          # Local LLM enabled by default
```

### 4. Start the Platform

```bash
# Start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

This will start:
- **API Gateway**: http://localhost:8080
- **Dashboard**: http://localhost:5173
- **Attribution Service**: http://localhost:8085
- **Analytics Service**: http://localhost:8086
- **LLM Router**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **MinIO Console**: http://localhost:9001 (minio/minio123)

### 5. Access the Dashboard

Open your browser and navigate to:

```
http://localhost:5173
```

**Default Login:**
- Email: `admin@demo.com`
- Password: `demo123`

---

## 📖 Usage Guide

### Creating a Campaign

1. Navigate to **Campaigns** in the sidebar
2. Click **"New Campaign"**
3. Fill in:
   - Campaign Name
   - Objective (conversions, traffic, awareness, leads)
   - Daily Budget
4. Click **"Create"**

### Running AI Agents

1. Go to **AI Agents** page
2. View available agents and their status
3. Agents run automatically based on campaigns or manually via API

Example API call to run an agent:

```bash
curl -X POST http://localhost:8080/agents/run \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "CreativeAgent",
    "context": {
      "objective": "conversions",
      "brand_voice": "professional and engaging",
      "target_audience": "tech professionals",
      "channel": "meta"
    },
    "llm_provider": "local"
  }'
```

### Configuring LLM Providers

#### Via Dashboard:

1. Go to **Settings** page
2. Toggle between **Local LLM** and **OpenAI**
3. Configure API keys and models
4. Select default provider

#### Via Environment Variables:

Edit `.env` file:

```bash
# Use Local LLM only
LLM_PROVIDER=local
LOCAL_LLM_ENABLED=true
OPENAI_ENABLED=false

# Use OpenAI
LLM_PROVIDER=openai
OPENAI_ENABLED=true
OPENAI_API_KEY=sk-your-key-here

# Use both (switch in dashboard)
LLM_PROVIDER=both
LOCAL_LLM_ENABLED=true
OPENAI_ENABLED=true
OPENAI_API_KEY=sk-your-key-here
```

### Tracking & Attribution

#### Install Tracking Pixel

Add to your website's `<head>` tag:

```html
<script src="http://localhost:8085/pixel.js"></script>
```

#### Track Custom Events

```javascript
// Track a conversion
window.AgenticTrack.send('conversion', {
  value: 99.99,
  currency: 'USD',
  product_id: 'prod_123'
})

// Track a custom event
window.AgenticTrack.send('add_to_cart', {
  product: 'T-Shirt',
  quantity: 2
})
```

### View Analytics

1. Navigate to **Analytics** page
2. View:
   - Summary metrics (CTR, CVR, revenue)
   - Conversion funnel
   - Performance charts
3. Filter by date range and campaigns

---

## 🏗️ Architecture

```
┌─────────────────┐
│  React Dashboard│ ← User Interface
└────────┬────────┘
         │
    ┌────▼────────────────┐
    │   API Gateway       │ ← Auth, CRUD, Agent Control
    └─┬──────┬───────┬────┘
      │      │       │
┌─────▼──┐ ┌▼─────┐ │
│  OLTP  │ │Redis │ │
│ (PG)   │ │Queue │ │
└────────┘ └──────┘ │
                    │
        ┌───────────▼────────────┐
        │  Agent Orchestrator    │ ← Celery Workers
        │  - CreativeAgent       │
        │  - ComplianceAgent     │
        │  - Optimizer           │
        │  - ChannelPlanner      │
        │  - BudgetPacer         │
        │  - AnalystAgent        │
        └──────────┬─────────────┘
                   │
        ┌──────────▼─────────┐
        │    LLM Router      │ ← AI Intelligence
        │  - Local (Mistral) │
        │  - OpenAI (GPT-4)  │
        └────────────────────┘
```

**Data Flow:**
1. User creates campaign via Dashboard
2. API Gateway validates and stores in PostgreSQL
3. Orchestrator triggers agents via Celery
4. Agents call LLM Router for AI generation
5. Channel Connectors publish to platforms
6. Attribution Service tracks conversions
7. Analytics Service processes metrics
8. Dashboard displays results

---

## 🔧 Configuration

### Environment Variables

All configuration is in `.env` file. Key variables:

| Category | Variable | Description | Default |
|----------|----------|-------------|---------|
| **LLM** | `LLM_PROVIDER` | Default provider (local/openai/both) | `local` |
| | `OPENAI_ENABLED` | Enable OpenAI | `false` |
| | `LOCAL_LLM_ENABLED` | Enable local LLM | `true` |
| | `OPENAI_API_KEY` | OpenAI API key | - |
| **Database** | `POSTGRES_DSN` | PostgreSQL connection | Auto-configured |
| | `CLICKHOUSE_URL` | ClickHouse URL | Auto-configured |
| **Redis** | `REDIS_URL` | Redis connection | Auto-configured |
| **API** | `API_PORT` | API Gateway port | `8080` |
| | `JWT_SECRET` | JWT signing secret | Change in production! |

### Scaling Configuration

Edit `docker-compose.yml`:

```yaml
orchestrator:
  # Scale Celery workers
  command: celery -A app.tasks worker --concurrency=8

api:
  # Scale API workers
  environment:
    - API_WORKERS=8
```

Or use Docker Compose scale:

```bash
docker-compose up --scale orchestrator=3
```

---

## 📊 API Documentation

### Authentication

All endpoints (except `/auth/*`) require Bearer token:

```bash
# Login
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@demo.com", "password": "demo123"}'

# Returns: {"access_token": "eyJ...", "token_type": "bearer"}
```

### Key Endpoints

#### Campaigns
- `GET /campaigns` - List all campaigns
- `POST /campaigns` - Create campaign
- `PUT /campaigns/{id}` - Update campaign
- `DELETE /campaigns/{id}` - Delete campaign
- `POST /campaigns/{id}/publish` - Publish to channels

#### Agents
- `POST /agents/run` - Execute an agent
- `GET /agents/runs` - List agent executions
- `GET /agents/config` - Get agent configurations
- `GET /agents/llm/status` - Get LLM provider status

#### Analytics
- `GET /analytics/summary` - Summary metrics
- `GET /analytics/timeseries` - Time-series data
- `GET /analytics/funnel` - Conversion funnel

Full API docs available at: http://localhost:8080/docs

---

## 🔍 Monitoring

### Prometheus Metrics

Access Prometheus at http://localhost:3000

Available metrics:
- Request latencies (p50, p95, p99)
- Agent execution times
- LLM token usage and costs
- Queue depths
- Error rates

### Grafana Dashboards

Access Grafana at http://localhost:3000 (admin/admin)

Pre-configured dashboards:
- Platform Health
- Agent Performance
- Campaign Metrics
- LLM Usage & Costs

---

## 🧪 Development

### Running Tests

```bash
# API tests
docker-compose exec api pytest

# Frontend tests
cd webapp && npm test
```

### Accessing Services

```bash
# API shell
docker-compose exec api python

# Database
docker-compose exec db psql -U postgres agentic

# Redis CLI
docker-compose exec redis redis-cli

# View logs
docker-compose logs -f api
docker-compose logs -f orchestrator
```

### Adding New Agents

1. Create agent file in `services/orchestrator/app/agents/`
2. Implement `run(context, provider)` function
3. Register in `services/orchestrator/app/tasks.py`
4. Add configuration to API and frontend

---

## 📝 Troubleshooting

### Common Issues

**Issue**: Local LLM fails to load
```bash
# Solution: Check GPU availability or switch to CPU
docker-compose logs llmrouter

# Force CPU mode - edit docker-compose.yml:
# Comment out GPU sections in llmrouter service
```

**Issue**: Services can't connect
```bash
# Check network
docker network ls
docker network inspect autonomous-marketeer_agentic-network

# Restart services
docker-compose restart
```

**Issue**: Database migrations needed
```bash
# Run migrations
docker-compose exec api alembic upgrade head
```

**Issue**: Out of memory
```bash
# Reduce Celery workers or disable local LLM
# Edit .env:
LOCAL_LLM_ENABLED=false
CELERY_WORKER_CONCURRENCY=2
```

---

## 🚢 Production Deployment

### Security Checklist

- [ ] Change `JWT_SECRET` and `SECRET_KEY`
- [ ] Update database passwords
- [ ] Enable HTTPS (use Traefik or Nginx)
- [ ] Configure firewall rules
- [ ] Set up backup strategy
- [ ] Enable audit logs
- [ ] Review CORS settings
- [ ] Rotate OAuth tokens monthly

### Recommended Setup

- **Minimum**: 4 vCPUs, 16GB RAM, 50GB SSD
- **Recommended**: 8 vCPUs, 32GB RAM, 100GB SSD
- **Database**: Separate PostgreSQL and ClickHouse instances
- **Cache**: Redis cluster
- **Storage**: S3-compatible object storage
- **Orchestration**: Kubernetes for multi-instance deployment

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/komparedocers/Autonomous-Marketeer/issues
- Documentation: See `agentic_ai_marketing_platform_architecture_implementation.md`

---

## 🎯 Roadmap

- [ ] Data-driven attribution (Markov chains)
- [ ] Creative image/video generation
- [ ] Media Mix Modeling (MMM)
- [ ] Auto audience discovery
- [ ] Slack/Email daily briefs
- [ ] More channel connectors
- [ ] A/B testing framework
- [ ] Budget recommender

---

**Built with ❤️ using FastAPI, React, and AI**
