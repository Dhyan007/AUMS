# aums/assignments.py

import os
import re
from urllib.parse import urljoin, unquote

from utils.console import print_separator
from utils.urls import make_absolute_url


def normalize_text(text):
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ADD THIS FUNCTION TO aums/assignments.py
# Place it before extract_assignment_details()

def inspect_assignment_page(page, assignment_url):

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

    # --------------------------------------------------------
    # PAGE TEXT
    # --------------------------------------------------------

    print_separator()
    print("📄 ASSIGNMENT PAGE CONTENT")
    print_separator()

    try:

        body_text = page.locator(
            "body"
        ).inner_text()

    except Exception as e:

        print(
            f"❌ Could not extract page text: {e}"
        )

        body_text = ""

    print(body_text)

    # --------------------------------------------------------
    # ATTACHMENTS
    # --------------------------------------------------------

    print_separator()
    print("📎 ATTACHMENTS")
    print_separator()

    attachments = []

    attachment_links = page.locator(
        'a[href*="/access/content/attachment/"]'
    )

    attachment_count = attachment_links.count()

    for i in range(attachment_count):

        link = attachment_links.nth(i)

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

        filename = (
            text.split("(")[0].strip()
            if text
            else absolute_url.rstrip("/").split("/")[-1]
        )

        attachment = {
            "name": filename,
            "filename": filename,
            "url": absolute_url
        }

        if not any(
            existing["url"] == absolute_url
            for existing in attachments
        ):

            attachments.append(
                attachment
            )

    if attachments:

        print(
            f"\nFound {len(attachments)} attachment(s).\n"
        )

        for i, attachment in enumerate(
            attachments,
            1
        ):

            print(
                f"{i}. {attachment['filename']}"
            )

            print(
                f"   URL: {attachment['url']}"
            )

    else:

        print(
            "\n❌ No assignment attachments detected."
        )

    # --------------------------------------------------------
    # RETURN DATA
    # --------------------------------------------------------

    return {
        "url": page.url,
        "text": body_text,
        "attachments": attachments
    }
def extract_assignment_metadata(page, assignment):
    title = assignment["title"]
    href = assignment["href"]

    locator = page.locator(
        f'a[href="{href}"]'
    )

    status = ""
    open_date = ""
    due_date = ""

    try:
        if locator.count() > 0:

            element = locator.first

            row = element.locator(
                "xpath=ancestor::tr[1]"
            )

            if row.count() > 0:

                row_text = normalize_text(
                    row.inner_text()
                )

                status_match = re.search(
                    r"(Not Started|Submitted[^|]*|In Progress|Returned[^|]*)",
                    row_text,
                    re.IGNORECASE
                )

                if status_match:
                    status = status_match.group(1).strip()

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

        if not text or not href:
            continue

        if re.search(
            r"Assignment\s+\d+",
            text,
            re.IGNORECASE
        ):

            assignments.append({
                "title": text,
                "href": href
            })

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


def _extract_filename(link):

    text = normalize_text(
        link.inner_text()
    )

    href = link.get_attribute("href") or ""

    if text:
        filename = text.split("(")[0].strip()
    else:
        filename = ""

    if not filename:
        filename = unquote(
            href.rstrip("/").split("/")[-1]
        )

    filename = os.path.basename(filename)

    return filename


def _is_assignment_attachment(href):

    if not href:
        return False

    href_lower = href.lower()

    return (
        "/access/content/attachment/"
        in href_lower
    )


def extract_assignment_details(
    page,
    assignment_url,
    download_dir="assignment_files"
):

    print("\n" + "=" * 70)
    print("📚 EXTRACTING ASSIGNMENT DETAILS")
    print("=" * 70)

    os.makedirs(
        download_dir,
        exist_ok=True
    )

    # ---------------------------------------------------------
    # OPEN ASSIGNMENT
    # ---------------------------------------------------------

    page.goto(
        assignment_url,
        wait_until="domcontentloaded"
    )

    page.wait_for_timeout(3000)

    print("\nCurrent URL:")
    print(page.url)

    # ---------------------------------------------------------
    # FULL PAGE TEXT
    # ---------------------------------------------------------

    try:

        body_text = page.locator(
            "body"
        ).inner_text()

    except Exception as e:

        print(
            f"❌ Could not extract page text: {e}"
        )

        body_text = ""

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

        if re.match(
            r"^Assignment\s+\d+",
            line,
            re.IGNORECASE
        ):

            title = line
            break

    # ---------------------------------------------------------
    # INSTRUCTIONS
    # ---------------------------------------------------------

    instructions = ""

    instruction_start = None

    for i, line in enumerate(lines):

        if line.lower() == "instructions":

            instruction_start = i + 1
            break

    if instruction_start is not None:

        instruction_lines = []

        stop_sections = {
            "submission",
            "source",
            "additional resources",
            "additional resources for assignment",
            "attachments",
            "attachment",
            "rubric"
        }

        for line in lines[instruction_start:]:

            normalized_line = line.lower().strip()

            if normalized_line in stop_sections:
                break

            instruction_lines.append(line)

        instructions = "\n".join(
            instruction_lines
        ).strip()

    # ---------------------------------------------------------
    # TASKS
    # ---------------------------------------------------------

    tasks = []

    for line in instructions.splitlines():

        match = re.match(
            r"^(\d+)\.\s*(.*)",
            line
        )

        if match:

            task = match.group(2).strip()

            if task:
                tasks.append(task)

    # ---------------------------------------------------------
    # ATTACHMENTS
    # ---------------------------------------------------------

    attachments = []

    attachment_links = page.locator(
        'a[href*="/access/content/attachment/"]'
    )

    attachment_count = (
        attachment_links.count()
    )

    print(
        f"\n📎 Assignment attachment links found: "
        f"{attachment_count}"
    )

    seen_urls = set()

    for i in range(attachment_count):

        link = attachment_links.nth(i)

        try:

            href = link.get_attribute(
                "href"
            )

            if not href:
                continue

            absolute_url = urljoin(
                assignment_url,
                href
            )

            if absolute_url in seen_urls:
                continue

            seen_urls.add(
                absolute_url
            )

            filename = _extract_filename(
                link
            )

            if not filename:
                filename = (
                    absolute_url
                    .rstrip("/")
                    .split("/")[-1]
                )

            attachments.append({
                "filename": filename,
                "url": absolute_url
            })

        except Exception as e:

            print(
                f"⚠️ Could not process "
                f"attachment {i}: {e}"
            )

    # ---------------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------------

    print_separator()

    print("📋 ASSIGNMENT")

    print_separator()

    print("\nTitle:")
    print(
        title if title else "Unknown"
    )

    print("\nInstructions:")
    print(
        instructions
        if instructions
        else "No instructions found."
    )

    print("\nTasks:")

    if tasks:

        for i, task in enumerate(
            tasks,
            1
        ):

            print(
                f"{i}. {task}"
            )

    else:

        print(
            "No numbered tasks detected."
        )

    print("\nAttachments:")

    if attachments:

        for i, attachment in enumerate(
            attachments,
            1
        ):

            print(
                f"{i}. {attachment['filename']}"
            )

            print(
                f"   {attachment['url']}"
            )

    else:

        print(
            "No assignment attachments found."
        )

    # ---------------------------------------------------------
    # RETURN STRUCTURED DATA
    # ---------------------------------------------------------

    return {
        "title": title,
        "instructions": instructions,
        "tasks": tasks,
        "attachments": attachments,
        "url": assignment_url
    }