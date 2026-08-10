import redis
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from rq import Queue
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()

redis_client = redis.Redis(
    host="tremendous-lustrous-bells-23906.db.redis.io",
    port=16851,
    password="UDpw3WAw3lUzFIkQV62r1kCGPft5klXD",
    decode_responses=True
)

# Separate raw connection for RQ (no decode_responses — RQ needs raw bytes for job serialization)
rq_redis_conn = redis.Redis(
    host="tremendous-lustrous-bells-23906.db.redis.io",
    port=16851,
    password="UDpw3WAw3lUzFIkQV62r1kCGPft5klXD"
)

task_queue = Queue(connection=rq_redis_conn)

limiter = Limiter(
    key_func=get_remote_address
)

socketio = SocketIO(cors_allowed_origins="*")