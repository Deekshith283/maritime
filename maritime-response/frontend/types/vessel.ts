export type VesselStatus =
  | "ACTIVE"
  | "IN_PORT"
  | "EMERGENCY"
  | "OFFLINE";

export interface Vessel {
  id: string;
  name: string;
  registrationNumber: string;
  captain: string;
  latitude: number;
  longitude: number;
  speed: number;
  destination: string;
  status: VesselStatus;
}
