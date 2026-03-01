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
