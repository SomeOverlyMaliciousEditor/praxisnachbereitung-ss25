from fastapi import FastAPI, Request, Response, Query, HTTPException, status, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from .db import get_conn

import os, io, csv, json
import paho.mqtt.client as mqtt

app = FastAPI(title="Inventar-App", version="0.1.0")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

MQTT_HOST = os.getenv("MQTT_HOST", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))


def mqtt_client() -> mqtt.Client:
    c = mqtt.Client()
    c.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
    return c


@app.get("/health")
async def health():
    db_state = "ok"
    mqtt_state = "ok"
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("select 1")
            cur.fetchone()
    except Exception as ex:
        db_state = f"error:{type(ex).__name__}"

    try:
        c = mqtt_client()
        c.disconnect()
    except Exception as ex:
        mqtt_state = f"degraded:{type(ex).__name__}"

    return {"status": "ok" if db_state == "ok" else "degraded", "db": db_state, "mqtt": mqtt_state}

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Inventar-App"})


# --------- Modelle ---------

class DeviceCreate(BaseModel):
    device_type_id: int
    location_id: int
    serial_number: str
    inventory_code: str | None = None
    note: str | None = None


class AssignmentCreate(BaseModel):
    device_id: int
    person_id: int


# --------- Devices-API ---------

@app.get("/devices")
async def list_devices():
    sql = """
    select d.device_id, d.serial_number, d.inventory_code, d.note,
           dt.name as device_type_name,
           l.name  as location_name
    from device d
    join device_type dt on dt.device_type_id = d.device_type_id
    join location     l on l.location_id     = d.location_id
    order by d.device_id;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return rows


@app.post("/devices", status_code=status.HTTP_201_CREATED)
async def create_device(payload: DeviceCreate):
    sql = """
    insert into device (device_type_id, location_id, serial_number, inventory_code, note)
    values (%(device_type_id)s, %(location_id)s, %(serial_number)s, %(inventory_code)s, %(note)s)
    returning device_id;
    """
    data = payload.dict()
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql, data)
            row = cur.fetchone()
    except Exception as ex:
        # IR-01: serial_number ist eindeutig -> Verletzung ergibt 409
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ex))

    return {"device_id": row["device_id"], **data}


# --------- Assignments-API ---------

@app.get("/assignments/active")
async def list_active_assignments():
    sql = """
    select a.assignment_id, a.device_id, a.person_id, a.issued_at, a.returned_at,
           d.serial_number,
           dt.name as device_type_name,
           p.first_name, p.last_name
    from assignment a
    join device      d  on d.device_id      = a.device_id
    join device_type dt on dt.device_type_id = d.device_type_id
    join person      p  on p.person_id      = a.person_id
    where a.returned_at is null
    order by a.issued_at desc;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return rows


@app.post("/assignments", status_code=status.HTTP_201_CREATED)
async def create_assignment(payload: AssignmentCreate):
    # IR-02: Ein Device darf maximal eine aktive Ausleihe haben
    check_sql = """
        select 1 from assignment
        where device_id = %(device_id)s and returned_at is null
        limit 1;
    """
    insert_sql = """
        insert into assignment (device_id, person_id)
        values (%(device_id)s, %(person_id)s)
        returning assignment_id, issued_at, returned_at;
    """
    data = payload.dict()
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(check_sql, {"device_id": data["device_id"]})
        exists = cur.fetchone()
        if exists:
            # zweite aktive Ausleihe -> 409
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Device already has an active assignment",
            )

        cur.execute(insert_sql, data)
        row = cur.fetchone()

    # MQTT-Event für Ausleihe
    c = mqtt_client()
    mqtt_data = json.dumps(
        {
            "assignment_id": row["assignment_id"],
            "device_id": data["device_id"],
            "person_id": data["person_id"],
            "issued_at": row["issued_at"].isoformat(),
        }
    )
    c.publish("inventory/assignments/issued", mqtt_data, qos=0, retain=False)
    c.disconnect()

    return row


