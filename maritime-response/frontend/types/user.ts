export type UserRole =
  | "ADMIN"
  | "COAST_GUARD"
  | "OPERATOR";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
}