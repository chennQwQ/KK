import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG Studio",
  description: "Enterprise RAG object studio",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
