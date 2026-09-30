# aums/portal.py

def find_portal_frame(page):

    print("🔍 Looking for AUMS portal frame...")

    for frame in page.frames:

        url = frame.url.lower()

        # Ignore CAS login/logout pages
        if "/cas/login" in url:
            continue

        if "/cas/logout" in url:
            continue

        # Actual AUMS portal
        if "/portal" in url:

            print(
                f"[AUMS] Portal frame: {frame.url}"
            )

            print("✅ AUMS portal frame found!")

            return frame

    print("❌ AUMS portal frame not found.")

    return None