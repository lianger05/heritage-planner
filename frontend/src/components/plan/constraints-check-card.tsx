"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { PlanConstraintsCheck } from "@/types/heritage";

const severityConfig = {
  high: { label: "高风险", className: "border-destructive/50 bg-destructive/5" },
  medium: { label: "中风险", className: "border-amber-300/50 bg-amber-50" },
  low: { label: "低风险", className: "border-yellow-300/50 bg-yellow-50" },
};

interface Props {
  data: PlanConstraintsCheck;
}

export function ConstraintsCheckCard({ data }: Props) {
  const hasViolations = data.violations?.length > 0;
  const hasWarnings = data.warnings?.length > 0;

  return (
    <Card className={!data.passed ? "border-destructive/30" : ""}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <span>⚖️</span> 法规合规校验
          </CardTitle>
          <Badge
            variant={data.passed ? "default" : "destructive"}
            className="text-sm px-3 py-1"
          >
            {data.passed ? "✅ 合规通过" : "❌ 存在违规"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 违规项 */}
        {hasViolations && (
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-destructive">
              违规项 ({data.violations.length})
            </h4>
            {data.violations.map((v, i) => {
              const config = severityConfig[v.severity] || severityConfig.low;
              return (
                <div
                  key={i}
                  className={`rounded-lg border p-3 space-y-1.5 ${config.className}`}
                >
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={v.severity === "high" ? "destructive" : "secondary"}
                      className="text-xs"
                    >
                      {config.label}
                    </Badge>
                    <span className="text-sm font-medium">{v.regulation}</span>
                  </div>
                  <p className="text-sm text-muted-foreground pl-2">{v.issue}</p>
                </div>
              );
            })}
          </div>
        )}

        {/* 警告 */}
        {hasWarnings && (
          <>
            {hasViolations && <Separator />}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-amber-600">
                ⚠️ 注意事项 ({data.warnings.length})
              </h4>
              {data.warnings.map((w, i) => (
                <div key={i} className="rounded-lg border border-amber-200 bg-amber-50/50 p-3">
                  <p className="text-sm text-muted-foreground">{w}</p>
                </div>
              ))}
            </div>
          </>
        )}

        {/* 通过且无警告 */}
        {data.passed && !hasViolations && !hasWarnings && (
          <div className="text-center py-4">
            <p className="text-sm text-muted-foreground">
              方案符合所有相关法规要求，无违规项和警告
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
