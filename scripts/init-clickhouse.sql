-- ClickHouse initialization script
-- Creates the events table for analytics

CREATE TABLE IF NOT EXISTS analytics.events (
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
PARTITION BY toYYYYMM(ts)
TTL ts + INTERVAL 400 DAY;

-- Create materialized view for hourly aggregations
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.events_hourly
ENGINE = SummingMergeTree()
ORDER BY (tenant_id, event, hour)
AS SELECT
    tenant_id,
    event,
    toStartOfHour(ts) as hour,
    count() as event_count,
    sum(revenue) as total_revenue
FROM analytics.events
GROUP BY tenant_id, event, hour;
