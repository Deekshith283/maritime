"use client";

import { useState } from "react";
import { createIncident } from "@/services/incidentService";
import { IncidentSeverity } from "@/types/incident";

interface Props {
  onSuccess: () => void;
}

export default function CreateIncidentDialog({
  onSuccess,
}: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const [severity, setSeverity] =
    useState<IncidentSeverity>("MEDIUM");

  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(
    e: React.FormEvent<HTMLFormElement>
  ) {
    e.preventDefault();

    try {
      setLoading(true);

      await createIncident({
        title,
        description,
        severity,
      });

      setTitle("");
      setDescription("");
      setSeverity("MEDIUM");

      setOpen(false);
      onSuccess();
    } catch (error) {
      console.error(error);
      alert("Failed to create incident.");
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
        + Create Incident
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-lg">
            <h2 className="mb-4 text-xl font-semibold">
              Create Incident
            </h2>

            <form
              onSubmit={handleSubmit}
              className="space-y-4"
            >
              <input
                type="text"
                placeholder="Title"
                className="w-full rounded-lg border p-2"
                value={title}
                onChange={(e) =>
                  setTitle(e.target.value)
                }
                required
              />

              <textarea
                placeholder="Description"
                className="w-full rounded-lg border p-2"
                rows={4}
                value={description}
                onChange={(e) =>
                  setDescription(e.target.value)
                }
                required
              />

              <select
                className="w-full rounded-lg border p-2"
                value={severity}
                onChange={(e) =>
                  setSeverity(
                    e.target.value as IncidentSeverity
                  )
                }
              >
                <option value="LOW">LOW</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="HIGH">HIGH</option>
                <option value="CRITICAL">CRITICAL</option>
              </select>

              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  className="rounded-lg border px-4 py-2"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={loading}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? "Creating..." : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}