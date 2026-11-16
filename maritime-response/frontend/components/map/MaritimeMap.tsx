"use client";

import React, { useEffect, useState } from "react";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  CircleMarker,
  Circle,
  Tooltip,
  useMap,
} from "react-leaflet";

import L from "leaflet";
import "leaflet/dist/leaflet.css";

/* ============================================================
   TYPES
============================================================ */

interface Vessel {
  id: number;
  name: string;
  registration_number: string;
  captain: string | null;
  latitude: number;
  longitude: number;
  speed: number;
  course: number | null;
  destination: string | null;
  status: string;
  is_active: boolean;
}

interface Incident {
  id: number;
  title: string;
  description: string | null;
  latitude: number;
  longitude: number;
  severity: string;
  status: string;
  reported_by: string | null;
}

/* ============================================================
   API
============================================================ */

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://192.168.1.5:8000";

/* ============================================================
   EDGE VESSEL ICON
============================================================ */

const edgeVesselIcon = L.divIcon({
  className: "",
  html: `
    <div
      style="
        width:20px;
        height:20px;
        background:#2563eb;
        border:3px solid white;
        border-radius:50%;
        box-shadow:0 2px 7px rgba(0,0,0,.4);
      "
    ></div>
  `,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
});

/* ============================================================
   AIS VESSEL ICON
============================================================ */

function createAISIcon(course: number | null) {
  const heading =
    course === null || Number.isNaN(course)
      ? 0
      : course;

  return L.divIcon({
    className: "",
    html: `
      <div
        style="
          width:34px;
          height:34px;
          position:relative;
          transform:rotate(${heading}deg);
          transform-origin:center center;
        "
      >

        <div
          style="
            position:absolute;
            left:50%;
            top:2px;
            transform:translateX(-50%);
            width:0;
            height:0;
            border-left:8px solid transparent;
            border-right:8px solid transparent;
            border-bottom:20px solid #0f766e;
            filter:drop-shadow(0 2px 2px rgba(0,0,0,.35));
          "
        ></div>

        <div
          style="
            position:absolute;
            left:50%;
            top:13px;
            transform:translateX(-50%);
            width:12px;
            height:12px;
            background:#14b8a6;
            border:2px solid white;
            border-radius:50%;
            box-shadow:0 1px 5px rgba(0,0,0,.4);
          "
        ></div>

      </div>
    `,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
  });
}

/* ============================================================
   INCIDENT COLOR
============================================================ */

function getIncidentColor(severity: string) {
  switch (severity?.toUpperCase()) {
    case "CRITICAL":
      return "#dc2626";

    case "HIGH":
      return "#ea580c";

    case "MEDIUM":
      return "#d97706";

    case "LOW":
      return "#16a34a";

    default:
      return "#64748b";
  }
}

/* ============================================================
   MAP LEGEND
============================================================ */

function MapLegend() {
  return (
    <div className="absolute bottom-5 left-5 z-[1000] rounded-xl bg-white p-4 shadow-lg ring-1 ring-slate-200">

      <div className="mb-3 flex items-center justify-between gap-6">

        <span className="text-sm font-semibold text-slate-900">
          Map Legend
        </span>

        <span className="flex items-center gap-1.5 text-xs font-medium text-green-600">
          <span className="h-2 w-2 rounded-full bg-green-500" />
          Live
        </span>

      </div>

      <div className="space-y-2 text-xs text-slate-600">

        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full border-2 border-white bg-blue-600 shadow" />
          Edge Vessel
        </div>

        <div className="flex items-center gap-2">

          <span
            style={{
              display: "inline-block",
              width: 0,
              height: 0,
              borderLeft: "6px solid transparent",
              borderRight: "6px solid transparent",
              borderBottom: "12px solid #0f766e",
            }}
          />

          AIS Vessel

        </div>

        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full bg-red-600" />
          Critical Incident
        </div>

        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full bg-orange-600" />
          High Severity
        </div>

      </div>

    </div>
  );
}

/* ============================================================
   MAP BOUNDS
============================================================ */

function MapBounds({
  vessels,
  incidents,
}: {
  vessels: Vessel[];
  incidents: Incident[];
}) {
  const map = useMap();

  useEffect(() => {
    const points: [number, number][] = [
      ...vessels
        .filter(
          (vessel) =>
            Number.isFinite(vessel.latitude) &&
            Number.isFinite(vessel.longitude)
        )
        .map(
          (vessel) =>
            [
              vessel.latitude,
              vessel.longitude,
            ] as [number, number]
        ),

      ...incidents
        .filter(
          (incident) =>
            Number.isFinite(incident.latitude) &&
            Number.isFinite(incident.longitude)
        )
        .map(
          (incident) =>
            [
              incident.latitude,
              incident.longitude,
            ] as [number, number]
        ),
    ];

    if (points.length > 0) {
      map.fitBounds(points, {
        padding: [60, 60],
        maxZoom: 12,
      });
    }
  }, [map, vessels, incidents]);

  return null;
}

