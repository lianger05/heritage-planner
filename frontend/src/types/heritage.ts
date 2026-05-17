// 古建遗产类型定义

export type ProtectionLevel =
  | "全国重点文物保护单位"
  | "省级文物保护单位"
  | "市级文物保护单位"
  | "区县级文物保护单位"
  | "未定级";

export type BuildingType =
  | "宫殿"
  | "寺庙"
  | "民居"
  | "园林"
  | "楼阁"
  | "桥梁"
  | "城墙"
  | "陵墓"
  | "书院"
  | "作坊"
  | "其他";

export interface Heritage {
  id: number;
  name: string;
  alias?: string;
  dynasty?: string;
  building_type: BuildingType;
  protection_level: ProtectionLevel;
  style?: string;
  province: string;
  city: string;
  district?: string;
  address?: string;
  description?: string;
}

export interface Plan {
  id: number;
  heritage_id: number;
  title: string;
  protection_measures?: PlanProtectionMeasures;
  tourism_routes?: PlanTourismRoutes;
  business_layout?: PlanBusinessLayout;
  economic_estimation?: PlanEconomicEstimation;
  constraints_check?: PlanConstraintsCheck;
  version: number;
}

export interface PlanProtectionMeasures {
  core_zone: string;
  buffer_zone: string;
  structural: string;
  environmental: string;
  monitoring: string;
}

export interface PlanTourismRoutes {
  main_route: {
    description: string;
    stops: string[];
    duration: string;
    highlights: string[];
  };
  alternative_routes: Array<{
    description: string;
    stops: string[];
    duration: string;
    suitable_for: string;
  }>;
  accessibility: string;
}

export interface PlanBusinessLayout {
  cultural_creative: { description: string; location: string; scale: string };
  dining: { description: string; location: string; style: string };
  accommodation: { description: string; location: string; type: string };
  experience: { description: string; items: string[] };
  prohibited: string[];
}

export interface PlanEconomicEstimation {
  investment: {
    amount: string;
    breakdown: Record<string, number>;
    confidence: "low" | "medium" | "high";
  };
  revenue: {
    annual: string;
    sources: Record<string, number>;
    confidence: "low" | "medium" | "high";
  };
  roi: {
    payback_period: string;
    npv_note: string;
    sensitivity: string;
  };
  assumptions: string[];
}

export interface PlanConstraintsCheck {
  violations: Array<{
    regulation: string;
    issue: string;
    severity: "high" | "medium" | "low";
  }>;
  warnings: string[];
  passed: boolean;
}
