from datetime import datetime
import os
import re
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
    inspect_assignment_page,
)


from aums.attachments import download_assignment_files

from utils.console import print_heading
from utils.urls import make_absolute_url

def process_pending_assignments(
    page,
    pending_assignments
):

    print_heading(
        "📥 PROCESSING PENDING ASSIGNMENTS"
    )

    total_downloaded = 0

    for index, assignment in enumerate(
        pending_assignments,
        1
    ):

        course = assignment.get(
            "course",
            "Unknown Course"
        )

        title = assignment.get(
            "title",
            "Unknown Assignment"
        )

        assignment_url = assignment.get(
            "url"
        )

        print("\n" + "=" * 70)

        print(
            f"📚 Course: {course}"
        )

        print(
            f"📝 Assignment {index}/"
            f"{len(pending_assignments)}: {title}"
        )

        print(
            f"🔗 URL: {assignment_url}"
        )

        print("=" * 70)

        if not assignment_url:

            print(
                "❌ Assignment URL not found."
            )

            continue

        try:

            # =================================================
            # CREATE ASSIGNMENT-SPECIFIC FOLDER
            # =================================================

            safe_course = re.sub(
                r'[\\/:*?"<>|]',
                "_",
                course
            ).strip()

            safe_title = re.sub(
                r'[\\/:*?"<>|]',
                "_",
                title
            ).strip()

            assignment_dir = os.path.join(
                DOWNLOAD_DIR,
                safe_course,
                safe_title
            )

            os.makedirs(
                assignment_dir,
                exist_ok=True
            )

            print(
                f"\n📁 Assignment folder:"
            )

            print(
                f"   {assignment_dir}"
            )

            # =================================================
            # OPEN / EXTRACT ASSIGNMENT
            # =================================================

            print(
                "\n🔍 Opening assignment..."
            )

            assignment_data = (
                inspect_assignment_page(
                    page,
                    assignment_url
                )
            )

            # =================================================
            # SAVE ASSIGNMENT TEXT
            # =================================================

            assignment_text = (
                assignment_data.get(
                    "text",
                    ""
                )
            )

            text_file = os.path.join(
                assignment_dir,
                "assignment.txt"
            )

            with open(
                text_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    assignment_text
                )

            print(
                "\n💾 Assignment text saved:"
            )

            print(
                f"   {text_file}"
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
                    assignment_dir
                )
            )

            total_downloaded += len(
                downloaded_files
            )

            # =================================================
            # RESULT
            # =================================================

            print(
                f"\n✅ Assignment processed: "
                f"{title}"
            )

            if downloaded_files:

                print(
                    "\n📎 Downloaded files:"
                )

                for file_path in downloaded_files:

                    print(
                        f"   ✓ {file_path}"
                    )

            else:

                print(
                    "\n📎 No files downloaded."
                )

        except Exception as e:

            print(
                f"\n❌ Failed to process "
                f"{title}"
            )

            print(
                f"   Error: {e}"
            )

    # =================================================
    # FINAL DOWNLOAD SUMMARY
    # =================================================

    print("\n" + "=" * 70)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 70)

    print(
        f"Pending assignments: "
        f"{len(pending_assignments)}"
    )

    print(
        f"Files downloaded: "
        f"{total_downloaded}"
    )

    print("=" * 70)
