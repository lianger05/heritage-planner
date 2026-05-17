import axios from "axios";

// 判断运行环境，选择正确的后端地址
function getApiBase(): string {
  // 优先使用显式设置的环境变量
  if (process.env.NEXT_PUBLIC_API_URL?.startsWith("http")) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  // 浏览器端：非本地环境直接指向 Render 后端
  if (typeof window !== "undefined" && window.location.hostname !== "localhost") {
    return "https://heritage-planner.onrender.com/api/v1";
  }
  // 本地开发：走 Next.js rewrites 代理
  return "/api/v1";
}

const API_BASE = getApiBase();

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ===== Heritage =====

export interface HeritageItem {
  id: number;
  name: string;
  alias?: string;
  dynasty?: string;
  building_type: string;
  protection_level: string;
  province: string;
  city: string;
  district?: string;
  address?: string;
  longitude?: number;
  latitude?: number;
  description?: string;
  current_status?: string;
  area_size?: number;
  is_open?: boolean;
  ticket_price?: number;
  annual_visitors?: number;
  created_at: string;
  updated_at: string;
}

export interface HeritageListResponse {
  items: HeritageItem[];
  total: number;
  page: number;
  page_size: number;
}

export async function getHeritageList(params?: {
  page?: number;
  page_size?: number;
  province?: string;
  city?: string;
  protection_level?: string;
  building_type?: string;
  keyword?: string;
}): Promise<HeritageListResponse> {
  const { data } = await api.get("/heritage/", { params });
  return data;
}

export async function getHeritageDetail(id: number): Promise<HeritageItem> {
  const { data } = await api.get(`/heritage/${id}`);
  return data;
}

export async function createHeritage(payload: Partial<HeritageItem>): Promise<HeritageItem> {
  const { data } = await api.post("/heritage/", payload);
  return data;
}

// ===== Plan =====

export interface PlanItem {
  id: number;
  heritage_id: number;
  title: string;
  description?: string;
  protection_measures?: Record<string, unknown>;
  tourism_routes?: Record<string, unknown>;
  business_layout?: Record<string, unknown>;
  economic_estimation?: Record<string, unknown>;
  constraints_check?: Record<string, unknown>;
  llm_model?: string;
  generation_time?: number;
  version: number;
  quality_score?: number;
  created_at: string;
  updated_at: string;
}

export async function generatePlan(payload: {
  heritage_id: number;
  title: string;
  description?: string;
  requirements?: Record<string, unknown>;
}): Promise<PlanItem> {
  const { data } = await api.post("/plan/generate", payload);
  return data;
}

export async function getPlanDetail(id: number): Promise<PlanItem> {
  const { data } = await api.get(`/plan/${id}`);
  return data;
}

export async function getPlansByHeritage(heritageId: number): Promise<PlanItem[]> {
  const { data } = await api.get(`/plan/heritage/${heritageId}`);
  return data;
}

export async function refinePlan(planId: number, feedback: string): Promise<PlanItem> {
  const { data } = await api.post(`/plan/${planId}/refine`, null, { params: { feedback } });
  return data;
}

// ===== Chat =====

export interface ChatResponse {
  session_id: string;
  reply: string;
  updated_plan?: Record<string, unknown>;
  references?: Array<Record<string, unknown>>;
}

export async function sendChatMessage(payload: {
  plan_id: number;
  message: string;
  session_id?: string;
}): Promise<ChatResponse> {
  const { data } = await api.post("/chat/message", payload);
  return data;
}

// ===== Map =====

export interface MapMarker {
  id: number;
  name: string;
  longitude: number;
  latitude: number;
  protection_level: string;
  building_type: string;
  is_open?: boolean;
}

export async function getMapMarkers(payload: {
  province?: string;
  city?: string;
  protection_level?: string;
  building_type?: string;
  keyword?: string;
}): Promise<MapMarker[]> {
  const { data } = await api.post("/map/markers", payload);
  return data;
}

// ===== Report =====

export interface ReportResponse {
  download_url: string;
  filename: string;
  format: string;
}

export async function generateReport(payload: {
  plan_id: number;
  format?: string;
}): Promise<ReportResponse> {
  const { data } = await api.post("/report/generate", payload);
  return data;
}

// ===== Regulation =====

export interface RegulationItem {
  id: number;
  title: string;
  source?: string;
  level?: string;
  content: string;
  summary?: string;
  relevance_score?: number;
}

export async function searchRegulations(payload: {
  query: string;
  protection_level?: string;
  top_k?: number;
}): Promise<RegulationItem[]> {
  const { data } = await api.post("/regulation/search", payload);
  return data;
}
