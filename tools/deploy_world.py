#!/usr/bin/env python3
"""Deploy the Sogni Worker world to a new Netlify site via API."""
import hashlib, json, os, sys, urllib.request, urllib.error

for _dc_path in (
    "/opt/muse/skills/custom-connector-setup/bin",
    "/opt/muse/skills/custom-connector-setup/templates/skill/bin",
):
    if os.path.exists(os.path.join(_dc_path, "dynamic_credentials.py")):
        sys.path.insert(0, _dc_path)
        break
from dynamic_credentials import add_surrogate_to_request, read_json_response

API = "https://api.netlify.com/api/v1"
DIST = "/home/hatch/workspace/goals/win-the-sogni-world-builders-challenge/hidden_files/project/kit-0.3.2/dist/sogni-worker"

def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    add_surrogate_to_request(req, "custom.netlify", allowed_hosts=["api.netlify.com"])
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        return resp.status, read_json_response(resp)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:500]

# 1. Use the site created earlier (21ed65a7-5dda-4c99-91a5-cc4485563ce9)
site_id = "21ed65a7-5dda-4c99-91a5-cc4485563ce9"
print("site:", site_id, "http://sogni-worker-world.netlify.app")

# 2. Hash files
files = {}
for root, _, fns in os.walk(DIST):
    for fn in fns:
        fp = os.path.join(root, fn)
        rel = "/" + os.path.relpath(fp, DIST)
        h = hashlib.sha1(open(fp, "rb").read()).hexdigest()
        files[rel] = h
print(f"hashed {len(files)} files")

# 3. Create deploy
status, dep = api("POST", f"/sites/{site_id}/deploys", {"files": files})
if status not in (200, 201):
    print("deploy create failed:", status, dep)
    sys.exit(1)
deploy_id = dep["id"]
required = dep.get("required", [])
print(f"deploy {deploy_id}: need upload {len(required)} files")

# 4. Upload required files
sha_to_path = {v: k for k, v in files.items()}
for i, sha in enumerate(required):
    rel = sha_to_path[sha]
    fp = os.path.join(DIST, rel.lstrip("/"))
    data = open(fp, "rb").read()
    req = urllib.request.Request(
        f"{API}/deploys/{deploy_id}/files/{rel.lstrip('/')}",
        data=data, method="PUT")
    req.add_header("Content-Type", "application/octet-stream")
    add_surrogate_to_request(req, "custom.netlify", allowed_hosts=["api.netlify.com"])
    try:
        resp = urllib.request.urlopen(req, timeout=300)
        assert resp.status in (200, 201, 204), resp.status
    except urllib.error.HTTPError as e:
        print(f"upload failed {rel}: {e.code}")
        sys.exit(1)
    if (i + 1) % 10 == 0:
        print(f"  uploaded {i + 1}/{len(required)}")
print("all files uploaded")

# 5. Check deploy state
status, dep = api("GET", f"/sites/{site_id}/deploys/{deploy_id}")
print("deploy state:", dep.get("state"))
print("URL:", dep.get("deploy_ssl_url") or site.get("url"))
print("SITE_ID:", site_id)
print("DEPLOY_ID:", deploy_id)
