# Agentic AI Marketing Automation Platform

> **Purpose:** A multi-tenant, agentic AI SaaS that creates, publishes, and optimizes ads/posts across channels (Google Ads, Meta/IG, LinkedIn, TikTok, YouTube, X/Twitter, Reddit, Email), and tracks full-funnel performance with first‑party attribution. Runs locally or on a single host with Docker Compose; cloud-ready for K8s.

---

## 1) System Overview

**Core capabilities**
- Multi-agent orchestration for creative generation, policy checks, campaign setup, pacing, optimization, and reporting.
- Channel connectors with OAuth; unified metrics schema.
- First‑party tracking pixel + server-side events; UTM normalization.
- Attribution models (last-touch, position-based, time-decay; data-driven later).
- A/B tests and multi-armed bandits for asset rotation.
- Human-in-the-loop approvals + audit trails.

**High-level diagram (logical)**
```
[ Web App (React) ]  <—>  [ API Gateway (FastAPI) ]
                               |        |\
                               |        | \--> [ Webhooks ]
                               |        |----> [ Billing ]
                               |        \----> [ Auth/RBAC ]
         ---------------------------------------------------------------
         |               |                  |                 |        |
  [ Agent Orchestrator ] |            [ Attribution ]   [ Analytics ]  |
         |               |                  |                 |        |
   [ Celery/Redis ]   [ LLM Router ]   [ Events DB ]   [ DW/Lake ]  [ Connectors ]
                           |
                     [ OpenAI / vLLM ]
```

**Tech stack**
- **Backend:** Python 3.11, FastAPI, SQLAlchemy, Pydantic, Celery, Redis
- **Data:** Postgres (OLTP), ClickHouse (events/analytics), MinIO (assets)
- **Frontend:** React + Vite, TypeScript, Tailwind, shadcn/ui
- **AI:** LLM Router → OpenAI (default) or local vLLM; moderation/guardrails
- **Observability:** Prometheus, Grafana, Loki; OpenTelemetry traces
- **Packaging:** Docker Compose (dev/prod-single); K8s-ready manifests optional

---

## 2) Requirements

**Functional**
- Connect ad/social channels via OAuth; create campaigns/posts; fetch insights.
- Generate creatives (copy, images prompts, variations) aligned with brand voice.
- Policy/compliance checks per channel prior to publish.
- Track pageviews, clicks, leads, and revenue; support client & server events.
- Optimize spend & rotation with bandits and budget pacing.
- Dashboards: spend, CTR/CVR, CPA/ROAS/LTV, cohorting, funnels.
- Multi-tenant with roles (Admin, Marketer, Analyst, Approver).

**Non-functional**
- Data isolation per tenant; encrypted secrets.
- Rate-limit safe connector operations; retries & idempotency.
- Horizontal scale for workers & analytics queries.

**Out of scope (v1)**
- Auto creative image rendering (stable-diffusion) — roadmap.
- MMM (media mix modeling) — roadmap.

---

## 3) Service Catalog

1. **api-gateway** (FastAPI)
   - Tenants, users, roles; projects; assets; campaigns; experiments; reports.
   - OAuth callback endpoints for channels.
   - Emits background jobs to Celery for long-running tasks.

2. **orchestrator** (FastAPI + Celery workers)
   - Agents: `CreativeAgent`, `ComplianceAgent`, `ChannelPlanner`, `BudgetPacer`, `Optimizer`, `AnalystAgent`.
   - Maintains agent memory; schedules/retries; cost tracking.

3. **llm-router** (FastAPI)
   - Routes prompts to OpenAI or local vLLM.
   - Moderation/guardrails, token budget, caching.

4. **connectors-*** (workers)
   - `googleads`, `meta`, `linkedin`, `tiktok`, `x`, `youtube`, `reddit`, `email`.
   - OAuth, creative upload, campaign ops, insights ingestion.

5. **attribution** (FastAPI)
   - `/collect` for pixel/beacon & server events.
   - Sessionization; UTM mapping; path stitching; model scoring.

6. **analytics** (FastAPI + ClickHouse)
   - Timeseries, funnels, cohorts, LTV.

7. **webapp** (React/Vite)
   - Dashboard, builder, agents, approvals, experiments, attribution, reports.

8. **scheduler** (Celery beat)
   - Sync cadence; nightly optimizations; weekly reports.

9. **billing** (Stripe webhook)
   - Plans, seats, usage metering (API calls, posts, spend managed).

---

## 4) Data Model (selected tables)

