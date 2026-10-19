process.env.BROWSER_CHANNEL = "chromium";

const { chromium } = require("C:/Users/Srushti/AppData/Roaming/npm/node_modules/notebooklm-mcp/node_modules/patchright");
const { CONFIG, NOTEBOOKLM_AUTH_URL } = require("C:/Users/Srushti/AppData/Roaming/npm/node_modules/notebooklm-mcp/dist/config.js");
const { AuthManager } = require("C:/Users/Srushti/AppData/Roaming/npm/node_modules/notebooklm-mcp/dist/auth/auth-manager.js");

function isNotebookUrl(url) {
  if (!url) return false;
  return (
    url.startsWith("https://notebook.google.com/") ||
    url.startsWith("https://notebooklm.google.com/") ||
    url.includes("notebook.google.com") ||
    url.includes("notebooklm.google.com")
  );
}

async function main() {
  console.log("====================================================");
  console.log("🚀 Starting NotebookLM / Gemini Notebook Authentication...");
  console.log(`📁 Profile Dir: ${CONFIG.chromeProfileDir}`);
  console.log("====================================================");

  const auth = new AuthManager();

  const launchOptions = {
    headless: false,
    viewport: CONFIG.viewport,
    locale: "en-US",
    timezoneId: "Europe/Berlin",
    args: [
      "--disable-blink-features=AutomationControlled",
      "--disable-dev-shm-usage",
      "--no-first-run",
      "--no-default-browser-check",
    ],
  };

  const context = await chromium.launchPersistentContext(
    CONFIG.chromeProfileDir,
    launchOptions
  );

  const page = context.pages().length > 0 ? context.pages()[0] : await context.newPage();

  const currentUrl = page.url();
  console.log(`🌐 Initial URL: ${currentUrl}`);

  if (!isNotebookUrl(currentUrl)) {
    console.log("Navigating to NotebookLM sign-in...");
    try {
      await page.goto(NOTEBOOKLM_AUTH_URL, { timeout: 60000 });
    } catch (e) {
      console.log("Navigation note:", e.message);
    }
  }

  console.log("⏳ Waiting for NotebookLM landing page (checks both notebook.google.com and notebooklm.google.com)...");

  const checkInterval = 1000;
  const maxAttempts = 300; // 5 minutes

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const url = page.url();

    if (isNotebookUrl(url) && !url.includes("accounts.google.com")) {
      console.log(`\n✅ NotebookLM detected! Current URL: ${url}`);
      console.log("💾 Saving session credentials to disk (state.json)...");
      await page.waitForTimeout(2000);
      await auth.saveBrowserState(context, page);
      console.log("🎉 Authentication successfully saved!");
      await context.close();
      process.exit(0);
    }

    if (attempt % 5 === 0) {
      console.log(`[Waiting] Current page: ${url.substring(0, 70)}...`);
    }

    await new Promise((r) => setTimeout(r, checkInterval));
  }

  console.error("❌ Authentication timed out after 5 minutes.");
  await context.close();
  process.exit(1);
}

main().catch((err) => {
  console.error("Fatal Error:", err);
  process.exit(1);
});
