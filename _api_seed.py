"""Create test data via API using urllib."""
import urllib.request
import json
import ssl

BASE = "http://localhost:8000"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def api(method, path, data=None, token=None):
    url = f"{BASE}{path}"
    body = json.dumps(data).encode() if data else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


# Login
status, data = api("POST", "/api/auth/login", {"email": "admin@activia-trace.com", "password": "admin123"})
if status != 200:
    print(f"Login failed: {status} {data}")
    exit(1)
token = data["access_token"]
print(f"✅ Login OK")

# Create carrera
status, data = api("POST", "/api/admin/carreras", {"nombre": "Ingeniería en Sistemas", "codigo": "IS-2023"}, token)
if status in (200, 201):
    carrera_id = data["id"]
    print(f"✅ Carrera: {carrera_id}")
else:
    print(f"❌ Carrera: {status} {data}")
    carrera_id = None

# Create cohorte
if carrera_id:
    status, data = api("POST", "/api/admin/cohortes",
                       {"carrera_id": carrera_id, "nombre": "2023-1", "anio": 2023}, token)
    if status in (200, 201):
        print(f"✅ Cohorte: {data['id']}")
        cohorte_id = data["id"]
    else:
        print(f"❌ Cohorte: {status} {data}")
        cohorte_id = None

# Create materia
if carrera_id:
    status, data = api("POST", "/api/admin/materias",
                       {"carrera_id": carrera_id, "nombre": "Análisis de Sistemas II", "codigo": "ASI-2023", "carga_horaria": 120}, token)
    if status in (200, 201):
        materia_id = data["id"]
        print(f"✅ Materia: {materia_id}")
    else:
        print(f"❌ Materia: {status} {data}")
        materia_id = None

# Create programa
if carrera_id and materia_id:
    status, data = api("POST", "/api/programas/",
                       {"materia_id": materia_id, "cohorte_id": cohorte_id, "nombre": "Análisis de Sistemas II - 2023-1"}, token)
    if status in (200, 201):
        print(f"✅ Programa: {data['id']}")
    else:
        print(f"❌ Programa: {status} {data}")

print("\n✅ Seed completo!")