**Postgres (OLTP)**
- `tenants(id, name, plan, created_at)`
- `users(id, tenant_id, email, role, status, password_hash, created_at)`
- `channels(id, tenant_id, type, oauth_json, status, created_at)`
- `campaigns(id, tenant_id, name, objective, status, budget_daily, start_at, end_at)`
- `ad_assets(id, tenant_id, type, title, text, media_url, tags, policy_flags, created_at)`
- `ad_sets(id, campaign_id, audience_json, placements_json, bid_strategy, budget_split)`
- `ads(id, ad_set_id, asset_id, channel, status, external_id, meta_json)`
- `experiments(id, tenant_id, name, hypothesis, metric, bandit_cfg_json)`
- `agent_runs(id, tenant_id, agent, input_ctx_json, output_json, status, tokens, cost, started_at, ended_at)`
- `events_inbox(id, tenant_id, source, payload_json, received_at, processed)`
- `attributions(id, tenant_id, session_id, touchpoints_json, model, value, currency, ts)`
- `audit_logs(id, tenant_id, actor, action, entity, before_json, after_json, ts)`

**ClickHouse (events/analytics)**
- `events (tenant_id String, user_id String, session_id String, event String, ts DateTime, url String, ref String, utm_source String, utm_medium String, utm_campaign String, revenue Float64, properties JSON)`

**MinIO (S3)**
- Bucket `assets/` for images, CSVs, exports.

---

## 5) Tracking Pixel & Server Events

**Browser pixel** (snippet)
```html
<script>
(function(){
  const sid = localStorage.getItem('am_sid') || crypto.randomUUID();
  localStorage.setItem('am_sid', sid);
  function send(ev, props={}){
    const body={event:ev, ts:new Date().toISOString(), url:location.href, ref:document.referrer, sid,
      utm_source:new URLSearchParams(location.search).get('utm_source'),
      utm_medium:new URLSearchParams(location.search).get('utm_medium'),
      utm_campaign:new URLSearchParams(location.search).get('utm_campaign'), props};
    navigator.sendBeacon('https://api.example.com/attribution/collect', JSON.stringify(body));
  }
  window.AgenticTrack={send};
  send('pageview');
})();
</script>
```

**Server event** (purchase example)
```http
POST /attribution/collect
{"event":"purchase","sid":"<session-id>","value":129.0,"currency":"EUR"}
```

**Attribution models**
- Last-touch; First-touch; Position-based (40/20/40); Time-decay (half-life configurable).
- Data-driven (Markov removal effects) — v2.

---

## 6) Agent Designs

- **CreativeAgent**: Generates multi-variant copy (headline, primary, CTA) per channel spec; tags assets with intents; uses brand guidelines.
- **ComplianceAgent**: Heuristic + LLM critique against platform policies; flags risky phrases; ensures length/aspect-ratio constraints.
- **ChannelPlanner**: Maps objective to campaign structure, placements, bids; emits connector jobs.
- **BudgetPacer**: Monitors spend vs. pacing curve; shifts budget between ad sets; respects min data thresholds.
- **Optimizer**: Thompson Sampling on CTR and CVR; pauses losers; promotes winners; creative rotation rules.
- **AnalystAgent**: Weekly narrative explaining changes and next steps; anomaly alerts.

**Agent run lifecycle (sequence)**
```
User action -> API /agents/run -> Celery task -> Agent executes (LLM calls + rules)
  -> emits connector jobs -> publish/update on channels -> events flow back
  -> Optimizer reads metrics -> adjustments -> report generated
```

---

## 7) Connectors (per channel)

**Common responsibilities**
- OAuth flow & token refresh; store encrypted tokens.
- Create/update campaigns/ad sets/ads or organic posts.
- Fetch insights (impressions, clicks, cost, conv.) with pagination & rate limits.
- Normalize to a shared schema; push to analytics & OLTP.
- Preflight policy & format validation before upload.

**Resilience**
- Idempotency keys; exponential backoff; partial failures logged in `events_inbox`.

---

## 8) API Design (selected endpoints)

**Auth & Tenancy**
- `POST /auth/login` → JWT
- `POST /tenants` | `GET /me`

**Campaigns**
- `POST /campaigns` create
- `GET /campaigns/:id`
- `POST /campaigns/:id/publish` (channels[])

**Agents**
- `POST /agents/run` {agent, context}
- `GET /agents/runs?campaign_id=...`

**Attribution**
- `POST /attribution/collect`
- `GET /attribution/paths?campaign_id=...&model=time_decay`

**Analytics**
- `GET /analytics/timeseries?metric=roas&gran=d`
- `GET /analytics/funnel?steps=click,lead,purchase`

**Connectors**
- `GET /connectors` list; `POST /connectors/:type/oauth/callback`

---

