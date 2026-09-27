import type { Metadata } from "next";
import localFont from "next/font/local";
import { Analytics } from "@vercel/analytics/react";
import "./globals.css";

const spaceGrotesk = localFont({
  src: [
    {
      path: "../../public/fonts/SpaceGrotesk-Regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../../public/fonts/SpaceGrotesk-Medium.woff2",
      weight: "500",
      style: "normal",
    },
    {
      path: "../../public/fonts/SpaceGrotesk-Bold.woff2",
      weight: "700",
      style: "normal",
    },
  ],
  variable: "--font-space-grotesk",
  display: "swap",
});

const inter = localFont({
  src: [
    {
      path: "../../public/fonts/Inter-Regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../../public/fonts/Inter-Medium.woff2",
      weight: "500",
      style: "normal",
    },
    {
      path: "../../public/fonts/Inter-SemiBold.woff2",
      weight: "600",
      style: "normal",
    },
    {
      path: "../../public/fonts/Inter-Bold.woff2",
      weight: "700",
      style: "normal",
    },
  ],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = localFont({
  src: [
    {
      path: "../../public/fonts/JetBrainsMono-Regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../../public/fonts/JetBrainsMono-Medium.woff2",
      weight: "500",
      style: "normal",
    },
    {
      path: "../../public/fonts/JetBrainsMono-Bold.woff2",
      weight: "700",
      style: "normal",
    },
  ],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "UBSI API: Unofficial REST API Aggregator 6 Layanan Kampus UBSI | Muara AI",
  description:
    "Agregator REST API modern untuk layanan Universitas Bina Sarana Informatika (SIAKAD, Elearning MyBest, E-Journal, E-Library, Repository, Berita). Caching Redis sub-250ms, open-source & developer-first.",
  keywords: [
    "UBSI API",
    "SIAKAD UBSI API",
    "Elearning MyBest UBSI",
    "Ejournal UBSI",
    "Muara AI",
    "API Kampus UBSI",
    "Yuken Velino",
    "Verzio",
  ],
  metadataBase: new URL("https://ubsi-api.muaraai.com"),
  alternates: {
    canonical: "https://ubsi-api.muaraai.com",
  },
  openGraph: {
    title: "UBSI API: Unofficial REST API Aggregator 6 Layanan Kampus UBSI",
    description:
      "Agregator data modern berkecepatan tinggi untuk SIAKAD, Elearning, Jurnal, E-Library, dan Repository UBSI.",
    url: "https://ubsi-api.muaraai.com",
    siteName: "UBSI API: Muara AI",
    locale: "id_ID",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "UBSI API: Unofficial REST API Aggregator 6 Layanan Kampus UBSI",
    description:
      "Agregator REST API modern untuk 6 layanan Universitas Bina Sarana Informatika.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": ["SoftwareApplication", "WebAPI"],
    name: "UBSI API",
    applicationCategory: "DeveloperApplication, EducationalApplication",
    operatingSystem: "Cloud, Docker, Linux",
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "IDR",
    },
    author: [
      {
        "@type": "Person",
        name: "Yuken Velino",
        url: "https://github.com/Curzyori",
      },
      {
        "@type": "Person",
        name: "Verzio",
        url: "https://github.com/MyKineID",
      },
    ],
    publisher: {
      "@type": "Organization",
      name: "Muara AI",
      url: "https://github.com/MuaraAI",
    },
  };

  return (
    <html
      lang="id"
      className={`${spaceGrotesk.variable} ${inter.variable} ${jetbrainsMono.variable}`}
    >
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className="bg-background text-foreground antialiased min-h-screen">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-[#2DD4BF] focus:text-[#06251F] focus:font-semibold focus:rounded-md focus:shadow-float focus:outline-none focus:ring-2 focus:ring-[#2DD4BF]"
        >
          Langsung ke konten utama
        </a>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
