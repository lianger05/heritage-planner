import { create } from "zustand";

interface AppState {
  // 当前选中的古建
  selectedHeritage: number | null;
  setSelectedHeritage: (id: number | null) => void;

  // 当前方案
  currentPlan: number | null;
  setCurrentPlan: (id: number | null) => void;

  // 对话会话
  chatSessionId: string | null;
  setChatSessionId: (id: string | null) => void;

  // 地图视图
  mapCenter: [number, number];
  mapZoom: number;
  setMapView: (center: [number, number], zoom: number) => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedHeritage: null,
  setSelectedHeritage: (id) => set({ selectedHeritage: id }),

  currentPlan: null,
  setCurrentPlan: (id) => set({ currentPlan: id }),

  chatSessionId: null,
  setChatSessionId: (id) => set({ chatSessionId: id }),

  mapCenter: [114.35, 34.79], // 开封默认中心
  mapZoom: 12,
  setMapView: (center, zoom) => set({ mapCenter: center, mapZoom: zoom }),
}));
