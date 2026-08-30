export interface StaticRouteDocument {
  path: string
  title: string
  canonicalPath: string
}

export const staticRouteDocuments: StaticRouteDocument[] = [
  {
    path: 'games',
    title: 'NHL Games | Hockey Stat Pack',
    canonicalPath: '/games',
  },
]

export function renderStaticRouteDocument(
  homeHtml: string,
  route: StaticRouteDocument,
): string {
  return homeHtml
    .replace(
      /<title>[^<]*<\/title>/,
      `<title>${route.title}</title>`,
    )
    .replace(
      /<link rel="canonical" href="[^"]*" \/>/,
      `<link rel="canonical" href="${route.canonicalPath}" />`,
    )
}
