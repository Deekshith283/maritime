interface Props {
  status: "ACTIVE" | "IN_PROGRESS" | "RESOLVED";
}

export default function IncidentStatusBadge({
  status,
}: Props) {
  const colors = {
    ACTIVE: "bg-red-100 text-red-700",
    IN_PROGRESS: "bg-yellow-100 text-yellow-700",
    RESOLVED: "bg-green-100 text-green-700",
  };

  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-semibold ${colors[status]}`}
    >
      {status.replace("_", " ")}
    </span>
  );
}