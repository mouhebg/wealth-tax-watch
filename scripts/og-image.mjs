// Renders scripts/og-image.html to assets/og-image.png (1200x630).
// Needs Playwright: npx playwright@latest (or a global install) with Chromium.
import { chromium } from "playwright";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
await page.goto(pathToFileURL(path.join(root, "scripts/og-image.html")).href, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: path.join(root, "assets/og-image.png") });
await browser.close();
console.log("wrote assets/og-image.png");
