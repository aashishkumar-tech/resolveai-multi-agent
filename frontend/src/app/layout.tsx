import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Hierarchical Agent UI",
  description: "Production-ready hierarchical multi-agent demo UI",
  icons: {
    icon: "/icon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
