import MaritimeMapLoader from "@/components/map/MaritimeMapLoader";

export default function MapPage() {
  return (
    <div className="min-h-screen bg-slate-100 p-6">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-slate-900">
            Maritime Map
          </h1>

          <p className="mt-1 text-slate-600">
            Live vessels and active maritime incidents.
          </p>
        </div>

        <MaritimeMapLoader />
      </div>
    </div>
  );
}
