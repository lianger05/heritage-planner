"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { PlanProtectionMeasures } from "@/types/heritage";

const sections = [
  { key: "core_zone", label: "核心保护区", icon: "🛡️" },
  { key: "buffer_zone", label: "建设控制地带", icon: "🏗️" },
  { key: "structural", label: "结构加固", icon: "🔧" },
  { key: "environmental", label: "环境整治", icon: "🌳" },
  { key: "monitoring", label: "监测预警", icon: "👁️" },
] as const;

interface Props {
  data: PlanProtectionMeasures;
}

export function ProtectionMeasuresCard({ data }: Props) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <span>🏛️</span> 保护措施
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {sections.map((section, i) => {
          const content = data[section.key as keyof PlanProtectionMeasures];
          if (!content) return null;
          return (
            <div key={section.key}>
              {i > 0 && <Separator className="mb-4" />}
              <div className="flex items-start gap-3">
                <span className="text-lg mt-0.5 shrink-0">{section.icon}</span>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-foreground mb-1">{section.label}</h4>
                  <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                    {typeof content === "string" ? content : JSON.stringify(content)}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
