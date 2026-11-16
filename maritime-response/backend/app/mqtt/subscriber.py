import json

import paho.mqtt.client as mqtt

from app.database.database import SessionLocal
from app.models.vessel import Vessel
from app.models.incident import Incident


# ============================================================
# MQTT CONFIGURATION
# ============================================================

BROKER = "localhost"
PORT = 1883
TOPIC = "maritime/sensors"


# ============================================================
# INCIDENT HELPERS
# ============================================================

def get_active_incident(db, title):
    return (
        db.query(Incident)
        .filter(
            Incident.title == title,
            Incident.status == "ACTIVE",
        )
        .first()
    )


def create_or_update_incident(
    db,
    title,
    description,
    severity,
    latitude,
    longitude,
):
    existing = get_active_incident(
        db,
        title,
    )

    if existing:
        existing.latitude = latitude
        existing.longitude = longitude
        existing.description = description
        existing.severity = severity

        print(
            f"♻️ Updated existing incident: {title}"
        )

    else:
        incident = Incident(
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            severity=severity,
            status="ACTIVE",
            reported_by="EDGE",
        )

        db.add(incident)

        print(
            f"🚨 New incident created: {title}"
        )


def resolve_incident(db, title):
    existing = get_active_incident(
        db,
        title,
    )

    if existing:
        existing.status = "RESOLVED"

        print(
            f"✅ Incident resolved: {title}"
        )


# ============================================================
# SAVE / UPDATE MAIN EDGE VESSEL
# ============================================================

def save_vessel(data):
    db = SessionLocal()

    try:
        gps = data.get(
            "gps",
            {},
        )

        latitude = gps.get(
            "latitude"
        )

        longitude = gps.get(
            "longitude"
        )

        if latitude is None or longitude is None:
            print(
                "⚠️ GPS data missing"
            )
            return

        # Find the main Edge vessel
        vessel = (
            db.query(Vessel)
            .filter(
                Vessel.registration_number == "EDGE001"
            )
            .first()
        )

        if vessel:

            vessel.latitude = latitude
            vessel.longitude = longitude

            # If your Edge payload later contains speed,
            # it will be stored here.
            if "speed" in data:
                vessel.speed = data.get(
                    "speed",
                    vessel.speed,
                )

            vessel.status = "ACTIVE"
            vessel.is_active = True

            print(
                f"🚢 Edge Vessel updated: "
                f"{latitude}, {longitude}"
            )

        else:

            vessel = Vessel(
                name="Edge Vessel",
                registration_number="EDGE001",
                captain="Unknown",
                latitude=latitude,
                longitude=longitude,
                speed=0,
                course=None,
                destination=None,
                status="ACTIVE",
                is_active=True,
            )

            db.add(vessel)

            print(
                f"🚢 Edge Vessel created: "
                f"{latitude}, {longitude}"
            )

        db.commit()

    except Exception as e:

        db.rollback()

        print(
            f"❌ Error saving Edge vessel: {e}"
        )

    finally:
        db.close()


# ============================================================
# SAVE / UPDATE AIS VESSELS
# ============================================================

def save_ais_vessels(data):
    db = SessionLocal()

    try:

        ais_vessels = data.get(
            "ais",
            [],
        )

        if not ais_vessels:

            print(
                "📡 No AIS vessels received"
            )

            return

        saved_count = 0

        # ----------------------------------------------------
        # PROCESS EACH AIS VESSEL
        # ----------------------------------------------------

        for ais in ais_vessels:

            vessel_id = ais.get(
                "vessel_id"
            )

            latitude = ais.get(
                "latitude"
            )

            longitude = ais.get(
                "longitude"
            )

            speed = ais.get(
                "speed",
                0,
            )

            course = ais.get(
                "course",
                0,
            )

            # ------------------------------------------------
            # VALIDATE VESSEL ID
            # ------------------------------------------------

            if not vessel_id:

                print(
                    "⚠️ AIS vessel missing vessel_id"
                )

                continue

            # ------------------------------------------------
            # VALIDATE GPS
            # ------------------------------------------------

            if latitude is None or longitude is None:

                print(
                    f"⚠️ AIS vessel {vessel_id} "
                    "missing GPS"
                )

                continue

            # ------------------------------------------------
            # NORMALIZE COURSE
            # ------------------------------------------------

            if course is None:
                course = 0

            try:
                course = float(course)
            except (TypeError, ValueError):
                course = 0

            # Keep course between 0 and 359 degrees
            course = course % 360

            # ------------------------------------------------
            # UNIQUE AIS REGISTRATION NUMBER
            # ------------------------------------------------

            registration_number = (
                f"AIS-{vessel_id}"
            )

            # ------------------------------------------------
            # FIND EXISTING AIS VESSEL
            # ------------------------------------------------

            vessel = (
                db.query(Vessel)
                .filter(
                    Vessel.registration_number
                    == registration_number
                )
                .first()
            )

            # ------------------------------------------------
            # UPDATE EXISTING AIS VESSEL
            # ------------------------------------------------

            if vessel:

                vessel.latitude = latitude
                vessel.longitude = longitude
                vessel.speed = speed

                # IMPORTANT:
                # Store the AIS course in PostgreSQL.
                vessel.course = course

                vessel.status = "ACTIVE"
                vessel.is_active = True

                print(
                    f"📡 AIS vessel updated: "
                    f"{vessel_id} | "
                    f"{latitude}, {longitude} | "
                    f"{speed} knots | "
                    f"course {course}°"
                )

            # ------------------------------------------------
            # CREATE NEW AIS VESSEL
            # ------------------------------------------------

            else:

                vessel = Vessel(
                    name=vessel_id,
                    registration_number=registration_number,
                    captain="AIS",
                    latitude=latitude,
                    longitude=longitude,
                    speed=speed,

                    # IMPORTANT:
                    # Store course when creating vessel.
                    course=course,

                    destination=None,
                    status="ACTIVE",
                    is_active=True,
                )

                db.add(vessel)

                print(
                    f"📡 AIS vessel created: "
                    f"{vessel_id} | "
                    f"{latitude}, {longitude} | "
                    f"{speed} knots | "
                    f"course {course}°"
                )

            saved_count += 1

        # ----------------------------------------------------
        # COMMIT ALL AIS CHANGES
        # ----------------------------------------------------

        db.commit()

        print(
            f"📡 AIS vessels processed: "
            f"{saved_count}"
        )

    except Exception as e:

        db.rollback()

        print(
            f"❌ Error saving AIS vessels: {e}"
        )

    finally:
        db.close()


