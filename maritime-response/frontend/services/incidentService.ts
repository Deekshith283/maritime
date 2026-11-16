import { api } from "@/lib/api";
import { Incident } from "@/types/incident";

/**
 * Get all incidents
 */
export async function getIncidents(): Promise<Incident[]> {
  try {
    const response = await api.get<Incident[]>("/incidents");
    return response.data;
  } catch (error) {
    console.error("Error fetching incidents:", error);
    throw error;
  }
}

/**
 * Create a new incident
 */
export async function createIncident(
  data: Partial<Incident>
): Promise<Incident> {
  try {
    const response = await api.post<Incident>("/incidents", data);
    return response.data;
  } catch (error) {
    console.error("Error creating incident:", error);
    throw error;
  }
}

/**
 * Update an existing incident
 */
export async function updateIncident(
  id: string,
  data: Partial<Incident>
): Promise<Incident> {
  try {
    const response = await api.put<Incident>(`/incidents/${id}`, data);
    return response.data;
  } catch (error) {
    console.error("Error updating incident:", error);
    throw error;
  }
}

/**
 * Delete an incident
 */
export async function deleteIncident(id: string): Promise<void> {
  try {
    await api.delete(`/incidents/${id}`);
  } catch (error) {
    console.error("Error deleting incident:", error);
    throw error;
  }
}