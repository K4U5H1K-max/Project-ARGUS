import { SITE } from "@/lib/theme/tokens";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? SITE.url;

/** JSON-LD structured data for search engines. */
export function StructuredData() {
  const organization = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: SITE.name,
    url: siteUrl,
    description: SITE.description,
  };

  const website = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: SITE.name,
    url: siteUrl,
    description: SITE.description,
  };

  const software = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: SITE.name,
    applicationCategory: "BusinessApplication",
    description: SITE.description,
    operatingSystem: "Web",
    url: siteUrl,
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "USD",
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organization) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(website) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(software) }}
      />
    </>
  );
}
