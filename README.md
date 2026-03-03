# GESTORINTERNO-ANTO
Backend y frontend de datos para gestión interina de restaurante con gestor en C-json
## Problema actual: 
La comunicación de pedidos disponibles a prometer por parte de cocina para caja y camarero se gestiona mediante notas adhesivas ubicadas en el refrigerador de pasteles, no les permite ser inmediatos en momentos decisivos y dependen mucho de como marquen y escriban los números correctamente para que el “sistema” funcione,  se tiene una propuesta para la solución que se explicara más adelante.
## Solución web
Permite gestionar los platos de carta disponibles a prometer para cada cliente, donde cocina puede anular platos cuando se acaban de forma inmediata, además gestionar requerimientos por platillo,
solucionando problemas de necesidad entre platillos, por ejemplo, Requerimiento "A" es usado para Foccaccia, donde existen 2, si ese Requerimiento se acaba, ambos platillos quedan en 0.
## Stack tecnológico
Frontend: Vue.js
Base de datos: json plano emulando un nosql
Backend: Fastapi
Embebido de inmediates y gestión de servidor físico: C/C++ 
### Ramas de desarrollo:
main        ← estable, producción
backend     ← desarrollo FastAPI
frontend    ← desarrollo Vue
cocina-c    ← desarrollo C/C++
## CASOS DE USO
### CU-01: Consultar disponibilidad del menú

Actor: Camarero / Cajero
Precondición: Sistema activo y conectado a la red interna
Flujo: El camarero consulta desde tablet o caja qué platos tienen disponibles mayor a 0
Postcondición: Visualiza disponibilidad en tiempo real sin preguntar a cocina
Archivo involucrado: menu.json

### CU-02: Actualizar disponibilidad de un plato

Actor: Personal de cocina
Precondición: Plato existe en el sistema
Flujo: Cocina ingresa la cantidad disponible del plato al inicio del turno o cuando hay cambio
Postcondición: Todos los dispositivos conectados reciben el cambio al instante vía WebSocket
Archivo involucrado: menu.json

### CU-03: Registrar venta de un plato

Actor: Camarero / Sistema
Precondición: Plato con disponibles mayor a 0
Flujo: Al confirmar un pedido el sistema resta 1 de disponibles y registra la venta
Postcondición: menu.json actualizado, entrada nueva en registros.json
Archivos involucrados: menu.json, registros.json

### CU-04: Asignar pedido a mesa y mozo

Actor: Camarero
Precondición: Mesa activa y plato disponible
Flujo: El camarero selecciona mesa, plato y queda registrado con su nombre
Postcondición: Cocina ve en pantalla qué plato va a qué mesa y de qué mozo
Archivos involucrados: mesas.json, trazabilidad.json

### CU-05: Visualizar pedidos en cocina

Actor: Personal de cocina
Precondición: Pantalla conectada a la Raspberry, sistema activo
Flujo: La pantalla muestra en tiempo real los pedidos activos con mesa y mozo asignado
Postcondición: Cocina despacha el plato correcto a la mesa correcta sin confusión
Archivo involucrado: mesas.json leído por programa C/C++ o web service.

### CU-06: Consultar turno activo

Actor: Sistema / Cualquier usuario
Precondición: Sistema activo
Flujo: El sistema determina automáticamente el turno según la hora del servidor
Postcondición: Todos los registros quedan etiquetados con el turno correcto sin intervención manual
Archivo involucrado: sección core de menu.json

### CU-07: Análisis de demanda por turno

Actor: Gerencia
Precondición: registros.json con datos acumulados
Flujo: Gerencia consulta qué platos se vendieron más por turno y fecha
Postcondición: Información disponible para decisiones de compra y planificación
Archivo involucrado: registros.json

### CU-08: Trazabilidad de pedido

Actor: Gerencia / Administración
Precondición: trazabilidad.json con datos acumulados
Flujo: Se consulta qué mozo atendió qué mesa, qué pidieron y a qué hora
Postcondición: Visibilidad completa del flujo de atención para auditoría o resolución de conflictos
Archivo involucrado: trazabilidad.json

### CU-09: Proyección de insumos MRP (Fase 2)

Actor: Gerencia / Taller
Precondición: registros.json acumulado y recetas.json con ingredientes por plato
Flujo: Se cruzan ventas históricas con recetas para calcular consumo real de insumos
Postcondición: Lista de requerimientos de compra por insumo para el período analizado
Archivos involucrados: registros.json, recetas.json

## Sección core en menu.json:

Mañana: 06:00 - 14:59
Tarde: 15:00 - 23:59
Turno calculado automáticamente por hora del sistema
utils.py funciones:

obtener_turno_activo → calcula turno por hora del sistema
leer_menu / escribir_menu → lectura y escritura del JSON
buscar_plato_por_id → recorre categorías excluyendo core
actualizar_disponibles → suma o resta, no permite negativos
guardar_registro → acumula en registros.json solo en restas


Endpoints FastAPI:

GET /menu → CU-01, CU-06
GET /menu/{categoria} → CU-01
GET /turno → CU-06
PATCH /menu/{id}/disponibles → CU-02, CU-03
WebSocket /ws → CU-02, CU-05


Escalabilidad hacia MRP:

Fase 2: agregar recetas.json relacionando platos con ingredientes
Cruzar con registros.json para obtener consumo real de insumos
Base para proyección de compras y abastecimiento del taller (CU-09)


Infraestructura:

Raspberry Pi OS como servidor y punto de acceso WiFi
HTTP suficiente para red interna cerrada
UPS recomendado contra cortes de luz
FastAPI arranca automáticamente con systemd
C/C++ compilado corre sobre el SO, lee JSONs y muestra pedidos en pantalla


Hallazgo de seguridad (sistema actual):

Sistema de gestión actual opera en HTTP sobre red general entre restaurante y taller
Maneja datos bancarios sin cifrado
Riesgo real de interceptación sin acceso físico ni IP propia en la red
Recomendación urgente: exigir HTTPS al proveedor o implementar VPN con WireGuard


Entorno Debian:

Python 3.13 con venv en ~/venv
Activar con source ~/venv/bin/activate
Proyecto en ~/restaurante_api
Node v20.19.2, npm 9.2.0
Vue CLI en ~/.npm-global


Pendiente:

Clonar repo en Debian y organizar por rama
Crear main.py con FastAPI y WebSocket
Crear proyecto Vue 3
Crear mesas.json y trazabilidad.json
Actualizar utils.py con lógica de mesas y trazabilidad
Configurar Raspberry como punto de acceso
Configurar systemd para arranque automático
Fase 2: recetas.json para MRP
## Usar laptops como servidor
### deploy.sh
Despliaga los recursos necesarios para el programa como ejecutable para que la computadora linux funcione como servidor
### deploy.bat
Es el mismo funcionamiento que el deploy.sh pero en windows, se recomienda nunca usar un dispositivo windows como servidor al tener subprocesos cargados.
