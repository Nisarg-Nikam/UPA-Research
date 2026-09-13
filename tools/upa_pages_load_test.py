import concurrent.futures
import ssl
import time
import urllib.request
from collections import Counter

URL = "https://upa-research.pages.dev/"
LEVELS = [64, 256, 512, 1024]
TIMEOUT = 30

# Reuse one SSL context for the test.
SSL_CONTEXT = ssl.create_default_context()

def fetch(_):
    start = time.perf_counter()
    try:
        req = urllib.request.Request(
            URL,
            headers={"User-Agent": "UPA-Research-load-test/1.0"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=SSL_CONTEXT) as response:
            # Read the response so the request is completed.
            response.read()
            elapsed = time.perf_counter() - start
            return response.status, elapsed, None
    except Exception as exc:
        elapsed = time.perf_counter() - start
        return None, elapsed, repr(exc)

def run_level(concurrency):
    print(f"\n{'=' * 60}")
    print(f"Testing {concurrency} concurrent homepage requests")
    print(f"Target: {URL}")
    print(f"{'=' * 60}")

    start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        results = list(pool.map(fetch, range(concurrency)))

    total = time.perf_counter() - start

    statuses = Counter(r[0] for r in results)
    failures = [r for r in results if r[0] is None]
    times = [r[1] for r in results]

    print(f"Total time       : {total:.3f} sec")
    print(f"Completed        : {len(results)}")
    print(f"Successful       : {len(results) - len(failures)}")
    print(f"Failed           : {len(failures)}")
    print(f"Approx. req/sec  : {concurrency / total:.2f}")
    print(f"Min response     : {min(times):.3f} sec")
    print(f"Max response     : {max(times):.3f} sec")
    print(f"Avg response     : {sum(times) / len(times):.3f} sec")
    print(f"HTTP statuses    : {dict(statuses)}")

    if failures:
        print("\nFirst 10 failures:")
        for _, elapsed, error in failures[:10]:
            print(f"  {elapsed:.3f}s  {error}")

def main():
    print("UPA Research Cloudflare Pages load test")
    print("SAFE MODE: tests the homepage only; does NOT call /api/visitors.")
    print("This test does not modify the website or visitor counter.")

    for level in LEVELS:
        run_level(level)

    print("\nLoad test complete.")
    print("Note: this measures requests generated from this computer/network,")
    print("not 1,024 real human visitors or 1,024 browser sessions.")

if __name__ == "__main__":
    main()