# ============================================================
# SAVE INCIDENTS
# ============================================================

def save_incidents(data):
    db = SessionLocal()

    try:

        gps = data.get(
            "gps",
            {},
        )

        latitude = gps.get(
            "latitude"
        )

        longitude = gps.get(
            "longitude"
        )

        if latitude is None or longitude is None:

            print(
                "⚠️ Cannot save incidents without GPS"
            )

            return

        # ====================================================
        # FIRE
        # ====================================================

        fire_detected = data.get(
            "fire",
            {},
        ).get(
            "fire_detected",
            False,
        )

        if fire_detected:

            create_or_update_incident(
                db,
                "FIRE",
                "Fire detected onboard",
                "CRITICAL",
                latitude,
                longitude,
            )

        else:

            resolve_incident(
                db,
                "FIRE",
            )

        # ====================================================
        # WATER
        # ====================================================

        water_detected = data.get(
            "water",
            {},
        ).get(
            "water_detected",
            False,
        )

        if water_detected:

            create_or_update_incident(
                db,
                "WATER",
                "Water ingress detected",
                "HIGH",
                latitude,
                longitude,
            )

        else:

            resolve_incident(
                db,
                "WATER",
            )

        # ====================================================
        # ENGINE
        # ====================================================

        engine_ok = data.get(
            "engine",
            {},
        ).get(
            "engine_ok",
            True,
        )

        if not engine_ok:

            create_or_update_incident(
                db,
                "ENGINE",
                "Engine operating outside safe limits",
                "HIGH",
                latitude,
                longitude,
            )

        else:

            resolve_incident(
                db,
                "ENGINE",
            )

        # ====================================================
        # PANIC
        # ====================================================

        panic_pressed = data.get(
            "panic",
            {},
        ).get(
            "panic_pressed",
            False,
        )

        if panic_pressed:

            create_or_update_incident(
                db,
                "PANIC",
                "Emergency SOS activated",
                "CRITICAL",
                latitude,
                longitude,
            )

        else:

            resolve_incident(
                db,
                "PANIC",
            )

        db.commit()

        print(
            "💾 Incident data saved to PostgreSQL"
        )

    except Exception as e:

        db.rollback()

        print(
            f"❌ Error saving incidents: {e}"
        )

    finally:
        db.close()


# ============================================================
# MQTT CONNECT CALLBACK
# ============================================================

def on_connect(
    client,
    userdata,
    flags,
    rc,
):

    if rc == 0:

        print(
            "✅ MQTT Connected"
        )

        client.subscribe(
            TOPIC
        )

        print(
            f"📡 Subscribed to {TOPIC}"
        )

    else:

        print(
            f"❌ MQTT connection failed. "
            f"Return code: {rc}"
        )


# ============================================================
# MQTT MESSAGE CALLBACK
# ============================================================

def on_message(
    client,
    userdata,
    msg,
):

    print(
        "\n"
        + "=" * 60
    )

    print(
        "🔥 MQTT MESSAGE RECEIVED"
    )

    print(
        "=" * 60
    )

    try:

        raw_payload = (
            msg.payload.decode()
        )

        print(
            "Raw payload:"
        )

        print(
            raw_payload
        )

        # ----------------------------------------------------
        # PARSE JSON
        # ----------------------------------------------------

        data = json.loads(
            raw_payload
        )

        print(
            "\nParsed data:"
        )

        print(
            data
        )

        # ----------------------------------------------------
        # SAVE MAIN EDGE VESSEL
        # ----------------------------------------------------

        save_vessel(
            data
        )

        # ----------------------------------------------------
        # SAVE AIS VESSELS
        # ----------------------------------------------------

        save_ais_vessels(
            data
        )

        # ----------------------------------------------------
        # SAVE INCIDENTS
        # ----------------------------------------------------

        save_incidents(
            data
        )

        print(
            "\n💾 Data saved to PostgreSQL"
        )

    except json.JSONDecodeError as e:

        print(
            f"❌ Invalid JSON payload: {e}"
        )

    except Exception as e:

        print(
            f"❌ MQTT message processing error: {e}"
        )


# ============================================================
# MQTT CLIENT
# ============================================================

client = mqtt.Client()

client.on_connect = on_connect

client.on_message = on_message


# ============================================================
# START MQTT
# ============================================================

def start_mqtt():

    print(
        "Starting MQTT..."
    )

    try:

        client.connect(
            BROKER,
            PORT,
            60,
        )

        print(
            "Connected, starting loop..."
        )

        client.loop_start()

        print(
            "Loop started."
        )

    except Exception as e:

        print(
            f"❌ MQTT connection error: {e}"
        )