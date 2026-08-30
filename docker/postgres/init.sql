-- ==========================================
-- NetSentinel Database Initialization
-- Week 12
-- ==========================================

-- Network performance test results
CREATE TABLE IF NOT EXISTS performance_results (
    id SERIAL PRIMARY KEY,
    test_type VARCHAR(50) NOT NULL,
    average_latency_ms DOUBLE PRECISION,
    p95_latency_ms DOUBLE PRECISION,
    total_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    packet_loss_percent DOUBLE PRECISION DEFAULT 0,
    error_rate_percent DOUBLE PRECISION DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Postman API test results
CREATE TABLE IF NOT EXISTS postman_results (
    id SERIAL PRIMARY KEY,
    total_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    total_assertions INTEGER DEFAULT 0,
    failed_assertions INTEGER DEFAULT 0,
    average_response_time_ms DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Network connectivity results
CREATE TABLE IF NOT EXISTS network_connectivity (
    id SERIAL PRIMARY KEY,
    source VARCHAR(255),
    destination VARCHAR(255),
    status VARCHAR(50),
    latency_ms DOUBLE PRECISION,
    packet_loss_percent DOUBLE PRECISION DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI generated reports
CREATE TABLE IF NOT EXISTS ai_reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL,
    report_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test execution history
CREATE TABLE IF NOT EXISTS test_runs (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(100) NOT NULL,
    test_type VARCHAR(50),
    status VARCHAR(50),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for frequently queried timestamps
CREATE INDEX IF NOT EXISTS idx_performance_results_created_at
    ON performance_results(created_at);

CREATE INDEX IF NOT EXISTS idx_postman_results_created_at
    ON postman_results(created_at);

CREATE INDEX IF NOT EXISTS idx_network_connectivity_created_at
    ON network_connectivity(created_at);

CREATE INDEX IF NOT EXISTS idx_ai_reports_created_at
    ON ai_reports(created_at);

CREATE INDEX IF NOT EXISTS idx_test_runs_created_at
    ON test_runs(created_at);
