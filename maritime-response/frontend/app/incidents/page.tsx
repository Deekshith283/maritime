"use client";

import { useEffect, useMemo, useState } from "react";

import IncidentFilters from "@/components/incidents/IncidentFilters";
import IncidentList from "@/components/incidents/IncidentList";
import CreateIncidentDialog from "@/components/incidents/CreateIncidentDialog";

import { Incident } from "@/types/incident";
import { getIncidents } from "@/services/incidentService";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("ALL");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadIncidents();
  }, []);

  async function loadIncidents() {
    try {
      setLoading(true);

      const data = await getIncidents();
      setIncidents(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load incidents.");
    } finally {
      setLoading(false);
    }
  }

  const filteredIncidents = useMemo(() => {
    return incidents.filter((incident) => {
      const matchesSearch =
        incident.title.toLowerCase().includes(search.toLowerCase()) ||
        incident.description.toLowerCase().includes(search.toLowerCase());

      const matchesStatus =
        status === "ALL" || incident.status === status;

      return matchesSearch && matchesStatus;
    });
  }, [incidents, search, status]);

  if (loading) {
    return (
      <main className="p-6">
        <p>Loading incidents...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="p-6">
        <p className="text-red-600">{error}</p>
      </main>
    );
  }

  return (
    <main className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Incident Management
          </h1>

          <p className="text-muted-foreground">
            Monitor and manage all maritime incidents.
          </p>
        </div>

        <CreateIncidentDialog
          onSuccess={loadIncidents}
        />
      </div>

      <IncidentFilters
        search={search}
        onSearchChange={setSearch}
        status={status}
        onStatusChange={setStatus}
      />

      {filteredIncidents.length === 0 ? (
        <div className="rounded-lg border border-dashed p-8 text-center text-gray-500">
          No incidents found.
        </div>
      ) : (
        <IncidentList incidents={filteredIncidents} />
      )}
    </main>
  );
}