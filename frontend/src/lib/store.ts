import { create } from "zustand";
import { persist } from "zustand/middleware";

interface RequestState {
  isLoading: boolean;
  error: string | null;
}

interface AppState {
  // 当前选中的古建 ID
  selectedHeritage: number | null;
  setSelectedHeritage: (id: number | null) => void;

  // 当前方案 ID
  currentPlan: number | null;
  setCurrentPlan: (id: number | null) => void;

  // 对话会话
  chatSessionId: string | null;
  setChatSessionId: (id: string | null) => void;

  // 地图视图（持久化，刷新后保持位置）
  mapCenter: [number, number];
  mapZoom: number;
  setMapView: (center: [number, number], zoom: number) => void;

  // 请求状态（不持久化）
  planRequest: RequestState;
  setPlanRequest: (state: Partial<RequestState>) => void;
  heritageRequest: RequestState;
  setHeritageRequest: (state: Partial<RequestState>) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      selectedHeritage: null,
      setSelectedHeritage: (id) => set({ selectedHeritage: id }),

      currentPlan: null,
      setCurrentPlan: (id) => set({ currentPlan: id }),

      chatSessionId: null,
      setChatSessionId: (id) => set({ chatSessionId: id }),

      mapCenter: [114.35, 34.79], // 开封默认中心
      mapZoom: 12,
      setMapView: (center, zoom) => set({ mapCenter: center, mapZoom: zoom }),

      planRequest: { isLoading: false, error: null },
      setPlanRequest: (state) =>
        set((prev) => ({
          planRequest: { ...prev.planRequest, ...state },
        })),

      heritageRequest: { isLoading: false, error: null },
      setHeritageRequest: (state) =>
        set((prev) => ({
          heritageRequest: { ...prev.heritageRequest, ...state },
        })),
    }),
    {
      name: "heritage-planner-storage",
      partialize: (state) => ({
        // 仅持久化视图状态，不持久化请求状态和临时选择
        mapCenter: state.mapCenter,
        mapZoom: state.mapZoom,
      }),
    }
  )
);
