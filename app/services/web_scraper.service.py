import re
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright


EMAIL_RE = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

PHONE_RE = re.compile(
    r"(?:\+?\d[\d\s().-]{7,}\d)"
)

SOCIAL_DOMAINS = [
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "youtube.com",
    "tiktok.com",
]


def scrape_website(url = "https://ams1.13sqft.com"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        try:
            # Make sure the URL is absolute
            url = urljoin(url, "/")

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            data = extract_data(page)

            # -------------------------
            # Contact page
            # -------------------------
            if data["contact_page"]:
                try:
                    page.goto(
                        data["contact_page"],
                        wait_until="domcontentloaded",
                        timeout=30000
                    )

                    contact_text = page.locator("body").inner_text()

                    data["emails"] = add_unique(
                        data["emails"],
                        EMAIL_RE.findall(contact_text)
                    )

                    data["phones"] = add_unique(
                        data["phones"],
                        PHONE_RE.findall(contact_text)
                    )

                except Exception as e:
                    print(f"Could not scrape contact page: {e}")

            # -------------------------
            # About page
            # -------------------------
            # if data["about_page"]:
            #     try:
            #         page.goto(
            #             data["about_page"],
            #             wait_until="domcontentloaded",
            #             timeout=30000
            #         )

            #         data["about"] = page.locator("body").inner_text()

                except Exception as e:
                    print(f"Could not scrape about page: {e}")
            print(f"Scraped data: {data}")
            return data

        finally:
            browser.close()
scrape_website()

def extract_links(page):
    return page.locator("a").evaluate_all("""
        els => els.map(a => ({
            text: (a.innerText || "").trim(),
            href: a.href
        }))
    """)


def find_social_links(links):
    socials = {}

    for link in links:
        href = link["href"]

        try:
            domain = urlparse(href).netloc.lower()
        except Exception:
            continue

        for social_domain in SOCIAL_DOMAINS:
            if domain == social_domain or domain.endswith("." + social_domain):
                socials[social_domain] = href

    return socials


def find_contact_about_links(links):
    contact = None
    about = None

    for link in links:
        text = link["text"].lower().strip()
        href = link["href"]

        if not href:
            continue

        path = urlparse(href).path.lower()

        if contact is None and (
            "contact" in text or "/contact" in path
        ):
            contact = href

        if about is None and (
            text == "about"
            or "/about" in path
        ):
            about = href

    return contact, about


def extract_data(page):
    text = page.locator("body").inner_text()

    emails = sorted(set(EMAIL_RE.findall(text)))
    phones = sorted(set(PHONE_RE.findall(text)))

    links = extract_links(page)

    socials = find_social_links(links)
    contact_url, about_url = find_contact_about_links(links)

    return {
        "emails": emails,
        "phones": phones,
        "social_media": socials,
        "contact_page": contact_url,
        "about_page": about_url,
    }


def add_unique(items, new_items):
    items.extend(new_items)
    return sorted(set(items))