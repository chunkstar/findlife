import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OP-COM // Operational Command",
  description:
    "Tactical executive coach. BLUF first. Wisdom Council on demand.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
