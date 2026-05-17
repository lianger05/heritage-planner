"use client";

import { useState, useRef, useEffect } from "react";
import {
  getHeritageList,
  generatePlan,
  getPlanDetail,
  sendChatMessage,
  type HeritageItem,
  type PlanItem,
} from "@/lib/api";
import { cn } from "@/lib/utils";
import { useApiError } from "@/hooks/use-api-error";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { LoadingPlanResult, LoadingCard } from "@/components/ui/loading-card";
import { ProtectionMeasuresCard } from "@/components/plan/protection-measures-card";
import { TourismRoutesCard } from "@/components/plan/tourism-routes-card";
import { BusinessLayoutCard } from "@/components/plan/business-layout-card";
import { EconomicEstimationCard } from "@/components/plan/economic-estimation-card";
import { ConstraintsCheckCard } from "@/components/plan/constraints-check-card";
import { ChatMessage } from "@/components/plan/chat-message";
import { TypingIndicator } from "@/components/plan/typing-indicator";
import type {
  PlanProtectionMeasures,
  PlanTourismRoutes,
  PlanBusinessLayout,
  PlanEconomicEstimation,
  PlanConstraintsCheck,
} from "@/types/heritage";

export default function PlanPage() {
  const [step, setStep] = useState<"select" | "generate" | "result" | "chat">("select");
  const [heritageList, setHeritageList] = useState<HeritageItem[]>([]);
  const [selectedHeritage, setSelectedHeritage] = useState<HeritageItem | null>(null);
  const [planTitle, setPlanTitle] = useState("");
  const [planDescription, setPlanDescription] = useState("");
  const [generating, setGenerating] = useState(false);
  const [loadingHeritage, setLoadingHeritage] = useState(false);
  const [currentPlan, setCurrentPlan] = useState<PlanItem | null>(null);
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatSessionId, setChatSessionId] = useState<string | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const { catchError } = useApiError();
  const chatEndRef = useRef<HTMLDivElement>(null);
  const [searchQuery, setSearchQuery] = useState("");

  // 加载古建列表
  async function loadHeritage() {
    setLoadingHeritage(true);
    try {
      const res = await getHeritageList({ page: 1, page_size: 50, province: "河南", city: "开封" });
      setHeritageList(res.items);
      if (heritageList.length === 0) setStep("select");
    } catch (err) {
      catchError(err, { title: "加载失败", description: "无法获取古建列表" });
    } finally {
      setLoadingHeritage(false);
    }
  }

  // 生成方案
  async function handleGenerate() {
    if (!selectedHeritage || !planTitle) return;
    setGenerating(true);
    try {
      const plan = await generatePlan({
        heritage_id: selectedHeritage.id,
        title: planTitle,
        description: planDescription || undefined,
      });
      setCurrentPlan(plan);
      setStep("result");
    } catch (err) {
      catchError(err, { title: "生成失败", description: "AI方案生成出错，请重试" });
    } finally {
      setGenerating(false);
    }
  }

  // AI对话
  async function handleChat() {
    if (!chatInput.trim() || !currentPlan) return;
    const userMsg = chatInput;
    setChatInput("");
    setChatMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setIsTyping(true);

    try {
      const res = await sendChatMessage({
        plan_id: currentPlan.id,
        message: userMsg,
        session_id: chatSessionId || undefined,
      });
      setChatSessionId(res.session_id);
      setChatMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);
    } catch (err) {
      catchError(err, { title: "对话失败", description: "AI对话出错，请重试" });
    } finally {
      setIsTyping(false);
    }
  }

  // 自动滚到底部
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, isTyping]);

  // 初始加载
  useEffect(() => {
    loadHeritage();
  }, []);

  const filteredHeritage = heritageList.filter((h) =>
    h.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const steps = [
    { key: "select" as const, label: "选择古建" },
    { key: "generate" as const, label: "生成方案" },
    { key: "result" as const, label: "查看方案" },
    { key: "chat" as const, label: "AI对话" },
  ];
  const stepIndex = steps.findIndex((s) => s.key === step);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* 步骤指示器 */}
      <div className="flex items-center gap-2 mb-8">
        {steps.map((s, i) => (
          <div key={s.key} className="flex items-center gap-2">
            <div
              className={cn(
                "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors",
                step === s.key
                  ? "bg-primary text-primary-foreground"
                  : i < stepIndex
                  ? "bg-primary/20 text-primary"
                  : "bg-muted text-muted-foreground"
              )}
            >
              {i + 1}
            </div>
            <span
              className={cn(
                "text-sm transition-colors",
                step === s.key ? "font-medium" : "text-muted-foreground"
              )}
            >
              {s.label}
            </span>
            {i < 3 && <div className="w-12 h-px bg-border" />}
          </div>
        ))}
      </div>

      {/* Step: 选择古建 */}
      {step === "select" && (
        <div className="space-y-4">
          <div>
            <h2 className="text-xl font-medium">选择古建</h2>
            <p className="text-sm text-muted-foreground mt-1">
              选择一个古建遗产，为其生成保护性开发方案
            </p>
          </div>

          {/* 搜索栏 */}
          {heritageList.length > 0 && (
            <div className="relative">
              <input
                className="w-full rounded-lg border border-input bg-background px-4 py-2.5 text-sm pl-10 focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="搜索古建名称..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <span className="absolute left-3 top-2.5 text-muted-foreground">🔍</span>
            </div>
          )}

          {loadingHeritage ? (
            <div className="grid grid-cols-2 gap-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <LoadingCard key={i} />
              ))}
            </div>
          ) : heritageList.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground mb-3">点击加载开封地区古建列表</p>
              <Button onClick={loadHeritage}>加载古建数据</Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {filteredHeritage.map((h) => (
                <Card
                  key={h.id}
                  className={cn(
                    "cursor-pointer transition-all hover:shadow-md hover:border-primary/50",
                    selectedHeritage?.id === h.id && "border-primary shadow-sm"
                  )}
                  onClick={() => {
                    setSelectedHeritage(h);
                    setPlanTitle(`${h.name}保护性开发方案`);
                    setStep("generate");
                  }}
                >
                  <CardContent className="p-4">
                    <div className="font-medium">{h.name}</div>
                    <div className="flex gap-2 mt-1.5">
                      <Badge variant="secondary" className="text-xs">
                        {h.protection_level.replace("文物保护单位", "")}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {h.dynasty} · {h.building_type}
                      </span>
                    </div>
                    {h.description && (
                      <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                        {h.description}
                      </p>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Step: 生成方案 */}
      {step === "generate" && selectedHeritage && (
        <div className="space-y-5">
          <h2 className="text-xl font-medium">生成方案</h2>

          {/* 已选古建卡片 */}
          <Card className="bg-muted/30">
            <CardContent className="p-4">
              <div className="font-medium">{selectedHeritage.name}</div>
              <div className="flex gap-2 mt-1">
                <Badge variant="outline" className="text-xs">
                  {selectedHeritage.protection_level}
                </Badge>
                <Badge variant="secondary" className="text-xs">
                  {selectedHeritage.dynasty}
                </Badge>
                <span className="text-xs text-muted-foreground">{selectedHeritage.building_type}</span>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium">方案标题</label>
              <input
                className="w-full mt-1.5 rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                value={planTitle}
                onChange={(e) => setPlanTitle(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium">额外需求（可选）</label>
              <textarea
                className="w-full mt-1.5 rounded-md border border-input bg-background px-3 py-2 text-sm min-h-[80px] focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="例如：侧重旅游动线设计、控制投资在500万以内、优先考虑无障碍设施..."
                value={planDescription}
                onChange={(e) => setPlanDescription(e.target.value)}
              />
            </div>
          </div>

          <div className="flex gap-3">
            <Button variant="outline" onClick={() => setStep("select")}>
              返回选择
            </Button>
            <Button onClick={handleGenerate} disabled={generating || !planTitle}>
              {generating ? "AI 生成中..." : "🚀 生成方案"}
            </Button>
          </div>

          {generating && (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                AI 正在分析古建信息、检索法规、生成方案，预计 15-30 秒...
              </p>
              <LoadingPlanResult />
            </div>
          )}
        </div>
      )}

      {/* Step: 方案结果 */}
      {step === "result" && currentPlan && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-medium">{currentPlan.title}</h2>
              <p className="text-xs text-muted-foreground mt-1">
                版本 v{currentPlan.version} · {currentPlan.llm_model} · {currentPlan.generation_time?.toFixed(1)}s
              </p>
            </div>
            <Button onClick={() => setStep("chat")}>
              💬 AI 对话修改
            </Button>
          </div>

          {/* Tabs 组织各板块 */}
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid grid-cols-5 w-full">
              <TabsTrigger value="overview">📋 总览</TabsTrigger>
              <TabsTrigger value="protection">🏛️ 保护</TabsTrigger>
              <TabsTrigger value="tourism">🗺️ 动线</TabsTrigger>
              <TabsTrigger value="business">🏪 业态</TabsTrigger>
              <TabsTrigger value="economic">📊 经济</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4 mt-4">
              {/* 总览概要 */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="rounded-lg border p-3 text-center">
                  <div className="text-xs text-muted-foreground mb-1">保护措施</div>
                  <div className="text-sm font-medium">
                    {currentPlan.protection_measures ? "✅ 已规划" : "—"}
                  </div>
                </div>
                <div className="rounded-lg border p-3 text-center">
                  <div className="text-xs text-muted-foreground mb-1">旅游动线</div>
                  <div className="text-sm font-medium">
                    {currentPlan.tourism_routes
                      ? `${((currentPlan.tourism_routes as unknown as unknown as PlanTourismRoutes)?.main_route?.stops?.length || 0)} 个站点`
                      : "—"}
                  </div>
                </div>
                <div className="rounded-lg border p-3 text-center">
                  <div className="text-xs text-muted-foreground mb-1">业态布局</div>
                  <div className="text-sm font-medium">
                    {currentPlan.business_layout
                      ? `${((currentPlan.business_layout as unknown as unknown as PlanBusinessLayout)?.prohibited?.length || 0)} 项禁业`
                      : "—"}
                  </div>
                </div>
                <div className="rounded-lg border p-3 text-center">
                  <div className="text-xs text-muted-foreground mb-1">投资规模</div>
                  <div className="text-sm font-medium">
                    {(currentPlan.economic_estimation as unknown as unknown as PlanEconomicEstimation)?.investment?.amount || "—"}
                  </div>
                </div>
              </div>

              {/* 总览中展示各板块摘要 */}
              {currentPlan.protection_measures && (
                <ProtectionMeasuresCard data={currentPlan.protection_measures as unknown as PlanProtectionMeasures} />
              )}
              {currentPlan.tourism_routes && (
                <TourismRoutesCard data={currentPlan.tourism_routes as unknown as PlanTourismRoutes} />
              )}
            </TabsContent>

            <TabsContent value="protection" className="mt-4">
              {currentPlan.protection_measures ? (
                <ProtectionMeasuresCard data={currentPlan.protection_measures as unknown as PlanProtectionMeasures} />
              ) : (
                <Card><CardContent className="py-8 text-center text-muted-foreground">暂无保护措施数据</CardContent></Card>
              )}
            </TabsContent>

            <TabsContent value="tourism" className="mt-4">
              {currentPlan.tourism_routes ? (
                <TourismRoutesCard data={currentPlan.tourism_routes as unknown as PlanTourismRoutes} />
              ) : (
                <Card><CardContent className="py-8 text-center text-muted-foreground">暂无旅游动线数据</CardContent></Card>
              )}
            </TabsContent>

            <TabsContent value="business" className="mt-4">
              {currentPlan.business_layout ? (
                <BusinessLayoutCard data={currentPlan.business_layout as unknown as PlanBusinessLayout} />
              ) : (
                <Card><CardContent className="py-8 text-center text-muted-foreground">暂无业态布局数据</CardContent></Card>
              )}
            </TabsContent>

            <TabsContent value="economic" className="mt-4">
              {currentPlan.economic_estimation ? (
                <EconomicEstimationCard data={currentPlan.economic_estimation as unknown as PlanEconomicEstimation} />
              ) : (
                <Card><CardContent className="py-8 text-center text-muted-foreground">暂无经济估算数据</CardContent></Card>
              )}
            </TabsContent>
          </Tabs>

          {/* 合规校验 - 始终可见 */}
          {currentPlan.constraints_check && (
            <ConstraintsCheckCard data={currentPlan.constraints_check as unknown as PlanConstraintsCheck} />
          )}
        </div>
      )}

      {/* Step: AI 对话 */}
      {step === "chat" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-medium">AI 规划对话</h2>
              <p className="text-sm text-muted-foreground mt-0.5">
                与 AI 规划专家讨论方案，提出修改意见或追问细节
              </p>
            </div>
            <Button variant="ghost" size="sm" onClick={() => setStep("result")}>
              ← 返回方案
            </Button>
          </div>

          <Card className="h-[550px] flex flex-col">
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-3">
                {chatMessages.length === 0 && !isTyping && (
                  <div className="text-center py-16">
                    <p className="text-sm text-muted-foreground mb-2">
                      💡 试试这样问：
                    </p>
                    <div className="space-y-1.5 text-xs text-muted-foreground">
                      <p>&ldquo;能否增加一条适合老人的游览路线？&rdquo;</p>
                      <p>&ldquo;投资预算可以压缩到300万以内吗？&rdquo;</p>
                      <p>&ldquo;建议增加夜游项目的业态布局&rdquo;</p>
                    </div>
                  </div>
                )}
                {chatMessages.map((msg, i) => (
                  <ChatMessage key={i} role={msg.role as "user" | "assistant"} content={msg.content} />
                ))}
                {isTyping && <TypingIndicator />}
                <div ref={chatEndRef} />
              </div>
            </ScrollArea>

            <Separator />

            <div className="p-3 flex gap-2">
              <input
                className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="输入消息..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleChat()}
                disabled={isTyping}
              />
              <Button onClick={handleChat} disabled={isTyping || !chatInput.trim()}>
                发送
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
