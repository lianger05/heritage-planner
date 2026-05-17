"use client";

import { useState, useEffect, Suspense } from "react";
import { getPlanDetail, type PlanItem } from "@/lib/api";
import { useSearchParams } from "next/navigation";
import { useApiError } from "@/hooks/use-api-error";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { LoadingCard } from "@/components/ui/loading-card";
import { ProtectionMeasuresCard } from "@/components/plan/protection-measures-card";
import { TourismRoutesCard } from "@/components/plan/tourism-routes-card";
import { BusinessLayoutCard } from "@/components/plan/business-layout-card";
import { EconomicEstimationCard } from "@/components/plan/economic-estimation-card";
import { ConstraintsCheckCard } from "@/components/plan/constraints-check-card";
import type {
  PlanProtectionMeasures,
  PlanTourismRoutes,
  PlanBusinessLayout,
  PlanEconomicEstimation,
  PlanConstraintsCheck,
} from "@/types/heritage";

function ReportContent() {
  const searchParams = useSearchParams();
  const planId = searchParams.get("plan_id");
  const [plan, setPlan] = useState<PlanItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [format, setFormat] = useState<"markdown">("markdown");
  const { catchError } = useApiError();
  const { toast } = useToast();

  useEffect(() => {
    if (planId) {
      setLoading(true);
      getPlanDetail(Number(planId))
        .then(setPlan)
        .catch((err) => catchError(err, { title: "加载失败" }))
        .finally(() => setLoading(false));
    }
  }, [planId]);

  // 客户端 Markdown 导出
  function handleExport() {
    if (!plan) return;

    const lines: string[] = [
      `# ${plan.title}`,
      "",
      `> 版本 v${plan.version} | ${plan.llm_model} | ${plan.generation_time?.toFixed(1)}s`,
      "",
    ];

    if (plan.protection_measures) {
      lines.push("## 保护措施", "");
      const d = plan.protection_measures as unknown as PlanProtectionMeasures;
      lines.push(`### 核心保护区\n${d.core_zone || ""}\n`);
      lines.push(`### 建设控制地带\n${d.buffer_zone || ""}\n`);
      lines.push(`### 结构加固\n${d.structural || ""}\n`);
      lines.push(`### 环境整治\n${d.environmental || ""}\n`);
      lines.push(`### 监测预警\n${d.monitoring || ""}\n`);
    }

    if (plan.tourism_routes) {
      lines.push("## 旅游动线", "");
      const d = plan.tourism_routes as unknown as PlanTourismRoutes;
      lines.push(`### 推荐路线\n${d.main_route?.description || ""}\n`);
      if (d.main_route?.stops) {
        lines.push(`**游览站点：** ${d.main_route.stops.join(" → ")}\n`);
      }
      if (d.main_route?.duration) {
        lines.push(`**建议时长：** ${d.main_route.duration}\n`);
      }
      if (d.alternative_routes?.length) {
        d.alternative_routes.forEach((r, i) => {
          lines.push(`### 备选路线 ${i + 1}\n${r.description}\n适合：${r.suitable_for}\n`);
        });
      }
    }

    if (plan.business_layout) {
      lines.push("## 业态布局", "");
      const d = plan.business_layout as unknown as PlanBusinessLayout;
      if (d.cultural_creative) lines.push(`### 文创零售\n${d.cultural_creative.description}\n位置：${d.cultural_creative.location}\n`);
      if (d.dining) lines.push(`### 餐饮服务\n${d.dining.description}\n风格：${d.dining.style}\n`);
      if (d.accommodation) lines.push(`### 住宿接待\n${d.accommodation.description}\n类型：${d.accommodation.type}\n`);
      if (d.experience) lines.push(`### 体验互动\n${d.experience.description}\n`);
      if (d.prohibited?.length) lines.push(`### 禁止业态\n${d.prohibited.map((p) => `- ${p}`).join("\n")}\n`);
    }

    if (plan.economic_estimation) {
      lines.push("## 经济估算", "");
      const d = plan.economic_estimation as unknown as PlanEconomicEstimation;
      lines.push(`### 投资\n**总额：** ${d.investment?.amount || "—"}\n`);
      lines.push(`### 收入\n**年均：** ${d.revenue?.annual || "—"}\n`);
      lines.push(`### 投资回报\n**回本周期：** ${d.roi?.payback_period || "—"}\n`);
    }

    if (plan.constraints_check) {
      const d = plan.constraints_check as unknown as PlanConstraintsCheck;
      lines.push("## 法规合规校验", "");
      lines.push(d.passed ? "**✅ 合规通过**\n" : "**❌ 存在违规**\n");
      if (d.violations?.length) {
        d.violations.forEach((v) => lines.push(`- [${v.severity}] ${v.regulation}: ${v.issue}`));
        lines.push("");
      }
    }

    lines.push("---", "", "*本方案由 AI 生成，仅供参考。请务必经过专业规划师审核后再用于正式项目。*");

    const blob = new Blob([lines.join("\n")], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${plan.title || "方案报告"}.md`;
    a.click();
    URL.revokeObjectURL(url);

    toast({ title: "导出成功", description: "Markdown 报告已下载" });
  }

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-8 space-y-4">
        <LoadingCard />
        <LoadingCard />
        <LoadingCard />
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-8 text-center text-muted-foreground">
        请从项目管理页面选择方案查看报告
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-medium">方案报告</h1>
          <p className="text-xs text-muted-foreground mt-1">
            版本 v{plan.version} · {plan.llm_model}
          </p>
        </div>
        <div className="flex gap-2 items-center">
          <Select value={format} onValueChange={(v) => setFormat(v as "markdown")}>
            <SelectTrigger className="w-[130px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="markdown">Markdown</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={handleExport}>
            📥 导出
          </Button>
        </div>
      </div>

      {/* 报告内容 - 复用卡片组件 */}
      <Card>
        <CardContent className="p-6 space-y-6">
          <div>
            <h2 className="text-lg font-semibold">{plan.title}</h2>
          </div>

          <Separator />

          {plan.protection_measures && (
            <ProtectionMeasuresCard data={plan.protection_measures as unknown as PlanProtectionMeasures} />
          )}
          {plan.tourism_routes && (
            <TourismRoutesCard data={plan.tourism_routes as unknown as PlanTourismRoutes} />
          )}
          {plan.business_layout && (
            <BusinessLayoutCard data={plan.business_layout as unknown as PlanBusinessLayout} />
          )}
          {plan.economic_estimation && (
            <EconomicEstimationCard data={plan.economic_estimation as unknown as PlanEconomicEstimation} />
          )}

          <Separator />

          {plan.constraints_check && (
            <ConstraintsCheckCard data={plan.constraints_check as unknown as PlanConstraintsCheck} />
          )}

          <div className="text-xs text-muted-foreground border-t pt-4">
            *本方案由 AI 生成，仅供参考。请务必经过专业规划师审核后再用于正式项目。
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function ReportPage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-3xl mx-auto px-4 py-8 text-center text-muted-foreground">
          加载中...
        </div>
      }
    >
      <ReportContent />
    </Suspense>
  );
}
