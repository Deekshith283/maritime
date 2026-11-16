"use client";

export default function WeatherCard() {
  return (
    <div className="rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <h2 className="text-lg font-semibold text-slate-900">
        Maritime Conditions
      </h2>

      <p className="mt-1 text-sm text-slate-500">
        Current monitoring area
      </p>

      <div className="mt-6">
        <div className="text-4xl font-bold text-slate-900">
          28°C
        </div>

        <p className="mt-1 text-sm text-slate-500">
          Coastal conditions
        </p>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="rounded-lg bg-slate-50 p-3">
          <p className="text-xs text-slate-500">Wind</p>
          <p className="mt-1 font-semibold text-slate-800">
            12 knots
          </p>
        </div>

        <div className="rounded-lg bg-slate-50 p-3">
          <p className="text-xs text-slate-500">Visibility</p>
          <p className="mt-1 font-semibold text-slate-800">
            Good
          </p>
        </div>

        <div className="rounded-lg bg-slate-50 p-3">
          <p className="text-xs text-slate-500">Wave Height</p>
          <p className="mt-1 font-semibold text-slate-800">
            1.2 m
          </p>
        </div>

        <div className="rounded-lg bg-slate-50 p-3">
          <p className="text-xs text-slate-500">Sea State</p>
          <p className="mt-1 font-semibold text-slate-800">
            Moderate
          </p>
        </div>
      </div>
    </div>
  );
}
