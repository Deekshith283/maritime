"use client";

import { useMemo, useState } from "react";

import AddVesselDialog from "@/components/vessels/AddVesselDialog";
import VesselList from "@/components/vessels/VesselList";

const vessels = [
  {
    id: "1",
    name: "MV Ocean Star",
    registrationNumber: "KA-001",
    captain: "Captain Ravi",
    latitude: 12.91,
    longitude: 74.85,
    speed: 14,
    destination: "Mangalore Port",
    status: "ACTIVE",
  },
  {
    id: "2",
    name: "Sea Guardian",
    registrationNumber: "KA-002",
    captain: "Captain Arjun",
    latitude: 13.05,
    longitude: 74.70,
    speed: 0,
    destination: "Goa Harbour",
    status: "IN_PORT",
  },
] as const;

export default function VesselsPage() {
  const [search, setSearch] = useState("");

  const filteredVessels = useMemo(() => {
    return vessels.filter((vessel) =>
      vessel.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <main className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Vessel Management
          </h1>

          <p className="text-muted-foreground">
            Monitor and manage all registered vessels.
          </p>
        </div>

        <AddVesselDialog />
      </div>

      <div className="rounded-xl border bg-white p-4 shadow-sm">
        <input
          type="text"
          placeholder="Search vessels..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-lg border p-2 outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <VesselList vessels={[...filteredVessels]} />
    </main>
  );
}