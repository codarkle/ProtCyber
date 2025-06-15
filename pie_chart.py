import math

def draw_pie_chart_3d(pdf, data, x, y, radius, depth=-30, vertical_scale=0.5):
    counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for i in data:
        counts[i] = counts.get(i, 0) + 1

    total = len(data)
    if total == 0:
        return  # avoid division by zero

    colors = {
        4: (0, 0, 255),    # Blue - Informative
        3: (0, 255, 0),    # Green - Low
        2: (255, 255, 0),  # Yellow - Medium
        1: (255, 0, 0)     # Red - High
    }

    start_angle = 0

    # Draw "depth" layers for 3D effect - from bottom to top
    for d in range(depth, 0, 1):
        offset_y = y + d  # vertical offset for depth
        temp_start_angle = 0
        for impact, count in counts.items():
            if count == 0:
                continue
            angle = 360 * count / total
            # Darker color for depth
            base_color = colors[impact]
            dark_color = tuple(max(0, int(c * 0.6)) for c in base_color)
            pdf.set_fill_color(*dark_color)
            pie_slice_ellipse(pdf, x, offset_y, radius, radius * vertical_scale, temp_start_angle, temp_start_angle + angle)
            temp_start_angle += angle

    # Draw top pie slices normally
    for impact, count in counts.items():
        if count == 0:
            continue
        angle = 360 * count / total
        pdf.set_fill_color(*colors[impact])
        pie_slice_ellipse(pdf, x, y, radius, radius * vertical_scale, start_angle, start_angle + angle)
        start_angle += angle

def pie_slice_ellipse(pdf, x_center, y_center, radius_x, radius_y, start_angle, end_angle):
    start_rad = math.radians(start_angle)
    end_rad = math.radians(end_angle)
    pdf.set_line_width(0.5)
    pdf.set_draw_color(0)

    num_segments = 30
    step = (end_rad - start_rad) / num_segments
    points = [(x_center, y_center)]
    for i in range(num_segments + 1):
        angle = start_rad + i * step
        x = x_center + radius_x * math.cos(angle)
        y = y_center + radius_y * math.sin(angle)  # apply vertical scaling here!
        points.append((x, y))

    polygon(pdf, points, 'F')

def polygon(pdf, points, style=''):
    pdf._out(f'{points[0][0]:.2f} {points[0][1]:.2f} m')
    for point in points[1:]:
        pdf._out(f'{point[0]:.2f} {point[1]:.2f} l')
    if style == 'F':
        pdf._out('f')
    elif style in ('FD', 'DF'):
        pdf._out('B')
    else:
        pdf._out('S')

def add_pie_legend(pdf, x, y):
    pdf.set_font('Arial', '', 12)
    legend_items = [
        ("Informative", (0, 0, 255)),
        ("Low", (0, 255, 0)),
        ("Medium", (255, 255, 0)),
        ("High", (255, 0, 0))
    ]
    
    for i, (label, color) in enumerate(legend_items):
        pdf.set_fill_color(*color)
        pdf.rect(x, y + i * 10, 5, 5, 'F')  # Color box
        pdf.set_xy(x + 8, y + i * 10 - 1)
        pdf.cell(40, 6, label, ln=0)

def draw_boxed_text(pdf, text, x, y, w, h, bg_color=(200, 200, 200), border_color=(150, 150, 150), radius=0):
    # Set colors
    pdf.set_fill_color(*bg_color)
    pdf.set_draw_color(*border_color)

    # Draw filled rectangle (background)
    pdf.rect(x, y, w, h, style='F')

    # Draw rectangle border
    pdf.rect(x, y, w, h)

    # Note: fpdf does not support border-radius natively.

    # Draw text with padding inside the box
    padding = 2
    pdf.set_xy(x + padding, y + padding)
    pdf.multi_cell(w - 2*padding, 6, text)