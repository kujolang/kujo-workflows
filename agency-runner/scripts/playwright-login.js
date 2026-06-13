const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

async function main() {
  const loginUrl = process.env.AGENCY_LOGIN_URL;
  const sessionFile = process.env.AGENCY_SESSION_FILE;
  const manual = process.env.AGENCY_MANUAL === "1";
  if (!loginUrl || !sessionFile) {
    throw new Error("AGENCY_LOGIN_URL and AGENCY_SESSION_FILE are required");
  }

  const browser = await chromium.launch({ headless: !manual });
  const page = await browser.newPage();
  await page.goto(loginUrl, { waitUntil: "domcontentloaded" });

  if (!manual) {
    const username = process.env.AGENCY_USERNAME || "";
    const password = process.env.AGENCY_PASSWORD || "";
    if (!username || !password) {
      throw new Error("Username/password are required unless manual login is enabled");
    }
    await page.locator(process.env.AGENCY_USERNAME_SELECTOR).first().fill(username);
    await page.locator(process.env.AGENCY_PASSWORD_SELECTOR).first().fill(password);
    await Promise.all([
      page.waitForLoadState("networkidle", { timeout: 30000 }).catch(() => {}),
      page.locator(process.env.AGENCY_SUBMIT_SELECTOR).first().click(),
    ]);
  } else {
    console.log("Manual login window opened. Complete login, then press Enter here.");
    await new Promise((resolve) => process.stdin.once("data", resolve));
  }

  const pattern = process.env.AGENCY_SUCCESS_URL_PATTERN || "";
  if (pattern && !(new RegExp(pattern).test(page.url()))) {
    throw new Error(`Login success URL pattern did not match current URL: ${page.url()}`);
  }

  fs.mkdirSync(path.dirname(sessionFile), { recursive: true });
  await page.context().storageState({ path: sessionFile });
  await browser.close();
  console.log(`Saved storage state: ${sessionFile}`);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
