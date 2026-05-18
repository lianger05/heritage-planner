"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { getMapMarkers, type MapMarker } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { cn } from "@/lib/utils";
import { useApiError } from "@/hooks/use-api-error";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { LoadingListItem } from "@/components/ui/loading-card";
import { Layers } from "lucide-react";

// 高德地图图层类型
type MapLayerType = "standard" | "satellite";

// 高德地图类型声明
interface AMapInstance {
  destroy: () => void;
  setCenter: (pos: [number, number]) => void;
  setZoom: (zoom: number) => void;
  remove: (overlay: unknown) => void;
  add: (overlay: unknown) => void;
  clearMap: () => void;
  on: (event: string, cb: () => void) => void;
  getCenter: () => { lng: number; lat: number };
  setFitView: () => void;
  setLayers: (layers: unknown[]) => void;
}

interface AMapMarkerInstance {
  on: (event: string, cb: (e: { target: { getExtData: () => { id: number } } }) => void) => void;
  getExtData: () => { id: number };
}

export default function MapPage() {
  const [markers, setMarkers] = useState<MapMarker[]>([]);
  const [loading, setLoading] = useState(true);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [layerType, setLayerType] = useState<MapLayerType>("standard");
  const [filter, setFilter] = useState({
    province: "河南",
    city: "开封",
    protection_level: "",
    building_type: "",
  });
  const [selectedMarker, setSelectedMarker] = useState<MapMarker | null>(null);
  const { setSelectedHeritage } = useAppStore();
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<AMapInstance | null>(null);
  const markersRef = useRef<AMapMarkerInstance[]>([]);
  const infoWindowRef = useRef<unknown>(null);
  const { catchError } = useApiError();

  // 保护等级配色
  const levelColors: Record<string, string> = {
    全国重点文物保护单位: "#E53935",
    省级文物保护单位: "#FB8C00",
    市级文物保护单位: "#43A047",
    区县级文物保护单位: "#1E88E5",
  };

  // 加载古建标记
  const loadMarkers = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getMapMarkers(filter);
      setMarkers(data);
    } catch (err) {
      catchError(err, { title: "加载失败", description: "无法获取地图标记" });
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    loadMarkers();
  }, [loadMarkers]);

  // 初始化高德地图
  useEffect(() => {
    let destroyed = false;

    async function initMap() {
      if (!mapContainerRef.current) return;

      (window as unknown as Record<string, unknown>)._AMapSecurityConfig = {
        securityJsCode: process.env.NEXT_PUBLIC_AMAP_SECRET || "",
      };

      try {
        const AMapLoader = (await import("@amap/amap-jsapi-loader")).default;
        const AMap = await AMapLoader.load({
          key: process.env.NEXT_PUBLIC_AMAP_KEY || "",
          version: "2.0",
          plugins: ["AMap.Scale", "AMap.ToolBar"],
        });

        if (destroyed) return;

        const map = new AMap.Map(mapContainerRef.current, {
          center: [114.35, 34.79],
          zoom: 12,
          viewMode: "2D",
          mapStyle: "amap://styles/whitesmoke",
        });

        map.addControl(new AMap.Scale());
        map.addControl(new AMap.ToolBar({ position: "RB" }));

        // 创建 InfoWindow
        const infoWindow = new AMap.InfoWindow({
          offset: new AMap.Pixel(0, -35),
          closeWhenClickMap: true,
        });
        infoWindowRef.current = infoWindow;

        mapRef.current = map;
        setMapLoaded(true);
      } catch (err) {
        console.error("AMap load failed:", err);
        setMapLoaded(false);
      }
    }

    initMap();

    return () => {
      destroyed = true;
      if (mapRef.current) {
        mapRef.current.destroy();
        mapRef.current = null;
      }
    };
  }, []);

  // 地图图层切换 (标准/卫星)
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const AMap = (window as any).AMap;
    if (!AMap?.TileLayer) return;

    try {
      if (layerType === "satellite") {
        map.setLayers([
          new AMap.TileLayer.Satellite(),
          new AMap.TileLayer.RoadNet(),
        ]);
      } else {
        map.setLayers([new AMap.TileLayer()]);
      }
    } catch (_e) {
      // setLayers 在一些 AMap 版本中可能不可用，静默降级
    }
  }, [layerType, mapLoaded]);

  // 标记点渲染
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded || markers.length === 0) return;

    markersRef.current.forEach((m) => map.remove(m as unknown));
    markersRef.current = [];

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const AMap = (window as any).AMap;
    if (!AMap) return;

    const newMarkers: AMapMarkerInstance[] = [];

    markers.forEach((marker) => {
      if (!marker.longitude || !marker.latitude) return;

      const color = levelColors[marker.protection_level] || "#7B1FA2";

      const m = new AMap.Marker({
        position: [marker.longitude, marker.latitude],
        title: marker.name,
        offset: new AMap.Pixel(-13, -30),
        content: `<div style="
          width: 26px; height: 30px;
          background: ${color};
          border-radius: 50% 50% 50% 0;
          transform: rotate(-45deg);
          display: flex; align-items: center; justify-content: center;
          box-shadow: 0 2px 6px rgba(0,0,0,0.3);
          border: 2px solid #fff;
        "><span style="transform:rotate(45deg);color:#fff;font-size:11px;font-weight:bold;">
          ${marker.protection_level.includes("全国") ? "国" : marker.protection_level.includes("省级") ? "省" : marker.protection_level.includes("市级") ? "市" : "区"}
        </span></div>`,
        extData: { id: marker.id },
      });

      m.on("click", () => {
        const extData = m.getExtData?.();
        if (extData?.id) {
          setSelectedHeritage(extData.id);
          setSelectedMarker(marker);

          // 弹出 InfoWindow
          const infoWin = infoWindowRef.current as { open: (map: unknown, pos: [number, number]) => void; setContent: (html: string) => void };
          if (infoWin) {
            infoWin.setContent(`
              <div style="padding:8px 12px;font-family:system-ui;min-width:180px;">
                <div style="font-size:14px;font-weight:600;margin-bottom:4px;">${marker.name}</div>
                <div style="font-size:12px;color:#666;margin-bottom:6px;">
                  ${marker.protection_level} · ${marker.building_type}
                </div>
                <a href="/plan" style="color:hsl(24,50%,50%);font-size:12px;text-decoration:none;">
                  🚀 生成规划方案 →
                </a>
              </div>
            `);
            infoWin.open(map, [marker.longitude, marker.latitude]);
          }
        }
      });

      map.add(m);
      newMarkers.push(m);
    });

    markersRef.current = newMarkers;

    if (markers.length > 0) {
      map.setFitView();
    }

    return () => {
      markersRef.current.forEach((m) => {
        try { map.remove(m as unknown); } catch (_e) { /* ignore */ }
      });
      markersRef.current = [];
    };
  }, [markers, mapLoaded, levelColors, setSelectedHeritage]);

  const protectionLevels = [
    { value: "", label: "全部" },
    { value: "全国重点文物保护单位", label: "全国重点" },
    { value: "省级文物保护单位", label: "省级" },
    { value: "市级文物保护单位", label: "市级" },
    { value: "区县级文物保护单位", label: "区县级" },
  ];

  const buildingTypes = [
    { value: "", label: "全部" },
    { value: "宫殿", label: "宫殿" },
    { value: "寺庙", label: "寺庙" },
    { value: "民居", label: "民居" },
    { value: "园林", label: "园林" },
    { value: "楼阁", label: "楼阁" },
    { value: "桥梁", label: "桥梁" },
    { value: "城墙", label: "城墙" },
  ];

  return (
    <div className="flex h-[calc(100vh-3.5rem)]">
      {/* Sidebar */}
      <div className="w-80 border-r flex flex-col bg-background shrink-0">
        {/* 筛选区 */}
        <div className="p-4 border-b space-y-3">
          <h2 className="font-medium text-sm">筛选条件</h2>

          <div className="space-y-2">
            <label className="text-xs text-muted-foreground">保护等级</label>
            <Select
              value={filter.protection_level || "__all__"}
              onValueChange={(v) =>
                setFilter({ ...filter, protection_level: v === "__all__" ? "" : v })
              }
            >
              <SelectTrigger className="text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {protectionLevels.map((l) => (
                  <SelectItem key={l.value || "__all__"} value={l.value || "__all__"}>
                    {l.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-xs text-muted-foreground">建筑类型</label>
            <Select
              value={filter.building_type || "__all__"}
              onValueChange={(v) =>
                setFilter({ ...filter, building_type: v === "__all__" ? "" : v })
              }
            >
              <SelectTrigger className="text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {buildingTypes.map((t) => (
                  <SelectItem key={t.value || "__all__"} value={t.value || "__all__"}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* 古建列表 */}
        <ScrollArea className="flex-1">
          {loading ? (
            <div className="p-2 space-y-1">
              {Array.from({ length: 8 }).map((_, i) => (
                <LoadingListItem key={i} />
              ))}
            </div>
          ) : markers.length === 0 ? (
            <div className="p-8 text-center text-sm text-muted-foreground">暂无数据</div>
          ) : (
            <div className="divide-y">
              {markers.map((marker) => (
                <button
                  key={marker.id}
                  className={cn(
                    "w-full text-left p-4 hover:bg-accent/50 transition-colors",
                    selectedMarker?.id === marker.id && "bg-accent"
                  )}
                  onClick={() => {
                    setSelectedMarker(marker);
                    setSelectedHeritage(marker.id);
                    if (marker.longitude && marker.latitude && mapRef.current) {
                      mapRef.current.setCenter([marker.longitude, marker.latitude]);
                      mapRef.current.setZoom(15);
                    }
                  }}
                >
                  <div className="font-medium text-sm">{marker.name}</div>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge
                      className="text-xs text-white"
                      style={{ backgroundColor: levelColors[marker.protection_level] || "#7B1FA2" }}
                    >
                      {marker.protection_level.replace("文物保护单位", "")}
                    </Badge>
                    <span className="text-xs text-muted-foreground">{marker.building_type}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </ScrollArea>

        <Separator />
        <div className="p-3 text-xs text-muted-foreground text-center">
          共 {markers.length} 处古建
        </div>
      </div>

      {/* 地图区域 */}
      <div className="flex-1 relative">
        {/* 图层切换按钮 */}
        {mapLoaded && (
          <div className="absolute top-3 right-3 z-10 bg-white rounded-lg shadow-md p-1 flex gap-1">
            <Button
              variant={layerType === "standard" ? "default" : "ghost"}
              size="sm"
              className="h-8 text-xs"
              onClick={() => setLayerType("standard")}
            >
              <Layers className="h-3 w-3 mr-1" />
              标准
            </Button>
            <Button
              variant={layerType === "satellite" ? "default" : "ghost"}
              size="sm"
              className="h-8 text-xs"
              onClick={() => setLayerType("satellite")}
            >
              <Layers className="h-3 w-3 mr-1" />
              卫星
            </Button>
          </div>
        )}

        {!mapLoaded && (
          <div className="absolute inset-0 flex items-center justify-center bg-muted/30 z-10">
            <div className="text-center space-y-2 text-muted-foreground">
              <div className="animate-pulse text-2xl">🗺️</div>
              <p className="text-sm">
                {process.env.NEXT_PUBLIC_AMAP_KEY ? "地图加载中..." : "请配置高德地图 API Key"}
              </p>
            </div>
          </div>
        )}
        <div ref={mapContainerRef} className="w-full h-full" />
      </div>
    </div>
  );
}
