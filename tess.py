from weasyprint import HTML
from jinja2 import Template
import base64
import os

# Path to the map image
map_image_path = r"C:\Users\okusa\Sentiment\Sent_anlys\map_image.png"


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

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
            margin: 5px;
            line-height: 1.4;
            font-size: 10px;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-top: 5px 0;
            font-size: 24px;
        }
        h2 {
            color: #444;
            border-bottom: 1px solid #ccc;
            margin-top: 10px;
            font-size: 14px;
        }
        p {
            padding: 0;
            margin-top: 1px;
        }
        .section {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 35px;
            margin-bottom: 15px;
        }
        .text {
            flex: 3;
            margin-right: 10px;
        }
        .charts {
            flex: 4;
            margin-top: 0;
        }
        img {
            display: block;
            margin: 10px auto;
            max-width: 100%;
            max-height: 300px;
            object-fit: contain;
        }
        table {
            width: 90%;
            border-collapse: collapse;
            margin: 5px 0;
        }
        table, th, td {
            border: 1px solid #ccc;
        }
        th, td {
            padding: 3px;
            text-align: left;
            font-size: 8px;
        }
        th {
            background-color: #f4f4f4;
            font-size: 8px;
        }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p><strong>Date:</strong> {{ date }}</p>
    <h2>Dangote Refinery</h2>
    <div class="section">
        <div class="text">
            <p><strong>Capacity & Impact:</strong> Operating at ~50% capacity, the refinery processes 650,000 barrels/day, producing petrol, diesel, and jet fuel. Export destinations include Europe, Ghana, and South Africa, disrupting traditional gasoline trade routes and challenging long-standing suppliers.</p>
            <p><strong>Foreign Exchange & Export Earnings:</strong> By reducing import dependency and boosting export earnings, the refinery enhances Nigeria’s economic resilience, stabilizing foreign exchange reserves and increasing revenue streams.</p>
            <p><strong>Strategic Expansion:</strong> Plans include constructing 6.3 million liters of storage capacity to boost export operations, addressing short-term crude oil supply issues faced by Dangote and NNPC.</p>
            <p><strong>Energy Diversification:</strong> Emphasizing the importance of a diversified energy strategy, including investments in gas and renewables, to ensure long-term sustainability.</p>
        </div>
        <div class="charts">
            <h3>Regional & Global Dynamics</h3>
            <p><strong>Decline in MR Tanker Imports:</strong> Reduced reliance on gasoline imports impacts traditional MR flows, particularly from Europe.</p>
            <p><strong>Rising Export Demand:</strong> Increased production capacity drives regional exports to Ghana and other markets, boosting Handysize and MR demand.</p>
            <p><strong>Global Impact:</strong> New export routes emerge as local refining capacity reduces Nigeria’s dependency on imports, shifting tanker flows and increasing competition in other markets.</p>
            <p><strong>Geopolitical Considerations:</strong> The refinery strengthens Nigeria’s role in the global oil and gas ecosystem, supporting regional energy security and fostering trade ties.</p>
        </div>
    </div>

    <h2>Global Tanker Market Overview</h2>
    <div class="section">
        <div class="text">
            <p>{{ overview }}</p>
            <img src="data:image/png;base64, {{ map_image }}" alt="Strategic Tanker Routes Map" style="max-width:80%; margin: 20px auto; border: 1px solid #ccc;">
        </div>
        <div class="charts">
            <table class="routes">
                <thead>
                    <tr>
                        <th>Route</th>
                        <th>Highest TCE Changes - Description</th>
                        <th>Worldscale</th>
                        <th>TCE ($/day)</th>
                        <th>+/-</th>
                    </tr>
                </thead>
                <tbody>
                    {% for route in highest_changes %}
                    <tr>
                        <td>{{ route['Route'] }}</td>
                        <td>{{ route['Description'] }}</td>
                        <td>{{ route['Worldscale'] }}</td>
                        <td>${{ route['TCE'] }}</td>
                        <td style="color: {{ 'green' if route['Change (TCE)'] > 0 else 'red' }};">
                            {{ route['Change (TCE)'] }}
                            {% if route['Change (TCE)'] > 0 %}
                                &#9650;
                            {% elif route['Change (TCE)'] < 0 %}
                                &#9660;
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

base_dir = os.getcwd()
absolute_paths = {
    "SI": encode_image_to_base64(os.path.join(base_dir, "images/SI=F_price_comparison.png")),
    "GC": encode_image_to_base64(os.path.join(base_dir, "images/GC=F_price_comparison.png")),
    "CL": encode_image_to_base64(os.path.join(base_dir, "images/CL=F_price_comparison.png")),
    "BZ": encode_image_to_base64(os.path.join(base_dir, "images/BZ=F_price_comparison.png")),
}

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
    "sigc_graphs": [absolute_paths["SI"], absolute_paths["GC"],],
    "bzcl_graphs": [absolute_paths["BZ"], absolute_paths["CL"],],
    "map_image": base64_image,
}

template = Template(compact_table_template)
rendered_html = template.render(**report_data)

# Generate the PDF
output_pdf_path = "Maritime_Per_Week_Compact_Tables_With_Map.pdf"
HTML(string=rendered_html).write_pdf(output_pdf_path)

print(f"PDF generated: {output_pdf_path}")
