"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { PlanTourismRoutes } from "@/types/heritage";

interface Props {
  data: PlanTourismRoutes;
}

export function TourismRoutesCard({ data }: Props) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <span>🗺️</span> 旅游动线
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="main" className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="main">推荐路线</TabsTrigger>
            {data.alternative_routes?.length > 0 && (
              <TabsTrigger value="alternatives">
                备选路线 ({data.alternative_routes.length})
              </TabsTrigger>
            )}
          </TabsList>

          <TabsContent value="main" className="space-y-4">
            {/* 主路线描述 */}
            <p className="text-sm text-muted-foreground leading-relaxed">
              {data.main_route.description}
            </p>

            {/* 时间线式步骤展示 */}
            <div className="relative pl-6">
              {data.main_route.stops?.map((stop, i) => (
                <div key={i} className="relative pb-4 last:pb-0">
                  {/* 连接线 */}
                  {i < data.main_route.stops.length - 1 && (
                    <div className="absolute left-[-18px] top-6 bottom-0 w-px bg-border" />
                  )}
                  {/* 步骤圆点 */}
                  <div className="absolute left-[-22px] top-1 w-4 h-4 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-[10px] font-medium">
                    {i + 1}
                  </div>
                  <div className="text-sm font-medium">{stop}</div>
                </div>
              ))}
            </div>

            {/* 亮点标签 */}
            {data.main_route.highlights?.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {data.main_route.highlights.map((h, i) => (
                  <Badge key={i} variant="secondary" className="text-xs">
                    ✨ {h}
                  </Badge>
                ))}
              </div>
            )}

            {/* 游览时长 */}
            {data.main_route.duration && (
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">⏱️ 建议游览</span>
                <Badge variant="outline">{data.main_route.duration}</Badge>
              </div>
            )}
          </TabsContent>

          <TabsContent value="alternatives" className="space-y-4">
            {data.alternative_routes?.map((route, i) => (
              <div key={i}>
                {i > 0 && <Separator className="mb-4" />}
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-medium">备选路线 {i + 1}</h4>
                    {route.suitable_for && (
                      <Badge variant="outline" className="text-xs">
                        {route.suitable_for}
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">{route.description}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {route.stops?.map((stop, j) => (
                      <Badge key={j} variant="secondary" className="text-xs">
                        {stop}
                      </Badge>
                    ))}
                  </div>
                  {route.duration && (
                    <span className="text-xs text-muted-foreground">⏱️ {route.duration}</span>
                  )}
                </div>
              </div>
            ))}
          </TabsContent>
        </Tabs>

        {/* 无障碍信息 */}
        {data.accessibility && (
          <>
            <Separator className="my-4" />
            <div className="flex items-start gap-2">
              <span className="text-sm">ℹ️</span>
              <p className="text-sm text-muted-foreground">{data.accessibility}</p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
