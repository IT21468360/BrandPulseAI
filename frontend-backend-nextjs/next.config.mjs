// next.config.mjs

/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      // English XAI API
      {
        source: '/api/xai/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/xai/:path*`,
      },
      // Sinhala XAI API
      {
        source: '/api/xai/sinhala/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/xai/sinhala/:path*`,
      },
      // English report endpoints
      {
        source: '/api/xai/reports/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/xai/reports/:path*`,
      },
      // Sinhala report endpoints
      {
        source: '/api/xai/sinhala/reports/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/xai/sinhala/reports/:path*`,
      },
      // Static English reports
      {
        source: '/reports/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/reports/:path*`,
      },
      // Static Sinhala reports
      {
        source: '/reports/sinhala/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/reports/sinhala/:path*`,
      },
    ]
  },
}

export default nextConfig
