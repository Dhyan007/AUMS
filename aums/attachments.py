# aums/attachments.py

import os
from urllib.parse import urlparse

import requests

from utils.console import print_separator


def _safe_filename(filename):

    filename = os.path.basename(
        filename.strip()
    )

    if not filename:
        return None

    return filename


def download_assignment_files(
    assignment,
    download_dir="assignment_files"
):

    print_separator()
    print("📥 DOWNLOADING ASSIGNMENT FILES")
    print_separator()

    os.makedirs(
        download_dir,
        exist_ok=True
    )

    attachments = assignment.get(
        "attachments",
        []
    )

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

        filename = _safe_filename(
            filename
        )

        if not filename:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        if filename in seen_filenames:
            continue

        seen_filenames.add(filename)

        filepath = os.path.join(
            download_dir,
            filename
        )

        try:

            print(
                f"⬇️ Downloading: {filename}"
            )

            response = requests.get(
                url,
                timeout=30
            )

            response.raise_for_status()

            with open(
                filepath,
                "wb"
            ) as file:

                file.write(
                    response.content
                )

            downloaded_files.append(
                filepath
            )

            print(
                f"✓ Saved: {filepath}"
            )

        except Exception as e:

            print(
                f"❌ Failed to download "
                f"{filename}: {e}"
            )

    print()

    print(
        f"✅ DOWNLOADED "
        f"{len(downloaded_files)} UNIQUE FILES"
    )

    print_separator()

    return downloaded_files