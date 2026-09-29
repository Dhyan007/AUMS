import os
import re
from pathlib import Path
import requests
from utils.console import print_separator

def download_assignment_files(assignment, download_dir="assignment_files"):
    """
    Download unique assignment attachments.

    Uses the attachment information already extracted from
    the authenticated AUMS page.
    """

    print_separator()
    print("📥 DOWNLOADING ASSIGNMENT FILES")
    print_separator()

    os.makedirs(download_dir, exist_ok=True)

    attachments = assignment.get("attachments", [])

    downloaded_files = []
    seen_urls = set()
    seen_filenames = set()

    for attachment in attachments:

        filename = (
            attachment.get("filename")
            or attachment.get("name")
        )

        url = attachment.get("url")

        if not filename or not url:
            continue

        # Avoid duplicate attachment entries
        if url in seen_urls:
            continue

        seen_urls.add(url)

        # Avoid overwriting the same filename repeatedly
        if filename in seen_filenames:
            continue

        seen_filenames.add(filename)

        filepath = os.path.join(
            download_dir,
            filename
        )

        try:

            response = requests.get(
                url,
                timeout=30
            )

            response.raise_for_status()

            with open(filepath, "wb") as f:
                f.write(response.content)

            downloaded_files.append(filepath)

            print(f"✓ {filename}")

        except Exception as e:

            print(
                f"❌ Failed to download {filename}: {e}"
            )

    print()
    print(
        f"✅ DOWNLOADED {len(downloaded_files)} UNIQUE FILES"
    )

    print_separator()

    return downloaded_files