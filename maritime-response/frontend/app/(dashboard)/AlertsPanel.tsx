"use client";

import { useEffect, useState } from "react";

interface Incident {
  id: number;
  title: string;
  description: string | null;
  latitude: number;
  longitude: number;
  severity: string;
  status: string;
  reported_by: string | null;
}

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://192.168.1.5:8000";

function getSeverityStyles(severity: string) {
  switch (severity.toUpperCase()) {
    case "CRITICAL":
      return {
        badge:
          "bg-red-100 text-red-700",
        dot:
          "bg-red-600",
        border:
          "border-l-red-600",
      };

    case "HIGH":
      return {
        badge:
          "bg-orange-100 text-orange-700",
        dot:
          "bg-orange-600",
        border:
          "border-l-orange-600",
      };

    case "MEDIUM":
      return {
        badge:
          "bg-amber-100 text-amber-700",
        dot:
          "bg-amber-500",
        border:
          "border-l-amber-500",
      };

    case "LOW":
      return {
        badge:
          "bg-emerald-100 text-emerald-700",
        dot:
          "bg-emerald-500",
        border:
          "border-l-emerald-500",
      };

    default:
      return {
        badge:
          "bg-slate-100 text-slate-600",
        dot:
          "bg-slate-500",
        border:
          "border-l-slate-500",
      };
  }
}

export default function AlertsPanel() {
  const [incidents, setIncidents] =
    useState<Incident[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  async function loadIncidents() {
    try {
      const response = await fetch(
        `${API_URL}/incidents/`,
        {
          cache: "no-store",
        }
      );

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      const data: Incident[] =
        await response.json();

      /* =====================================================
         ACTIVE INCIDENTS ONLY
      ===================================================== */

      const activeIncidents =
        data.filter(
          (incident) =>
            incident.status
              ?.toUpperCase() ===
            "ACTIVE"
        );

      /* =====================================================
         SORT:
         CRITICAL → HIGH → MEDIUM → LOW
      ===================================================== */

      const severityOrder: Record<
        string,
        number
      > = {
        CRITICAL: 1,
        HIGH: 2,
        MEDIUM: 3,
        LOW: 4,
      };

      activeIncidents.sort(
        (a, b) =>
          (severityOrder[
            a.severity?.toUpperCase()
          ] || 99) -
          (severityOrder[
            b.severity?.toUpperCase()
          ] || 99)
      );

      setIncidents(
        activeIncidents
      );

      setError("");

    } catch (err) {

      console.error(
        "Failed to load incidents:",
        err
      );

      setError(
        "Unable to load safety alerts."
      );

    } finally {

      setLoading(false);

    }
  }

  /* =========================================================
     LIVE UPDATE
  ========================================================= */

  useEffect(() => {

    loadIncidents();

    const interval =
      setInterval(
        loadIncidents,
        5000
      );

    return () => {
      clearInterval(interval);
    };

  }, []);

  return (
    <div className="rounded-xl bg-white shadow-sm ring-1 ring-slate-200">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="border-b border-slate-200 p-5">

        <div className="flex items-center justify-between gap-4">

          <div>

            <h2 className="text-lg font-semibold text-slate-900">
              Active Safety Alerts
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Live alerts received from the
              maritime monitoring system.
            </p>

          </div>

          {!loading && !error && (

            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                incidents.length > 0
                  ? "bg-red-100 text-red-700"
                  : "bg-emerald-100 text-emerald-700"
              }`}
            >
              {incidents.length}{" "}
              {incidents.length === 1
                ? "Active"
                : "Active"}
            </span>

          )}

        </div>

      </div>

      {/* =====================================================
          LOADING
      ===================================================== */}

      {loading && (

        <div className="p-5 text-sm text-slate-500">
          Loading safety alerts...
        </div>

      )}

      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (

        <div className="p-5">

          <p className="text-sm text-red-600">
            {error}
          </p>

          <button
            onClick={loadIncidents}
            className="mt-3 rounded-lg bg-slate-900 px-3 py-2 text-xs font-medium text-white hover:bg-slate-800"
          >
            Retry
          </button>

        </div>

      )}

      {/* =====================================================
          NO ACTIVE ALERTS
      ===================================================== */}

      {!loading &&
        !error &&
        incidents.length === 0 && (

          <div className="flex flex-col items-center justify-center p-8 text-center">

            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100">

              <span className="text-lg">
                ✓
              </span>

            </div>

            <p className="font-medium text-slate-800">
              No active safety alerts
            </p>

            <p className="mt-1 text-xs text-slate-500">
              The maritime monitoring system
              currently reports normal conditions.
            </p>

          </div>

        )}

      {/* =====================================================
          ACTIVE ALERTS
      ===================================================== */}

      {!loading &&
        !error &&
        incidents.length > 0 && (

          <div className="max-h-[420px] divide-y divide-slate-100 overflow-y-auto">

            {incidents.map(
              (incident) => {

                const severity =
                  incident.severity
                    ?.toUpperCase() ||
                  "UNKNOWN";

                const styles =
                  getSeverityStyles(
                    severity
                  );

                const validCoordinates =
                  Number.isFinite(
                    incident.latitude
                  ) &&
                  Number.isFinite(
                    incident.longitude
                  );

                return (

                  <div
                    key={incident.id}
                    className={`border-l-4 ${styles.border} p-5 transition hover:bg-slate-50`}
                  >

                    <div className="flex items-start justify-between gap-4">

                      <div className="min-w-0 flex-1">

                        {/* =================================
                            TITLE
                        ================================= */}

                        <div className="flex flex-wrap items-center gap-2">

                          <span
                            className={`h-2.5 w-2.5 shrink-0 rounded-full ${styles.dot}`}
                          />

                          <span className="font-semibold text-slate-900">
                            {incident.title}
                          </span>

                          <span
                            className={`rounded-full px-2 py-1 text-xs font-semibold ${styles.badge}`}
                          >
                            {severity}
                          </span>

                        </div>

                        {/* =================================
                            DESCRIPTION
                        ================================= */}

                        <p className="mt-2 text-sm text-slate-600">
                          {incident.description ||
                            "Safety incident detected."}
                        </p>

                        {/* =================================
                            LOCATION
                        ================================= */}

                        <div className="mt-2 text-xs text-slate-400">

                          Location:{" "}

                          {validCoordinates
                            ? `${incident.latitude.toFixed(
                                5
                              )}, ${incident.longitude.toFixed(
                                5
                              )}`
                            : "Unavailable"}

                        </div>

                        {/* =================================
                            REPORTED BY
                        ================================= */}

                        <div className="mt-1 text-xs text-slate-400">

                          Reported by:{" "}

                          {incident.reported_by ||
                            "Unknown"}

                        </div>

                      </div>

                      {/* =====================================
                          ACTIVE STATUS
                      ===================================== */}

                      <span className="flex shrink-0 items-center gap-1.5 text-xs font-semibold text-red-600">

                        <span className="h-2 w-2 animate-pulse rounded-full bg-red-500" />

                        ACTIVE

                      </span>

                    </div>

                  </div>

                );
              }
            )}

          </div>

        )}

    </div>
  );
}