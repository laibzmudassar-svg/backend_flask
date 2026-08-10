import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger


def configure_logging(app):
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )

    # --- stdout handler (console / log forwarding) ---
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # --- rotating file handler (prevents disk space exhaustion) ---
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=1_000_000,   # 1 MB per file
        backupCount=5         # keep last 5 rotated files
    )
    file_handler.setFormatter(formatter)

    app.logger.handlers = []
    app.logger.addHandler(stream_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    return app.logger