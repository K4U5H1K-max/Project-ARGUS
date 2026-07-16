import type { MetadataRoute } from "next";

import { SITE } from "@/lib/theme/tokens";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: SITE.url,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 1,
    },
  ];
}
