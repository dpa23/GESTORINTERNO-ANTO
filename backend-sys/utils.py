import json
import os
from datetime import datetime, time
from typing import Optional

# ─── Rutas ───────────────────────────────────────────────────────────────────

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
MENU_PATH      = os.path.join(BASE_DIR, "core", "menu.json")
REGISTROS_PATH = os.path.join(BASE_DIR, "output-back", "registros.json")
PEDIDOS_ACT_PATH = os.path.join(BASE_DIR, "output-back", "pedidos_act.json")



# ─── Menú ────────────────────────────────────────────────────────────────────

def leer_menu() -> dict:
    with open(MENU_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def escribir_menu(menu: dict) -> None:
    with open(MENU_PATH, "w", encoding="utf-8") as f:
        json.dump(menu, f, ensure_ascii=False, indent=2)


# ─── Turno ───────────────────────────────────────────────────────────────────

def _str_a_time(hora_str: str) -> time:
    h, m = map(int, hora_str.split(":"))
    return time(h, m)


def obtener_turno_activo(menu: dict) -> str:
    turnos = menu.get("core", {}).get("turnos", {})
    ahora  = datetime.now().time().replace(second=0, microsecond=0)

    for nombre, rango in turnos.items():
        inicio = _str_a_time(rango["hora_inicio"])
        fin    = _str_a_time(rango["hora_fin"])
        if inicio <= ahora <= fin:
            return nombre

    return "Sin turno"


# ─── Búsqueda ────────────────────────────────────────────────────────────────

def buscar_plato_por_id(menu: dict, plato_id: int) -> Optional[dict]:
    for categoria, items in menu.items():
        if categoria == "core":
            continue
        if not isinstance(items, list):
            continue
        for plato in items:
            if plato.get("id") == plato_id:
                return plato
    return None


# ─── Disponibilidad ──────────────────────────────────────────────────────────

def actualizar_disponibles(menu: dict, plato_id: int, delta: int) -> dict:
    plato = buscar_plato_por_id(menu, plato_id)

    if plato is None:
        return {"ok": False, "error": f"Plato {plato_id} no encontrado."}

    nuevo = plato["disponibles"] + delta

    if nuevo < 0:
        return {"ok": False, "error": f"Stock insuficiente. Disponibles actuales: {plato['disponibles']}."}

    plato["disponibles"] = nuevo
    escribir_menu(menu)

    return {"ok": True, "nuevos_disponibles": nuevo}


# ─── Registros ───────────────────────────────────────────────────────────────

def guardar_registro(turno: str, plato: dict, cantidad: int, mozo: str) -> None:
    os.makedirs(os.path.dirname(REGISTROS_PATH), exist_ok=True)

    registros = []
    if os.path.exists(REGISTROS_PATH):
        with open(REGISTROS_PATH, "r", encoding="utf-8") as f:
            registros = json.load(f)

    ahora = datetime.now()
    registros.append({
        "fecha":    ahora.strftime("%Y-%m-%d"),
        "hora":     ahora.strftime("%H:%M"),
        "turno":    turno,
        "mozo":     mozo,
        "id":       plato["id"],
        "nombre":   plato["nombre"],
        "cantidad": cantidad,
    })

def leer_registros() -> list:
    if not os.path.exists(REGISTROS_PATH):
        return []
    with open(REGISTROS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    with open(REGISTROS_PATH, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)
# ─── Pedidos Activos ───────────────────────────────────────────────────────
def leer_pedidos_activos() -> list:
    if not os.path.exists(PEDIDOS_ACT_PATH):
        return []
    with open(PEDIDOS_ACT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
def escribir_pedidos_activos(pedidos: list) -> None:
    os.makedirs(os.path.dirname(PEDIDOS_ACT_PATH), exist_ok=True)
    with open(PEDIDOS_ACT_PATH, "w", encoding="utf-8") as f:
        json.dump(pedidos, f, ensure_ascii=False, indent=2)


def agregar_pedido_activo(turno: str, mozo: str, plato: dict, cantidad: int) -> dict:
    pedidos = leer_pedidos_activos()
    ahora   = datetime.now()

    # ID único basado en timestamp
    pedido_id = int(ahora.timestamp() * 1000)

    nuevo = {
        "pedido_id": pedido_id,
        "fecha":     ahora.strftime("%Y-%m-%d"),
        "hora":      ahora.strftime("%H:%M"),
        "turno":     turno,
        "mozo":      mozo,
        "nombre":    plato["nombre"],
        "cantidad":  cantidad,
        "estado":    "pendiente",   # pendiente | listo
    }

    pedidos.append(nuevo)
    escribir_pedidos_activos(pedidos)
    return nuevo

def actualizar_pedido_activo(pedido_id: int, updates: dict) -> Optional[dict]:
    pedidos = leer_pedidos_activos()
    pedido  = next((p for p in pedidos if p["pedido_id"] == pedido_id), None)

    if pedido is None:
        return None

    pedido.update(updates)
    escribir_pedidos_activos(pedidos)
    return pedido

def vaciar_pedidos_activos() -> None:
    escribir_pedidos_activos([])

def eliminar_pedido_activo(pedido_id: int) -> bool:
    pedidos = leer_pedidos_activos()
    nuevos  = [p for p in pedidos if p["pedido_id"] != pedido_id]
    if len(nuevos) == len(pedidos):
        return False
    escribir_pedidos_activos(nuevos)
    return True

