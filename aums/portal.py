def find_portal_frame(page):
    for frame in page.frames:
        if "/portal" in frame.url and "/portal/tool/" not in frame.url:
            print("\n[AUMS] Portal frame:", frame.url)
            return frame

    print("\n❌ AUMS portal frame not found.")
    return None
