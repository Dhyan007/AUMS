from urllib.parse import urljoin


def make_absolute_url(base_url, target_url):
    if not target_url:
        return target_url
    return urljoin(base_url, target_url)