/* ============================================================
   MAIN MAP
============================================================ */

export default function MaritimeMap() {

  const [vessels, setVessels] =
    useState<Vessel[]>([]);

  const [incidents, setIncidents] =
    useState<Incident[]>([]);

  const [loading, setLoading] =
    useState(true);

  /* ==========================================================
     LOAD DATA
  ========================================================== */

  async function loadData() {
    try {

      console.log(
        "🌐 Loading maritime data from:",
        API_URL
      );

      const [
        vesselsResponse,
        incidentsResponse,
      ] = await Promise.all([
        fetch(
          `${API_URL}/vessels/`,
          {
            cache: "no-store",
          }
        ),

        fetch(
          `${API_URL}/incidents/`,
          {
            cache: "no-store",
          }
        ),
      ]);

      console.log(
        "🚢 Vessels API:",
        vesselsResponse.status
      );

      console.log(
        "🚨 Incidents API:",
        incidentsResponse.status
      );

      if (
        !vesselsResponse.ok ||
        !incidentsResponse.ok
      ) {
        throw new Error(
          "Failed to load maritime data"
        );
      }

      const vesselsData: Vessel[] =
        await vesselsResponse.json();

      const incidentsData: Incident[] =
        await incidentsResponse.json();

      console.log(
        "🚢 Vessels received:",
        vesselsData
      );

      console.log(
        "🚨 All incidents received:",
        incidentsData
      );

      /* ======================================================
         VALID VESSELS
      ====================================================== */

      const validVessels =
        vesselsData.filter(
          (vessel) =>
            Number.isFinite(vessel.latitude) &&
            Number.isFinite(vessel.longitude)
        );

      /* ======================================================
         ACTIVE INCIDENTS ONLY
      ====================================================== */

      const activeIncidents =
        incidentsData.filter(
          (incident) => {

            const isActive =
              incident.status?.toUpperCase() ===
              "ACTIVE";

            const validCoordinates =
              Number.isFinite(
                incident.latitude
              ) &&
              Number.isFinite(
                incident.longitude
              );

            return (
              isActive &&
              validCoordinates
            );
          }
        );

      console.log(
        "🚨 ACTIVE INCIDENTS:",
        activeIncidents
      );

      setVessels(
        validVessels
      );

      setIncidents(
        activeIncidents
      );

    } catch (error) {

      console.error(
        "❌ Map data error:",
        error
      );

    } finally {

      setLoading(false);

    }
  }

  /* ==========================================================
     LIVE UPDATE EVERY 5 SECONDS
  ========================================================== */

  useEffect(() => {

    loadData();

    const interval =
      setInterval(
        loadData,
        5000
      );

    return () => {
      clearInterval(
        interval
      );
    };

  }, []);

  /* ==========================================================
     RENDER
  ========================================================== */

  return (
    <div className="relative h-[650px] w-full overflow-hidden rounded-xl shadow-sm ring-1 ring-slate-200">

      {/* ======================================================
          LOADING
      ====================================================== */}

      {loading && (
        <div className="absolute left-4 top-4 z-[1000] rounded-lg bg-white px-4 py-2 text-sm shadow">

          Loading maritime data...

        </div>
      )}

      {/* ======================================================
          MAP
      ====================================================== */}

      <MapContainer
        center={[
          12.97,
          74.78,
        ]}
        zoom={10}
        scrollWheelZoom={true}
        className="h-full w-full"
      >

        {/* ==================================================
            OPEN STREET MAP
        ================================================== */}

        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* ==================================================
            AUTOMATIC BOUNDS
        ================================================== */}

        <MapBounds
          vessels={vessels}
          incidents={incidents}
        />

        {/* ==================================================
            LEGEND
        ================================================== */}

        <MapLegend />

        {/* ==================================================
            VESSELS
        ================================================== */}

        {vessels.map(
          (vessel) => {

            const isAIS =
              vessel.registration_number
                .startsWith("AIS-");

            /* =================================================
               AIS VESSEL
            ================================================= */

            if (isAIS) {

              return (
                <Marker
                  key={`ais-vessel-${vessel.id}`}
                  position={[
                    vessel.latitude,
                    vessel.longitude,
                  ]}
                  icon={
                    createAISIcon(
                      vessel.course
                    )
                  }
                >

                  <Popup>

                    <div className="min-w-[220px]">

                      <strong className="text-base">
                        {vessel.name}
                      </strong>

                      <div className="mt-2 space-y-1 text-sm">

                        <div>
                          <strong>
                            Type:
                          </strong>{" "}
                          AIS Vessel
                        </div>

                        <div>
                          <strong>
                            Registration:
                          </strong>{" "}
                          {vessel.registration_number}
                        </div>

                        <div>
                          <strong>
                            Speed:
                          </strong>{" "}
                          {vessel.speed} knots
                        </div>

                        <div>
                          <strong>
                            Course:
                          </strong>{" "}
                          {vessel.course !== null
                            ? `${vessel.course}°`
                            : "Unknown"}
                        </div>

                        <div>
                          <strong>
                            Status:
                          </strong>{" "}
                          {vessel.status}
                        </div>

                        <div>
                          <strong>
                            Location:
                          </strong>{" "}
                          {vessel.latitude.toFixed(5)},
                          {" "}
                          {vessel.longitude.toFixed(5)}
                        </div>

                      </div>

                    </div>

                  </Popup>

                </Marker>
              );
            }

            /* =================================================
               EDGE VESSEL
            ================================================= */

            return (
              <Marker
                key={`edge-vessel-${vessel.id}`}
                position={[
                  vessel.latitude,
                  vessel.longitude,
                ]}
                icon={edgeVesselIcon}
              >

                <Popup>

                  <div className="min-w-[220px]">

                    <strong className="text-base">
                      {vessel.name}
                    </strong>

                    <div className="mt-2 space-y-1 text-sm">

                      <div>
                        <strong>
                          Type:
                        </strong>{" "}
                        Edge Vessel
                      </div>

                      <div>
                        <strong>
                          Registration:
                        </strong>{" "}
                        {vessel.registration_number}
                      </div>

                      <div>
                        <strong>
                          Captain:
                        </strong>{" "}
                        {vessel.captain ||
                          "Unknown"}
                      </div>

                      <div>
                        <strong>
                          Speed:
                        </strong>{" "}
                        {vessel.speed} knots
                      </div>

                      <div>
                        <strong>
                          Destination:
                        </strong>{" "}
                        {vessel.destination ||
                          "Not specified"}
                      </div>

                      <div>
                        <strong>
                          Status:
                        </strong>{" "}
                        {vessel.status}
                      </div>

                      <div>
                        <strong>
                          Location:
                        </strong>{" "}
                        {vessel.latitude.toFixed(5)},
                        {" "}
                        {vessel.longitude.toFixed(5)}
                      </div>

                    </div>

                  </div>

                </Popup>

              </Marker>
            );
          }
        )}

        {/* ==================================================
            INCIDENTS
            IMPORTANT:
            React.Fragment is used here.
            Do NOT wrap Leaflet layers in <div>.
        ================================================== */}

        {incidents.map(
          (incident) => {

            const color =
              getIncidentColor(
                incident.severity
              );

            const isCritical =
              incident.severity
                ?.toUpperCase() ===
              "CRITICAL";

            return (
              <React.Fragment
                key={`incident-${incident.id}`}
              >

                {/* ==========================================
                    CRITICAL INCIDENT OUTER RING
                ========================================== */}

                {isCritical && (
                  <Circle
                    center={[
                      incident.latitude,
                      incident.longitude,
                    ]}
                    radius={180}
                    pathOptions={{
                      color: color,
                      fillColor: color,
                      fillOpacity: 0.08,
                      weight: 2,
                    }}
                  />
                )}

                {/* ==========================================
                    INCIDENT MARKER
                ========================================== */}

                <CircleMarker
                  center={[
                    incident.latitude,
                    incident.longitude,
                  ]}
                  radius={
                    isCritical
                      ? 13
                      : 10
                  }
                  pathOptions={{
                    color: "#ffffff",
                    fillColor: color,
                    fillOpacity: 0.95,
                    weight: 4,
                  }}
                >

                  {/* ========================================
                      PERMANENT LABEL
                  ======================================== */}

                  <Tooltip
                    permanent
                    direction="top"
                    offset={[
                      0,
                      -10,
                    ]}
                  >

                    <span
                      style={{
                        fontWeight: 700,
                        fontSize: "12px",
                      }}
                    >
                      🚨 {incident.title}
                    </span>

                  </Tooltip>

                  {/* ========================================
                      INCIDENT POPUP
                  ======================================== */}

                  <Popup>

                    <div className="min-w-[240px]">

                      <div className="mb-2 flex items-center gap-2">

                        <span
                          className="inline-block h-4 w-4 rounded-full"
                          style={{
                            backgroundColor:
                              color,
                          }}
                        />

                        <strong className="text-base">
                          {incident.title}
                        </strong>

                      </div>

                      <div className="space-y-1 text-sm">

                        <div>
                          <strong>
                            Severity:
                          </strong>{" "}
                          {incident.severity}
                        </div>

                        <div>
                          <strong>
                            Status:
                          </strong>{" "}
                          {incident.status}
                        </div>

                        <div>
                          <strong>
                            Description:
                          </strong>{" "}
                          {incident.description ||
                            "No description"}
                        </div>

                        <div>
                          <strong>
                            Location:
                          </strong>{" "}
                          {incident.latitude.toFixed(5)},
                          {" "}
                          {incident.longitude.toFixed(5)}
                        </div>

                        <div>
                          <strong>
                            Reported by:
                          </strong>{" "}
                          {incident.reported_by ||
                            "Unknown"}
                        </div>

                      </div>

                    </div>

                  </Popup>

                </CircleMarker>

              </React.Fragment>
            );
          }
        )}

      </MapContainer>

    </div>
  );
}