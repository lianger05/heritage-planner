/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080/api/v1",
    NEXT_PUBLIC_AMAP_KEY: process.env.NEXT_PUBLIC_AMAP_KEY || "",
  },
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        // 添加尾部斜杠匹配 FastAPI 路由定义，避免 307 重定向
        destination: "http://localhost:8080/api/v1/:path*/",
      },
    ];
  },
};

module.exports = nextConfig;
