#!/usr/bin/env python3
"""Script de debug para probar Tracksolid API directo en el VPS."""
import os
import json
import hashlib
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAPI_URL = os.getenv("TRACKSOLID_OPENAPI_URL", "").strip()
APP_KEY = os.getenv("TRACKSOLID_APP_KEY", "").strip()
APP_SECRET = os.getenv("TRACKSOLID_APP_SECRET", "").strip()
ACCOUNT = os.getenv("TRACKSOLID_ACCOUNT", "").strip()
PASSWORD_MD5 = os.getenv("TRACKSOLID_PASSWORD_MD5", "").strip()

print("=== CREDENCIALES ===")
print(f"URL: {OPENAPI_URL}")
print(f"APP_KEY: {APP_KEY[:4]}... (len={len(APP_KEY)})")
print(f"APP_SECRET: len={len(APP_SECRET)}")
print(f"ACCOUNT: {ACCOUNT}")
print(f"PASSWORD_MD5: {PASSWORD_MD5[:6]}... (len={len(PASSWORD_MD5)})")
print()

def get_current_date():
    import pytz
    return datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")

def generate_sign(params, app_secret):
    sorted_params = ''.join(f"{k}{v}" for k, v in sorted(params.items()))
    sign_str = f"{app_secret}{sorted_params}{app_secret}"
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

def send_post(url, params):
    resp = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=params, timeout=15)
    return resp.json()

# 1. Obtener token
print("=== 1. OBTENIENDO TOKEN ===")
param_map = {
    "app_key": APP_KEY,
    "v": "1.0",
    "timestamp": get_current_date(),
    "sign_method": "md5",
    "format": "json",
    "method": "jimi.oauth.token.get",
    "user_id": ACCOUNT,
    "user_pwd_md5": PASSWORD_MD5,
    "expires_in": "7200",
}
param_map["sign"] = generate_sign(param_map, APP_SECRET)
token_resp = send_post(OPENAPI_URL, param_map)
print(json.dumps(token_resp, indent=2, ensure_ascii=False))

if token_resp.get("code") != 0:
    print("\n*** ERROR: No se pudo obtener token. Revisa credenciales. ***")
    exit(1)

ACCESS_TOKEN = token_resp["result"]["accessToken"]
print(f"\nToken OK: {ACCESS_TOKEN[:20]}...")

# 2. Buscar device detail por IMEI
IMEI_TEST = input("\nEscribe un IMEI para buscar: ").strip()

print(f"\n=== 2. DEVICE DETAIL (imei={IMEI_TEST}) ===")
param_map = {
    "app_key": APP_KEY,
    "v": "1.0",
    "timestamp": get_current_date(),
    "sign_method": "md5",
    "format": "json",
    "method": "jimi.track.device.detail",
    "access_token": ACCESS_TOKEN,
    "imei": IMEI_TEST,
}
param_map["sign"] = generate_sign(param_map, APP_SECRET)
detail_resp = send_post(OPENAPI_URL, param_map)
print(json.dumps(detail_resp, indent=2, ensure_ascii=False))

# 3. Listar sub-cuentas (child list)
print(f"\n=== 3. CHILD LIST (target={ACCOUNT}) ===")
param_map = {
    "app_key": APP_KEY,
    "v": "1.0",
    "timestamp": get_current_date(),
    "sign_method": "md5",
    "format": "json",
    "method": "jimi.user.child.list",
    "access_token": ACCESS_TOKEN,
    "target": ACCOUNT,
}
param_map["sign"] = generate_sign(param_map, APP_SECRET)
child_resp = send_post(OPENAPI_URL, param_map)
print(json.dumps(child_resp, indent=2, ensure_ascii=False))

# 4. Si hay sub-cuentas, listar dispositivos de la primera
if child_resp.get("code") == 0 and child_resp.get("result"):
    sub_accounts = child_resp["result"]
    print(f"\nSub-cuentas encontradas: {len(sub_accounts)}")
    first_acc = sub_accounts[0].get("account", "")
    print(f"\n=== 4. DEVICE LIST (primera sub-cuenta: {first_acc}) ===")
    param_map = {
        "app_key": APP_KEY,
        "v": "1.0",
        "timestamp": get_current_date(),
        "sign_method": "md5",
        "format": "json",
        "method": "jimi.user.device.list",
        "access_token": ACCESS_TOKEN,
        "target": first_acc,
    }
    param_map["sign"] = generate_sign(param_map, APP_SECRET)
    devlist_resp = send_post(OPENAPI_URL, param_map)
    print(json.dumps(devlist_resp, indent=2, ensure_ascii=False))
else:
    print("\nNo hay sub-cuentas o hubo error. Intentando device list con cuenta principal...")
    param_map = {
        "app_key": APP_KEY,
        "v": "1.0",
        "timestamp": get_current_date(),
        "sign_method": "md5",
        "format": "json",
        "method": "jimi.user.device.list",
        "access_token": ACCESS_TOKEN,
        "target": ACCOUNT,
    }
    param_map["sign"] = generate_sign(param_map, APP_SECRET)
    devlist_resp = send_post(OPENAPI_URL, param_map)
    print(json.dumps(devlist_resp, indent=2, ensure_ascii=False))

print("\n=== FIN ===")
