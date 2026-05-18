import axios, { type AxiosError } from "axios";

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

// API Key：如果后端启用了认证，前端需要提供 X-API-Key
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

// 公共请求头
function getHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (API_KEY) {
    headers["X-API-Key"] = API_KEY;
  }
  return headers;
}

// 超时配置（毫秒）
const DEFAULT_TIMEOUT = 60000; // 普通请求
const AI_TIMEOUT = 180000; // AI 生成请求（DeepSeek/Qwen 可能需要较长时间）

export const api = axios.create({
  baseURL: API_BASE,
  timeout: DEFAULT_TIMEOUT,
  headers: getHeaders(),
});

// ---- 响应拦截器：统一错误处理 ----

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.code === "ECONNABORTED") {
      // 超时错误
      console.error(`[API] 请求超时 (${error.config?.url})`);
      return Promise.reject(
        new Error("请求超时，请检查网络连接后重试", { cause: error })
      );
    }
    if (!error.response) {
      // 网络错误（无响应）
      console.error(`[API] 网络错误 (${error.config?.url}):`, error.message);
      return Promise.reject(
        new Error("网络连接失败，请检查后端服务是否正常运行", { cause: error })
      );
    }
    // 服务端返回错误，保持原始错误以便上层捕获
    return Promise.reject(error);
  }
);

// ---- 重试策略 ----

/**
 * 对 GET 请求进行有限次数重试（处理瞬时网络故障）
 * 写操作（POST/PUT/DELETE）不自动重试，避免重复操作
 */
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config;
    if (!config) return Promise.reject(error);

    // 仅对网络错误和 5xx 进行重试，且仅限 GET 请求
    const shouldRetry =
      (error.code === "ECONNABORTED" || !error.response || (error.response?.status ?? 0) >= 500) &&
      (config.method?.toUpperCase() === "GET");

    if (!shouldRetry) return Promise.reject(error);

    // 限制最大重试次数
    const maxRetries = 2;
    const retryCount = (config as typeof config & { __retryCount?: number }).__retryCount || 0;
    if (retryCount >= maxRetries) {
      console.error(`[API] 已达最大重试次数 (${config.url})`);
      return Promise.reject(error);
    }

    (config as typeof config & { __retryCount: number }).__retryCount = retryCount + 1;

    // 指数退避：1s, 2s
    const delay = Math.pow(2, retryCount) * 1000;
    console.warn(`[API] 第 ${retryCount + 1} 次重试 (${config.url})，等待 ${delay}ms...`);
    await new Promise((resolve) => setTimeout(resolve, delay));

    return api.request(config);
  }
);

// 为 AI 生成请求提供更长超时的 axios 实例
export const aiApi = axios.create({
  baseURL: API_BASE,
  timeout: AI_TIMEOUT,
  headers: getHeaders(),
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
  const { data } = await api.post(`/plan/${planId}/refine`, { feedback });
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
