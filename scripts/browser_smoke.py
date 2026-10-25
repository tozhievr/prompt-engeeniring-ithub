#!/usr/bin/env python3
"""Chromium smoke test for each published app, including JS errors."""
import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="dist")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    projects = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    failures = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"])
            for item in [{"slug": "gallery", "url": "./"}] + projects:
                page = browser.new_page(viewport={"width": 1366, "height": 768})
                errors = []
                page.on("pageerror", lambda err: errors.append(str(err)))
                url = f"http://127.0.0.1:{server.server_port}/{item['url'].removeprefix('./')}"
                try:
                    response = page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    page.wait_for_timeout(2500)
                    if response is None or response.status >= 400:
                        errors.append(f"HTTP {response.status if response else 'no response'}")
                    if not page.title():
                        errors.append("missing document title")
                    if errors:
                        failures.append(f"{item['slug']}: " + "; ".join(errors))
                    else:
                        print(f"PASS {item['slug']}")
                except Exception as exc:
                    failures.append(f"{item['slug']}: {exc}")
                finally:
                    page.close()
            browser.close()
    finally:
        server.shutdown()
    if failures:
        print("\n".join(failures))
        raise SystemExit(1)
    print("Browser smoke tests passed.")

if __name__ == "__main__":
    main()