@app.post("/assignments/{assignment_id}/return")
async def return_assignment(assignment_id: int):
    sql = """
        update assignment
        set returned_at = now()
        where assignment_id = %(assignment_id)s and returned_at is null
        returning assignment_id, device_id, person_id, issued_at, returned_at;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, {"assignment_id": assignment_id})
        row = cur.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active assignment not found",
            )

    # MQTT-Event: Rückgabe
    c = mqtt_client()
    mqtt_data = json.dumps(
        {
            "assignment_id": assignment_id,
            "device_id": row["device_id"],
            "person_id": row["person_id"],
            "returned_at": row["returned_at"].isoformat(),
        }
    )
    c.publish("inventory/assignments/returned", mqtt_data, qos=0, retain=False)
    c.disconnect()

    return row


# --------- CSV-Report wie im Starter (optional weiter nutzbar) ---------

@app.get("/reports/device-status")
async def device_status():
    sql = """
    select status, count(*) as cnt
    from device
    group by status
    order by status;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return rows

@app.get("/reports/device-status.csv")
async def device_status_csv():
    sql = """
    select status, count(*) as cnt
    from device
    group by status
    order by status;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["status", "cnt"], delimiter=";", lineterminator="\n")
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

    data = buf.getvalue().encode("utf-8-sig")
    headers = {"Content-Disposition": 'attachment; filename="device-status.csv"'}
    return Response(content=data, media_type="text/csv; charset=utf-8", headers=headers)

@app.post("/mqtt/publish")
async def mqtt_publish(topic: str = Query(...), payload: str = Query(...)):
    c = mqtt_client()
    c.publish(topic, payload, qos=0, retain=False)
    c.disconnect()
    return {"ok": True, "topic": topic, "payload": payload}


#---------------------------------------------------


# 1) Inventar-Übersichtsseite
@app.get("/inventory")
async def inventory_overview(request: Request):
    sql_devices = """
        select d.device_id,
               d.serial_number,
               d.inventory_code,
               d.note,
               dt.name as device_type_name,
               l.name  as location_name,
               case
                   when exists (
                       select 1 from assignment a
                       where a.device_id = d.device_id
                         and a.returned_at is null
                   )
                   then 'ausgeliehen'
                   else 'frei'
               end as status
        from device d
        join device_type dt on dt.device_type_id = d.device_type_id
        join location     l on l.location_id     = d.location_id
        order by d.device_id;
    """

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql_devices)
        devices = cur.fetchall()

    return templates.TemplateResponse(
        "inventory.html",
        {
            "request": request,
            "title": "Inventar",
            "devices": devices,
        },
    )


# 2) Formular „Gerät hinzufügen“ (GET zeigt Formular)
@app.get("/inventory/devices/new")
async def new_device_form(request: Request):
    sql_types = "select device_type_id, name from device_type order by name;"
    sql_locations = "select location_id, name from location order by name;"

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql_types)
        device_types = cur.fetchall()
        cur.execute(sql_locations)
        locations = cur.fetchall()

    return templates.TemplateResponse(
        "device_form.html",
        {
            "request": request,
            "title": "Gerät hinzufügen",
            "device_types": device_types,
            "locations": locations,
        },
    )


# 3) Formular-Submit „Gerät hinzufügen“ (POST verarbeitet Formular)
@app.post("/inventory/devices/new")
async def create_device_from_form(
    request: Request,
    device_type_id: int = Form(...),
    location_id: int = Form(...),
    serial_number: str = Form(...),
    inventory_code: str | None = Form(None),
    note: str | None = Form(None),
    ):
    sql = """
        insert into device (device_type_id, location_id, serial_number, inventory_code, note)
        values (%(device_type_id)s, %(location_id)s, %(serial_number)s, %(inventory_code)s, %(note)s);
    """
    data = {
        "device_type_id": device_type_id,
        "location_id": location_id,
        "serial_number": serial_number,
        "inventory_code": inventory_code,
        "note": note,
    }

    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql, data)
    except Exception as ex:
        # IR-01: serial_number eindeutig -> Fehler z. B. wieder auf Formularseite zurückleiten
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Device with serial_number '{serial_number}' already exists or invalid data: {ex}",
        )

    # Nach erfolgreichem Insert zurück zur Übersicht
    return RedirectResponse(url="/inventory", status_code=status.HTTP_303_SEE_OTHER)