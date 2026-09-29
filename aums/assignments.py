import re
from urllib.parse import urljoin
from utils.console import print_separator
from utils.urls import make_absolute_url

def normalize_text(text):
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_assignment_metadata(page, assignment):

    title = assignment["title"]
    href = assignment["href"]

    # --------------------------------------------------------
    # Try to find parent row
    # --------------------------------------------------------

    locator = page.locator(
        f'a[href="{href}"]'
    )

    status = ""
    open_date = ""
    due_date = ""

    try:

        if locator.count() > 0:

            element = locator.first

            # Find nearest row
            row = element.locator(
                "xpath=ancestor::tr[1]"
            )

            if row.count() > 0:

                row_text = normalize_text(
                    row.inner_text()
                )

                # Status
                status_match = re.search(
                    r"(Not Started|Submitted[^|]*|In Progress|Returned[^|]*)",
                    row_text,
                    re.IGNORECASE
                )

                if status_match:
                    status = status_match.group(1).strip()

                # Dates
                dates = re.findall(
                    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
                    r"\s+\d{1,2},\s+\d{4}"
                    r"(?:\s+\d{1,2}:\d{2}\s+[AP]M)?",
                    row_text,
                    re.IGNORECASE
                )

                # Better generic date extraction
                date_matches = re.findall(
                    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
                    r"\s+\d{1,2},\s+\d{4}"
                    r"(?:\s+\d{1,2}:\d{2}\s+[AP]M)?",
                    row_text,
                    re.IGNORECASE
                )

                if len(date_matches) >= 1:
                    open_date = date_matches[0]

                if len(date_matches) >= 2:
                    due_date = date_matches[1]

    except Exception:
        pass

    return {
        "title": title,
        "url": href,
        "status": status,
        "open": open_date,
        "due": due_date
    }


def extract_assignments(page):

    print_separator()

    print("🔍 Extracting assignments...")

    body_text = page.locator("body").inner_text()

    # --------------------------------------------------------
    # Try to identify assignment links
    # --------------------------------------------------------

    links = page.locator("a")

    link_count = links.count()

    assignments = []

    for i in range(link_count):

        link = links.nth(i)

        try:
            text = normalize_text(link.inner_text())
        except Exception:
            text = ""

        try:
            href = link.get_attribute("href")
        except Exception:
            href = None

        if not text:
            continue

        if not href:
            continue

        # Assignment titles normally contain "Assignment"
        if re.search(
            r"Assignment\s+\d+",
            text,
            re.IGNORECASE
        ):

            assignments.append({
                "title": text,
                "href": href
            })

    # Remove duplicates
    unique = []

    seen = set()

    for assignment in assignments:

        key = (
            assignment["title"],
            assignment["href"]
        )

        if key not in seen:

            seen.add(key)
            unique.append(assignment)

    assignments = unique

    print(
        f"\nFound {len(assignments)} assignment links."
    )

    return assignments


def find_target_assignment(page, target_title):

    print_separator()

    print("🎯 Looking for target assignment:")
    print(target_title)

    assignments = extract_assignments(page)

    if not assignments:

        print("❌ No assignments found.")

        return None

    target = None

    for assignment in assignments:

        if (
            normalize_text(
                assignment["title"]
            ).lower()
            ==
            normalize_text(
                target_title
            ).lower()
        ):

            target = assignment
            break

    # If exact match fails, try partial match
    if target is None:

        for assignment in assignments:

            if target_title.lower() in assignment[
                "title"
            ].lower():

                target = assignment
                break

    if target is None:

        print("❌ Target assignment not found.")

        print("\nAvailable assignments:")

        for assignment in assignments:

            print(
                f"- {assignment['title']}"
            )

        return None

    metadata = extract_assignment_metadata(
        page,
        target
    )

    print("\n✅ Target assignment found!")

    print("\nTitle:")
    print(metadata["title"])

    print("\nStatus:")
    print(
        metadata["status"]
        if metadata["status"]
        else "Unknown"
    )

    print("\nOpen:")
    print(
        metadata["open"]
        if metadata["open"]
        else "Unknown"
    )

    print("\nDue:")
    print(
        metadata["due"]
        if metadata["due"]
        else "Unknown"
    )

    print("\nURL:")
    print(metadata["url"])

    return metadata


