import { VesselStatus } from "@/types/vessel";

interface Props {
  status: VesselStatus;
}

export default function VesselStatusBadge({ status }: Props) {
  const colors: Record<VesselStatus, string> = {
    ACTIVE: "bg-green-100 text-green-700",
    IN_PORT: "bg-blue-100 text-blue-700",
    EMERGENCY: "bg-red-100 text-red-700",
    OFFLINE: "bg-gray-200 text-gray-700",
  };

  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-semibold ${colors[status]}`}
    >
      {status.replace("_", " ")}
    </span>
  );
}