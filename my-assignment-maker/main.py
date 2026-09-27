from playwright.sync_api import sync_playwright

AUMS_URL = (
    "https://aumscb.amrita.edu/cas/login"
    "?service=https%3A%2F%2Faumscb.amrita.edu%2Faums%2FJsp%2FCore_Common%2Findex.jsp"
)

TARGET_COURSE = "Int M.Sc..2023.R.DS.1.22CSC402"


with sync_playwright() as p:

    # =======================================
    # 1. Open browser
    # =======================================

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    print("Opening AUMS...")

    page.goto(AUMS_URL)

    print("\nAUMS opened.")
    print("Log in manually.")

    input("\nPress ENTER after you have logged in...")


    # =======================================
    # 2. Check login
    # =======================================

    try:

        page.get_by_text(
            "Welcome Dhyan Sudheer"
        ).wait_for(
            state="visible",
            timeout=10000
        )

        print("\n✅ Login detected!")

    except:

        print("\n❌ Login detection failed.")

        browser.close()
        exit()


    # =======================================
    # 3. Find portal frame
    # =======================================

    print(
        "\n🔍 Looking for AUMS portal frame..."
    )

    portal_frame = None

    for frame in page.frames:

        if frame.url.rstrip("/") == (
            "https://aumscb.amrita.edu/portal"
        ):

            portal_frame = frame

            break


    if portal_frame is None:

        print(
            "\n❌ Portal frame not found."
        )

        browser.close()

        exit()


    print(
        "\n✅ Portal frame found!"
    )


    # =======================================
    # 4. Find target course
    # =======================================

    print(
        f"\n🔍 Looking for course:\n"
        f"{TARGET_COURSE}"
    )

    course = portal_frame.locator(
        f'a.link-container[title="{TARGET_COURSE}"]'
    )


    if course.count() == 0:

        print(
            "\n❌ Course not found."
        )

        browser.close()

        exit()


    print(
        "\n✅ Course found!"
    )


    # =======================================
    # 5. Get course URL automatically
    # =======================================

    course_url = course.first.get_attribute(
        "href"
    )

    print(
        "\nCourse URL:"
    )

    print(
        course_url
    )


    if not course_url:

        print(
            "\n❌ Course URL could not be found."
        )

        browser.close()

        exit()


    # =======================================
    # 6. Extract site ID
    # =======================================

    site_id = course_url.rstrip("/").split("/")[-1]

    print(
        "\nDetected site ID:"
    )

    print(
        site_id
    )


    # =======================================
    # 7. Open course directly
    # =======================================

    print(
        "\n🖱️ Opening course..."
    )

    page.goto(
        course_url,
        wait_until="domcontentloaded"
    )

    page.wait_for_timeout(3000)


    # =======================================
    # 8. Find course frame
    # =======================================

    print(
        "\n🔍 Looking for course page frame..."
    )

    course_frame = None

    for frame in page.frames:

        if f"/portal/site/{site_id}" in frame.url:

            course_frame = frame

            break


    if course_frame is None:

        print(
            "\n❌ Course frame not found."
        )

        print(
            "\nAvailable frames:"
        )

        for i, frame in enumerate(page.frames):

            print(
                f"{i}: {frame.url}"
            )

        browser.close()

        exit()


    print(
        "\n✅ Course frame found!"
    )

    print(
        "\nCourse frame URL:"
    )

    print(
        course_frame.url
    )


    # =======================================
    # 9. Find Assignments link
    # =======================================

    print(
        "\n🔍 Searching for Assignments..."
    )

    assignments = course_frame.locator(
        'a.Mrphs-toolsNav__menuitem--link'
        '[title^="Assignments"]'
    )


    if assignments.count() == 0:

        print(
            "\n❌ Assignments link not found."
        )

        browser.close()

        exit()


    print(
        "\n✅ Assignments link found!"
    )


    # =======================================
    # 10. Extract Assignments URL
    # =======================================

    assignments_url = (
        assignments.first.get_attribute(
            "href"
        )
    )


    print(
        "\nAssignments URL:"
    )

    print(
        assignments_url
    )


    if not assignments_url:

        print(
            "\n❌ Assignments URL not found."
        )

        browser.close()

        exit()


    # =======================================
    # 11. Open Assignments directly
    # =======================================

    print(
        "\n🖱️ Opening Assignments..."
    )

    page.goto(
        assignments_url,
        wait_until="domcontentloaded"
    )

    page.wait_for_timeout(3000)


    # =======================================
    # 12. Print current URL
    # =======================================

    print(
        "\n✅ Assignments page opened!"
    )

    print(
        "\nCurrent URL:"
    )

    print(
        page.url
    )


    # =======================================
    # 13. Extract page content
    # =======================================

    print(
        "\n\n"
        + "=" * 70
    )

    print(
        "ASSIGNMENTS PAGE CONTENT"
    )

    print(
        "=" * 70
    )


    for i, frame in enumerate(page.frames):

        try:

            text = frame.locator(
                "body"
            ).inner_text(
                timeout=3000
            )

            if text.strip():

                print(
                    f"\n--- FRAME {i} ---"
                )

                print(
                    text[:10000]
                )

        except:

            pass


    # =======================================
    # 14. Keep browser open
    # =======================================

    input(
        "\nPress ENTER to close the browser..."
    )

    browser.close()