def inspect_assignment_page(
    page,
    assignment_url
):

    print_separator()

    print("📄 OPENING INDIVIDUAL ASSIGNMENT")

    print("\nURL:")
    print(assignment_url)

    page.goto(
        assignment_url,
        wait_until="domcontentloaded"
    )

    page.wait_for_timeout(3000)

    print("\n✅ Assignment page loaded!")

    print("\nCurrent URL:")
    print(page.url)

    # ========================================================
    # PAGE TEXT
    # ========================================================

    print_separator()

    print("📄 ASSIGNMENT PAGE CONTENT")

    print_separator()

    try:

        body_text = page.locator(
            "body"
        ).inner_text()

    except Exception as e:

        print(
            "❌ Could not extract page text:"
        )

        print(e)

        body_text = ""

    print(body_text)

    # ========================================================
    # SAVE PAGE TEXT
    # ========================================================

    output_file = "assignment_21_content.txt"

    try:

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(body_text)

        print_separator()

        print("💾 Page text saved to:")
        print(output_file)

    except Exception as e:

        print(
            f"❌ Could not save page text: {e}"
        )

    # ========================================================
    # ATTACHMENTS
    # ========================================================

    print_separator()

    print("📎 ATTACHMENTS")

    print_separator()

    attachments = []

    links = page.locator("a")

    link_count = links.count()

    for i in range(link_count):

        link = links.nth(i)

        try:
            text = normalize_text(
                link.inner_text()
            )
        except Exception:
            text = ""

        try:
            href = link.get_attribute(
                "href"
            )
        except Exception:
            href = None

        if not href:
            continue

        combined = (
            text + " " + href
        ).lower()

        attachment_keywords = [
            "attachment",
            "download",
            ".pdf",
            ".txt",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".csv",
            ".zip",
            ".jpg",
            ".jpeg",
            ".png",
            ".java",
            ".py",
            ".c",
            ".cpp"
        ]

        if any(
            keyword in combined
            for keyword in attachment_keywords
        ):

            absolute_url = make_absolute_url(
                page.url,
                href
            )

            attachment = {
                "name": (
                    text
                    if text
                    else "Unnamed attachment"
                ),
                "url": absolute_url
            }

            duplicate = False

            for existing in attachments:

                if (
                    existing["url"]
                    ==
                    attachment["url"]
                ):

                    duplicate = True
                    break

            if not duplicate:

                attachments.append(
                    attachment
                )

    if attachments:

        print(
            f"\nFound {len(attachments)} "
            "possible attachment(s).\n"
        )

        for i, attachment in enumerate(
            attachments,
            1
        ):

            print(
                f"{i}. {attachment['name']}"
            )

            print(
                f"   URL: {attachment['url']}"
            )

    else:

        print(
            "\n❌ No obvious attachments "
            "detected."
        )

    # ========================================================
    # ALL LINKS
    # ========================================================

    print_separator()

    print("🔗 ALL LINKS ON ASSIGNMENT PAGE")

    print_separator()

    for i in range(link_count):

        link = links.nth(i)

        try:
            text = normalize_text(
                link.inner_text()
            )
        except Exception:
            text = ""

        try:
            href = link.get_attribute(
                "href"
            )
        except Exception:
            href = None

        if not href:
            continue

        absolute_url = make_absolute_url(
            page.url,
            href
        )

        print(f"\n{i}. {text}")

        print(
            f"   {absolute_url}"
        )

    # ========================================================
    # FRAME INFORMATION
    # ========================================================

    print_separator()

    print("🖼️ FRAMES ON ASSIGNMENT PAGE")

    print_separator()

    for i, frame in enumerate(
        page.frames
    ):

        try:

            print(
                f"\nFRAME {i}"
            )

            print(
                frame.url
            )

        except Exception:
            pass

    # ========================================================
    # RETURN DATA
    # ========================================================

    return {
        "url": page.url,
        "text": body_text,
        "attachments": attachments
    }


def extract_assignment_details(page, assignment_url, download_dir="assignment_files"):

    print("\n" + "=" * 70)
    print("📚 EXTRACTING ASSIGNMENT DETAILS")
    print("=" * 70)

    os.makedirs(download_dir, exist_ok=True)

    # ---------------------------------------------------------
    # FULL PAGE TEXT
    # ---------------------------------------------------------

    body_text = page.locator("body").inner_text()

    lines = [
        line.strip()
        for line in body_text.splitlines()
        if line.strip()
    ]

    # ---------------------------------------------------------
    # TITLE
    # ---------------------------------------------------------

    title = ""

    for line in lines:

        if line.startswith("Assignment ") and ":" in line:
            title = line
            break

    # ---------------------------------------------------------
    # INSTRUCTIONS
    # ---------------------------------------------------------

    instructions = ""

    for i, line in enumerate(lines):

        if line.lower() == "instructions":

            instruction_lines = []

            for next_line in lines[i + 1:]:

                if next_line.lower() == "submission":
                    break

                if next_line.lower() == "source":
                    break

                instruction_lines.append(next_line)

            instructions = "\n".join(instruction_lines)

            break

    # ---------------------------------------------------------
    # TASKS
    # ---------------------------------------------------------

    tasks = []

    for line in instructions.splitlines():

        match = re.match(r"^(\d+)\.\s*(.*)", line)

        if match:
            tasks.append(match.group(2).strip())

    # ---------------------------------------------------------
    # ATTACHMENTS
    # ---------------------------------------------------------

    attachments = []

    attachment_links = page.locator(
        'a[href*="/access/content/attachment/"]'
    )

    attachment_count = attachment_links.count()

    print(f"\n📎 Attachment links found: {attachment_count}")

    for i in range(attachment_count):

        link = attachment_links.nth(i)

        try:

            filename = link.inner_text().strip()

            href = link.get_attribute("href")

            if not href:
                continue

            href = urljoin(assignment_url, href)

            # Remove extra text
            filename = filename.split("(")[0].strip()

            if not filename:
                filename = href.split("/")[-1]

            attachments.append({
                "filename": filename,
                "url": href
            })

        except Exception as e:

            print(
                f"⚠️ Could not process attachment {i}: {e}"
            )

    # ---------------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("📋 ASSIGNMENT")
    print("=" * 70)

    print("\nTitle:")
    print(title)

    print("\nInstructions:")
    print(instructions)

    print("\nTasks:")

    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task}")

    print("\nAttachments:")

    for i, attachment in enumerate(attachments, 1):

        print(
            f"{i}. {attachment['filename']}"
        )

        print(
            f"   {attachment['url']}"
        )

    return {
        "title": title,
        "instructions": instructions,
        "tasks": tasks,
        "attachments": attachments,
        "url": assignment_url
    }