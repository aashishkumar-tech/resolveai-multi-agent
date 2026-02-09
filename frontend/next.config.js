/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for Docker deployments
  output: "standalone",
  
  experimental: {
    serverActions: {
      allowedOrigins: ["localhost:3000"],
    },
  },
  
  // Environment variables available at build time
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
  },
  
  webpack: (config, { dev }) => {
    if (dev) {
      // Avoid ENOENT cache rename issues on some Windows setups
      config.cache = false;
    }
    return config;
  },
};

export default nextConfig;
