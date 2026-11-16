"use client";

import { Marker, Popup } from "react-leaflet";
import L from "leaflet";

interface Props {
  latitude: number;
  longitude: number;
  vesselName: string;
  status: string;
}

const vesselIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default function VesselMarker({
  latitude,
  longitude,
  vesselName,
  status,
}: Props) {
  return (
    <Marker position={[latitude, longitude]} icon={vesselIcon}>
      <Popup>
        <div>
          <h3 className="font-semibold">{vesselName}</h3>
          <p>Status: {status}</p>
        </div>
      </Popup>
    </Marker>
  );
}