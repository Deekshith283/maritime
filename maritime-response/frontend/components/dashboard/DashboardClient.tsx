"use client";

import KPISection from "@/app/(dashboard)/KPISection";
import VesselTable from "@/app/(dashboard)/VesselTable";
import AlertsPanel from "@/app/(dashboard)/AlertsPanel";
import WeatherCard from "@/app/(dashboard)/WeatherCard";
import MaritimeMapLoader from "@/components/map/MaritimeMapLoader";

export default function DashboardClient() {
  return (
    <div className="min-h-screen bg-slate-100 p-6">
      <div className="mx-auto max-w-7xl">

        {/* HEADER */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-slate-900">
            Maritime Safety Dashboard
          </h1>

          <p className="mt-1 text-slate-600">
            Monitor vessels, incidents, alerts, and maritime conditions.
          </p>
        </div>

        <div className="space-y-6">

          {/* KPI CARDS */}
          <KPISection />

          {/* VESSELS + WEATHER */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">

            <div className="lg:col-span-2">
              <VesselTable />
            </div>

            <div>
              <WeatherCard />
            </div>

          </div>

          {/* ACTIVE ALERTS */}
          <AlertsPanel />

          {/* LIVE MARITIME MAP */}
          <section className="rounded-xl bg-white shadow-sm ring-1 ring-slate-200">

            <div className="border-b border-slate-200 p-5">
              <h2 className="text-lg font-semibold text-slate-900">
                Maritime Map
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Live vessels and active maritime incidents.
              </p>
            </div>

            <div className="overflow-hidden rounded-b-xl">
              <MaritimeMapLoader />
            </div>

          </section>

        </div>
      </div>
    </div>
  );
}