/**
 * 根布局组件
 *
 * 🔐 高德地图 API Key 安全说明：
 *   - NEXT_PUBLIC_AMAP_KEY 和 NEXT_PUBLIC_AMAP_SECRET 通过环境变量注入
 *   - 生产环境务必在 AMap 控制台 (console.amap.com) 配置：
 *     1. HTTP Referer 白名单：仅允许你的域名（如 heritage-planner.vercel.app）
 *     2. IP 白名单（可选）：限制后端服务器出站 IP
 *     3. 应用类型选 "Web端(JS API)"
 *   - Key 不得硬编码在源代码中，仅通过环境变量传入
 *   - 地图实际加载在 /map 页面（src/app/map/page.tsx）
 *
 * @see https://console.amap.com/dev/key/app
 */
import type { Metadata } from "next";
import "./globals.css";
import { LayoutShell } from "@/components/layout/layout-shell";
import { Toaster } from "@/components/ui/toaster";

export const metadata: Metadata = {
  title: "古建文旅规划助手",
  description: "AI驱动的古建保护性开发方案生成平台",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-background font-sans antialiased">
        <LayoutShell>{children}</LayoutShell>
        <Toaster />
      </body>
    </html>
  );
}
