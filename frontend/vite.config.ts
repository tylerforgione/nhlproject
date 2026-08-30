import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { resolve } from 'node:path'

import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

import {
  renderStaticRouteDocument,
  staticRouteDocuments,
} from './static-route-documents'

const canonicalBuildPlaceholder = 'https://canonical.invalid/'

function buildStaticRouteDocuments() {
  return {
    name: 'static-route-documents',
    apply: 'build' as const,
    transformIndexHtml: {
      order: 'pre' as const,
      handler(html: string) {
        return html.replace('href="/"', `href="${canonicalBuildPlaceholder}"`)
      },
    },
    async closeBundle() {
      const outputDirectory = resolve(process.cwd(), 'dist')
      const homeDocumentPath = resolve(outputDirectory, 'index.html')
      const builtHomeHtml = await readFile(homeDocumentPath, 'utf8')
      const homeHtml = builtHomeHtml.replace(canonicalBuildPlaceholder, '/')
      await writeFile(homeDocumentPath, homeHtml)

      await Promise.all(
        staticRouteDocuments.map(async (route) => {
          const routeDirectory = resolve(outputDirectory, route.path)
          await mkdir(routeDirectory, { recursive: true })
          await writeFile(
            resolve(routeDirectory, 'index.html'),
            renderStaticRouteDocument(homeHtml, route),
          )
        }),
      )
    },
  }
}

export default defineConfig(({ mode }) => {
  const environment = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react(), buildStaticRouteDocuments()],
    server: {
      proxy: {
        '/api': {
          target:
            environment.VITE_API_PROXY_TARGET ?? 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  }
})
