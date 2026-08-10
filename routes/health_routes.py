from flask import Blueprint, jsonify
from extensions import db, redis_client
from sqlalchemy import text
import time

health_bp = Blueprint('health', __name__)


@health_bp.route('/healthz')
def healthz():
    """Liveness check - is the app process alive?"""
    return jsonify({"status": "ok"}), 200


@health_bp.route('/readyz')
def readyz():
    """Readiness check - can the app serve traffic? Probes dependencies."""
    checks = {}
    overall_ok = True

    # --- Database check ---
    try:
        db.session.execute(text('SELECT 1'))
        checks['database'] = {"status": "ok"}
    except Exception as e:
        checks['database'] = {"status": "error", "detail": str(e)}
        overall_ok = False

    # --- Redis check (latency measured) ---
    try:
        start = time.time()
        redis_client.ping()
        latency_ms = round((time.time() - start) * 1000, 2)
        checks['redis'] = {"status": "ok", "latency_ms": latency_ms}
    except Exception as e:
        checks['redis'] = {"status": "error", "detail": str(e)}
        overall_ok = False

    status_code = 200 if overall_ok else 503
    return jsonify({
        "status": "ok" if overall_ok else "degraded",
        "checks": checks
    }), status_code