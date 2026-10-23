import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IntelliAssist | AI Support",
  description: "AI-powered customer support assistant",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
