import Link from "next/link";
import { Map, FileText, MessageSquare, FolderOpen } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { HeroSection } from "@/components/home/hero-section";

const features = [
  {
    icon: Map,
    title: "地图浏览",
    description: "在全国地图上浏览古建分布，按省份、保护等级、建筑类型筛选",
    href: "/map",
    emoji: "🗺️",
  },
  {
    icon: FileText,
    title: "方案生成",
    description: "AI 自动生成保护性开发方案，包含动线规划、业态布局、经济估算",
    href: "/plan",
    emoji: "📋",
  },
  {
    icon: MessageSquare,
    title: "AI 对话",
    description: "与 AI 规划专家讨论方案细节，多轮对话精细化调整",
    href: "/plan",
    emoji: "💬",
  },
  {
    icon: FolderOpen,
    title: "项目管理",
    description: "管理古建信息、规划方案，导出专业报告",
    href: "/project",
    emoji: "📁",
  },
];

const workflow = [
  { step: 1, label: "选择古建", description: "从数据库中选择目标古建遗产" },
  { step: 2, label: "AI 生成方案", description: "知识图谱 + 法规检索 + LLM 自动规划" },
  { step: 3, label: "对话优化", description: "多轮对话精细化调整方案细节" },
  { step: 4, label: "导出报告", description: "一键导出专业规划报告" },
];

export default function HomePage() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-12">
      {/* Hero */}
      <HeroSection />

      {/* 功能卡片 */}
      <section>
        <h2 className="text-lg font-medium mb-4">核心功能</h2>
        <div className="grid grid-cols-2 gap-4">
          {features.map((feature) => (
            <Link key={feature.href + feature.title} href={feature.href}>
              <Card className="h-full hover:shadow-md hover:border-primary/50 transition-all cursor-pointer group">
                <CardContent className="p-5">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl shrink-0 group-hover:scale-110 transition-transform">
                      {feature.emoji}
                    </span>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium mb-1">{feature.title}</h3>
                      <p className="text-sm text-muted-foreground">{feature.description}</p>
                    </div>
                    <span className="text-muted-foreground group-hover:text-primary transition-colors shrink-0">→</span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      <Separator />

      {/* 使用流程 */}
      <section>
        <h2 className="text-lg font-medium mb-6">使用流程</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {workflow.map((item) => (
            <div key={item.step} className="text-center">
              <div className="w-10 h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-medium mx-auto mb-3">
                {item.step}
              </div>
              <h4 className="text-sm font-medium mb-1">{item.label}</h4>
              <p className="text-xs text-muted-foreground">{item.description}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
