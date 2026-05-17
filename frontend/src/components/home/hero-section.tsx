"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary/10 via-primary/5 to-transparent border">
      {/* 装饰性背景图案 - 传统建筑轮廓 */}
      <div className="absolute inset-0 opacity-[0.03]" aria-hidden="true">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="pagoda" x="0" y="0" width="120" height="120" patternUnits="userSpaceOnUse">
              <path d="M60 10 L80 30 L75 30 L90 50 L85 50 L95 70 L25 70 L35 50 L30 50 L45 30 L40 30 Z" fill="currentColor" />
              <rect x="50" y="70" width="20" height="30" fill="currentColor" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#pagoda)" />
        </svg>
      </div>

      <div className="relative px-8 py-12 sm:px-12 sm:py-16">
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">
          古建文旅经济
          <br />
          <span className="text-primary">智能规划助手</span>
        </h1>
        <p className="mt-4 text-base text-muted-foreground max-w-xl leading-relaxed">
          基于 AI 技术的古建保护性开发方案自动生成平台。
          融合知识图谱、法规检索与大语言模型，为每一处古建量身定制保护、旅游、业态与经济的一体化规划方案。
        </p>
        <div className="mt-6 flex gap-3">
          <Button asChild size="lg">
            <Link href="/plan">🚀 开始规划</Link>
          </Button>
          <Button variant="outline" size="lg" asChild>
            <Link href="/map">🗺️ 浏览地图</Link>
          </Button>
        </div>

        {/* 统计数据 */}
        <div className="mt-8 flex gap-8 text-sm">
          <div>
            <div className="text-2xl font-bold text-primary">10+</div>
            <div className="text-muted-foreground">古建数据</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-primary">5+</div>
            <div className="text-muted-foreground">法规检索</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-primary">AI</div>
            <div className="text-muted-foreground">智能生成</div>
          </div>
        </div>
      </div>
    </section>
  );
}
