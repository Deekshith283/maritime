"use client";

import { Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { Incident } from "@/types/incident";

interface Props {
  incident: Incident;
}

const incidentIcon = new L.Icon({
  iconUrl: "/icons/incident-marker.png",
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

export default function IncidentMapMarker({
  incident,
}: Props) {
  return (
    <Marker
      position={[incident.latitude, incident.longitude]}
      icon={incidentIcon}
    >
      <Popup>
        <div className="space-y-2">
          <h3 className="font-semibold">
            {incident.title}
          </h3>

          <p>{incident.description}</p>

          <p>
            <strong>Status:</strong>{" "}
            {incident.status.replace("_", " ")}
          </p>

          <p>
            <strong>Severity:</strong>{" "}
            {incident.severity}
          </p>
        </div>
      </Popup>
    </Marker>
  );
}