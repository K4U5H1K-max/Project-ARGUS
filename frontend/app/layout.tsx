import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono, Space_Grotesk } from "next/font/google";

import { StructuredData } from "@/components/common/StructuredData";
import { GlobalBackground } from "@/components/layout/GlobalBackground";
import { Footer } from "@/components/layout/Footer";
import { TopNav } from "@/components/layout/TopNav";
import { MotionProvider } from "@/components/motion/MotionProvider";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { ThemeProvider } from "@/lib/theme/ThemeProvider";
import { SITE } from "@/lib/theme/tokens";

import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  display: "swap",
});

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? SITE.url;

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: `${SITE.name} | ${SITE.tagline}`,
    template: `%s | ${SITE.name}`,
  },
  description: SITE.description,
  keywords: [
    "industrial safety",
    "digital twin",
    "risk assessment",
    "knowledge graph",
    "geo intelligence",
    "AI safety platform",
    "operational intelligence",
    "explainable AI",
    "industrial IoT",
  ],
  authors: [{ name: "ARGUS", url: siteUrl }],
  creator: "ARGUS",
  publisher: "ARGUS",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: siteUrl,
    siteName: SITE.name,
    title: `${SITE.name} — ${SITE.tagline}`,
    description: SITE.description,
  },
  twitter: {
    card: "summary_large_image",
    title: `${SITE.name} — ${SITE.tagline}`,
    description: SITE.description,
    creator: "@argus",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: "/favicon.svg",
    apple: "/favicon.svg",
  },
  category: "technology",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f5f7fa" },
    { media: "(prefers-color-scheme: dark)", color: "#0a0e14" },
  ],
  width: "device-width",
  initialScale: 1,
  colorScheme: "dark light",
};

const themeScript = `
(function() {
  try {
    var stored = localStorage.getItem('argus-theme');
    var mode = stored === 'light' || stored === 'dark' ? stored : null;
    var resolved = mode || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.classList.add(resolved);
    document.documentElement.style.colorScheme = resolved;
  } catch (e) {}
})();
`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
        <StructuredData />
      </head>
      <body className="min-h-full flex flex-col font-sans">
        <a
          href="#home"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-chip focus:border focus:border-accent-cyan/40 focus:bg-bg-elevated focus:px-4 focus:py-2 focus:font-mono focus:text-sm focus:text-accent-cyan"
        >
          Skip to content
        </a>
        <QueryProvider>
          <ThemeProvider>
            <MotionProvider>
              <GlobalBackground />
              <TopNav />
              <main id="main-content" className="flex-1">
                {children}
              </main>
              <Footer />
            </MotionProvider>
          </ThemeProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
