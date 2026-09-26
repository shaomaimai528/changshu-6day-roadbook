const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const BASE_URL = process.env.TRIP_URL || "http://127.0.0.1:8080/";
const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const OUT_DIR = process.env.TRIP_VERIFY_OUT || path.join(process.cwd(), ".verify");

fs.mkdirSync(OUT_DIR, { recursive: true });

async function waitForMap(page) {
  await page.waitForFunction(() => {
    return document.querySelector("#map") && document.querySelectorAll(".leaflet-marker-icon").length > 0;
  }, null, { timeout: 20000 });
  await page.waitForTimeout(500);
}

async function assert(condition, message, failures) {
  if (!condition) failures.push(message);
}

async function runViewport(browser, viewport) {
  const context = await browser.newContext({
    viewport: { width: viewport.width, height: viewport.height },
    deviceScaleFactor: 1,
    locale: "zh-CN"
  });
  const page = await context.newPage();
  const failures = [];
  const consoleErrors = [];

  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => consoleErrors.push("PAGEERROR " + error.message));

  await page.goto(BASE_URL, { waitUntil: "domcontentloaded", timeout: 30000 });
  await waitForMap(page);

  await assert((await page.title()).includes("常熟出发"), "页面标题不正确", failures);
  await assert((await page.locator(".leaflet-marker-icon").count()) >= 3, "地图标记没有渲染", failures);
  await assert((await page.locator(".leaflet-overlay-pane canvas").count()) >= 1, "路线画布没有渲染", failures);

  if (viewport.name === "mobile") {
    await assert(await page.locator(".rail").isHidden(), "移动端仍显示桌面行程栏", failures);
    await assert(await page.locator("#map").isVisible(), "移动端地图不可见", failures);
    await assert(await page.locator("#mobileDaybar").isVisible(), "移动端日期条不可见", failures);
    await assert((await page.locator(".mobile-day-chip").count()) === 6, "移动端日期条不是 6 天", failures);

    for (const dayId of ["d1", "d2", "d3", "d4", "d5", "d6"]) {
      await page.locator(`.mobile-day-chip[data-day-chip="${dayId}"]`).click();
      await page.waitForTimeout(120);
      await assert(await page.locator(`.mobile-day-chip[data-day-chip="${dayId}"]`).getAttribute("aria-selected") === "true", `移动端 ${dayId} 未高亮`, failures);
      await assert((await page.locator("#mobileBrief").innerText()).length > 10, `移动端 ${dayId} 速览为空`, failures);
    }

    await page.locator('.mobile-day-chip[data-day-chip="d1"]').click();
    await page.waitForTimeout(120);
    await page.locator("#mobileBrief [data-open-day]").click();
    await page.waitForTimeout(250);
    await assert(await page.locator("#detailPanel").isVisible(), "移动端当天详情不能展开", failures);
    const mobileDetailText = await page.locator("#detailContent").innerText();
    await assert(mobileDetailText.includes("122 km / 2 h"), "移动端 10/1 路线距离缺失", failures);
    await assert(mobileDetailText.includes("当天时间轴"), "移动端当天时间轴缺失", failures);
    await assert(mobileDetailText.includes("预约提醒"), "移动端预约提醒缺失", failures);

    await page.locator("#sheetHandle").click();
    await page.waitForTimeout(250);
    await assert(await page.locator("#detailPanel").isHidden(), "移动端当天详情不能收起", failures);
  } else {
    await assert(await page.locator(".rail").isVisible(), "桌面行程栏不可见", failures);
    for (const dayId of ["d1", "d2", "d3", "d4", "d5", "d6"]) {
      await page.locator(`.rail-scroll [data-day="${dayId}"]`).click();
      await page.waitForTimeout(150);
      await assert(await page.locator(`.rail-scroll [data-day="${dayId}"]`).getAttribute("aria-pressed") === "true", `${dayId} 未高亮`, failures);
    }
    await page.locator('.rail-scroll [data-day="d1"]').click();
    await page.waitForTimeout(150);
    await assert((await page.locator("#detailContent").innerText()).includes("122 km / 2 h"), "10/1 路线距离缺失", failures);
    await page.locator('.rail-scroll [data-day="d2"]').click();
    await page.waitForTimeout(150);
    await assert((await page.locator("#detailContent").innerText()).includes("65 km / 1 h"), "10/2 路线距离缺失", failures);
    await page.locator('.rail-scroll [data-day="d3"]').click();
    await page.waitForTimeout(150);
    await assert((await page.locator("#detailContent").innerText()).includes("秦王宫"), "10/3 景点详情缺失", failures);
    await page.locator('.rail-scroll [data-day="d4"]').click();
    await page.waitForTimeout(150);
    await page.locator('[data-option="a"]').click();
    await page.waitForTimeout(150);
    await assert((await page.locator("#detailContent").innerText()).includes("皇家园林复刻"), "10/4 方案 A 详情缺失", failures);
    await page.locator('[data-option="b"]').click();
    await page.waitForTimeout(150);
    await assert((await page.locator("#detailContent").innerText()).includes("夜场灯会"), "10/4 方案 B 详情缺失", failures);
    await page.locator('.rail-scroll [data-day="d5"]').click();
    await page.waitForTimeout(150);
    await assert((await page.locator("#detailContent").innerText()).includes("东湖"), "10/5 东湖详情缺失", failures);
    await page.locator('.rail-scroll [data-day="d6"]').click();
    await page.waitForTimeout(150);
    await assert((await page.locator("#detailContent").innerText()).includes("1.5 km"), "10/6 月河短途距离缺失", failures);

    await page.locator("#overviewButton").click();
    await page.waitForTimeout(200);
    await assert(await page.locator("#overviewButton").getAttribute("aria-pressed") === "true", "总览恢复失败", failures);
    await page.keyboard.press("ArrowRight");
    await page.waitForTimeout(150);
    await assert((await page.locator("#detailContent").innerText()).includes("10/1"), "键盘切换日期失败", failures);
  }

  let visibleText = await page.locator("body").innerText();
  for (const oldTerm of ["宁波", "神仙居", "南浔", "鲁迅故里", "沈园", "南湖"]) {
    await assert(!visibleText.includes(oldTerm), `页面仍含旧路线词：${oldTerm}`, failures);
  }
  if (viewport.name === "mobile") {
    await page.locator('.mobile-day-chip[data-day-chip="d1"]').click();
    await page.waitForTimeout(120);
    await page.locator("#mobileBrief [data-open-day]").click();
    await page.waitForTimeout(250);
    await assert(await page.locator("#detailPanel").isVisible(), "移动端详情面板不能展开", failures);
  } else {
    await page.locator("#overviewButton").click();
    await page.waitForTimeout(200);
    await page.locator("#toggleDetailButton").click();
    await page.waitForTimeout(200);
  }
  visibleText = await page.locator("#detailContent").innerText();
  await assert(visibleText.includes("临浦"), "10/1 住宿信息缺失", failures);

  if (viewport.name === "mobile") {
    await page.locator("#sheetHandle").click();
    await page.waitForTimeout(200);
    for (const [dayId, stay] of [["d2", "横店"], ["d5", "绍兴"]]) {
      await page.locator(`.mobile-day-chip[data-day-chip="${dayId}"]`).click();
      await page.waitForTimeout(120);
      await page.locator("#mobileBrief [data-open-day]").click();
      await page.waitForTimeout(200);
      await assert((await page.locator("#detailContent").innerText()).includes(stay), `${dayId} 住宿信息缺失`, failures);
      await page.locator("#sheetHandle").click();
      await page.waitForTimeout(200);
    }
  } else {
    await page.locator("#toggleDetailButton").click();
    await page.waitForTimeout(200);
    for (const [dayId, stay] of [["d2", "横店"], ["d5", "绍兴"]]) {
      await page.locator(`.rail-scroll [data-day="${dayId}"]`).click();
      await page.waitForTimeout(150);
      await assert((await page.locator("#detailContent").innerText()).includes(stay), `${dayId} 住宿信息缺失`, failures);
    }
  }

  const screenshot = path.join(OUT_DIR, `${viewport.name}.png`);
  await page.screenshot({ path: screenshot, fullPage: false });
  await context.close();

  return { viewport: viewport.name, failures, consoleErrors, screenshot };
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: EDGE });
  const results = [];
  for (const viewport of [
    { name: "desktop", width: 1440, height: 900 },
    { name: "tablet", width: 1024, height: 768 },
    { name: "mobile", width: 390, height: 844 }
  ]) {
    results.push(await runViewport(browser, viewport));
  }
  await browser.close();
  fs.writeFileSync(path.join(OUT_DIR, "results.json"), JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 2));
  if (results.some((result) => result.failures.length || result.consoleErrors.length)) {
    process.exitCode = 1;
  }
})();
