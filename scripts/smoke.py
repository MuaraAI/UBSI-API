#!/usr/bin/env python3
"""UBSI API — Live Smoke Test CLI.

Usage:
  python scripts/smoke.py [--base-url http://127.0.0.1:8300]
"""
import argparse
import sys
import time
from typing import Any

import requests

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def run_check(name: str, url: str, check_fn) -> bool:
    t0 = time.time()
    try:
        r = requests.get(url, timeout=15)
        elapsed = (time.time() - t0) * 1000
        ok, detail = check_fn(r)
        if ok:
            print(f" {GREEN}✓{RESET} {BOLD}{name:25s}{RESET} [{r.status_code}] ({elapsed:5.1f}ms) — {detail}")
            return True
        else:
            print(f" {RED}✗{RESET} {BOLD}{name:25s}{RESET} [{r.status_code}] ({elapsed:5.1f}ms) — {RED}FAILED{RESET}: {detail}")
            return False
    except Exception as e:
        elapsed = (time.time() - t0) * 1000
        print(f" {RED}✗{RESET} {BOLD}{name:25s}{RESET} [ERR] ({elapsed:5.1f}ms) — {RED}ERROR{RESET}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Live Smoke Test for UBSI API")
    parser.add_argument("--base-url", default="http://127.0.0.1:8300", help="Base URL of UBSI API")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    print(f"\n{BOLD}=== UBSI API Live Smoke Test ==={RESET}")
    print(f"Target: {base}\n")

    results = []

    # 1. Health
    def check_health(r):
        if r.status_code != 200:
            return False, f"Expected 200, got {r.status_code}"
        data = r.json()
        if data.get("status") == "ok":
            return True, f"status=ok, redis={data.get('redis')}"
        return False, f"Unexpected body: {data}"

    results.append(run_check("Health Check", f"{base}/health", check_health))

    # 2. News
    def check_news(r):
        if r.status_code != 200:
            return False, f"status={r.status_code}"
        body = r.json()
        if body.get("success") and isinstance(body.get("data"), list):
            return True, f"{len(body['data'])} posts"
        return False, "success is False or data not list"

    results.append(run_check("News Posts", f"{base}/v1/news?page=1&per_page=3", check_news))

    # 3. Elibrary Search
    def check_elibrary(r):
        if r.status_code != 200:
            return False, f"status={r.status_code}"
        body = r.json()
        if body.get("success") and "total_count" in body.get("data", {}):
            return True, f"total={body['data']['total_count']}, items={len(body['data']['items'])}"
        return False, "invalid elibrary envelope"

    results.append(run_check("Elibrary Search", f"{base}/v1/elibrary/search?q=algoritma", check_elibrary))

    # 4. Repository
    def check_repo(r):
        if r.status_code != 200:
            return False, f"status={r.status_code}"
        body = r.json()
        if body.get("success") and isinstance(body.get("data"), list):
            return True, f"{len(body['data'])} recent items"
        return False, "invalid repository envelope"

    results.append(run_check("Repository Recent", f"{base}/v1/repository/recent", check_repo))

    # 5. EJournal
    def check_ejournal(r):
        if r.status_code != 200:
            return False, f"status={r.status_code}"
        body = r.json()
        if body.get("success") and isinstance(body.get("data"), list):
            return True, f"{len(body['data'])} journals in catalog"
        return False, "invalid ejournal envelope"

    results.append(run_check("EJournal Catalog", f"{base}/v1/ejournal/journals", check_ejournal))

    # 6. StudentV2 (Private)
    def check_studentv2(r):
        if r.status_code == 200:
            body = r.json()
            return True, f"{len(body.get('data', []))} schedule courses"
        if r.status_code == 400 and r.json().get("error", {}).get("code") == "CONFIG_MISSING":
            return True, "config missing (expected when env empty)"
        return False, f"status={r.status_code}, error={r.json().get('error')}"

    results.append(run_check("StudentV2 Schedule", f"{base}/v1/studentv2/schedule", check_studentv2))

    # 7. Elearning (Private)
    def check_elearning(r):
        if r.status_code == 200:
            body = r.json()
            return True, f"{len(body.get('data', []))} LMS courses"
        if r.status_code == 400 and r.json().get("error", {}).get("code") == "CONFIG_MISSING":
            return True, "config missing (expected when env empty)"
        return False, f"status={r.status_code}, error={r.json().get('error')}"

    results.append(run_check("Elearning Courses", f"{base}/v1/elearning/courses", check_elearning))

    total = len(results)
    passed = sum(1 for r in results if r)
    print(f"\n{BOLD}Result: {passed}/{total} passed.{RESET}")
    if passed == total:
        print(f"{GREEN}{BOLD}All Smoke Tests PASSED!{RESET}\n")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}Some Smoke Tests FAILED!{RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
