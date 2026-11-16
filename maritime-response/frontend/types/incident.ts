export type IncidentSeverity =
  | "LOW"
  | "MEDIUM"
  | "HIGH"
  | "CRITICAL";

export type IncidentStatus =
  | "ACTIVE"
  | "IN_PROGRESS"
  | "RESOLVED";

export interface Incident {
  id: string;
  title: string;
  description: string;
  latitude: number;
  longitude: number;
  severity: IncidentSeverity;
  status: IncidentStatus;
  reportedBy: string;
  createdAt: string;
}