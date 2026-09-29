from pathlib import Path

from config import AUMS_LOGIN_URL, SESSION_FILE


def open_aums(page):
    print("\n🌐 Opening AUMS...")

    page.goto(
        AUMS_LOGIN_URL,
        wait_until="domcontentloaded"
    )

    page.wait_for_timeout(3000)


def wait_for_manual_login(page):
    print("\n" + "=" * 70)
    print("🔐 AUMS LOGIN REQUIRED")
    print("=" * 70)

    print("\nAUMS has opened in the browser.")
    print("Please log in manually.")

    input("\nPress ENTER after you have reached the AUMS home page...")

    page.wait_for_timeout(3000)

    print("\nCurrent URL:")
    print(page.url)


def save_session(context):
    path = Path(SESSION_FILE)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    context.storage_state(
        path=str(path)
    )

    print(f"\n✅ Session saved: {path}")


def session_exists():
    return Path(SESSION_FILE).exists()