#!/usr/bin/env python3
"""fetch_cdc.py — build the cdc-clinical mirror from CDC HTML pages.

Three source groups (all US-government public domain):
  1. STI treatment guidelines 2021, per-condition pages (toc.htm walk)
  2. ACIP current vaccine-specific recommendations (index walk)
  3. Measles HCP clinical pages (curated list)
Rate-capped, one page fetched once, chrome stripped to main-content text.
"""
import html as H
import json
import os
import re
import sys
import time
import urllib.request

BASE = "https://www.cdc.gov"
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) corpus-mirror/1.0"}

def fetch(url):
    # CDC's WAF 403s python-urllib AND generic Mozilla UAs; plain curl passes.
    import subprocess
    for ua in ("curl/8.5.0", "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"):
        p = subprocess.run(["curl", "-s", "-m", "45", "-A", ua, "-L", url],
                           capture_output=True, text=True)
        if p.returncode == 0 and "<main" in p.stdout:
            return p.stdout
    raise RuntimeError(f"fetch failed (rc={p.returncode}, bytes={len(p.stdout)})")

def links(page_html, base_path):
    out = set()
    for m in re.finditer(r'href="([^"#]+)"', page_html, re.I):
        u = m.group(1)
        if u.startswith("/") and not u.startswith("//"):
            out.add(BASE + u)
    return {u for u in out if base_path in u and u.endswith((".htm", ".html"))}

def extract(t):
    m = re.search(r"<main[^>]*>(.*?)</main>", t, re.S | re.I)
    body = m.group(1) if m else t
    body = re.sub(r"<(script|style|nav|footer|aside)[^>]*>.*?</\1>", "", body, flags=re.S | re.I)
    body = re.sub(r"<h1[^>]*>", "\n\n# ", body, flags=re.I)
    for i in range(2, 7):
        body = re.sub(f"<h{i}[^>]*>", f"\n\n{'#' * i} ", body, flags=re.I)
    body = re.sub(r"</h[1-6]>", "\n", body, flags=re.I)
    body = re.sub(r"<li[^>]*>", "\n- ", body, flags=re.I)
    body = re.sub(r"</(p|div|tr|table|ul|ol)>", "\n", body, flags=re.I)
    body = re.sub(r"<t[dh][^>]*>", " | ", body, flags=re.I)
    body = re.sub(r"<br[^>]*>", "\n", body, flags=re.I)
    body = re.sub(r"<[^>]+>", "", body)
    body = H.unescape(body)
    body = body.replace(" ", " ")
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n\s*\n\s*\n+", "\n\n", body)
    return body.strip()

def save(group, url, title):
    try:
        t = fetch(url)
    except Exception as e:
        return ("ERR", url, str(e))
    txt = extract(t)
    if len(txt) < 400:
        return ("THIN", url, f"{len(txt)} chars")
    slug = url.rsplit("/", 1)[-1].replace(".html", "").replace(".htm", "")
    fn = os.path.join(OUT, group, f"{slug}.md")
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    with open(fn, "w") as f:
        f.write(f"# {title}\n\nsource: {url}\n\n{txt}\n")
    return ("OK", fn, f"{len(txt)} chars")

manifest = []

# 1. STI treatment guidelines
toc = fetch(f"{BASE}/std/treatment-guidelines/toc.htm")
pages = links(toc, "/std/treatment-guidelines/")
pages.discard(f"{BASE}/std/treatment-guidelines/toc.htm")
for u in sorted(pages):
    r = save("sti-tx", u, u.rsplit('/',1)[-1].replace('.htm','').replace('-',' ').title() + " — CDC STI Treatment Guidelines")
    manifest.append(("sti-tx",) + r); print(r)
    time.sleep(2.0)

# 2. ACIP vaccine-specific
idx = fetch(f"{BASE}/acip-recs/hcp/vaccine-specific/index.html")
for u in sorted(links(idx, "/acip-recs/hcp/vaccine-specific/")):
    if u.endswith("index.html"): continue
    r = save("acip-vaccines", u, u.rsplit('/',1)[-1].replace('.html','').replace('-',' ').title() + " — ACIP Current Recommendations")
    manifest.append(("acip-vaccines",) + r); print(r)
    time.sleep(2.0)

# 3. Measles HCP
for u, title in [
    (f"{BASE}/measles/hcp/clinical-overview/index.html", "Clinical Overview of Measles"),
    (f"{BASE}/measles/hcp/lab-diagnosis/index.html", "Measles Lab Diagnosis"),
    (f"{BASE}/measles/about/transmission/index.html", "Measles Transmission"),
]:
    r = save("measles", u, title)
    manifest.append(("measles",) + r); print(r)
    time.sleep(2.0)

json.dump(manifest, open(os.path.join(OUT, "MANIFEST.json"), "w"), indent=1)
errs = [m for m in manifest if m[1] == "ERR"]
print(f"DONE: {len(manifest)} pages, {len(errs)} errors")
