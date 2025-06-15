from collections import defaultdict
from fpdf.enums import XPos, YPos
import mysql.connector

from beautify_response import beautify_http_response

SEVERITY_LEVELS = {
    1:  "High",
    2:  "Medium",
    3:  "Low",
    4:  "Informative"
}

SEVERITY_LABELS = {v: k for k, v in SEVERITY_LEVELS.items()}

unmatched_vulnerabilities = set()

# def emphasize_name_in_text(text, vuln_name):
#     if not text or not vuln_name:
#         return text
#     return text.replace(vuln_name, f'**{vuln_name}**')
def write_highlighted_text(pdf, text, vuln_name):
    if not text or not vuln_name:
        pdf.multi_cell(0, 8, text or '')
        return

    parts = text.split(vuln_name)
    for i, part in enumerate(parts):
        pdf.set_font('helvetica', '', 12)
        pdf.write(8, part)
        if i < len(parts) - 1:
            pdf.set_font('helvetica', 'B', 12)
            pdf.write(8, vuln_name)
    pdf.ln(10)


def add_label_value(pdf, label, value):
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(pdf.get_string_width(label) + 2, 8, f"{label}", border=0, align='L')

    pdf.set_x(pdf.w / 2)
    pdf.set_font('helvetica', '', 12)
    pdf.cell(pdf.get_string_width(value), 8, f"{value}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

def sanitize_text(text):
    if not isinstance(text, str):
        return ''
    text = (
        text
        .replace('’', "'")
        .replace('‘', "'")
        .replace('“', '"')
        .replace('”', '"')
        .replace('—', '-')
        .replace('–', '-')
        .replace('\u00a0', ' ')  
        .replace('\u2014', '-')  
        .replace('\u2013', '-')  
    )
    try:
        text = text.encode('latin-1', 'replace').decode('latin-1')
    except:
        text = ''  
    return text

def get_vulnerability_from_db(vuln_name):
    print(f"[MOCK DB] Returning mock data for: {vuln_name}")
    return {
        "description": f"{vuln_name} can be exploited if not properly handled.",
        "recommendation": "Follow secure development practices and apply appropriate headers.",
        "severity": "High" if "X-Frame" in vuln_name else "Low",
        "cvss_score": "7.5" if "X-Frame" in vuln_name else "3.1",
        "exploitability": "Medium" if "X-Frame" in vuln_name else "Low",
        "requires_authentication": "No",
        "data_exfiltration_possible": "No",
        "confidentiality_impact": "Medium",
        "integrity_impact": "Low",
        "availability_impact": "Low",
        "references": [
            "https://owasp.org/www-project-secure-headers/",
            "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers"
        ],
        "issues": [
            f"Issue related to {vuln_name}"
        ]
    }

def get_vulnerability_from_db_src(vuln_name):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  
            database='db_protcyber_v7'  
        )
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT
            v.id,
            v.file_name,
            v.description,
            v.recommendation,
            v.severity,
            v.cvss_score,
            v.exploitability,
            v.requires_authentication,
            v.data_exfiltration_possible,
            v.confidentiality_impact,
            v.integrity_impact,
            v.availability_impact
        FROM vulnerabilities v
        WHERE LOWER(TRIM(v.file_name)) = LOWER(TRIM(%s))
        """

        cursor.execute(query, (vuln_name,))
        result = cursor.fetchone()

        #-----
        if result and 'id' in result:
            ref_query = "SELECT reference_url FROM vulnerability_references WHERE vulnerability_id = %s"
            cursor.execute(ref_query, (result['id'],))
            refs = [row['reference_url'] for row in cursor.fetchall()]
            result['references'] = refs

            iss_query = "SELECT issue FROM vulnerability_related_issues WHERE vulnerability_id = %s"
            cursor.execute(iss_query, (result['id'],))
            issues = [row['issue'] for row in cursor.fetchall()]
            result['issues'] = issues

        else:
            result['references'] = []
            result['issues'] = []

        #----

        cursor.close()
        connection.close()

        if not result:
            unmatched_vulnerabilities.add(vuln_name)
            return {
                "cvss_score": "N/A",
                "description": "N/A",
                "recommendation": "N/A",
                "exploitability": "N/A",
                "requires_authentication": "N/A",
                "data_exfiltration_possible": "N/A",
                "confidentiality_impact": "N/A",
                "integrity_impact": "N/A",
                "availability_impact": "N/A",
            }
        
        # cursor.close()
        # connection.close()

        return result

    except Exception as e:
        print(f"[DB Error] Failed to fetch details for '{vuln_name}': {e}")
        unmatched_vulnerabilities.add(vuln_name)
        return {
            "cvss_score": "N/A",
            "description": "N/A",
            "recommendation": "N/A",
            "exploitability": "N/A",
            "requires_authentication": "N/A",
            "data_exfiltration_possible": "N/A",
            "confidentiality_impact": "N/A",
            "integrity_impact": "N/A",
            "availability_impact": "N/A",
        }

def draw_summary_table(pdf, summary_data):
    with pdf.table(width=120, col_widths=(1, 1), borders_layout="SINGLE_TOP_LINE") as table:
        pdf.set_fill_color('#CCCCCC')
        row = table.row()
        row.cell("Executive Summary Data", colspan=2, align='C')
        for index, (key, value) in enumerate(summary_data):
            # Alternate row fill color
            if index % 2 == 0:
                pdf.set_fill_color('#FFFFFF')
            else:
                pdf.set_fill_color('#CCCCCC')

            row = table.row()
            row.cell(key, align='L')
            row.cell(value, align='L')

def sort_by_impact(items):
    # Define valid impact levels: 1=high, 2=medium, 3=low, 4=informative
    valid_impacts = {1, 2, 3, 4}  # Only using keys now, since we don't need the labels here
    
    grouped = defaultdict(lambda: {"urls": [], "impact": 0})

    for item in items:
        name = item.get("name", '').strip()
        url = item.get("url", '').strip()
        impact = item.get("impact", 0)

        if not name or not url or impact not in valid_impacts:
            print(f"[WARNING] Empty name found in item: {item}")
            continue

        grouped[name]["urls"].append(url)
        grouped[name]["impact"] = impact

    result = [
        {
            "name": name,
            "url": data["urls"],
            "impact": data["impact"]  # Keep as int
        }
        for name, data in grouped.items()
    ]

    result.sort(key=lambda x: x["impact"])  # Lower number = higher severity

    return result

def draw_analysis_table(pdf, filtered_items):
    with pdf.table(col_widths=(6, 150, 10), borders_layout="SINGLE_TOP_LINE") as table:
        pdf.set_fill_color('#CCCCCC')
        row = table.row()
        row.cell("List of Vulnerabilities found", colspan=3, align='C')
        pdf.set_fill_color('#FFFFFF')
        for item in filtered_items:
            name = item.get('name', '')
            urls = item.get('url', [])
            impact = item.get('impact', 0)
            # Impact image cell
            row = table.row()
            row.cell(img=f'assets/icons/{impact}.png', align='L', padding=(0, 0, 0, 1))
            row.cell(name, padding=(0, 0, 0, 5))
            row.cell(f'{len(urls)}', align='R')


def display_vulnerability_item(pdf, vulnerability_item):
    http_data = vulnerability_item.get('http', [])
    if http_data:
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(0, 10, "REQUEST / RESPONSE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        pdf.set_font('helvetica', '', 10)

        for entry in http_data:
            request = entry.get('request', '').strip()
            response = entry.get('response', '').strip()

            if request:
                pdf.set_fill_color('#e5e5e5')
                pdf.set_font('helvetica', 'B', 10)
                pdf.cell(0, 8, "Request:", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
                pdf.set_font('helvetica', '', 10)
                beautify_http_response(pdf, request)
                pdf.ln()

            if response:
                pdf.set_fill_color('#e5e5e5')
                pdf.set_font('helvetica', 'B', 10)
                pdf.cell(0, 8, "Response:", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
                pdf.set_font('helvetica', '', 10)
                beautify_http_response(pdf, response)
                pdf.ln()

    
    pdf.ln(5)
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, "Description", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.set_font('helvetica', '', 12)
    write_highlighted_text(pdf, vulnerability_item.get('Description', ''), vulnerability_item.get('name', ''))
    pdf.ln(2)

    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, "Recommendation", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.set_font('helvetica', '', 12)
    write_highlighted_text(pdf, vulnerability_item.get('Recommendation', ''), vulnerability_item.get('name', ''))
    pdf.ln(5)

    add_label_value(pdf, "Severity:", vulnerability_item.get('impact', ''))    

    pdf.set_x(pdf.l_margin)
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(pdf.get_string_width("CVSS Score: ") + 2, 8, "CVSS Score:", ln=0)

    pdf.set_x(pdf.w / 2)
    pdf.set_font('helvetica', '', 12)
    pdf.multi_cell(0, 8, f"{vulnerability_item.get('CVSS_Score', '')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

    add_label_value(pdf, "Exploitability:", vulnerability_item.get('Exploitability', ''))

    def yes_no(value):
        if str(value).strip() == '1':
            return 'Yes'
        if str(value).strip() == '0':
            return 'No'
        return str(value)
    add_label_value(pdf, "Requires Authentication:", yes_no(vulnerability_item.get('Requires_Authentication', '')))
    add_label_value(pdf, "Data Exfiltration Possible:", yes_no(vulnerability_item.get('Data_Exfiltration_Possible', '')))
    add_label_value(pdf, "Confidentiality Impact:", vulnerability_item.get('Confidentiality_Impact', ''))
    add_label_value(pdf, "Integrity Impact:", vulnerability_item.get('Integrity_Impact', ''))
    add_label_value(pdf, "Availability Impact:", vulnerability_item.get('Availability_Impact', ''))

#-----------------
    issues = vulnerability_item.get('issues', [])
    if issues:
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, "Related Issue(s)", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        pdf.set_font('helvetica', '', 12)
        for issue in issues:
            pdf.multi_cell(0, 8, issue, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
#-----------------

#-----------------
    references = vulnerability_item.get('references', [])
    if references:
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, "Reference(s)", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        pdf.set_font('helvetica', '', 12)
        for ref in references:
            pdf.multi_cell(0, 8, ref, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
#-----------------

def display_overview(pdf, overview_item):
    title = overview_item.get('title', '')
    impact = overview_item.get('impact', '')
    icon_path = f'assets/icons/{impact}.png'
    # Draw the text
    pdf.set_font('helvetica', 'B', 13)
    text_width = pdf.get_string_width(title)
    pdf.cell(text_width, 15, title, new_x=XPos.RIGHT, new_y=YPos.TOP, align='L')
    # Draw the image right after the text
    x = pdf.get_x() + 3  # A small space between text and image
    y = pdf.get_y() + 5.5  # Center vertically within the 15 height cell

    pdf.image(icon_path, x=x, y=y, w=4, h=4)

    # Move to the next line after both
    pdf.set_y(pdf.get_y() + 15)
    pdf.ln(2)
    
    for overview_content in overview_item.get('content', []):
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, overview_content.get('title', []), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        pdf.set_font('helvetica', '', 12)
        for text in overview_content.get('text', []):
            pdf.multi_cell(0, 8, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
            pdf.ln(1)
        pdf.ln(2)

    pdf.ln(15)


def display_conclusion(pdf, conclusion):
    pdf.set_font('helvetica', 'B', 20)
    pdf.cell(0, 15, 'Conclusion', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

    pdf.set_font('helvetica', '', 12)
    for text in conclusion:
        pdf.multi_cell(0, 10, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

    pdf.ln(15)
