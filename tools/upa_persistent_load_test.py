import argparse, http.client, ssl, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlsplit

URL = "https://upa-research.pages.dev/"
LEVELS = [64, 256, 512, 1024]

def client(url, n, timeout):
    u = urlsplit(url)
    conn = http.client.HTTPSConnection(u.hostname, u.port or 443,
                                       timeout=timeout,
                                       context=ssl.create_default_context())
    out = []
    try:
        for _ in range(n):
            t = time.perf_counter()
            conn.request("GET", u.path or "/", headers={
                "Connection": "keep-alive",
                "User-Agent": "UPA-Research-Persistent-Load-Test/1.0",
            })
            r = conn.getresponse()
            r.read()
            out.append((r.status, time.perf_counter()-t, None))
    except Exception as e:
        out.append((None, time.perf_counter()-t, repr(e)))
    finally:
        conn.close()
    return out

def run(url, concurrency, per_client, timeout):
    t0 = time.perf_counter()
    rows = []
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        fs = [ex.submit(client, url, per_client, timeout)
              for _ in range(concurrency)]
        for f in as_completed(fs):
            rows.extend(f.result())
    elapsed = time.perf_counter()-t0
    ok = [x for x in rows if x[0] == 200]
    bad = [x for x in rows if x[0] != 200]
    lat = [x[1] for x in rows]
    print(f"\n{concurrency} persistent clients x {per_client} requests")
    print("-"*60)
    print(f"Total requests : {len(rows)}")
    print(f"HTTP 200       : {len(ok)}")
    print(f"Failures       : {len(bad)}")
    print(f"Total time     : {elapsed:.3f} sec")
    print(f"Throughput     : {len(rows)/elapsed:.2f} req/s")
    print(f"Min latency    : {min(lat):.3f} sec")
    print(f"Max latency    : {max(lat):.3f} sec")
    print(f"Avg latency    : {sum(lat)/len(lat):.3f} sec")
    if bad:
        print("Sample failures:")
        for s, dt, e in bad[:5]:
            print(f"  {s} after {dt:.3f}s: {e}")

ap = argparse.ArgumentParser()
ap.add_argument("--url", default=URL)
ap.add_argument("--requests-per-client", type=int, default=3)
ap.add_argument("--timeout", type=float, default=30)
a = ap.parse_args()

print("="*60)
print("UPA Research - Persistent HTTP Load Test")
print("="*60)
print("Homepage only; /api/visitors is NOT called.")
print("All connections originate from this one machine/network.")
for level in LEVELS:
    run(a.url, level, a.requests_per_client, a.timeout)
