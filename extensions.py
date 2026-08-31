import os
import redis
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from rq import Queue
from flask_socketio import SocketIO

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# Separate raw connection for RQ (no decode_responses — RQ needs raw bytes for job serialization)
rq_redis_conn = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD
)

task_queue = Queue(connection=rq_redis_conn)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
)

socketio = SocketIO(cors_allowed_origins="*")