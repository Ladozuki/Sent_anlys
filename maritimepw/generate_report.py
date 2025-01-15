from weasyprint import HTML
import os
from jinja2 import Template

# Compact table HTML template
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
            margin: 20px
        }
    
        body {
            font-family: Arial, sans-serif;
            margin: 5px
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
        .charts h3 {
            margin-top: 0;
            font-size: 12px;
            color: #333;
            text-decoration: underline;
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
        .routes th:nth-child(1),
        .routes td:nth-child(1) {
            width: 15%; /* Adjust column width for 'Route' */
        }

        .routes th:nth-child(2),
        .routes td:nth-child(2) {
            width: 35%; /* Adjust column width for 'Description' */
        }

        .routes th:nth-child(3),
        .routes td:nth-child(3),
        .routes th:nth-child(4),
        .routes td:nth-child(4),
        .routes th:nth-child(5),
        .routes td:nth-child(5) {
            width: 10%; /* Adjust column width for numeric data */
        }
        img {
            display: block;
            margin: 10px auto;
            max-width: 100%;
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
            <h3>Global Impact</h3>
            <p><strong>Oil Price Dynamics:</strong> Increased local refining capacity reduces Nigeria’s import requirements, influencing global product tanker flows.</p>
            <p><strong>Tanker Demand Shifts:</strong> Long-haul crude shipments to Nigeria may decline, while new export routes for refined products emerge.</p>
            <p><strong>Geopolitical Considerations:</strong> The refinery enhances Nigeria’s strategic importance in the global oil and gas ecosystem, fostering increased investment and trade ties.</p>
        </div>
    </div>

    <h2>Global Tanker Market Overview</h2>
<div class="section">
    <div class="text">
        <p>{{ overview }}</p>
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
                            &#9650; <!-- Upward arrow -->
                        {% elif route['Change (TCE)'] < 0 %}
                            &#9660; <!-- Downward arrow -->
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <h3>All Routes - Detailed Table</h3>
        <table class="routes">
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
                {% for route in remaining_routes %}
                <tr>
                    <td>{{ route['Route'] }}</td>
                    <td>{{ route['Description'] }}</td>
                    <td>{{ route['Worldscale'] }}</td>
                    <td>${{ route['TCE'] }}</td>
                    <td style="color: {{ 'green' if route['Change (TCE)'] > 0 else 'red' }};">
                        {{ route['Change (TCE)'] }}
                        {% if route['Change (TCE)'] > 0 %}
                            &#9650; <!-- Upward arrow -->
                        {% elif route['Change (TCE)'] < 0 %}
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

# Route data for the report
full_route_data = [
    {"Route": "TD27", "Description": "130K Guyana to ARA", "Worldscale": 71.11, "TCE": 23510, "Change (TCE)": 2138},
    {"Route": "TD25", "Description": "70K US Gulf to UK-Continent", "Worldscale": 168.06, "TCE": 41586, "Change (TCE)": -590},
    {"Route": "TD22", "Description": "270K US Gulf to China", "Worldscale": 6820000.00, "TCE": 29834, "Change (TCE)": 2399},
    {"Route": "TC16", "Description": "60K ARA to West Africa", "Worldscale": 116.94, "TCE": 18096, "Change (TCE)": -1656},
    {"Route": "TD3C", "Description": "270K Middle East Gulf to China (VLCC)", "Worldscale": 59.7, "TCE": 37822, "Change (TCE)": 10679},
    {"Route": "TD6", "Description": "135K Black Sea to Mediterranean (Suezmax)", "Worldscale": 78.85, "TCE": 19780, "Change (TCE)": 1489},
    {"Route": "TD7", "Description": "80K North Sea to Continent (Aframax)", "Worldscale": 108.33, "TCE": 19680, "Change (TCE)": -165},
    {"Route": "TD9", "Description": "70K Caribbean to US Gulf (LR1)", "Worldscale": 159.38, "TCE": 33965, "Change (TCE)": 1258},
    {"Route": "TD15", "Description": "260K West Africa to China (VLCC)", "Worldscale": 61.44, "TCE": 40035, "Change (TCE)": 9515},
    {"Route": "TD20", "Description": "130K West Africa to UK-Continent (Suezmax)", "Worldscale": 74.72, "TCE": 26123, "Change (TCE)": 4085},
    {"Route": "TC5", "Description": "55K CPP Middle East Gulf to Japan (LR1)", "Worldscale": 158.13, "TCE": 22468, "Change (TCE)": -108},
    {"Route": "TC8", "Description": "65K CPP Middle East Gulf to UK-Continent (LR1)", "Worldscale": 45.494, "TCE": 25120, "Change (TCE)": 2259},
    {"Route": "TC12", "Description": "35K Naphtha West Coast India to Japan (MR)", "Worldscale": 143.31, "TCE": 10676, "Change (TCE)": 291},
    {"Route": "TC15", "Description": "80K Naphtha Mediterranean to Far East (Aframax)", "Worldscale": 3094167, "TCE": 8946, "Change (TCE)": -605},
    {"Route": "TC16", "Description": "60K CPP Amsterdam to West Africa (LR1)", "Worldscale": 116.94, "TCE": 18096, "Change (TCE)": -1656},
    {"Route": "TC17", "Description": "35K CPP Jubail to Dar es Salaam (MR)", "Worldscale": 216.07, "TCE": 20319, "Change (TCE)": 777},
    {"Route": "TC18", "Description": "38K CPP US Gulf to Brazil (MR)", "Worldscale": 167.5, "TCE": 17785, "Change (TCE)": 677},
    {"Route": "TC19", "Description": "37K CPP Amsterdam to Lagos (MR)", "Worldscale": 167.81, "TCE": 20102, "Change (TCE)": 2479},
    {"Route": "TC20", "Description": "90K CPP Middle East Gulf to UK-Continent (Aframax)", "Worldscale": 3956250, "TCE": 36279, "Change (TCE)": 2492},
]



# Resolve absolute paths
base_dir = os.getcwd()  # Get the current working directory
absolute_paths = {
    "SI": os.path.join(base_dir, "images/SI=F_price_comparison.png"),
    "GC": os.path.join(base_dir, "images/GC=F_price_comparison.png"),
    "CL": os.path.join(base_dir, "images/CL=F_price_comparison.png"),
    "BZ": os.path.join(base_dir, "images/BZ=F_price_comparison.png"),
}

# Update report data with absolute paths
updated_report_data_with_all_routes = {
    "title": "Maritime Per Week",
    "date": "13 January 2025",
    "overview": """
    The tanker market saw dynamic activity this week, with VLCC and Suezmax earnings on Middle East Gulf and West Africa routes experiencing significant gains. Aframax and MR tankers showed steadier movements, supported by balanced demand in the Atlantic and Asia-Pacific regions.

    Key Index Movements: The Baltic Dirty Tanker Index (BDTI) rose 34 points to 855, reflecting robust crude demand. The Baltic Clean Tanker Index (BCTI) gained 11 points to 640, underscoring resilience in clean product markets.

    West Africa Focus: Exports to Asia and Europe remain pivotal, further impacted by Nigeria's Dangote Refinery, poised to recalibrate global tanker flows through reduced refined product imports and increased local refining.
    """,
    "highest_changes": sorted(full_route_data, key=lambda x: x["Change (TCE)"], reverse=True)[:5],
    "remaining_routes": full_route_data,
    "refinery_images": [
        absolute_paths["SI"],
        absolute_paths["GC"],
    ],
    "market_images": [
        absolute_paths["BZ"],
    ],
}

# Render the HTML
template = Template(compact_table_template)
rendered_html = template.render(**updated_report_data_with_all_routes)

# Save to PDF
output_pdf_path = "Maritime_Per_Week_Compact_Tables.pdf"
HTML(string=rendered_html).write_pdf(output_pdf_path)

print(f"PDF generated: {output_pdf_path}")