## 9) Docker Compose (v1)

```yaml
version: "3.9"
services:
  api:
    build: ./services/api
    env_file: .env
    ports: ["8080:8080"]
    depends_on: [db, redis]
  orchestrator:
    build: ./services/orchestrator
    env_file: .env
    depends_on: [db, redis, llmrouter]
  llmrouter:
    build: ./services/llm-router
    env_file: .env
    ports: ["9090:9090"]
  attribution:
    build: ./services/attribution
    env_file: .env
    ports: ["8085:8085"]
    depends_on: [clickhouse]
  analytics:
    build: ./services/analytics
    env_file: .env
    ports: ["8086:8086"]
    depends_on: [clickhouse]
  connectors-googleads:
    build: ./services/connectors/googleads
    env_file: .env
    depends_on: [api, redis]
  webapp:
    build: ./webapp
    env_file: .env
    ports: ["5173:5173"]
    depends_on: [api]
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: example
      POSTGRES_DB: agentic
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]
  clickhouse:
    image: clickhouse/clickhouse-server:24.8
    ports: ["8123:8123", "9000:9000"]
    volumes: ["chdata:/var/lib/clickhouse"]
  redis:
    image: redis:7
    ports: ["6379:6379"]
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minio
      MINIO_ROOT_PASSWORD: minio123
    ports: ["9000:9000", "9001:9001"]
volumes:
  pgdata:
  chdata:
```

**.env (sample)**
```
POSTGRES_DSN=postgresql+psycopg://postgres:example@db:5432/agentic
REDIS_URL=redis://redis:6379/0
CLICKHOUSE_URL=http://clickhouse:8123
OPENAI_API_KEY=sk-...
JWT_SECRET=change-me
PUBLIC_API_HOST=https://api.example.com
```

---

## 10) Implementation Notes (per service)

### api-gateway
- **Stack:** FastAPI, SQLAlchemy, Alembic, JWT, OPA/own RBAC.
- **Patterns:** DTO via Pydantic; Repository layer; Unit of Work for transactions.
- **Webhooks:** `/webhooks/stripe`, `/webhooks/meta`, `/webhooks/google` with shared verifier.
- **Idempotency:** `Idempotency-Key` header for POST endpoints that create resources.

### orchestrator
- **Celery** workers with queues per agent: `q.creative`, `q.optimize`.
- **Retry** policy: exponential backoff, bounded max retries; DLQ in Redis stream.
- **Costing:** token usage from `llm-router` logged to `agent_runs`.

### llm-router
- **Guards:** prompt lint (PII scrub, brand blacklist), moderation call; refusal-on-fail.
- **Caching:** prompt+params hash → Redis cache with TTL; cost-aware.

### connectors
- **OAuth secrets** encrypted at rest (AES-256 via Fernet + KMS key).
- **Rate-limits:** leaky bucket; per-app & per-user tokens; jitter on retries.
- **Schema normalization:** map provider metrics → `metrics_normalized` view.

### attribution
- **Sessionization:** cookie/localStorage `sid`; 30-min inactivity windows.
- **Path stitching:** joins events by `sid` and UTM; builds ordered touchpoint arrays.
- **Models:** pluggable scorer functions registered in a catalog.

### analytics
- **ClickHouse** materialized views: hourly timeseries per (tenant,campaign,channel).
- **Exports:** signed URLs from MinIO for CSV/XLSX; async generation.

### webapp
- **Routing:** dashboard, campaigns, agents, approvals, experiments, attribution, reports.
- **UI kit:** shadcn/ui; charts via Recharts; data tables with tanstack/table.
- **Auth:** JWT in httpOnly cookie; tenant switcher.

---

## 11) Security, Privacy & Compliance
- **RBAC** at API + row-level security (RLS) in Postgres per `tenant_id`.
- **Secrets**: environment variables via Docker; rotate; use Vault/KMS in prod.
- **PII** minimal collection; DSR endpoints (export/delete) for GDPR.
- **Audit logs** for every state-changing action.
- **CSP** and signed pixel; CORS narrowed to whitelisted origins.

---

## 12) Observability
- **Metrics:** request latencies, job durations, LLM token cost, queue depth, connector API quotas.
- **Logs:** structured JSON; Loki scrape; correlation-id propagation.
- **Tracing:** OpenTelemetry → Tempo/Jaeger.
- **Dashboards:**
  - Platform health (p50/p95 latencies, error rates)
  - Agent costs & win-rate
  - Channel spend & ROAS

---

