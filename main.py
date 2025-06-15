import json
import os
import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from utils import get_vulnerability_from_db, sanitize_text, SEVERITY_LEVELS

from pie_chart import draw_pie_chart_3d, add_pie_legend
from openai_func import get_processed_info
from utils import sort_by_impact, draw_summary_table, draw_analysis_table, display_vulnerability_item, display_conclusion, display_overview

from report_config import (
    COMPANY_NAME,
    LOGO_PATH,
    FRONT_IMAGE,
    contents,
    confidentiality_template,
    scope_template,
    excutive_summary_template,
    recommendations_template,
    overviews,
    conclusion,
)


SEVERITY_COLORS = {
    1:  ((255, 200, 200), (255, 0, 0)),     # Light red -> red
    2:  ((255, 220, 180), (255, 140, 0)),   # Light orange -> dark orange
    3:  ((200, 255, 200), (0, 200, 0)),     # Light green -> green
    4:  ((200, 200, 255), (0, 0, 255)),     # Light blue -> blue
}

class PDFReport(FPDF):
    def __init__(self, title, domain, logo_path=None, front_image=None):
        super().__init__()
        self.title = title
        self.domain = domain
        self.logo_path = logo_path
        self.front_image = front_image
        self.set_margins(left=30, top=14, right=30)
        self.set_auto_page_break(auto=True, margin=20)
        self.severity = 0

    def header(self):
        if self.logo_path and os.path.exists(self.logo_path):
            page_width = self.w
            image_width = 40
            x = (page_width - image_width) / 2
            self.image(self.logo_path, x, 10, image_width)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        title_text = f'{COMPANY_NAME} {self.title} || '
        domain_text = f'{self.domain}'

        self.set_font('helvetica', 'B', 10)
        title_width = self.get_string_width(title_text)
        self.set_font('helvetica', '', 10)
        domain_width = self.get_string_width(domain_text)
        total_width = title_width + domain_width

        page_width = self.w - 2 * self.l_margin
        start_x = (page_width - total_width) / 2 + self.l_margin
        self.set_x(start_x)
        self.set_font('helvetica', 'B', 10)
        self.cell(title_width, 10, title_text, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_font('helvetica', '', 10)
        self.cell(domain_width, 10, domain_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        if self.page_no() == 1:
            return
        self.set_font('helvetica', '', 12)
        self.cell(0, -10, f'{self.page_no() - 1}', align='R')

        if self.severity != 0:
            """Draw a smooth gradient on the right border based on impact level."""
            border_width = 15
            steps = 30
            step_width = border_width / steps

            # Fallback if impact is not recognized
            start_color, end_color = SEVERITY_COLORS.get(self.severity, ((220, 220, 220), (100, 100, 100)))

            for i in range(steps):
                ratio = i / (steps - 1)
                r = int(start_color[0] + ratio * (end_color[0] - start_color[0]))
                g = int(start_color[1] + ratio * (end_color[1] - start_color[1]))
                b = int(start_color[2] + ratio * (end_color[2] - start_color[2]))

                self.set_fill_color(r, g, b)
                x = self.w - border_width + (i * step_width)
                self.rect(x, 0, step_width, self.h, 'F')

    def set_severity(self, impact): 
        self.severity = impact

    def add_front_page(self):
        self.add_page()
        self.set_font('helvetica', 'B', 32)
        self.set_y(100)
        self.cell(0, 10, f'{COMPANY_NAME}', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        self.ln(3)
        self.set_font('helvetica', 'B', 20)
        self.cell(0, 10, self.title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        self.set_font('helvetica', '', 14)
        self.cell(0, 10, self.domain, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        if self.front_image and os.path.exists(self.front_image):
            self.image(self.front_image, 0, 135, self.w)

    def table_of_content(self, contents):
        self.add_page()
        self.set_y(50)
        self.set_font('helvetica', 'B', 24)
        self.cell(0, 15, 'Table of Contents', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(5)

        def add_entry(item):
            prefix = ' ' * item.get('indent', 0)
            font_style = 'B' if item.get('bold', False) else ''
            self.set_font('helvetica', font_style, 12)
            title_text = prefix + item['title']
            title_width = self.get_string_width(title_text)
            dots = '.' * int((150 - title_width) / self.get_string_width('.'))
            self.cell(0, 8, f'{title_text} {dots} {item["page"]}', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

        for item in contents:
            add_entry(item)

    def display_text(self, content, content_title):
        self.set_font('helvetica', 'B', 14)
        self.set_x(self.l_margin)
        self.cell(0, 15, content_title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        self.set_font('helvetica', '', 12)
        for para in content:
            clean_para = sanitize_text(str(para))
            self.set_x(self.l_margin)
            self.multi_cell(0, 8, clean_para)
        self.ln(4)

    def display_title(self, content_title):
        self.set_font('helvetica', 'B', 20)
        self.set_x(self.l_margin)
        self.multi_cell(0, 10, content_title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(6)


def generate_report(json_file_path, output_file_path=None):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    domain = data.get('target', 'Unknown Domain')
    vulnerabilities = data.get('issues', [])
    impact_array = [v.get('impact') for v in vulnerabilities if v.get('impact')]

    # Inside your `generate_report()` function:
    page_title = "Web Vulnerability Assessment Report"
    client_name = '<Unknown Client>'
    sample_server = '<Sample Server>'

    # Format all templates
    confidentiality = [p.format(client_name=client_name, domain=domain) for p in confidentiality_template]
    scope = [p.format(sample_server=sample_server) for p in scope_template]
    excutive_summary = [p.format(sample_server=sample_server) for p in excutive_summary_template]
    recommendations = [p.format(sample_server=sample_server) for p in recommendations_template]

    summary = {
        "date": data.get('date', str(datetime.datetime.now().date())),
        "duration": data.get('duration', '0′ 0″').replace('′', "'").replace('″', '"'),
        "requests": data.get('requests', 0),
        "risk": data.get('risk', 0),
        "status": data.get('status', "finished"),
        "version": data.get('version', "0.0.1")
    }

    pdf = PDFReport(page_title, domain, LOGO_PATH, FRONT_IMAGE)
    pdf.add_front_page()
    # pdf.table_of_content(contents)

    # Vulnerability Assessment Report
    pdf.add_page()
    pdf.display_title("Vulnerability Assessment Report")
    pdf.display_text(confidentiality, "Statement of Confidentiality")
    pdf.display_text(scope, "Scope")

    # Executive Summary
    pdf.add_page()
    pdf.display_text(excutive_summary, "Executive Summary")
    pdf.ln(10)

    summary_data = [
        ("Target Domain:", domain),
        ("Date:", summary['date']),
        ("Duration:", summary['duration']),
        ("Requests:", str(summary['requests'])),
        ("Risk:", str(summary['risk'])),
        ("Status:", summary['status']),
        ("Version:", summary['version']),
    ]

    # Summary page
    draw_summary_table(pdf, summary_data)

    # 3d pie chart  
    draw_pie_chart_3d(pdf, impact_array, x=245, y=250, radius=120)
    add_pie_legend(pdf, x=150, y=200)

    # Recommendations
    pdf.add_page()
    pdf.display_text(recommendations, "Recommendations")

    # Detailed Analysis
    pdf.add_page()
    pdf.display_text([], "Detailed Analysis")
    filtered_items = sort_by_impact(vulnerabilities)
    draw_analysis_table(pdf, filtered_items)

    # Vulnerabilities
    pdf.add_page()
    pdf.display_text([], "Vulnerabilities")

    for index1, item in enumerate(filtered_items):
        for index2, url in enumerate(item['url']):
            vulnerability_item = next( (v for v in vulnerabilities if v.get('url') == url and v.get('name') == item['name']), 0 )   
            if not vulnerability_item:
                continue

            pdf.set_severity(item['impact'])
            if index2 == 0:
                pdf.set_font('helvetica', 'B', 12)
                pdf.set_x(pdf.l_margin)
                pdf.cell(0, 10, f'{index1 + 1}. {sanitize_text(item["name"])}', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

            title = vulnerability_item.get('name', 'Unknown vulnerability')
            # print(f"Processing vulnerability: {title}") 
            db_data = get_vulnerability_from_db(title)
            if not db_data:
                # print(f"[WARNING] No data found in DB for vulnerability: {title}")
                continue                #optionally skip if no DB data

            def resolve_field(db_val, json_val, default='N/A'):
                if db_val is not None and str(db_val).strip() != "":
                    return sanitize_text(str(db_val))
                if json_val is not None and str(json_val).strip() != "":
                    return sanitize_text(str(json_val))
                # print(f"[WARNING] No data for field '{title}' in DB or JSON, using default: {default}")
                return default

            vulnerability_item['Description'] = resolve_field(
                db_data.get('description') if db_data else None,
                vulnerability_item.get('Description')
            )

            vulnerability_item['Recommendation'] = resolve_field(
                db_data.get('recommendation') if db_data else None,
                vulnerability_item.get('Recommendation')
            )

            vulnerability_item['impact'] = resolve_field(
                db_data.get('severity') if db_data else None,
                SEVERITY_LEVELS.get(item['impact'])
            )

            vulnerability_item['CVSS_Score'] = resolve_field(db_data.get('cvss_score') if db_data else None, None)
            vulnerability_item['Exploitability'] = resolve_field(db_data.get('exploitability') if db_data else None, None)
            vulnerability_item['Requires_Authentication'] = resolve_field(db_data.get('requires_authentication') if db_data else None, None)
            vulnerability_item['Data_Exfiltration_Possible'] = resolve_field(db_data.get('data_exfiltration_possible') if db_data else None, None)
            vulnerability_item['Confidentiality_Impact'] = resolve_field(db_data.get('confidentiality_impact') if db_data else None, None)
            vulnerability_item['Integrity_Impact'] = resolve_field(db_data.get('integrity_impact') if db_data else None, None)
            vulnerability_item['Availability_Impact'] = resolve_field(db_data.get('availability_impact') if db_data else None, None)
            vulnerability_item['issues'] = db_data.get('issues', [])
            vulnerability_item['references'] = db_data.get('references', [])

            http_data = vulnerability_item.get('http', [])

            pdf.set_font('helvetica', 'B', 12)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 5, f'{index1 + 1}.{index2 + 1}.{sanitize_text(url)}', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

            if not http_data:
                pdf.set_font('helvetica', '', 12)
                pdf.set_x(pdf.l_margin + 10)
                pdf.cell(0, 10, "No Data for this vulnerability", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
                pdf.ln(8)
                continue

            display_vulnerability_item(pdf, vulnerability_item)
            pdf.add_page()



    # Overview
    pdf.add_page()
    pdf.display_title("Overview of Web Vulnerability Severity Levels and Security Impact")
    for overview_item in overviews:
        pdf.set_severity(overview_item.get('impact', 0))
        display_overview(pdf, overview_item)

    pdf.set_severity(0)
    # Conclusion
    pdf.add_page()
    pdf.set_severity(0)
    display_conclusion(pdf, conclusion)

    pdf.output(output_file_path)

# Example usage:

def process_folder(main_folder=None):
    if main_folder is None:
        main_folder = os.getcwd()  # Set to current working directory

    reports_root = os.path.join(main_folder, "reports")
    for root, dirs, files in os.walk(main_folder):
        for file in files:
            if file.endswith(".json"):
                json_path = os.path.join(root, file)

                # Read JSON
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception as e:
                    print(f"Skipping {json_path}: {e}")
                    continue

                file_name = os.path.splitext(os.path.basename(json_path))[0]

                # Calculate relative path
                rel_path = os.path.relpath(root, main_folder)
                report_dir = os.path.join(reports_root, rel_path)
                os.makedirs(report_dir, exist_ok=True)

                # Save report
                report_filename = os.path.splitext(file)[0] + ".pdf"
                report_path = os.path.join(report_dir, report_filename)

                # Generate report
                generate_report(json_path, report_path)
                # print(f" Report generated: {report_path}")


from utils import unmatched_vulnerabilities

if unmatched_vulnerabilities:
    print("\n🔍 Unmatched vulnerabilities (not found in DB):")
    for name in sorted(unmatched_vulnerabilities):
        print(f"❌ {name}")
else:
    print("\n✅ All vulnerabilities were matched successfully.")

# Example usage
if __name__ == "__main__":
    process_folder()  # Uses the current folder by default
