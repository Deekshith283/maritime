"use client";

import { useEffect, useState } from "react";

interface Vessel {
  id: number;
  name: string;
  registration_number: string;
  captain: string;
  latitude: number;
  longitude: number;
  speed: number;
  course: number | null;
  destination: string | null;
  status: string;
  is_active: boolean;
}

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://192.168.1.5:8000";

export default function VesselTable() {
  const [vessels, setVessels] =
    useState<Vessel[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  async function fetchVessels() {
    try {
      const response = await fetch(
        `${API_URL}/vessels/`,
        {
          cache: "no-store",
        }
      );

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      const data: Vessel[] =
        await response.json();

      setVessels(data);
      setError("");

    } catch (err) {

      console.error(
        "Failed to fetch vessels:",
        err
      );

      setError(
        "Unable to load vessel data."
      );

    } finally {

      setLoading(false);

    }
  }

  useEffect(() => {

    fetchVessels();

    const interval =
      setInterval(
        fetchVessels,
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

        <div className="flex items-center justify-between">

          <div>

            <h2 className="text-lg font-semibold text-slate-900">
              Vessel Overview
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Live vessel information from the
              maritime backend.
            </p>

          </div>

          {!loading && !error && (
            <span className="flex items-center gap-2 text-xs font-medium text-emerald-600">

              <span className="h-2 w-2 rounded-full bg-emerald-500" />

              Live

            </span>
          )}

        </div>

      </div>

      {/* =====================================================
          LOADING
      ===================================================== */}

      {loading && (
        <div className="p-5 text-sm text-slate-500">
          Loading vessels...
        </div>
      )}

      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (
        <div className="p-5 text-sm text-red-600">
          {error}
        </div>
      )}

      {/* =====================================================
          EMPTY
      ===================================================== */}

      {!loading &&
        !error &&
        vessels.length === 0 && (
          <div className="p-5 text-sm text-slate-500">
            No vessels registered.
          </div>
        )}

      {/* =====================================================
          TABLE
      ===================================================== */}

      {!loading &&
        !error &&
        vessels.length > 0 && (

          <div className="overflow-x-auto">

            <table className="w-full text-left text-sm">

              <thead className="bg-slate-50 text-xs uppercase text-slate-500">

                <tr>

                  <th className="px-5 py-3">
                    Vessel
                  </th>

                  <th className="px-5 py-3">
                    Status
                  </th>

                  <th className="px-5 py-3">
                    Destination
                  </th>

                  <th className="px-5 py-3">
                    Speed
                  </th>

                  <th className="px-5 py-3">
                    Course
                  </th>

                  <th className="px-5 py-3">
                    Location
                  </th>

                </tr>

              </thead>

              <tbody className="divide-y divide-slate-100">

                {vessels.map(
                  (vessel) => {

                    const isActive =
                      vessel.status
                        ?.toUpperCase() ===
                      "ACTIVE";

                    const isAIS =
                      vessel.registration_number
                        ?.startsWith("AIS-");

                    return (

                      <tr
                        key={vessel.id}
                        className="transition hover:bg-slate-50"
                      >

                        {/* =================================
                            VESSEL
                        ================================= */}

                        <td className="px-5 py-4">

                          <div className="flex items-center gap-2">

                            <span
                              className={`h-2.5 w-2.5 rounded-full ${
                                isAIS
                                  ? "bg-teal-500"
                                  : "bg-blue-600"
                              }`}
                            />

                            <div>

                              <div className="font-medium text-slate-900">
                                {vessel.name}
                              </div>

                              <div className="text-xs text-slate-500">

                                {vessel.registration_number}

                                {" · "}

                                {vessel.captain ||
                                  "Unknown"}

                              </div>

                            </div>

                          </div>

                        </td>

                        {/* =================================
                            STATUS
                        ================================= */}

                        <td className="px-5 py-4">

                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                              isActive
                                ? "bg-emerald-100 text-emerald-700"
                                : "bg-slate-100 text-slate-600"
                            }`}
                          >
                            {vessel.status}
                          </span>

                        </td>

                        {/* =================================
                            DESTINATION
                        ================================= */}

                        <td className="px-5 py-4 text-slate-600">

                          {vessel.destination ||
                            "—"}

                        </td>

                        {/* =================================
                            SPEED
                        ================================= */}

                        <td className="px-5 py-4 font-medium text-slate-700">

                          {Number.isFinite(
                            vessel.speed
                          )
                            ? `${vessel.speed.toFixed(2)} knots`
                            : "—"}

                        </td>

                        {/* =================================
                            COURSE
                        ================================= */}

                        <td className="px-5 py-4 text-slate-600">

                          {vessel.course !== null &&
                          Number.isFinite(
                            vessel.course
                          )
                            ? `${vessel.course.toFixed(0)}°`
                            : "—"}

                        </td>

                        {/* =================================
                            LOCATION
                        ================================= */}

                        <td className="px-5 py-4 text-slate-600">

                          {Number.isFinite(
                            vessel.latitude
                          ) &&
                          Number.isFinite(
                            vessel.longitude
                          )
                            ? `${vessel.latitude.toFixed(
                                5
                              )}, ${vessel.longitude.toFixed(
                                5
                              )}`
                            : "—"}

                        </td>

                      </tr>

                    );
                  }
                )}

              </tbody>

            </table>

          </div>
        )}

    </div>
  );
}