"use client";

import { Marker, Popup } from "react-leaflet";
import L from "leaflet";

interface Props {
  latitude: number;
  longitude: number;
  title: string;
  severity: string;
}

const incidentIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default function IncidentMarker({
  latitude,
  longitude,
  title,
  severity,
}: Props) {
  return (
    <Marker position={[latitude, longitude]} icon={incidentIcon}>
      <Popup>
        <div>
          <h3 className="font-semibold">{title}</h3>
          <p>Severity: {severity}</p>
        </div>
      </Popup>
    </Marker>
  );
}