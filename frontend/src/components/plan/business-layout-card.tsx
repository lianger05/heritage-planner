"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { PlanBusinessLayout } from "@/types/heritage";

const categories = [
  { key: "cultural_creative", label: "文创零售", icon: "🎨", detailKey: "location" },
  { key: "dining", label: "餐饮服务", icon: "🍜", detailKey: "style" },
  { key: "accommodation", label: "住宿接待", icon: "🏨", detailKey: "type" },
  { key: "experience", label: "体验互动", icon: "✨", detailKey: "items" },
] as const;

interface Props {
  data: PlanBusinessLayout;
}

export function BusinessLayoutCard({ data }: Props) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <span>🏪</span> 业态布局
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 4类业态网格 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {categories.map((cat) => {
            const section = data[cat.key as keyof PlanBusinessLayout] as
              | { description?: string; location?: string; scale?: string; style?: string; type?: string; items?: string[] }
              | undefined;
            if (!section) return null;

            return (
              <div
                key={cat.key}
                className="rounded-lg border bg-card p-3 space-y-2"
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">{cat.icon}</span>
                  <h4 className="text-sm font-medium">{cat.label}</h4>
                </div>
                {section.description && (
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {section.description}
                  </p>
                )}
                {"location" in section && section.location && (
                  <div className="text-xs text-muted-foreground">📍 {section.location}</div>
                )}
                {"scale" in section && section.scale && (
                  <div className="text-xs text-muted-foreground">📐 {section.scale}</div>
                )}
                {"style" in section && section.style && (
                  <Badge variant="outline" className="text-xs">{section.style}</Badge>
                )}
                {"type" in section && section.type && (
                  <Badge variant="outline" className="text-xs">{section.type}</Badge>
                )}
                {"items" in section && section.items && section.items.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {section.items.map((item: string, j: number) => (
                      <Badge key={j} variant="secondary" className="text-xs">
                        {item}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* 禁止业态 */}
        {data.prohibited?.length > 0 && (
          <>
            <Separator />
            <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-3">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm">⚠️</span>
                <h4 className="text-sm font-medium text-destructive">禁止业态</h4>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {data.prohibited.map((item, i) => (
                  <Badge key={i} variant="destructive" className="text-xs">
                    🚫 {item}
                  </Badge>
                ))}
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
