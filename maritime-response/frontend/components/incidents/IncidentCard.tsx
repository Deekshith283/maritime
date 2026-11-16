import { Incident } from "@/types/incident";
import IncidentStatusBadge from "./IncidentStatusBadge";

interface Props {
  incident: Incident;
}

export default function IncidentCard({
  incident,
}: Props) {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          {incident.title}
        </h2>

        <IncidentStatusBadge
          status={incident.status}
        />
      </div>

      <p className="mb-4 text-gray-600">
        {incident.description}
      </p>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="font-medium">
            Severity:
          </span>{" "}
          {incident.severity}
        </div>

        <div>
          <span className="font-medium">
            Reported By:
          </span>{" "}
          {incident.reportedBy}
        </div>

        <div>
          <span className="font-medium">
            Latitude:
          </span>{" "}
          {incident.latitude}
        </div>

        <div>
          <span className="font-medium">
            Longitude:
          </span>{" "}
          {incident.longitude}
        </div>

        <div className="col-span-2">
          <span className="font-medium">
            Reported At:
          </span>{" "}
          {new Date(incident.createdAt).toLocaleString()}
        </div>
      </div>
    </div>
  );
}