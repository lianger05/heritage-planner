/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    // Vercel 生产环境：设置 NEXT_PUBLIC_API_URL 指向 Render 后端
    // 本地开发：设置 NEXT_PUBLIC_API_URL=/api/v1，由 rewrites 代理
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "/api/v1",
    // 高德地图 JS API Key（需在 AMap 控制台配置 HTTP Referer 白名单）
    NEXT_PUBLIC_AMAP_KEY: process.env.NEXT_PUBLIC_AMAP_KEY || "",
    // 高德地图安全密钥（用于数字签名，与 Key 配套使用）
    NEXT_PUBLIC_AMAP_SECRET: process.env.NEXT_PUBLIC_AMAP_SECRET || "",
  },
  async rewrites() {
    // 使用 Vercel rewrites 代理后端请求，避免浏览器直连 Render 被 DNS 污染/网络不通
    const renderUrl =
      process.env.RENDER_BACKEND_URL || "https://heritage-planner.onrender.com";
    return [
      {
        source: "/api/v1/:path*",
        destination: `${renderUrl}/api/v1/:path*/`,
      },
    ];
  },
};

module.exports = nextConfig;
