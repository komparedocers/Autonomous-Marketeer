"""Attribution Service for tracking and attribution."""
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import clickhouse_connect
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "analytics")

# Create FastAPI app
app = FastAPI(title="Attribution Service")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ClickHouse client
ch_client = None


class Event(BaseModel):
    """Event schema."""
    event: str
    sid: str  # Session ID
    user_id: Optional[str] = None
    tenant_id: Optional[str] = "t0"
    ts: Optional[str] = None
    url: Optional[str] = None
    ref: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    value: Optional[float] = 0.0
    currency: Optional[str] = "USD"
    props: Optional[Dict] = {}


@app.on_event("startup")
async def startup():
    """Initialize ClickHouse connection."""
    global ch_client
    try:
        ch_client = clickhouse_connect.get_client(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            database=CLICKHOUSE_DB,
        )
        logger.info("ClickHouse connection established")

        # Create events table if not exists
        ch_client.command("""
            CREATE TABLE IF NOT EXISTS events (
                tenant_id String,
                user_id String,
                session_id String,
                event String,
                ts DateTime,
                url String,
                ref String,
                utm_source String,
                utm_medium String,
                utm_campaign String,
                revenue Float64,
                properties String
            ) ENGINE = MergeTree()
            ORDER BY (tenant_id, session_id, ts)
        """)
        logger.info("Events table ready")

    except Exception as e:
        logger.error(f"Failed to connect to ClickHouse: {e}")


@app.get("/health")
async def health_check():
    """Health check."""
    return {
        "status": "healthy",
        "clickhouse": ch_client is not None,
    }


@app.post("/collect")
async def collect_event(event: Event, bg: BackgroundTasks):
    """Collect tracking event."""
    # Set timestamp if not provided
    if not event.ts:
        event.ts = datetime.utcnow().isoformat()

    # Write event to ClickHouse in background
    bg.add_task(write_event, event)

    return {"ok": True, "event": event.event}


def write_event(event: Event):
    """Write event to ClickHouse."""
    if not ch_client:
        logger.error("ClickHouse client not initialized")
        return

    try:
        ch_client.insert(
            "events",
            [[
                event.tenant_id,
                event.user_id or "",
                event.sid,
                event.event,
                event.ts,
                event.url or "",
                event.ref or "",
                event.utm_source or "",
                event.utm_medium or "",
                event.utm_campaign or "",
                event.value,
                json.dumps(event.props),
            ]],
            column_names=[
                "tenant_id", "user_id", "session_id", "event", "ts",
                "url", "ref", "utm_source", "utm_medium", "utm_campaign",
                "revenue", "properties"
            ],
        )
        logger.info(f"Event written: {event.event} for session {event.sid}")
    except Exception as e:
        logger.error(f"Failed to write event: {e}")


@app.get("/paths")
async def get_attribution_paths(
    tenant_id: str = "t0",
    session_id: Optional[str] = None,
    model: str = "last_touch",
    limit: int = 100,
):
    """Get attribution paths for sessions."""
    if not ch_client:
        return {"error": "ClickHouse not available"}

    try:
        # Build query
        query = """
            SELECT
                session_id,
                groupArray(event) as events,
                groupArray(utm_source) as sources,
                groupArray(utm_campaign) as campaigns,
                sum(revenue) as total_revenue
            FROM events
            WHERE tenant_id = {tenant_id:String}
        """

        params = {"tenant_id": tenant_id}

        if session_id:
            query += " AND session_id = {session_id:String}"
            params["session_id"] = session_id

        query += """
            GROUP BY session_id
            HAVING total_revenue > 0
            ORDER BY total_revenue DESC
            LIMIT {limit:UInt32}
        """
        params["limit"] = limit

        result = ch_client.query(query, parameters=params)

        # Process results into attribution paths
        paths = []
        for row in result.result_rows:
            sid, events, sources, campaigns, revenue = row

            # Apply attribution model
            touchpoints = []
            for i, event in enumerate(events):
                if sources[i]:  # Only include touchpoints with UTM data
                    touchpoints.append({
                        "source": sources[i],
                        "campaign": campaigns[i],
                        "event": event,
                    })

            if touchpoints:
                # Calculate attribution based on model
                attribution = calculate_attribution(touchpoints, revenue, model)

                paths.append({
                    "session_id": sid,
                    "touchpoints": touchpoints,
                    "total_revenue": revenue,
                    "attribution": attribution,
                    "model": model,
                })

        return {"paths": paths}

    except Exception as e:
        logger.error(f"Failed to get attribution paths: {e}")
        return {"error": str(e)}


def calculate_attribution(touchpoints: List[Dict], revenue: float, model: str) -> Dict:
    """Calculate attribution based on model."""
    num_touchpoints = len(touchpoints)

    if num_touchpoints == 0:
        return {}

    attribution = {}

    if model == "last_touch":
        # 100% to last touchpoint
        last = touchpoints[-1]
        key = f"{last['source']}_{last['campaign']}"
        attribution[key] = revenue

    elif model == "first_touch":
        # 100% to first touchpoint
        first = touchpoints[0]
        key = f"{first['source']}_{first['campaign']}"
        attribution[key] = revenue

    elif model == "linear":
        # Equal distribution
        value_per_touch = revenue / num_touchpoints
        for tp in touchpoints:
            key = f"{tp['source']}_{tp['campaign']}"
            attribution[key] = attribution.get(key, 0) + value_per_touch

    elif model == "position_based":
        # 40% first, 40% last, 20% distributed to middle
        if num_touchpoints == 1:
            key = f"{touchpoints[0]['source']}_{touchpoints[0]['campaign']}"
            attribution[key] = revenue
        elif num_touchpoints == 2:
            for tp in touchpoints:
                key = f"{tp['source']}_{tp['campaign']}"
                attribution[key] = revenue * 0.5
        else:
            # First 40%
            first = touchpoints[0]
            key_first = f"{first['source']}_{first['campaign']}"
            attribution[key_first] = revenue * 0.4

            # Last 40%
            last = touchpoints[-1]
            key_last = f"{last['source']}_{last['campaign']}"
            attribution[key_last] = attribution.get(key_last, 0) + revenue * 0.4

            # Middle 20% distributed
            middle_value = revenue * 0.2 / (num_touchpoints - 2)
            for tp in touchpoints[1:-1]:
                key = f"{tp['source']}_{tp['campaign']}"
                attribution[key] = attribution.get(key, 0) + middle_value

    else:
        # Default to last touch
        last = touchpoints[-1]
        key = f"{last['source']}_{last['campaign']}"
        attribution[key] = revenue

    return attribution


@app.get("/pixel.js")
async def get_tracking_pixel():
    """Return tracking pixel JavaScript."""
    js_code = """
(function(){
  const sid = localStorage.getItem('am_sid') || crypto.randomUUID();
  localStorage.setItem('am_sid', sid);

  function send(ev, props={}){
    const body = {
      event: ev,
      ts: new Date().toISOString(),
      url: location.href,
      ref: document.referrer,
      sid: sid,
      utm_source: new URLSearchParams(location.search).get('utm_source'),
      utm_medium: new URLSearchParams(location.search).get('utm_medium'),
      utm_campaign: new URLSearchParams(location.search).get('utm_campaign'),
      props: props
    };

    navigator.sendBeacon('ATTRIBUTION_URL/collect', JSON.stringify(body));
  }

  window.AgenticTrack = {send};
  send('pageview');
})();
    """.replace("ATTRIBUTION_URL", "http://localhost:8085")

    return js_code


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8085, reload=True)
