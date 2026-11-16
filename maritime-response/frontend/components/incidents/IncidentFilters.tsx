interface IncidentFiltersProps {
  search: string;
  onSearchChange: (value: string) => void;

  status: string;
  onStatusChange: (value: string) => void;
}

export default function IncidentFilters({
  search,
  onSearchChange,
  status,
  onStatusChange,
}: IncidentFiltersProps) {
  return (
    <div className="flex flex-col gap-4 rounded-xl border bg-white p-4 shadow-sm md:flex-row md:items-center md:justify-between">
      {/* Search */}
      <input
        type="text"
        placeholder="Search incidents..."
        value={search}
        onChange={(e) => onSearchChange(e.target.value)}
        className="w-full rounded-lg border px-4 py-2 outline-none focus:ring-2 focus:ring-red-500 md:w-80"
      />

      {/* Status Filter */}
      <select
        value={status}
        onChange={(e) => onStatusChange(e.target.value)}
        className="rounded-lg border px-4 py-2 outline-none focus:ring-2 focus:ring-red-500"
      >
        <option value="ALL">All Status</option>
        <option value="ACTIVE">Active</option>
        <option value="IN_PROGRESS">In Progress</option>
        <option value="RESOLVED">Resolved</option>
      </select>
    </div>
  );
}