def find_course_links(portal_frame):
    links = portal_frame.locator(
        "a.link-container[href*='/portal/site/']"
    )

    results = []

    for i in range(links.count()):
        link = links.nth(i)
        href = link.get_attribute("href")
        title = link.get_attribute("title")
        text = link.inner_text().strip()

        if href and title and title != "Home":
            results.append({
                "title": title,
                "text": text,
                "href": href,
            })

    return results


def find_course(portal_frame, target_course):
    courses = find_course_links(portal_frame)

    print(f"\n[AUMS] Course links found: {len(courses)}")

    for course in courses:
        if course["title"] == target_course:
            print("\n✅ Course found!")
            print("Course title:", course["title"])
            print("Course URL:", course["href"])
            return course

    # Fallback: partial title match
    for course in courses:
        if target_course in course["title"]:
            print("\n✅ Course found by partial match!")
            print("Course title:", course["title"])
            print("Course URL:", course["href"])
            return course

    print("\n❌ Target course not found.")
    return None


def find_course_frame(page, course_url):
    for frame in page.frames:
        if frame.url.rstrip("/") == course_url.rstrip("/"):
            return frame

    for frame in page.frames:
        if "/portal/site/" in frame.url and "tool/" not in frame.url:
            return frame

    return None


def find_assignments_link(course_frame):
    locator = course_frame.locator(
        "a.Mrphs-toolsNav__menuitem--link"
    )

    for i in range(locator.count()):
        link = locator.nth(i)
        title = link.get_attribute("title") or ""
        text = link.inner_text().strip()

        if text.lower() == "assignments" or title.startswith("Assignments"):
            return link.get_attribute("href")

    print("\n❌ Assignments link not found.")
    return None
