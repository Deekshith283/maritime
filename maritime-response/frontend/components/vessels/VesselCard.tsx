import { Vessel } from "@/types/vessel";
import VesselStatusBadge from "./VesselStatusBadge";

interface Props {
  vessel: Vessel;
}

export default function VesselCard({ vessel }: Props) {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          {vessel.name}
        </h2>

        <VesselStatusBadge status={vessel.status} />
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="font-medium">Registration:</span>{" "}
          {vessel.registrationNumber}
        </div>

        <div>
          <span className="font-medium">Captain:</span>{" "}
          {vessel.captain}
        </div>

        <div>
          <span className="font-medium">Destination:</span>{" "}
          {vessel.destination}
        </div>

        <div>
          <span className="font-medium">Speed:</span>{" "}
          {vessel.speed} knots
        </div>

        {"latitude" in vessel && (
          <div>
            <span className="font-medium">Latitude:</span>{" "}
            {vessel.latitude}
          </div>
        )}

        {"longitude" in vessel && (
          <div>
            <span className="font-medium">Longitude:</span>{" "}
            {vessel.longitude}
          </div>
        )}
      </div>
    </div>
  );
}