
import statistics
import time

import requests

URL = "http://127.0.0.1:8000/chat"

SAMPLES = [
    "What is the refund policy for a damaged product?",
    "Can you explain the charges on my latest invoice?",
    "How can I check my order status?",
    "I need help with a damaged product.",
    "What is the warranty policy for a product never purchased from your company?",
]

latencies = []

for i, question in enumerate(SAMPLES, start=1):
    payload = {
        "message": question,
        "session_id": f"benchmark_session_{i}",
        "customer_id": "benchmark_customer",
    }

    start = time.perf_counter()

    try:
        response = requests.post(
            URL,
            json=payload,
            timeout=120,
        )
        elapsed = time.perf_counter() - start

        if response.status_code == 200:
            latencies.append(elapsed)
            print(f"Test {i}: {elapsed:.3f}s | HTTP {response.status_code}")
        else:
            print(f"Test {i}: HTTP {response.status_code}")
            print(response.text[:500])

    except requests.RequestException as exc:
        print(f"Test {i}: Request failed: {exc}")

if latencies:
    print("\n--- Latency Summary ---")
    print(f"Successful requests: {len(latencies)}")
    print(f"Average: {statistics.mean(latencies):.3f}s")
    print(f"Median: {statistics.median(latencies):.3f}s")

    if len(latencies) >= 2:
        print(f"Minimum: {min(latencies):.3f}s")
        print(f"Maximum: {max(latencies):.3f}s")
