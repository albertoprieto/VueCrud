import csv
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://api.gpsubicacionapi.com"
CSV_PATH = Path("SIM ESPAÑOL.csv")


def log(message: str):
    print(message, flush=True)


def fetch_json(url: str, method: str = "GET", payload: dict | None = None):
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        log(f"REQUEST {method} {url}")
        log(f"PAYLOAD {json.dumps(payload, ensure_ascii=False)}")
    else:
        log(f"REQUEST {method} {url}")
    req = urllib.request.Request(url=url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            result = json.loads(body) if body else None
            log(f"RESPONSE {resp.status} {body[:500] if body else ''}")
            return result
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        log(f"RESPONSE {exc.code} {body[:500] if body else ''}")
        try:
            return json.loads(body) if body else {"status": exc.code, "error": exc.reason}
        except Exception:
            return {"status": exc.code, "error": exc.reason, "body": body}
    except urllib.error.URLError as exc:
        log(f"ERROR {exc}")
        return {"error": str(exc)}


def norm_platform(p: str) -> str:
    p2 = (p or "").strip().upper()
    if p2 in {"TRACKSOLID", "TRACK", "TRACKSOLIDPRO"}:
        return "TRACKSOLID"
    if p2 in {"IOP", "IOPSGPS", "WANWAY"}:
        return "IOP"
    return p2


def only_digits(v: str) -> str:
    return "".join(ch for ch in (v or "") if ch.isdigit())


def find_header_and_rows(text: str):
    log("Buscando encabezado del CSV...")
    lines = text.splitlines()
    header_idx = -1
    for i, ln in enumerate(lines):
        up = (ln or "").upper()
        if "PLATAFORMA" in up and "IMEI" in up and "SERVICIO" in up:
            header_idx = i
            break
    if header_idx < 0:
        raise RuntimeError("No se encontró encabezado con PLATAFORMA e IMEI")
    rows_text = "\n".join(lines[header_idx:])
    log(f"Encabezado encontrado en linea {header_idx + 1}")
    return csv.DictReader(rows_text.splitlines(), delimiter=';')


def extract_row_from_dispositivo(plataforma: str, data: dict):
    raw = data.get("dispositivo")
    if isinstance(raw, list):
        raw = raw[0] if raw else {}
    if not isinstance(raw, dict):
        raw = {}

    deaccount = ""
    account_name = ""
    mobile_raw = ""

    if plataforma == "TRACKSOLID":
        deaccount = str(raw.get("account") or "").strip()
        account_name = str(raw.get("customerName") or "").strip()
        mobile_raw = str(raw.get("sim") or raw.get("simNum") or "")
    else:
        account = raw.get("account") if isinstance(raw.get("account"), dict) else {}
        brief = raw.get("deviceBrief") if isinstance(raw.get("deviceBrief"), dict) else {}
        deaccount = str(account.get("accountName") or "").strip()
        account_name = str(account.get("accountName") or "").strip()
        mobile_raw = str(brief.get("deviceMobile") or raw.get("sim") or raw.get("simNum") or "")

    device_mobile = only_digits(mobile_raw)
    return deaccount, account_name, device_mobile


def get_existing_keys():
    keys = set()
    page = 1
    size = 100
    log("Leyendo registros existentes desde la API...")
    while True:
        url = f"{BASE}/api/utilidades/consultas-sim?page={page}&size={size}"
        data = fetch_json(url)
        items = data.get("items") or []
        log(f"Pagina {page}: {len(items)} registros")
        if not items:
            break
        for it in items:
            key = (
                str(it.get("plataforma") or "").strip().upper(),
                only_digits(str(it.get("imei") or "")),
                only_digits(str(it.get("device_mobile") or it.get("deviceMobile") or "")),
                str(it.get("activation_date") or "").strip(),
            )
            keys.add(key)
        if len(items) < size:
            break
        page += 1
    return keys


def main():
    log(f"Iniciando bootstrap desde {CSV_PATH}")

    text = None
    for enc in ("utf-8-sig", "latin-1"):
        try:
            log(f"Leyendo CSV con encoding {enc}...")
            text = CSV_PATH.read_text(encoding=enc, errors="replace")
            break
        except Exception:
            continue
    if text is None:
        raise SystemExit("No se pudo leer el CSV")

    reader = find_header_and_rows(text)
    existing = get_existing_keys()
    seen = set(existing)
    log(f"Llaves existentes cargadas: {len(existing)}")

    inserted = 0
    skipped_missing = 0
    skipped_duplicate = 0
    skipped_unsupported = 0
    failed = 0

    for idx, r in enumerate(reader, start=1):
        plataforma_raw = (r.get("PLATAFORMA") or "").strip()
        imei = only_digits(r.get("IMEI") or "")
        servicio = (r.get("SERVICIO") or "").strip()

        log(f"Fila {idx}: PLATAFORMA={plataforma_raw!r} IMEI={imei!r} SERVICIO={servicio!r}")

        if not plataforma_raw or not imei or not servicio:
            log(f"Fila {idx}: omitida por datos faltantes")
            skipped_missing += 1
            continue

        plataforma = norm_platform(plataforma_raw)
        if plataforma not in {"IOP", "TRACKSOLID"}:
            log(f"Fila {idx}: omitida por plataforma no soportada -> {plataforma}")
            skipped_unsupported += 1
            continue

        try:
            q_plat = urllib.parse.quote(plataforma)
            q_imei = urllib.parse.quote(imei)
            disp_url = f"{BASE}/api/plataformas/dispositivo/{q_imei}?plataforma={q_plat}"
            log(f"Fila {idx}: consultando dispositivo")
            disp_data = fetch_json(disp_url)

            deaccount, account_name, device_mobile = extract_row_from_dispositivo(plataforma, disp_data)
            log(f"Fila {idx}: dispositivo -> deaccount={deaccount!r} accountName={account_name!r} deviceMobile={device_mobile!r}")
            if not device_mobile:
                log(f"Fila {idx}: omitida porque no se pudo extraer deviceMobile")
                failed += 1
                continue

            sim_url = f"{BASE}/api/utilidades/sims/details?identifiers={urllib.parse.quote(device_mobile)}"
            log(f"Fila {idx}: consultando SIM details")
            sim_data = fetch_json(sim_url)

            items = sim_data.get("items") or []
            first = items[0] if items else {}
            ac = first.get("active_connection") if isinstance(first.get("active_connection"), dict) else {}

            activation_date = str(sim_data.get("activation_date") or ac.get("activation_date") or "").strip()
            vigencia_sim = str(sim_data.get("contract_end_date") or ac.get("contract_end_date") or "").strip()
            iccid = only_digits(str(sim_data.get("iccid") or first.get("iccid") or ""))
            log(f"Fila {idx}: SIM -> activation_date={activation_date!r} vigencia_sim={vigencia_sim!r} iccid={iccid!r}")

            tipo_csv = servicio.upper()
            tipo = "renovacion" if "RENOV" in tipo_csv else "activacion"

            required = [tipo, activation_date, deaccount, account_name, plataforma, imei, iccid, device_mobile, vigencia_sim]
            if any(not str(v or "").strip() for v in required):
                log(f"Fila {idx}: omitida por datos incompletos luego de enriquecer")
                skipped_missing += 1
                continue

            key = (plataforma, imei, device_mobile, activation_date)
            if key in seen:
                log(f"Fila {idx}: omitida por duplicado")
                skipped_duplicate += 1
                continue

            payload = {
                "tipo": tipo,
                "servicio": servicio,
                "activation_date": activation_date,
                "deaccount": deaccount,
                "account_name": account_name,
                "plataforma": plataforma,
                "imei": imei,
                "iccid": iccid,
                "device_mobile": device_mobile,
                "vigencia_sim": vigencia_sim,
            }

            fetch_json(f"{BASE}/api/utilidades/consultas-sim", method="POST", payload=payload)
            seen.add(key)
            inserted += 1
            log(f"INSERTADO | tipo={tipo} | servicio={servicio} | plataforma={plataforma} | imei={imei} | iccid={iccid}")

        except Exception as exc:
            log(f"Fila {idx}: ERROR -> {exc}")
            failed += 1
            continue

    log(json.dumps({
        "base": BASE,
        "csv": str(CSV_PATH),
        "inserted": inserted,
        "skipped_missing": skipped_missing,
        "skipped_duplicate": skipped_duplicate,
        "skipped_unsupported": skipped_unsupported,
        "failed": failed,
        "scanned_total_rows": inserted + skipped_missing + skipped_duplicate + skipped_unsupported + failed,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
