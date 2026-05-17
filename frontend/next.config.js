/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    // Vercel 生产环境：设置 NEXT_PUBLIC_API_URL 指向 Render 后端
    // 本地开发：设置 NEXT_PUBLIC_API_URL=/api/v1，由 rewrites 代理
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "/api/v1",
    NEXT_PUBLIC_AMAP_KEY: process.env.NEXT_PUBLIC_AMAP_KEY || "",
  },
  async rewrites() {
    // 生产环境不需要代理，前端直接调用 Render 后端
    if (process.env.NODE_ENV === "production") return [];
    // 开发环境：将 /api/v1 代理到本地后端
    return [
      {
        source: "/api/v1/:path*",
        // 尾部斜杠匹配 FastAPI 路由，避免 307 重定向
        destination: "http://localhost:8080/api/v1/:path*/",
      },
    ];
  },
};

module.exports = nextConfig;
