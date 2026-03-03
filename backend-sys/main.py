from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json

from utils import (
    obtener_turno_activo,
    leer_menu,
    buscar_plato_por_id,
    actualizar_disponibles,
    guardar_registro,
    leer_pedidos_activos,
    agregar_pedido_activo,
    actualizar_pedido_activo,
    vaciar_pedidos_activos,
    eliminar_pedido_activo,
    leer_registros
)

app = FastAPI(title="Gestor Interno Anto", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── WebSocket Manager ───────────────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        data = json.dumps(message, ensure_ascii=False)
        for ws in self.active_connections:
            try:
                await ws.send_text(data)
            except Exception:
                pass


manager = ConnectionManager()


# ─── Modelos ─────────────────────────────────────────────────────────────────

class ActualizarDisponibles(BaseModel):
    delta: int                    # +N cocina sube stock / -N camarero registra venta
    mozo: Optional[str] = None    # requerido si delta < 0

class NuevoPedido(BaseModel):
    mozo: str
    plato_id: int
    cantidad: int = 1

class ActualizarPedido(BaseModel):
    estado: Optional[str] = None    # pendiente | listo
    nombre: Optional[str] = None
    cantidad: Optional[int] = None
    mozo: Optional[str] = None


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/turno")
def get_turno():
    """CU-06: Turno activo según hora del servidor."""
    menu = leer_menu()
    return {"turno_activo": obtener_turno_activo(menu)}


@app.get("/menu")
def get_menu():
    """CU-01 + CU-06: Menú completo con turno activo."""
    menu = leer_menu()
    return {"turno_activo": obtener_turno_activo(menu), "menu": menu}


@app.get("/menu/{categoria}")
def get_categoria(categoria: str):
    """CU-01: Platos de una categoría específica."""
    menu = leer_menu()
    if categoria not in menu or categoria == "core":
        raise HTTPException(status_code=404, detail=f"Categoría '{categoria}' no encontrada.")
    return {categoria: menu[categoria]}


@app.patch("/menu/{plato_id}/disponibles")
async def patch_disponibles(plato_id: int, body: ActualizarDisponibles):
    """
    CU-02: Cocina actualiza stock (delta positivo).
    CU-03: Camarero registra venta (delta negativo, requiere mozo).
    Broadcast WebSocket a todos los conectados.
    """
    menu = leer_menu()

    if body.delta < 0 and not body.mozo:
        raise HTTPException(
            status_code=422,
            detail="El campo 'mozo' es requerido para registrar una venta."
        )

    resultado = actualizar_disponibles(menu, plato_id, body.delta)
    if not resultado["ok"]:
        raise HTTPException(status_code=400, detail=resultado["error"])

    # Registrar venta en registros.json
    if body.delta < 0:
        turno = obtener_turno_activo(menu)
        assert body.mozo is not None
        plato = buscar_plato_por_id(menu, plato_id)
        assert plato is not None
        guardar_registro(turno, plato, abs(body.delta), body.mozo)
        nuevo = agregar_pedido_activo(turno, body.mozo, plato, abs(body.delta))
        await manager.broadcast({
            "evento": "nuevo_pedido",
            "pedido": nuevo,
        }) 

    # Notificar a todos los clientes (cocina, caja, camareros)
    await manager.broadcast({
        "evento": "disponible_actualizado",
        "plato_id": plato_id,
        "nuevos_disponibles": resultado["nuevos_disponibles"],
    })

    return {
        "plato_id": plato_id,
        "nuevos_disponibles": resultado["nuevos_disponibles"],
    }
@app.get("/pedidos_activos")
def get_pedidos_activos():
    """Cocina y caja leen la cola de pedidos del turno."""
    return leer_pedidos_activos()

#--------NUEVAS FUNCIONES PARA LISTA DE PEDIDOS ACTIVOS----------------
@app.patch("/pedidos_activos/{pedido_id}")
async def patch_pedido_activo(pedido_id: int, body: ActualizarPedido):
    """
    Cocina marca listo (estado: 'listo').
    Caja modifica nombre, cantidad o mozo.
    """
    estados_validos = {"pendiente", "listo"}
    if body.estado and body.estado not in estados_validos:
        raise HTTPException(status_code=422, detail=f"Estado inválido. Usa: {estados_validos}")

    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    pedido  = actualizar_pedido_activo(pedido_id, updates)

    if pedido is None:
        raise HTTPException(status_code=404, detail=f"Pedido {pedido_id} no encontrado.")

    await manager.broadcast({
        "evento": "pedido_actualizado",
        "pedido": pedido,
    })

    return pedido


@app.delete("/pedidos_activos/turno")
async def cerrar_turno():
    """Vacía la cola de pedidos activos al cerrar el turno."""
    vaciar_pedidos_activos()
    await manager.broadcast({"evento": "turno_cerrado"})
    return {"ok": True, "mensaje": "Cola de pedidos vaciada."}

@app.delete("/pedidos_activos/{pedido_id}")
async def eliminar_pedido(pedido_id: int):
    ok = eliminar_pedido_activo(pedido_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Pedido no encontrado.")
    await manager.broadcast({
        "evento": "pedido_eliminado",
        "pedido_id": pedido_id,
    })
    return {"ok": True}

@app.get("/registros")
def get_registros(
    fecha: Optional[str] = None,        # "2026-03-02"
    turno: Optional[str] = None,        # "Mañana" | "Tarde"
    mozo: Optional[str] = None,         # "Valentino"
    plato_id: Optional[int] = None,     # 25
    nombre: Optional[str] = None,       # búsqueda parcial
):
    """
    CU-07 / CU-08: Registros de ventas con filtros opcionales.
    Gerencia consulta demanda por fecha, turno, mozo o platillo.
    """
    registros = leer_registros()

    if fecha:
        registros = [r for r in registros if r.get("fecha") == fecha]
    if turno:
        registros = [r for r in registros if r.get("turno", "").lower() == turno.lower()]
    if mozo:
        registros = [r for r in registros if r.get("mozo", "").lower() == mozo.lower()]
    if plato_id:
        registros = [r for r in registros if r.get("id") == plato_id]
    if nombre:
        registros = [r for r in registros if nombre.lower() in r.get("nombre", "").lower()]

    # Totales agrupados útiles para el dashboard
    totales_plato = {}
    totales_mozo = {}
    totales_turno = {}

    for r in registros:
        n = r["nombre"]
        m = r.get("mozo", "?")
        t = r.get("turno", "?")
        c = r.get("cantidad", 1)

        totales_plato[n] = totales_plato.get(n, 0) + c
        totales_mozo[m]  = totales_mozo.get(m, 0) + c
        totales_turno[t] = totales_turno.get(t, 0) + c

    return {
        "total_ventas": sum(r.get("cantidad", 1) for r in registros),
        "registros": registros,
        "por_plato": sorted(
            [{"nombre": k, "cantidad": v} for k, v in totales_plato.items()],
            key=lambda x: x["cantidad"], reverse=True
        ),
        "por_mozo": sorted(
            [{"mozo": k, "cantidad": v} for k, v in totales_mozo.items()],
            key=lambda x: x["cantidad"], reverse=True
        ),
        "por_turno": [{"turno": k, "cantidad": v} for k, v in totales_turno.items()],
    }

# ─── WebSocket ───────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """CU-02, CU-05: Canal en tiempo real. Al conectar envía estado inicial del menú."""
    await manager.connect(websocket)
    menu = leer_menu()
    await websocket.send_text(json.dumps({
        "evento": "estado_inicial",
        "turno_activo": obtener_turno_activo(menu),
        "menu": menu,
        "pedidos_activos": leer_pedidos_activos(),
    }, ensure_ascii=False))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)