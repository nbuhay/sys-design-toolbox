"""
Token Bucket Rate Limiter V1

This is a simple implementation of the token bucket algorithm for rate limiting
as a Python Flask app.

Usage:
- GET /healthcheck - Returns a simple healthcheck and svc uptime
- GET /verify - Returns back number requests remaining for the IPV4 client
"""
import datetime
import threading
import time
from dataclasses import dataclass
import psutil
import redis
from flask import Flask, request, make_response


@dataclass
class ResData:
    """Data used to create rate limiter response"""

    msg: str = ""
    code: int = 200


app = Flask(__name__)


# Create a Redis connection pool
redis_pool = redis.ConnectionPool(
    host="localhost", port=6379, db=0, decode_responses=True
)

# Initialize a Redis client instance using the connection pool
redis_client = redis.Redis(connection_pool=redis_pool)


def reset_all_client_limits():
    """Delete all keys in the current Redis database - resets all tokens to max"""
    redis_client.flushdb()


def start_scheduler():
    """Start token reset process. Run every WAIT_TIME seconds"""
    wait_time = 60
    while True:
        time.sleep(wait_time)

        with app.app_context():
            reset_all_client_limits()


# max connections
RATE_LIMIT = 4

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=start_scheduler)
scheduler_thread.start()


@app.route("/health")
def healthcheck():
    """healthcheck api endpoint

    Returns:
        flask.wrappers.Response: 200 when API is available
    """
    process = psutil.Process()
    start_time = datetime.datetime.fromtimestamp(process.create_time())
    uptime = datetime.datetime.now() - start_time
    res = make_response({"uptime": uptime.total_seconds()})
    print(type(res))
    return res


@app.route("/verify")
def verify():
    """check client has remaining tokens to process request

    Returns:
        flask.wrappers.Response: 200 when client has avaiable tokens, else 429
    """
    client_ip = request.remote_addr
    res_data = ResData()

    if redis_client.exists(client_ip):
        # already has made requests
        client_curr_cnt = int(redis_client.get(client_ip))
        if client_curr_cnt == 0:
            # reached max reqeusts
            res_data.msg = "rate limit reached"
            res_data.code = 429
        else:
            redis_client.decr(client_ip)
            res_data.msg = client_curr_cnt - 1
    else:
        # rate_limit-1 coz this request will count towards the limit
        redis_client.set(client_ip, RATE_LIMIT - 1)
        res_data.msg = RATE_LIMIT - 1

    remaining_reqs = redis_client.get(client_ip)
    res = make_response({"message": res_data.msg})
    res.headers["X-RateLimit-Limit"] = RATE_LIMIT
    res.headers["X-RateLimit-Remaining"] = remaining_reqs
    res.status_code = res_data.code
    return res


if __name__ == "__main__":
    app.run()
