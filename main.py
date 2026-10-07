from datetime import datetime
from config import (
    DOWNLOAD_DIR,
    SESSION_FILE,
)

from aums.browser import create_browser, close_browser

from aums.login import (
    open_aums,
    wait_for_manual_login,
    save_session,
    session_exists,
)

from aums.portal import find_portal_frame

from aums.courses import (
    find_course_links,
    find_course_frame,
    find_assignments_link,
)

from aums.assignments import (
    extract_assignments,
    extract_assignment_metadata,
)

from aums.attachments import download_assignment_files

from utils.console import print_heading
from utils.urls import make_absolute_url


def run():

    print_heading("📚 AUMS ASSIGNMENT MAKER")

    # ----------------------------------------------------
    # Start browser
    # ----------------------------------------------------

    playwright, browser, context, page = create_browser(
        headless=False
    )

    try:

        # ------------------------------------------------
        # Open AUMS
        # ------------------------------------------------

        open_aums(page)

        # ------------------------------------------------
        # Check saved session
        # ------------------------------------------------

        if session_exists():

            print(
                f"\n🔐 Existing session found: {SESSION_FILE}"
            )

        else:

            print(
                "\n🆕 No saved AUMS session found."
            )

        # ------------------------------------------------
        # Check whether session is actually valid
        # ------------------------------------------------

        print(
            "\n🔍 Looking for AUMS portal frame..."
        )

        portal_frame = find_portal_frame(page)

        # ------------------------------------------------
        # Saved session invalid / login required
        # ------------------------------------------------
        
        if portal_frame is None:

            print(
                "\n⚠️ AUMS login is required."
            )

            wait_for_manual_login(page)

            # --------------------------------------------
            # Save fresh authenticated session
            # --------------------------------------------

            print(
                "\n💾 Saving AUMS session..."
            )

            save_session(context)

            # --------------------------------------------
            # Give AUMS time to finish loading
            # --------------------------------------------

            page.wait_for_timeout(3000)

            # --------------------------------------------
            # Check portal again
            # --------------------------------------------

            print(
                "\n🔍 Checking AUMS portal again..."
            )

            portal_frame = find_portal_frame(page)

        # ------------------------------------------------
        # Portal still not found
        # ------------------------------------------------

        if portal_frame is None:

            print(
                "\n❌ AUMS portal frame not found."
            )

            print(
                "Please check that you successfully logged in."
            )

            return

        print(
            "\n✅ AUMS portal frame found!"
        )
                # =================================================
        # ALL COURSES → ALL PENDING ASSIGNMENTS
        # =================================================

        pending_assignments = (
            collect_all_pending_assignments(
                page,
                portal_frame
            )
        )

        # =================================================
        # DISPLAY FINAL RESULTS
        # =================================================

        print("\n" + "=" * 70)
        print("📚 ALL PENDING ASSIGNMENTS")
        print("=" * 70)

        if not pending_assignments:

            print("\n✅ No pending assignments found.")

        else:

            for index, assignment in enumerate(
                pending_assignments,
                1
            ):

                print("\n" + "-" * 70)

                print(
                    f"{index}. "
                    f"{assignment.get('course', 'Unknown Course')}"
                )

                print(
                    f"   📝 Assignment: "
                    f"{assignment.get('title', 'Unknown')}"
                )

                print(
                    f"   📌 Status: "
                    f"{assignment.get('status', 'Unknown')}"
                )

                print(
                    f"   📅 Open: "
                    f"{assignment.get('open', 'Unknown')}"
                )

                print(
                    f"   ⏰ Due: "
                    f"{assignment.get('due', 'Unknown')}"
                )

                print(
                    f"   🔗 URL: "
                    f"{assignment.get('url', 'Unknown')}"
                )

            print("\n" + "=" * 70)

            print(
                f"📊 TOTAL PENDING ASSIGNMENTS: "
                f"{len(pending_assignments)}"
            )

            print("=" * 70)

        input(
            "\nPress ENTER to close the browser..."
        )
        # =================================================
        # COURSE
        # =================================================

        print(
            "\n🔍 Looking for course:"
        )

        print(
            TARGET_COURSE
        )

        course = find_course(
            portal_frame,
            TARGET_COURSE
        )

        if course is None:

            print(
                "\n❌ Target course not found."
            )

            return

        # ------------------------------------------------
        # Open course
        # ------------------------------------------------

        print(
            "\n🖱️ Opening course..."
        )

        course_url = make_absolute_url(
            portal_frame.url,
            course["href"]
        )

        print(
            "\nCourse URL:"
        )

        print(
            course_url
        )

        page.goto(
            course_url,
            wait_until="domcontentloaded"
        )

        page.wait_for_timeout(2500)

        # ------------------------------------------------
        # Find course frame
        # ------------------------------------------------

        course_frame = find_course_frame(
            page,
            course["href"]
        )

        if course_frame is None:

            print(
                "\n❌ Course frame not found."
            )

            return

        print(
            "\n✅ Course frame found!"
        )

        print(
            "\nCourse frame URL:"
        )

        print(
            course_frame.url
        )

        # =================================================
        # ASSIGNMENTS
        # =================================================

        assignments_href = find_assignments_link(
            course_frame
        )

        if not assignments_href:

            print(
                "\n❌ Assignments link not found."
            )

            return

        assignments_url = make_absolute_url(
            course_frame.url,
            assignments_href
        )

        print(
            "\n🖱️ Opening Assignments directly..."
        )

        print(
            "\nAssignments URL:"
        )

        print(
            assignments_url
        )

        page.goto(
            assignments_url,
            wait_until="domcontentloaded"
        )

        page.wait_for_timeout(2500)

        print(
            "\n✅ Assignments page opened!"
        )

        # =================================================
        # FIND TARGET ASSIGNMENT
        # =================================================

        print(
            "\n🔍 Looking for assignment:"
        )

        print(
            TARGET_ASSIGNMENT
        )

        target_assignment = find_target_assignment(
            page,
            TARGET_ASSIGNMENT
        )

        if target_assignment is None:

            print(
                "\n❌ Target assignment not found."
            )

            return

        print(
            "\n✅ Assignment found!"
        )

        # =================================================
        # OPEN ASSIGNMENT
        # =================================================

        assignment_url = make_absolute_url(
            page.url,
            target_assignment["url"]
        )

        print(
            "\n🖱️ Opening assignment..."
        )

        print(
            "\nAssignment URL:"
        )

        print(
            assignment_url
        )

        # =================================================
        # EXTRACT ASSIGNMENT
        # =================================================

        assignment_data = inspect_assignment_page(
            page,
            assignment_url
        )

        # =================================================
        # DOWNLOAD FILES
        # =================================================

        print_heading(
            "📥 DOWNLOADING ASSIGNMENT FILES"
        )

        downloaded_files = (
            download_assignment_files(
                assignment_data,
                DOWNLOAD_DIR
            )
        )

        # =================================================
        # FINAL SUMMARY
        # =================================================

        print_heading(
            "✅ ASSIGNMENT EXTRACTION COMPLETE"
        )

        print(
            "Title:",
            target_assignment.get(
                "title",
                "Unknown"
            )
        )

        print(
            "Status:",
            target_assignment.get(
                "status",
                "Unknown"
            )
        )

        print(
            "Open:",
            target_assignment.get(
                "open",
                "Unknown"
            )
        )

        print(
            "Due:",
            target_assignment.get(
                "due",
                "Unknown"
            )
        )

        # =================================================
        # DOWNLOADED FILES
        # =================================================

        print(
            "\n📎 DOWNLOADED FILES:"
        )

        if downloaded_files:

            for file_path in downloaded_files:

                print(
                    "   ✓",
                    file_path
                )

        else:

            print(
                "   No files downloaded."
            )

        print_heading(
            "🎉 DONE"
        )

        input(
            "\nPress ENTER to close the browser..."
        )

    finally:

        close_browser(
            playwright,
            browser
        )

