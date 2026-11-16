import { api } from "@/lib/api";
import { Vessel } from "@/types/vessel";

export async function getVessels(): Promise<Vessel[]> {
  try {
    const response = await api.get("/vessels");
    return response.data;
  } catch (error) {
    console.error("Failed to fetch vessels:", error);
    throw error;
  }
}

export async function createVessel(
  data: Partial<Vessel>
): Promise<Vessel> {
  try {
    const response = await api.post("/vessels", data);
    return response.data;
  } catch (error) {
    console.error("Failed to create vessel:", error);
    throw error;
  }
}

export async function updateVessel(
  id: string,
  data: Partial<Vessel>
): Promise<Vessel> {
  try {
    const response = await api.put(`/vessels/${id}`, data);
    return response.data;
  } catch (error) {
    console.error("Failed to update vessel:", error);
    throw error;
  }
}

export async function deleteVessel(
  id: string
): Promise<void> {
  try {
    await api.delete(`/vessels/${id}`);
  } catch (error) {
    console.error("Failed to delete vessel:", error);
    throw error;
  }
}