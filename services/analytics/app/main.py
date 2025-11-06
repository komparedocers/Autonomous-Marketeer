"""Analytics Service for metrics and reporting."""
from fastapi import FastAPI
from typing import Optional
import clickhouse_connect
import logging
import os
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "analytics")

# Create FastAPI app
app = FastAPI(title="Analytics Service")

# ClickHouse client
ch_client = None


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
    except Exception as e:
        logger.error(f"Failed to connect to ClickHouse: {e}")


@app.get("/health")
async def health_check():
    """Health check."""
    return {
        "status": "healthy",
        "clickhouse": ch_client is not None,
    }


@app.get("/timeseries")
async def get_timeseries(
    tenant_id: str = "t0",
    metric: str = "impressions",
    granularity: str = "d",  # h=hour, d=day, w=week
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Get timeseries data for a metric."""
    if not ch_client:
        return {"error": "ClickHouse not available"}

    # Default to last 7 days
    if not end_date:
        end_date = datetime.utcnow().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

    # Map granularity to ClickHouse interval
    interval_map = {
        "h": "toStartOfHour(ts)",
        "d": "toDate(ts)",
        "w": "toMonday(ts)",
    }
    interval_func = interval_map.get(granularity, "toDate(ts)")

    try:
        # Build query based on metric
        if metric == "revenue":
            query = f"""
                SELECT
                    {interval_func} as period,
                    sum(revenue) as value
                FROM events
                WHERE tenant_id = {{tenant_id:String}}
                  AND ts >= {{start_date:String}}
                  AND ts <= {{end_date:String}}
                GROUP BY period
                ORDER BY period
            """
        else:
            # Count events
            query = f"""
                SELECT
                    {interval_func} as period,
                    count() as value
                FROM events
                WHERE tenant_id = {{tenant_id:String}}
                  AND ts >= {{start_date:String}}
                  AND ts <= {{end_date:String}}
                  AND event = {{event:String}}
                GROUP BY period
                ORDER BY period
            """

        params = {
            "tenant_id": tenant_id,
            "start_date": start_date,
            "end_date": end_date,
        }

        if metric != "revenue":
            # Map metric to event name
            event_map = {
                "impressions": "impression",
                "clicks": "click",
                "conversions": "conversion",
                "pageviews": "pageview",
            }
            params["event"] = event_map.get(metric, "pageview")

        result = ch_client.query(query, parameters=params)

        data = [
            {"period": str(row[0]), "value": float(row[1])}
            for row in result.result_rows
        ]

        return {
            "metric": metric,
            "granularity": granularity,
            "data": data,
        }

    except Exception as e:
        logger.error(f"Timeseries query failed: {e}")
        return {"error": str(e)}


@app.get("/funnel")
async def get_funnel(
    tenant_id: str = "t0",
    steps: str = "pageview,click,conversion",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Get funnel analysis."""
    if not ch_client:
        return {"error": "ClickHouse not available"}

    # Default to last 30 days
    if not end_date:
        end_date = datetime.utcnow().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

    step_list = steps.split(",")

    try:
        funnel_data = []

        for i, step in enumerate(step_list):
            # Count unique sessions that reached this step
            query = """
                SELECT
                    count(DISTINCT session_id) as count
                FROM events
                WHERE tenant_id = {tenant_id:String}
                  AND ts >= {start_date:String}
                  AND ts <= {end_date:String}
                  AND event = {event:String}
            """

            params = {
                "tenant_id": tenant_id,
                "start_date": start_date,
                "end_date": end_date,
                "event": step.strip(),
            }

            result = ch_client.query(query, parameters=params)
            count = result.result_rows[0][0] if result.result_rows else 0

            # Calculate conversion rate from previous step
            conversion_rate = 100.0
            if i > 0 and funnel_data[i - 1]["count"] > 0:
                conversion_rate = (count / funnel_data[i - 1]["count"]) * 100

            funnel_data.append({
                "step": step.strip(),
                "count": count,
                "conversion_rate": round(conversion_rate, 2),
            })

        return {
            "funnel": funnel_data,
            "start_date": start_date,
            "end_date": end_date,
        }

    except Exception as e:
        logger.error(f"Funnel query failed: {e}")
        return {"error": str(e)}


@app.get("/summary")
async def get_summary(
    tenant_id: str = "t0",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Get summary metrics."""
    if not ch_client:
        return {"error": "ClickHouse not available"}

    # Default to last 7 days
    if not end_date:
        end_date = datetime.utcnow().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

    try:
        query = """
            SELECT
                countIf(event = 'pageview') as pageviews,
                countIf(event = 'click') as clicks,
                countIf(event = 'conversion') as conversions,
                sum(revenue) as revenue,
                count(DISTINCT session_id) as sessions,
                count(DISTINCT user_id) as users
            FROM events
            WHERE tenant_id = {tenant_id:String}
              AND ts >= {start_date:String}
              AND ts <= {end_date:String}
        """

        params = {
            "tenant_id": tenant_id,
            "start_date": start_date,
            "end_date": end_date,
        }

        result = ch_client.query(query, parameters=params)

        if result.result_rows:
            pageviews, clicks, conversions, revenue, sessions, users = result.result_rows[0]

            return {
                "pageviews": pageviews,
                "clicks": clicks,
                "conversions": conversions,
                "revenue": float(revenue),
                "sessions": sessions,
                "users": users,
                "ctr": round((clicks / max(pageviews, 1)) * 100, 2),
                "cvr": round((conversions / max(clicks, 1)) * 100, 2),
                "start_date": start_date,
                "end_date": end_date,
            }
        else:
            return {"error": "No data found"}

    except Exception as e:
        logger.error(f"Summary query failed: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8086, reload=True)