def collect_all_pending_assignments(page, portal_frame):
    print("\n" + "=" * 70)
    print("📚 SCANNING ALL COURSES")
    print("=" * 70)

    courses = find_course_links(portal_frame)

    print(f"\n📚 Courses found: {len(courses)}")

    all_pending = []

    for index, course in enumerate(courses, 1):

        course_title = course["title"]

        print("\n" + "-" * 70)
        print(f"📖 COURSE {index}/{len(courses)}")
        print(course_title)
        print("-" * 70)

        try:

            course_url = make_absolute_url(
                portal_frame.url,
                course["href"]
            )

            print(f"🌐 Opening course...")

            page.goto(
                course_url,
                wait_until="domcontentloaded"
            )

            page.wait_for_timeout(2000)

            course_frame = find_course_frame(
                page,
                course_url
            )

            if course_frame is None:
                print("❌ Course frame not found.")
                continue

            assignments_href = find_assignments_link(
                course_frame
            )

            if not assignments_href:
                print("⚠️ Assignments link not found.")
                continue

            assignments_url = make_absolute_url(
                course_frame.url,
                assignments_href
            )

            print("📝 Opening assignments...")

            page.goto(
                assignments_url,
                wait_until="domcontentloaded"
            )

            page.wait_for_timeout(2000)

            assignments = extract_assignments(page)

            print(
                f"📋 Assignments found: "
                f"{len(assignments)}"
            )

            course_pending = 0

            for assignment in assignments:

                metadata = extract_assignment_metadata(
                    page,
                    assignment
                )

                status = metadata.get(
                    "status",
                    ""
                ).strip().lower()

                # Pending means the student has not completed
                # the assignment yet.
                pending_statuses = (
                    "not started",
                    "in progress",
                    "returned"
                )

                if any(
                    status.startswith(s)
                    for s in pending_statuses
                ):

                    metadata["course"] = course_title

                    all_pending.append(
                        metadata
                    )

                    course_pending += 1

            print(
                f"⏳ Pending assignments: "
                f"{course_pending}"
            )

        except Exception as e:

            print(
                f"❌ Error processing course "
                f"{course_title}: {e}"
            )

            continue

    # ---------------------------------------------------------
    # SORT BY DUE DATE
    # ---------------------------------------------------------

    def parse_due_date(assignment):

        due = assignment.get("due", "")

        if not due:
            return datetime.max

        formats = [
            "%b %d, %Y %I:%M %p",
            "%b %d, %Y",
        ]

        for fmt in formats:

            try:
                return datetime.strptime(
                    due,
                    fmt
                )

            except ValueError:
                pass

        return datetime.max

    all_pending.sort(
        key=parse_due_date
    )

    return all_pending
if __name__ == "__main__":
    run()