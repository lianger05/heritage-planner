"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Legend,
} from "recharts";
import type { PlanEconomicEstimation } from "@/types/heritage";

const CHART_COLORS = [
  "hsl(24, 50%, 50%)",
  "hsl(24, 40%, 60%)",
  "hsl(30, 35%, 65%)",
  "hsl(30, 30%, 72%)",
  "hsl(30, 25%, 80%)",
  "hsl(30, 20%, 88%)",
];

const confidenceMap: Record<string, { label: string; variant: "default" | "secondary" | "destructive" }> = {
  high: { label: "高置信度", variant: "default" },
  medium: { label: "中置信度", variant: "secondary" },
  low: { label: "低置信度", variant: "destructive" },
};

interface Props {
  data: PlanEconomicEstimation;
}

export function EconomicEstimationCard({ data }: Props) {
  // 投资分布数据
  const investmentData = data.investment?.breakdown
    ? Object.entries(data.investment.breakdown).map(([name, value]) => ({ name, value }))
    : [];

  // 收入来源数据
  const revenueData = data.revenue?.sources
    ? Object.entries(data.revenue.sources).map(([name, value]) => ({ name, value }))
    : [];

  const invConf = data.investment?.confidence
    ? confidenceMap[data.investment.confidence] || confidenceMap.low
    : null;
  const revConf = data.revenue?.confidence
    ? confidenceMap[data.revenue.confidence] || confidenceMap.low
    : null;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <span>📊</span> 经济估算
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 投资概览 */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium">投资概览</h4>
            {invConf && <Badge variant={invConf.variant} className="text-xs">{invConf.label}</Badge>}
          </div>
          <div className="text-2xl font-semibold text-primary mb-4">
            {data.investment?.amount || "—"}
          </div>
          {investmentData.length > 0 && (
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={investmentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={80}
                    paddingAngle={2}
                    dataKey="value"
                    label={({ name, percent }) =>
                      `${name} ${(percent * 100).toFixed(0)}%`
                    }
                    labelLine={false}
                  >
                    {investmentData.map((_, index) => (
                      <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value: number) => [`¥${value}`, ""]}
                    contentStyle={{
                      borderRadius: "8px",
                      border: "1px solid hsl(var(--border))",
                      fontSize: "12px",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <Separator />

        {/* 收入预估 */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium">收入预估</h4>
            {revConf && <Badge variant={revConf.variant} className="text-xs">{revConf.label}</Badge>}
          </div>
          <div className="text-2xl font-semibold text-primary mb-4">
            {data.revenue?.annual || "—"}<span className="text-sm font-normal text-muted-foreground ml-1">/年</span>
          </div>
          {revenueData.length > 0 && (
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={revenueData}>
                  <XAxis
                    dataKey="name"
                    tick={{ fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(v: number) => `¥${v}`}
                  />
                  <Tooltip
                    formatter={(value: number) => [`¥${value}`, ""]}
                    contentStyle={{
                      borderRadius: "8px",
                      border: "1px solid hsl(var(--border))",
                      fontSize: "12px",
                    }}
                  />
                  <Bar
                    dataKey="value"
                    fill="hsl(24, 50%, 50%)"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <Separator />

        {/* ROI */}
        <div className="grid grid-cols-3 gap-3">
          <div className="rounded-lg border p-3 text-center">
            <div className="text-xs text-muted-foreground mb-1">回本周期</div>
            <div className="text-lg font-semibold">{data.roi?.payback_period || "—"}</div>
          </div>
          <div className="rounded-lg border p-3 text-center">
            <div className="text-xs text-muted-foreground mb-1">净现值</div>
            <div className="text-sm font-medium">{data.roi?.npv_note || "—"}</div>
          </div>
          <div className="rounded-lg border p-3 text-center">
            <div className="text-xs text-muted-foreground mb-1">敏感度</div>
            <div className="text-sm font-medium">{data.roi?.sensitivity || "—"}</div>
          </div>
        </div>

        {/* 假设 */}
        {data.assumptions?.length > 0 && (
          <>
            <Separator />
            <div>
              <h4 className="text-xs font-medium text-muted-foreground mb-2">估算假设</h4>
              <ul className="space-y-1">
                {data.assumptions.map((a, i) => (
                  <li key={i} className="text-xs text-muted-foreground flex items-start gap-1.5">
                    <span className="mt-0.5">·</span> {a}
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
