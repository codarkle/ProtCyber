from bs4 import BeautifulSoup
import re
from fpdf.enums import XPos, YPos

def parse_and_prettify_link_header(link_header: str) -> str:
    """Parse Link header string and return pretty formatted multiline string."""
    # Reuse logic similar to the previous parse_link_header function
    parts = []
    current = ''
    inside_angle = False
    for char in link_header:
        if char == '<':
            inside_angle = True
        elif char == '>':
            inside_angle = False
        if char == ',' and not inside_angle:
            parts.append(current.strip())
            current = ''
        else:
            current += char
    if current:
        parts.append(current.strip())

    pretty_links = []
    for part in parts:
        # Separate URL and params
        if '>' in part:
            url_part, *params_part = part.split('>;')
            url = url_part.strip('<>')
            params_str = '>'.join(params_part).strip()
            pretty_links.append(f"<{url}>")
            if params_str:
                params = [p.strip() for p in params_str.split(';')]
                for p in params:
                    pretty_links.append(f"  {p}")
        else:
            pretty_links.append(part.strip('<>'))
    return '\n'.join(pretty_links)

def beautify_http_response(pdf, raw_response):
    # Step 1: Split headers and body
    split_parts = raw_response.split("\r\n\r\n", 1)
    headers_raw = split_parts[0].replace("\\r\\n", "\n").replace("\r\n", "\n")
    body_raw = split_parts[1] if len(split_parts) > 1 else ""

    # Step 2: Process headers line-by-line
    header_lines = headers_raw.split('\n')
    pretty_headers = []
    for line in header_lines:
        if line.lower().startswith('link:'):
            _, link_value = line.split(":", 1)
            link_value = link_value.strip()
            pretty_link = parse_and_prettify_link_header(link_value)
            pretty_headers.append("Link:")
            pretty_headers.append(pretty_link)
        elif ':' in line:
            key, val = line.split(':', 1)
            key_clean = key.strip()
            val_clean = val.strip()

            # Fix long unbroken strings (e.g. cookies) by adding zero-width space after semicolon
            val_clean = val_clean.replace(';', ';\u200b')

            # Replace multiple spaces with a single space
            val_clean = re.sub(r'\s+', ' ', val_clean)

            pretty_headers.append(f"{key_clean}: {val_clean}")
        else:
            pretty_headers.append(line.strip())

    headers_pretty_str = "\n".join(pretty_headers)

    # Step 3: Beautify HTML body
    body_cleaned = body_raw.encode('latin-1', 'replace').decode('latin-1')
    # soup = BeautifulSoup(body_cleaned, 'html.parser')
    soup = BeautifulSoup(body_cleaned, 'html5lib') # replacing with html5lib
    pretty_html = soup.prettify(formatter="html")

    # Step 4: Combine headers and body
    full_response = headers_pretty_str.strip() + "\n\n" + pretty_html.strip()

    # Step 5: Clean leading spaces per line and prepare for PDF
    lines = full_response.splitlines()
    clean_lines = [line.lstrip() for line in lines]
    clean_response = "\n".join(clean_lines)

    # Step 6: Add to PDF
    pdf.set_fill_color(229, 229, 229)
    pdf.set_font('Courier', '', 8)
    pdf.set_text_color(0)

    # pdf.set_font('helvetica', 'B', 10)
    # pdf.cell(0, 8, "Response:", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

    pdf.set_font('Courier', '', 10)
    pdf.multi_cell(0, 4.5, clean_response.encode('latin-1', 'replace').decode('latin-1'), fill=True, align='L')
    pdf.ln()


# Dummy placeholder for parse_and_prettify_link_header
# def parse_and_prettify_link_header(link_value):
#     # You can implement this as needed, here just returns the input
#     return link_value

