from app.ml import pipeline


def _rows_for_metric(name: str, values: list[float]):
    rows = []
    for idx, value in enumerate(values, start=1):
        rows.append({"metric_name": name, "metric_value": value, "rn": idx})
    return rows


def test_build_aligned_samples_requires_multiple_metrics():
    rows = _rows_for_metric("response_latency", [100.0] * 80)
    result = pipeline._build_aligned_samples(rows, min_points=50, window_size=100)
    assert result["ok"] is False
    assert result["reason"] == "not-enough-metrics"


def test_build_aligned_samples_requires_min_points():
    rows = _rows_for_metric("response_latency", [100.0] * 40) + _rows_for_metric("cpu", [80.0] * 40)
    result = pipeline._build_aligned_samples(rows, min_points=50, window_size=100)
    assert result["ok"] is False
    assert result["reason"] == "insufficient-points"
    assert result["points"] == 40


def test_build_aligned_samples_success_aligns_ranks():
    rows = _rows_for_metric("response_latency", [100.0] * 60) + _rows_for_metric("cpu", [80.0] * 60)
    result = pipeline._build_aligned_samples(rows, min_points=50, window_size=100)
    assert result["ok"] is True
    assert result["points"] == 60
    assert result["feature_names"] == ["response_latency", "cpu"]
    assert len(result["samples"]) == 60
    assert len(result["samples"][0]) == 2


def test_parse_level_and_message_handles_error_level():
    level, message = pipeline._parse_level_and_message(
        "Level: ERROR\nService is degraded.\nAction: Investigate logs."
    )
    assert level == "ERROR"
    assert message.startswith("Service is degraded.")


def test_parse_level_and_message_defaults_to_warning():
    level, message = pipeline._parse_level_and_message("Unexpected format")
    assert level == "WARNING"
    assert "Unexpected format" in message


def test_fallback_anomaly_message_contains_level_and_action():
    level, message = pipeline._fallback_anomaly_message(
        {
            "latest": {"score": -0.7},
            "top_features": [{"name": "cpu", "value": 99.1}],
        }
    )
    assert level == "ERROR"
    assert "abnormal behavior" in message
    assert "Action:" in message


def test_is_valid_llm_message_rejects_truncated_output():
    assert pipeline._is_valid_llm_message("Service") is False
    assert (
        pipeline._is_valid_llm_message(
            "Performance deviation observed.\nAction: Run a health check."
        )
        is True
    )


def test_apply_level_gates_downgrades_error_when_points_under_50():
    level, message = pipeline._apply_level_gates(
        "ERROR",
        "Clear abnormal behavior detected.\nAction: Check logs.",
        {"points_used": 22, "anomaly_count": 2},
    )
    assert level == "WARNING"
    assert "abnormal behavior" in message
    assert "fewer than 50 data points" in message


def test_apply_level_gates_forces_info_when_points_under_20():
    level, message = pipeline._apply_level_gates(
        "WARNING",
        "Unusual behavior detected.\nAction: Check metrics.",
        {"points_used": 12, "anomaly_count": 3},
    )
    assert level == "INFO"
    assert "Unusual behavior detected." in message
    assert "fewer than 20 data points" in message


def test_apply_level_gates_requires_persistence_for_error():
    level, message = pipeline._apply_level_gates(
        "ERROR",
        "Clear abnormal behavior detected.\nAction: Check logs.",
        {"points_used": 80, "anomaly_count": 1},
    )
    assert level == "WARNING"
    assert "Clear abnormal behavior detected." in message
    assert "waiting for persistence" in message