def run():

    print_heading(
        "📚 AUMS ASSIGNMENT MAKER"
    )

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

            print(
                "\n✅ No pending assignments found."
            )

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

        # =================================================
        # PROCESS / DOWNLOAD ALL PENDING ASSIGNMENTS
        # =================================================

        if pending_assignments:

            process_pending_assignments(
                page,
                pending_assignments
            )

        else:

            print(
                "\n⏭️ Nothing to download."
            )

        # =================================================
        # FINAL
        # =================================================

        print_heading(
            "🎉 ALL COURSES PROCESSED"
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

    print(
        f"\n📚 Courses found: {len(courses)}"
    )

    all_pending = []

    for index, course in enumerate(courses, 1):

        course_title = course["title"]

        print("\n" + "-" * 70)
        print(
            f"📖 COURSE {index}/{len(courses)}"
        )
        print(course_title)
        print("-" * 70)

        try:

            # =================================================
            # OPEN COURSE
            # =================================================

            course_url = make_absolute_url(
                portal_frame.url,
                course["href"]
            )

            print(
                "🌐 Opening course..."
            )

            page.goto(
                course_url,
                wait_until="domcontentloaded"
            )

            page.wait_for_timeout(3000)

            # =================================================
            # FIND COURSE FRAME
            # =================================================

            course_frame = find_course_frame(
                page,
                course_url
            )

            if course_frame is None:

                print(
                    "❌ Course frame not found."
                )

                continue

            # =================================================
            # FIND ASSIGNMENTS LINK
            # =================================================

            assignments_href = (
                find_assignments_link(
                    course_frame
                )
            )

            if not assignments_href:

                print(
                    "⚠️ Assignments link not found."
                )

                continue

            assignments_url = make_absolute_url(
                course_frame.url,
                assignments_href
            )

            print(
                "📝 Opening assignments..."
            )

            print(
                f"   URL: {assignments_url}"
            )

            # =================================================
            # OPEN ASSIGNMENTS PAGE
            # =================================================

            page.goto(
                assignments_url,
                wait_until="domcontentloaded"
            )

            # Give AUMS/Sakai time to render
            page.wait_for_timeout(5000)

            print(
                "\nCurrent assignments URL:"
            )

            print(
                page.url
            )

            # =================================================
            # EXTRACT ASSIGNMENTS
            # =================================================

            assignments = []

            # -------------------------------------------------
            # First: search the main page
            # -------------------------------------------------

            try:

                assignments = extract_assignments(
                    page
                )

            except Exception as e:

                print(
                    f"⚠️ Main page extraction failed: {e}"
                )

            # -------------------------------------------------
            # If nothing found, search every frame
            # -------------------------------------------------

            if not assignments:

                print(
                    "\n🔍 No assignments on main page."
                )

                print(
                    "🔍 Checking AUMS frames..."
                )

                for frame in page.frames:

                    try:

                        frame_assignments = (
                            extract_assignments(
                                frame
                            )
                        )

                        if frame_assignments:

                            assignments = (
                                frame_assignments
                            )

                            print(
                                f"\n✅ Found assignments "
                                f"in frame:"
                            )

                            print(
                                frame.url
                            )

                            break

                    except Exception:
                        continue

            print(
                f"\n📋 Assignments found: "
                f"{len(assignments)}"
            )

            # =================================================
            # NO ASSIGNMENTS
            # =================================================

            if not assignments:

                print(
                    "⏭️ No assignments found "
                    f"for {course_title}"
                )

                continue

            # =================================================
            # CHECK EACH ASSIGNMENT
            # =================================================

            course_pending = 0

            for assignment in assignments:

                try:

                    metadata = (
                        extract_assignment_metadata(
                            page,
                            assignment
                        )
                    )

                    status = (
                        metadata
                        .get("status", "")
                        .strip()
                        .lower()
                    )

                    # ------------------------------------------------
                    # Pending statuses
                    # ------------------------------------------------

                    pending_statuses = (
                        "not started",
                        "in progress",
                        "returned"
                    )

                    is_pending = any(
                        status.startswith(
                            pending_status
                        )
                        for pending_status
                        in pending_statuses
                    )

                    if is_pending:

                        metadata["course"] = (
                            course_title
                        )

                        # Convert relative URL
                        # into absolute URL
                        metadata["url"] = (
                            make_absolute_url(
                                page.url,
                                metadata["url"]
                            )
                        )

                        all_pending.append(
                            metadata
                        )

                        course_pending += 1

                        print(
                            f"   ⏳ {metadata['title']}"
                            f" → {metadata['status']}"
                        )

                except Exception as e:

                    print(
                        f"⚠️ Could not process "
                        f"assignment "
                        f"{assignment.get('title', 'Unknown')}: "
                        f"{e}"
                    )

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

    # =================================================
    # SORT BY DUE DATE
    # =================================================

    def parse_due_date(assignment):

        due = assignment.get(
            "due",
            ""
        )

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

    # =================================================
    # FINAL SCAN SUMMARY
    # =================================================

    print("\n" + "=" * 70)
    print("📊 COURSE SCAN COMPLETE")
    print("=" * 70)

    print(
        f"Courses scanned: {len(courses)}"
    )

    print(
        f"Pending assignments found: "
        f"{len(all_pending)}"
    )

    print("=" * 70)

    return all_pending
def download_all_pending_assignments(
    page,
    pending_assignments
):
    print("\n" + "=" * 70)
    print("📥 DOWNLOADING ALL PENDING ASSIGNMENTS")
    print("=" * 70)

    if not pending_assignments:
        print("\n✅ Nothing to download.")
        return

    total_files = 0

    for index, assignment in enumerate(
        pending_assignments,
        1
    ):

        course = assignment.get(
            "course",
            "Unknown Course"
        )

        title = assignment.get(
            "title",
            "Unknown Assignment"
        )

        assignment_url = assignment.get(
            "url"
        )

        if not assignment_url:
            print(
                f"\n❌ No URL for: {title}"
            )
            continue

        print("\n" + "-" * 70)
        print(
            f"📚 {course}"
        )
        print(
            f"📝 {title}"
        )
        print("-" * 70)

        try:

            assignment_data = inspect_assignment_page(
                page,
                assignment_url
            )

            # -------------------------------------------------
            # SAVE ASSIGNMENT TEXT
            # -------------------------------------------------

            safe_course = re.sub(
                r'[\\/:*?"<>|]',
                "_",
                course
            )

            safe_title = re.sub(
                r'[\\/:*?"<>|]',
                "_",
                title
            )

            output_dir = os.path.join(
                DOWNLOAD_DIR,
                safe_course,
                safe_title
            )

            os.makedirs(
                output_dir,
                exist_ok=True
            )

            text_file = os.path.join(
                output_dir,
                "assignment.txt"
            )

            with open(
                text_file,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    assignment_data.get(
                        "text",
                        ""
                    )
                )

            print(
                f"\n💾 Assignment text saved:"
            )
            print(text_file)

            # -------------------------------------------------
            # DOWNLOAD ATTACHMENTS
            # -------------------------------------------------

            downloaded_files = (
                download_assignment_files(
                    assignment_data,
                    output_dir
                )
            )

            total_files += len(
                downloaded_files
            )

        except Exception as e:

            print(
                f"\n❌ Failed to process "
                f"{title}: {e}"
            )

    print("\n" + "=" * 70)
    print("📊 DOWNLOAD COMPLETE")
    print("=" * 70)

    print(
        f"Assignments processed: "
        f"{len(pending_assignments)}"
    )

    print(
        f"Files downloaded: "
        f"{total_files}"
    )

    print("=" * 70)
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