"use client";

import { useState, useEffect } from "react";
import { getHeritageList, getPlansByHeritage, type HeritageItem, type PlanItem } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useApiError } from "@/hooks/use-api-error";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { LoadingCard, LoadingListItem } from "@/components/ui/loading-card";

export default function ProjectPage() {
  const [heritageList, setHeritageList] = useState<HeritageItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [plans, setPlans] = useState<PlanItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingHeritage, setLoadingHeritage] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const { catchError } = useApiError();

  useEffect(() => {
    loadHeritage();
  }, []);

  async function loadHeritage() {
    setLoadingHeritage(true);
    try {
      const res = await getHeritageList({ page: 1, page_size: 100 });
      setHeritageList(res.items);
    } catch (err) {
      catchError(err, { title: "加载失败", description: "无法获取古建列表" });
    } finally {
      setLoadingHeritage(false);
    }
  }

  async function loadPlans(heritageId: number) {
    setSelectedId(heritageId);
    setLoading(true);
    try {
      const data = await getPlansByHeritage(heritageId);
      setPlans(data);
    } catch (err) {
      catchError(err, { title: "加载失败", description: "无法获取方案列表" });
    } finally {
      setLoading(false);
    }
  }

  const filteredHeritage = heritageList.filter((h) =>
    h.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-xl font-medium mb-6">项目管理</h1>

      <div className="grid grid-cols-3 gap-6">
        {/* 古建列表 */}
        <div className="col-span-1 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium">古建列表</h2>
            <Badge variant="secondary" className="text-xs">
              {heritageList.length} 处
            </Badge>
          </div>

          {/* 搜索 */}
          <div className="relative">
            <input
              className="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm pl-8 focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="搜索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <span className="absolute left-2.5 top-1.5 text-xs text-muted-foreground">🔍</span>
          </div>

          <ScrollArea className="h-[560px] rounded-lg border">
            {loadingHeritage ? (
              <div className="p-2 space-y-1">
                {Array.from({ length: 8 }).map((_, i) => (
                  <LoadingListItem key={i} />
                ))}
              </div>
            ) : (
              <div className="divide-y">
                {filteredHeritage.map((h) => (
                  <button
                    key={h.id}
                    className={cn(
                      "w-full text-left p-3 text-sm hover:bg-accent/50 transition-colors",
                      selectedId === h.id && "bg-accent"
                    )}
                    onClick={() => loadPlans(h.id)}
                  >
                    <div className="font-medium">{h.name}</div>
                    <div className="flex gap-1.5 mt-1">
                      <Badge variant="secondary" className="text-[10px] px-1 py-0">
                        {h.protection_level.replace("文物保护单位", "")}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {h.dynasty} · {h.building_type}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>

        {/* 方案列表 */}
        <div className="col-span-2 space-y-3">
          <h2 className="text-sm font-medium">规划方案</h2>

          {selectedId ? (
            loading ? (
              <div className="space-y-3">
                {Array.from({ length: 3 }).map((_, i) => (
                  <LoadingCard key={i} />
                ))}
              </div>
            ) : plans.length === 0 ? (
              <Card>
                <CardContent className="py-16 text-center">
                  <p className="text-muted-foreground mb-3">暂无方案</p>
                  <Button asChild variant="outline" size="sm">
                    <a href="/plan">前往生成方案</a>
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-3">
                {plans.map((plan) => (
                  <Card key={plan.id} className="hover:shadow-sm transition-shadow">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-sm truncate">{plan.title}</h3>
                          <div className="flex gap-2 mt-1">
                            <Badge variant="outline" className="text-xs">
                              v{plan.version}
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              {plan.llm_model} · {plan.generation_time?.toFixed(1)}s
                            </span>
                          </div>
                        </div>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">⋯</Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem asChild>
                              <a href={`/report?plan_id=${plan.id}`}>📄 查看报告</a>
                            </DropdownMenuItem>
                            <DropdownMenuItem asChild>
                              <a href={`/plan`}>🔄 重新生成</a>
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )
          ) : (
            <Card>
              <CardContent className="py-16 text-center">
                <p className="text-sm text-muted-foreground">
                  ← 选择左侧古建查看相关方案
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
