from pathlib import Path

from playwright.sync_api import sync_playwright

from config import SESSION_FILE


def create_browser(headless=False):
    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(
        headless=headless
    )

    session_path = Path(SESSION_FILE)

    # ----------------------------------------------------
    # Restore existing AUMS session if available
    # ----------------------------------------------------

    if session_path.exists():
        print(f"\n🔐 Loading saved session: {session_path}")

        context = browser.new_context(
            storage_state=str(session_path)
        )

    else:
        print("\n🆕 No saved session found.")

        context = browser.new_context()

    page = context.new_page()

    return playwright, browser, context, page


def close_browser(playwright, browser):
    try:
        browser.close()
    finally:
        playwright.stop()