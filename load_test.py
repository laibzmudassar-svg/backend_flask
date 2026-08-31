import requests
import concurrent.futures
import time

BASE_URL = "http://127.0.0.1:5000"

def send_request(i):
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/")
        duration = round((time.time() - start) * 1000, 2)
        correlation_id = response.headers.get("X-Correlation-ID", "N/A")
        print(f"Request {i}: status={response.status_code}, time={duration}ms, correlation_id={correlation_id}")
        return response.status_code
    except Exception as e:
        print(f"Request {i}: FAILED - {e}")
        return None

if __name__ == "__main__":
    NUM_REQUESTS = 30
    CONCURRENCY = 10

    print(f"Sending {NUM_REQUESTS} requests with concurrency={CONCURRENCY}...")
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        results = list(executor.map(send_request, range(NUM_REQUESTS)))

    total_time = round(time.time() - start_time, 2)
    success_count = sum(1 for r in results if r == 200)

    print(f"\nDone in {total_time}s - {success_count}/{NUM_REQUESTS} succeeded")
