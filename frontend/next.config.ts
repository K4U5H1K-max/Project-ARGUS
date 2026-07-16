import type { NextConfig } from "next";

const apiBase = process.env.API_BASE_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  reactStrictMode: true,
  // Hide the floating Next.js "N / Issues" badge during demos
  devIndicators: false,
  async rewrites() {
    return [
      {
        source: "/api/backend/:path*",
        destination: `${apiBase}/:path*`,
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};

export default nextConfig;
