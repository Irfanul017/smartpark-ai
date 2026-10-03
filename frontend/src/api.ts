import axios from "axios";

export type Role = "USER" | "ADMIN" | "PARKING_OPERATOR";

export type User = { id: number; username: string; email: string; role: Role; created_at: string };
export type Slot = {
  id: number; slot_number: string; floor: string; zone: string; slot_type: string; vehicle_type: string;
  is_ev: boolean; is_accessible: boolean; is_reserved: boolean; is_occupied: boolean; distance_from_entrance: number;
  walking_distance: number; congestion_level: number; created_at: string;
};
export type ParkingRequest = { vehicle_type: string; requires_ev: boolean; requires_accessible: boolean; priority: number };
export type Recommendation = { slot: string; slot_id: number; score: number; category: string; reason: string; factors: Record<string, unknown> };
export type ParkingSession = { id: number; slot_id: number; user_id: number | null; vehicle_type: string; priority: number; started_at: string; ended_at: string | null };

const api = axios.create({ baseURL: "http://127.0.0.1:8000" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("smartpark_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const apiError = (error: unknown) => {
  if (axios.isAxiosError(error)) return String(error.response?.data?.detail ?? error.message);
  return "Something went wrong. Please try again.";
};

export default api;
