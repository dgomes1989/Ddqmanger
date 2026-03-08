import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/dashboard/Sidebar";

export const metadata: Metadata = {
  title: "DDQ Manager",
  description: "AI-powered Due Diligence Questionnaire assistant for investment managers",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-gray-50 font-sans">
        <div className="flex h-screen">
          <Sidebar />
          <main className="flex-1 overflow-auto">
            <div className="mx-auto max-w-6xl p-8">{children}</div>
          </main>
        </div>
      </body>
    </html>
  );
}