## 13) Deployment & Environments
- **Local dev:** `docker compose up --build`; seed script creates demo tenant & data.
- **Staging:** single VM with Compose; HTTPS via Caddy/Traefik; nightly DB backup.
- **Prod:** start with Compose (VM) then migrate to K8s when needed.
- **Backups:** Postgres (pg_dump + WAL), ClickHouse (S3 disks), MinIO replication.

---

## 14) Testing Strategy
- **Unit tests:** agents, attribution scoring, API validators.
- **Contract tests:** connector mocks with recorded cassettes.
- **E2E:** Cypress/Playwright for web; mocked providers; synthetic events.
- **Load tests:** k6/Gatling for `/collect` and analytics queries.

---

## 15) Rollout Plan
- **MVP scope:** Meta + Google connectors; Creative/Compliance/Planner agents; last-touch attribution; dashboard core cards.
- **Beta:** LinkedIn + TikTok; bandits + BudgetPacer; funnels & cohorts; weekly Analyst report.
- **GA:** full connector set; time-decay attribution; billing; admin SSO.

---

## 16) Risks & Mitigations
- **API access changes** → keep connectors versioned; feature flags.
- **Attribution gaps** → server-side events + Conversions API; UTMs mandatory.
- **Model hallucinations** → guardrails + approval workflow + policy checks.
- **Rate limits** → job queues + backoff + nightly sync windows.

---

## 17) Roadmap Highlights
- Data-driven attribution (Markov/Shapley)
- Creative image/video generation with safety filters
- MMM & budget recommender
- Auto audience discovery via embeddings
- Slack/Email “narrative” daily briefs

---

## 18) Code Skeletons (excerpts)

**/services/api/main.py**
```python
from fastapi import FastAPI, Depends
from routers import campaigns, agents, attribution, connectors
from auth import require_auth

app = FastAPI(title="Agentic Marketing API")
app.include_router(campaigns.router, prefix="/campaigns", dependencies=[Depends(require_auth)])
app.include_router(agents.router, prefix="/agents", dependencies=[Depends(require_auth)])
app.include_router(attribution.router, prefix="/attribution")
app.include_router(connectors.router, prefix="/connectors", dependencies=[Depends(require_auth)])
```

**/services/orchestrator/worker.py**
```python
from celery import Celery
from agents import creative, compliance, planner, optimizer, analyst

celery = Celery(__name__, broker="redis://redis:6379/0", backend="redis://redis:6379/1")

@celery.task(bind=True, max_retries=5)
def run_agent(self, agent_name: str, ctx: dict):
    registry = {
        "CreativeAgent": creative.run,
        "ComplianceAgent": compliance.run,
        "ChannelPlanner": planner.run,
        "Optimizer": optimizer.run,
        "AnalystAgent": analyst.run,
    }
    try:
        return registry[agent_name](ctx)
    except Exception as e:
        raise self.retry(exc=e, countdown=min(600, 2**self.request.retries))
```

**/services/attribution/main.py**
```python
from fastapi import FastAPI, Request, BackgroundTasks
from datetime import datetime
from clickhouse_connect import get_client

app = FastAPI()
ch = get_client(host='clickhouse', port=8123)

@app.post("/collect")
async def collect(req: Request, bg: BackgroundTasks):
    payload = await req.json()
    payload.setdefault("ts", datetime.utcnow().isoformat())
    bg.add_task(write_event, payload)
    return {"ok": True}

def write_event(ev: dict):
    ch.insert('events', [(
        ev.get('tenant_id','t0'), ev.get('user_id',''), ev.get('sid',''), ev.get('event',''),
        ev.get('ts'), ev.get('url',''), ev.get('ref',''), ev.get('utm_source',''), ev.get('utm_medium',''),
        ev.get('utm_campaign',''), float(ev.get('value',0.0)), ev
    )], column_names=["tenant_id","user_id","session_id","event","ts","url","ref","utm_source","utm_medium","utm_campaign","revenue","properties"])
```

---

## 19) Acceptance Criteria (MVP)
- Bring-up with `docker compose up` → web at `:5173`, API at `:8080`.
- Connect Meta & Google test accounts; publish a sample campaign.
- Pixel records pageviews & a demo purchase; attribution view shows last touch.
- Optimizer pauses the lowest CTR variant after threshold.
- Dashboard displays spend, CTR, CPA, ROAS per channel in last 7 days.

---

## 20) Ops Runbook (quick)
- **Rotate OAuth tokens** monthly; alarms on imminent expiry.
- **Check queues:** `redis-cli llen celery` should be < 100 normally.
- **ClickHouse size:** cap retention to 400 days for raw events; rollup older.
- **Disaster:** restore Postgres from latest nightly + replay WAL; rehydrate events from ClickHouse if needed.

---

**End of Document**

