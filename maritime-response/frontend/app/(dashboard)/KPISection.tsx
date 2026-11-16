"use client";

import { useEffect, useState } from "react";

interface Vessel {
  id: number;
  name: string;
  status: string;
  is_active: boolean;
  speed: number;
}

interface Incident {
  id: number;
  severity: string;
  status: string;
  title: string;
}

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://192.168.1.5:8000";

export default function KPISection() {
  const [vessels, setVessels] = useState<Vessel[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  async function loadDashboardData() {
    try {
      const [
        vesselsResponse,
        incidentsResponse,
      ] = await Promise.all([
        fetch(`${API_URL}/vessels/`, {
          cache: "no-store",
        }),

        fetch(`${API_URL}/incidents/`, {
          cache: "no-store",
        }),
      ]);

      if (!vesselsResponse.ok) {
        throw new Error(
          `Vessels API HTTP ${vesselsResponse.status}`
        );
      }

      if (!incidentsResponse.ok) {
        throw new Error(
          `Incidents API HTTP ${incidentsResponse.status}`
        );
      }

      const vesselsData: Vessel[] =
        await vesselsResponse.json();

      const incidentsData: Incident[] =
        await incidentsResponse.json();

      setVessels(vesselsData);
      setIncidents(incidentsData);

    } catch (error) {
      console.error(
        "Failed to load dashboard data:",
        error
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboardData();

    const interval = setInterval(
      loadDashboardData,
      5000
    );

    return () => {
      clearInterval(interval);
    };
  }, []);

  /* =========================================================
     ACTIVE VESSELS
  ========================================================= */

  const activeVessels =
    vessels.filter(
      (vessel) =>
        vessel.is_active === true &&
        vessel.status?.toUpperCase() ===
          "ACTIVE"
    ).length;

  /* =========================================================
     VESSELS IN PORT

     Count only vessels explicitly marked
     as IN PORT / DOCKED.

     We do NOT assume speed = 0 means
     the vessel is in port.
  ========================================================= */

  const vesselsInPort =
    vessels.filter((vessel) => {
      const status =
        vessel.status?.toUpperCase();

      return (
        status === "IN PORT" ||
        status === "DOCKED"
      );
    }).length;

  /* =========================================================
     ACTIVE INCIDENTS
  ========================================================= */

  const activeIncidents =
    incidents.filter(
      (incident) =>
        incident.status?.toUpperCase() ===
        "ACTIVE"
    ).length;

  /* =========================================================
     ACTIVE ALERTS

     Only HIGH and CRITICAL incidents.
  ========================================================= */

  const activeAlerts =
    incidents.filter((incident) => {
      const status =
        incident.status?.toUpperCase();

      const severity =
        incident.severity?.toUpperCase();

      return (
        status === "ACTIVE" &&
        (
          severity === "CRITICAL" ||
          severity === "HIGH"
        )
      );
    }).length;

  /* =========================================================
     KPI DATA
  ========================================================= */

  const kpis = [
    {
      title: "Active Vessels",
      value: loading
        ? "..."
        : activeVessels,
      subtitle:
        "Currently monitored",
    },

    {
      title: "Active Incidents",
      value: loading
        ? "..."
        : activeIncidents,
      subtitle:
        "Requiring attention",
    },

    {
      title: "Active Alerts",
      value: loading
        ? "..."
        : activeAlerts,
      subtitle:
        "Critical and high severity",
    },

    {
      title: "Vessels in Port",
      value: loading
        ? "..."
        : vesselsInPort,
      subtitle:
        "Currently docked",
    },
  ];

  /* =========================================================
     UI
  ========================================================= */

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">

      {kpis.map((kpi) => (
        <div
          key={kpi.title}
          className="
            rounded-xl
            bg-white
            p-5
            shadow-sm
            ring-1
            ring-slate-200
            transition
            hover:shadow-md
          "
        >

          <p className="text-sm font-medium text-slate-500">
            {kpi.title}
          </p>

          <p className="mt-2 text-3xl font-bold text-slate-900">
            {kpi.value}
          </p>

          <p className="mt-1 text-xs text-slate-500">
            {kpi.subtitle}
          </p>

        </div>
      ))}

    </div>
  );
}