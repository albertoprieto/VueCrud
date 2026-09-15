"""Repara un pago/ingreso bancario que quedó "atorado" porque la nota o
factura a la que estaba ligado se borró (bug corregido en main.py: ahora
eliminar una nota/factura con pagos ligados se bloquea, pero esto arregla
los que ya quedaron huérfanos de antes de ese fix).

Busca en ingresos_banco (por IMEI) y en pagos_nota (por banco/comprobante)
cualquier liga que apunte a una nota_id o factura_id que ya no existe, y la
desliga: el ingreso/comprobante NO se borra, solo se libera para poder
volver a ligarlo a la nota/factura correcta desde la pantalla de "Ligar
ingreso bancario".

Uso:
    python reparar_pago_huerfano.py 869066064865760           # dry-run
    python reparar_pago_huerfano.py 869066064865760 --aplicar # repara
"""
import sys
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
import os

_aqui = Path(__file__).resolve().parent
for _cand in (_aqui / ".env", _aqui.parent / ".env", Path.cwd() / ".env"):
    if _cand.is_file():
        load_dotenv(_cand)
        break
else:
    load_dotenv()


def db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    imei = sys.argv[1].strip()
    aplicar = "--aplicar" in sys.argv[2:]

    conn = db()
    cur = conn.cursor(dictionary=True)

    print(f"=== ingresos_banco con IMEI {imei} ===")
    cur.execute("SELECT * FROM ingresos_banco WHERE imeis LIKE %s", (f"%{imei}%",))
    ingresos = cur.fetchall()
    if not ingresos:
        print("Ninguno. Revisa si el pago está directo en pagos_nota (banco/comprobante) o si el IMEI está mal.")
    for ing in ingresos:
        print(f"  ingreso_id={ing['id']} banco={ing['banco']} monto={ing['monto']} "
              f"comprobante={ing['comprobante_path']}")

    huerfanos = []
    for ing in ingresos:
        cur.execute("SELECT * FROM ingreso_banco_notas WHERE ingreso_id=%s", (ing["id"],))
        for link in cur.fetchall():
            existe = True
            destino = None
            if link.get("nota_id"):
                cur.execute("SELECT id FROM notas_pago WHERE id=%s", (link["nota_id"],))
                existe = bool(cur.fetchone())
                destino = f"nota_id={link['nota_id']}"
            elif link.get("factura_id"):
                cur.execute("SELECT id FROM facturas_pago WHERE id=%s", (link["factura_id"],))
                existe = bool(cur.fetchone())
                destino = f"factura_id={link['factura_id']}"
            estado = "OK (existe)" if existe else "HUÉRFANO (la nota/factura ya no existe)"
            print(f"    liga id={link['id']} -> {destino} monto_aplicado={link['monto_aplicado']}  [{estado}]")
            if not existe:
                huerfanos.append(link["id"])

    if not huerfanos:
        print("\nNada que reparar en ingreso_banco_notas.")
    elif not aplicar:
        print(f"\n{len(huerfanos)} liga(s) huérfana(s) encontradas: {huerfanos}")
        print("Dry-run, no se modificó nada. Vuelve a correr con --aplicar para desligarlas.")
    else:
        cur2 = conn.cursor()
        fmt = ",".join(["%s"] * len(huerfanos))
        cur2.execute(f"DELETE FROM ingreso_banco_notas_conceptos WHERE link_id IN ({fmt})", tuple(huerfanos))
        cur2.execute(f"DELETE FROM ingreso_banco_notas WHERE id IN ({fmt})", tuple(huerfanos))
        conn.commit()
        cur2.close()
        print(f"\n{len(huerfanos)} liga(s) desligada(s). Los ingresos ya aparecen libres para volver a ligarse.")

    print(f"\n=== pagos_nota con ese IMEI en el comprobante/banco (por si el pago es directo, no vía ingresos_banco) ===")
    cur.execute("SELECT * FROM pagos_nota WHERE comprobante_path LIKE %s OR banco LIKE %s", (f"%{imei}%", f"%{imei}%"))
    directos = cur.fetchall()
    if not directos:
        print("Ninguno.")
    for p in directos:
        cur.execute("SELECT id FROM notas_pago WHERE id=%s", (p["nota_id"],)) if p["nota_id"] else None
        existe = bool(cur.fetchone()) if p["nota_id"] else False
        estado = "OK" if existe else "HUÉRFANO (nota_id apunta a una nota que ya no existe)"
        print(f"  pago_id={p['id']} nota_id={p['nota_id']} banco={p['banco']} monto={p['monto']}  [{estado}]")
        if p["nota_id"] and not existe:
            if not aplicar:
                print("    (dry-run) correría: UPDATE pagos_nota SET nota_id_original=nota_id, nota_id=NULL WHERE id=%s", p["id"])
            else:
                cur3 = conn.cursor()
                cur3.execute(
                    "UPDATE pagos_nota SET nota_id_original=nota_id, nota_id=NULL, "
                    "desvinculado_por='script-reparacion', desvinculado_fecha=NOW() WHERE id=%s",
                    (p["id"],)
                )
                conn.commit()
                cur3.close()
                print(f"    -> pago {p['id']} desvinculado, ahora aparece en /pagos-nota/sueltos")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
