import asyncio
from playwright.async_api import async_playwright
import json

async def investigate_redirects():
    async with async_playwright() as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Collect console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append({
            "type": msg.type,
            "text": msg.text
        }))

        # Collect page errors
        page_errors = []
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        print("=" * 80)
        print("INVESTIGATING /register PAGE")
        print("=" * 80)

        # Step 1-2: Navigate to register page and wait
        print("\n1. Navigating to http://localhost:3000/register")
        await page.goto("http://localhost:3000/register", wait_until="networkidle")

        print("2. Waiting 2 seconds for page to fully load...")
        await asyncio.sleep(2)

        # Step 3-4: Check current URL
        current_url = page.url
        print(f"\n3. Current URL after navigation: {current_url}")

        if current_url != "http://localhost:3000/register":
            print(f"4. ✗ Page REDIRECTED to: {current_url}")
        else:
            print("4. ✓ Page stayed at /register (no redirect)")

        # Step 5: Take screenshot
        screenshot_path = "/Users/mac/Projects/expense-tracker/frontend/register_page_screenshot.png"
        await page.screenshot(path=screenshot_path)
        print(f"\n5. Screenshot saved to: {screenshot_path}")

        # Step 6: Check console for errors
        print("\n6. Browser console messages:")
        if console_messages:
            for msg in console_messages:
                print(f"   [{msg['type'].upper()}] {msg['text']}")
        else:
            print("   No console messages")

        if page_errors:
            print("\n   Page errors:")
            for err in page_errors:
                print(f"   [ERROR] {err}")
        else:
            print("   No page errors")

        # Clear console messages for next navigation
        console_messages.clear()
        page_errors.clear()

        print("\n" + "=" * 80)
        print("INVESTIGATING /login PAGE")
        print("=" * 80)

        # Step 7-8: Navigate to login page
        print("\n7. Navigating to http://localhost:3000/login")
        await page.goto("http://localhost:3000/login", wait_until="networkidle")
        await asyncio.sleep(2)

        login_url = page.url
        print(f"8. Current URL after navigation: {login_url}")

        if login_url != "http://localhost:3000/login":
            print(f"   ✗ Page REDIRECTED to: {login_url}")
        else:
            print("   ✓ Page stayed at /login (no redirect)")

        # Take screenshot of login page
        login_screenshot_path = "/Users/mac/Projects/expense-tracker/frontend/login_page_screenshot.png"
        await page.screenshot(path=login_screenshot_path)
        print(f"\n   Screenshot saved to: {login_screenshot_path}")

        # Check console for login page
        print("\n   Browser console messages:")
        if console_messages:
            for msg in console_messages:
                print(f"   [{msg['type'].upper()}] {msg['text']}")
        else:
            print("   No console messages")

        if page_errors:
            print("\n   Page errors:")
            for err in page_errors:
                print(f"   [ERROR] {err}")
        else:
            print("   No page errors")

        # Step 9: Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"\n/register endpoint:")
        print(f"  - Final URL: {current_url}")
        print(f"  - Redirected: {'Yes' if current_url != 'http://localhost:3000/register' else 'No'}")

        print(f"\n/login endpoint:")
        print(f"  - Final URL: {login_url}")
        print(f"  - Redirected: {'Yes' if login_url != 'http://localhost:3000/login' else 'No'}")

        # Get page title and content for both
        await page.goto(current_url)
        register_title = await page.title()
        print(f"\nRegister page title: {register_title}")

        await page.goto(login_url)
        login_title = await page.title()
        print(f"Login page title: {login_title}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(investigate_redirects())
