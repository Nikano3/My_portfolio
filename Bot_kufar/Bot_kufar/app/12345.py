import asyncio
from playwright.async_api import async_playwright
chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
async def brow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=chrome_path, headless=True)
        page = await browser.new_page()

asyncio.run(brow())