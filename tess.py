from weasyprint import HTML
from jinja2 import Template
import base64

# Path to the map image
map_image_path = r"C:\Users\okusa\Sentiment\Sent_anlys\map_image.png"

# Convert the image to Base64
with open(map_image_path, "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode('utf-8')

# Compact table HTML template with a resized map in a column
compact_table_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        @page {
            size: A4;
            margin: 20px;
        }
        body {
            font-family: Arial, sans-serif;
            margin: 10px;
            line-height: 1.4;
            font-size: 10px;
        }
        h1 {
            text-align: center;
            color: #333;
            font-size: 18px;
        }
        h2 {
            color: #444;
            border-bottom: 1px solid #ccc;
            font-size: 14px;
            margin-top: 10px;
        }
        .section {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 15px;
            margin-bottom: 20px;
        }
        .text {
            flex: 2;
        }
        .charts {
            flex: 3;
        }
        img {
            max-width: 100%;
            height: auto;
            margin: 10px auto;
            border: 1px solid #ccc;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        table, th, td {
            border: 1px solid #ccc;
        }
        th, td {
            padding: 5px;
            text-align: left;
            font-size: 8px;
        }
        th {
            background-color: #f4f4f4;
        }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p><strong>Date:</strong> {{ date }}</p>

    <h2>Dangote Refinery</h2>
    <div class="section">
        <div class="text">
            <p><strong>Capacity & Impact:</strong> Operating at ~50%, the refinery processes 650,000 barrels/day, exporting petrol, diesel, and jet fuel. Key destinations include Europe and regional hubs like Ghana and South Africa, challenging traditional suppliers.</p>
            <p><strong>Strategic Expansion:</strong> Plans include building 6.3 million liters of storage capacity to enhance export capabilities.</p>
            <p><strong>Regional Dynamics:</strong> A decline in MR tanker imports contrasts with rising Handysize and MR demand for exports. Crude flows via Suezmax and VLCCs to Europe and Asia remain robust.</p>
        </div>
        <div class="charts">
            <h3>Strategic Tanker Routes</h3>
            <img src="data:image/png;base64,{{ map_image }}" alt="Strategic Tanker Routes Map" style="width: 80%; max-width: 300px;">
        </div>
    </div>

    <h2>Global Tanker Market Overview</h2>
    <div class="section">
        <div class="text">
            <table>
                <thead>
                    <tr>
                        <th>Route</th>
                        <th>Description</th>
                        <th>Worldscale</th>
                        <th>TCE ($/day)</th>
                        <th>+/-</th>
                    </tr>
                </thead>
                <tbody>
                    {% for route in routes %}
                    <tr>
                        <td>{{ route['Route'] }}</td>
                        <td>{{ route['Description'] }}</td>
                        <td>{{ route['Worldscale'] }}</td>
                        <td>${{ route['TCE'] }}</td>
                        <td style="color: {{ 'green' if route['Change'] > 0 else 'red' }};">
                            {{ route['Change'] }}
                            {% if route['Change'] > 0 %}
                                &#9650; <!-- Upward arrow -->
                            {% elif route['Change'] < 0 %}
                                &#9660; <!-- Downward arrow -->
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

# Route data for the table
routes = [
    {"Route": "TD27", "Description": "130K Guyana to ARA", "Worldscale": 71.11, "TCE": 23510, "Change": 2138},
    {"Route": "TD25", "Description": "70K US Gulf to UK-Continent", "Worldscale": 168.06, "TCE": 41586, "Change": -590},
    {"Route": "TD22", "Description": "270K US Gulf to China", "Worldscale": 6820000.00, "TCE": 29834, "Change": 2399},
]

# Render the HTML
report_data = {
    "title": "Maritime Per Week",
    "date": "13 January 2025",
    "routes": routes,
    "map_image": base64_image,
}

template = Template(compact_table_template)
rendered_html = template.render(**report_data)

# Generate the PDF
output_pdf_path = "Maritime_Per_Week_Compact_Tables_With_Map.pdf"
HTML(string=rendered_html).write_pdf(output_pdf_path)

print(f"PDF generated: {output_pdf_path}")
