#!/usr/bin/env python3
"""Upload Tidewatch assets to YOUR Roblox account (private) via Open Cloud Assets API.
Reads ~/.config/tidewatch/.env :  ROBLOX_API_KEY=...   ROBLOX_USER_ID=...
Usage (from a set folder): SSL_CERT_FILE=/etc/ssl/cert.pem python3 ../../scripts/upload_assets.py out/tex_x.png model.fbx ...
Status: used for every private upload since 2026-11-08 (PNG -> Decal, FBX -> Model); prints the asset id per file.
Images -> assetType Decal. Meshes via Open Cloud need FBX (assetType Model); OBJ is not accepted.
"""
import sys, os, json, time, mimetypes, uuid, urllib.request

def load_env():
    p = os.path.expanduser("~/.config/tidewatch/.env"); env = {}
    for line in open(p):
        if "=" in line and not line.startswith("#"):
            k, v = line.strip().split("=", 1); env[k] = v
    return env

def multipart(fields, fname, data, ctype):
    b = uuid.uuid4().hex; out = b""
    out += f'--{b}\r\nContent-Disposition: form-data; name="request"\r\nContent-Type: application/json\r\n\r\n{json.dumps(fields)}\r\n'.encode()
    out += f'--{b}\r\nContent-Disposition: form-data; name="fileContent"; filename="{fname}"\r\nContent-Type: {ctype}\r\n\r\n'.encode() + data + f"\r\n--{b}--\r\n".encode()
    return out, b

def upload(path, env):
    name = os.path.splitext(os.path.basename(path))[0]
    ext = os.path.splitext(path)[1].lower()
    atype = "Decal" if ext in (".png", ".jpg", ".jpeg") else "Model"
    fields = {"assetType": atype, "displayName": name, "description": "Tidewatch POC (private test)",
              "creationContext": {"creator": {"userId": env["ROBLOX_USER_ID"]}}}
    body, b = multipart(fields, os.path.basename(path), open(path, "rb").read(), ("model/fbx" if ext == ".fbx" else mimetypes.guess_type(path)[0] or "application/octet-stream"))
    req = urllib.request.Request("https://apis.roblox.com/assets/v1/assets", data=body, method="POST",
                                 headers={"x-api-key": env["ROBLOX_API_KEY"], "Content-Type": f"multipart/form-data; boundary={b}"})
    try:
        op = json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        print(name, "HTTP", e.code, e.read().decode()[:600]); return
    opid = op["path"].split("/")[-1]
    for _ in range(30):
        time.sleep(2)
        r = urllib.request.Request(f"https://apis.roblox.com/assets/v1/operations/{opid}", headers={"x-api-key": env["ROBLOX_API_KEY"]})
        res = json.load(urllib.request.urlopen(r))
        if res.get("done"):
            print(name, "->", res.get("response", res)); return
    print(name, "still processing, operation", opid)

if __name__ == "__main__":
    env = load_env()
    for f in sys.argv[1:]: upload(f, env)
