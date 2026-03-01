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
    }, ensure_ascii=False))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)