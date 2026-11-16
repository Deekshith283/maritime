"use client";

import { useState } from "react";
import { createVessel } from "@/services/vesselService";

export default function AddVesselDialog() {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const [name, setName] = useState("");
  const [registrationNumber, setRegistrationNumber] = useState("");
  const [captain, setCaptain] = useState("");
  const [destination, setDestination] = useState("");
  const [speed, setSpeed] = useState(0);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    try {
      setLoading(true);

      await createVessel({
        name,
        registrationNumber,
        captain,
        destination,
        speed,
        latitude: 0,
        longitude: 0,
        status: "ACTIVE",
      });

      alert("Vessel added successfully!");

      setOpen(false);

      setName("");
      setRegistrationNumber("");
      setCaptain("");
      setDestination("");
      setSpeed(0);

      window.location.reload();
    } catch (error) {
      console.error(error);
      alert("Failed to add vessel.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
      >
        + Add Vessel
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
            <h2 className="mb-5 text-2xl font-bold">
              Add Vessel
            </h2>

            <form
              onSubmit={handleSubmit}
              className="space-y-4"
            >
              <input
                type="text"
                placeholder="Vessel Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full rounded-lg border p-2"
                required
              />

              <input
                type="text"
                placeholder="Registration Number"
                value={registrationNumber}
                onChange={(e) => setRegistrationNumber(e.target.value)}
                className="w-full rounded-lg border p-2"
                required
              />

              <input
                type="text"
                placeholder="Captain Name"
                value={captain}
                onChange={(e) => setCaptain(e.target.value)}
                className="w-full rounded-lg border p-2"
                required
              />

              <input
                type="text"
                placeholder="Destination"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                className="w-full rounded-lg border p-2"
                required
              />

              <input
                type="number"
                placeholder="Speed (knots)"
                value={speed}
                onChange={(e) => setSpeed(Number(e.target.value))}
                className="w-full rounded-lg border p-2"
                min={0}
              />

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  className="rounded-lg border px-4 py-2"
                  disabled={loading}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={loading}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? "Saving..." : "Save Vessel"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}