import io
from typing import List, Dict, Any
import openpyxl
from openpyxl.utils import get_column_letter
from fastapi.responses import StreamingResponse


def _flatten_scraped_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flattens a single scraped data dict into a row suitable for Excel export.
    """
    emails = item.get("emails", []) or []
    phones = item.get("phones", []) or []
    social_media = item.get("social_media", {}) or {}
    if isinstance(social_media, dict):
        social_media_links = ", ".join(
            str(url) for url in social_media.values() if url
        )
    elif isinstance(social_media, str):
        social_media_links = social_media
        social_media = {}
    else:
        social_media_links = ""
        social_media = {}

    return {
        "Business Name": item.get("name", ""),
        "Emails": ", ".join(emails),
        "Phones": ", ".join(phones),
        "Social Media": social_media_links,
        "Facebook": social_media.get("facebook.com", ""),
        "Twitter/X": social_media.get("x.com", ""),
        "LinkedIn": social_media.get("linkedin.com", ""),
        "Instagram": social_media.get("instagram.com", ""),
        "Contact Page": item.get("contact_page", ""),
        "About Page": item.get("about_page", ""),
    }


def generate_excel_from_scraped_data(data: List[Dict[str, Any]]) -> io.BytesIO:
    """
    Generates an in-memory Excel file from a list of scraped data dicts.

    Args:
        data: List of scraped data dictionaries (each in the format shown above).

    Returns:
        BytesIO buffer containing the generated .xlsx file.
    """
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Scraped Leads"

    headers = [
        "Business Name",
        "Emails",
        "Phones",
        "Social Media",
        "Facebook",
        "Twitter/X",
        "LinkedIn",
        "Instagram",
        "Contact Page",
        "About Page",
    ]
    sheet.append(headers)

    for item in data:
        row = _flatten_scraped_item(item)
        sheet.append([row.get(h, "") for h in headers])

    # Auto-size columns roughly based on content length
    for col_idx, header in enumerate(headers, start=1):
        max_length = len(header)
        for row_idx in range(2, sheet.max_row + 1):
            cell_value = sheet.cell(row=row_idx, column=col_idx).value
            if cell_value:
                max_length = max(max_length, len(str(cell_value)))
        sheet.column_dimensions[get_column_letter(col_idx)].width = min(max_length + 2, 60)

    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


def export_scraped_data_as_excel_response(
    data: List[Dict[str, Any]],
    filename: str = "scraped_leads.xlsx",
) -> StreamingResponse:
    """
    Generates an Excel file from scraped data and returns it as a downloadable
    FastAPI StreamingResponse.

    Args:
        data: List of scraped data dictionaries.
        filename: Name of the downloaded file.

    Returns:
        StreamingResponse with appropriate headers to trigger a file download.
    """
    buffer = generate_excel_from_scraped_data(data)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )