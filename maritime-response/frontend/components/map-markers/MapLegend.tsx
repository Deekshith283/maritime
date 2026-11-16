"use client";

export default function MapLegend() {
  return (
    <div className="rounded-lg border bg-white p-4 shadow-md">
      <h3 className="mb-3 font-semibold">Map Legend</h3>

      <div className="space-y-2 text-sm">
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full bg-red-600"></span>
          Incident
        </div>

        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full bg-blue-600"></span>
          Vessel
        </div>
      </div>
    </div>
  );
}