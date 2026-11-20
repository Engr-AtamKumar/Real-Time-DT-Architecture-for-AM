CREATE EXTENSION IF NOT EXISTS timescaledb;

-- One row per telemetry event received through MQTT -> Node-RED.
-- t_pub  : publish time at the replay client (epoch seconds)
-- t_nr   : time Node-RED received the message (epoch seconds)
-- t_db   : time the row was written in the database (clock_timestamp)
-- t_orig : original acquisition time of the event in the 2023 recording (epoch seconds)
CREATE TABLE telemetry (
    time        TIMESTAMPTZ      NOT NULL,
    run_id      TEXT             NOT NULL,
    printer_id  INTEGER          NOT NULL,
    seq         BIGINT           NOT NULL,
    t_orig      DOUBLE PRECISION,
    t_pub       DOUBLE PRECISION,
    t_nr        DOUBLE PRECISION,
    t_db        TIMESTAMPTZ      NOT NULL DEFAULT clock_timestamp(),
    t_hotend    DOUBLE PRECISION,
    t_hotend_sp DOUBLE PRECISION,
    t_bed       DOUBLE PRECISION,
    p_hotend    DOUBLE PRECISION,
    p_bed       DOUBLE PRECISION,
    z           DOUBLE PRECISION,
    e           DOUBLE PRECISION,
    payload     JSONB
);
SELECT create_hypertable('telemetry', 'time', chunk_time_interval => INTERVAL '1 hour');
CREATE INDEX ON telemetry (run_id, printer_id, time DESC);
