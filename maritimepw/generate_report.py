from weasyprint import HTML
import os
from jinja2 import Template
import base64

# map_image_base64 = encode_image_to_base64(map_image_path)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
map_image_path = r"C:\Users\okusa\Sentiment\Sent_anlys\fuel_prices_map.png"
base64_image = encode_image(map_image_path)

# Resolve absolute paths
base_dir = os.getcwd()  # Get the current working directory
absolute_paths = {
    "SI": encode_image(os.path.join(base_dir, "images/SI=F_price_comparison.png")),
    "GC": encode_image(os.path.join(base_dir, "images/GC=F_price_comparison.png")),
    "CL": encode_image(os.path.join(base_dir, "images/CL=F_price_comparison.png")),
    "BZ": encode_image(os.path.join(base_dir, "images/BZ=F_price_comparison.png")),
}

# Compact table HTML template
# compact_table_template = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>{{ title }}</title>
#     <style>
#         @page {
#             size: A4;
#             margin: 20px;
#         }
#         body {
#             font-family: Arial, sans-serif;
#             margin: 5px;
#             line-height: 1.4;
#             font-size: 10px;
#         }
#         h1 {
#             text-align: center;
#             color: #333;
#             margin-top: 5px 0;
#             font-size: 24px;
#         }
#         h2 {
#             color: #444;
#             border-bottom: 1px solid #ccc;
#             margin-top: 10px;
#             font-size: 14px;
#         }
#         p {
#             padding: 0;
#             margin-top: 1px;
#         }
#         .section {
#             display: flex;
#             justify-content: space-between;
#             align-items: flex-start;
#             gap: 35px;
#             margin-bottom: 15px;
#         }
#         .text {
#             flex: 3;
#             margin-right: 10px;
#         }
#         .charts {
#             flex: 4;
#             margin-top: 0;
#         }
#         img {
#             display: block;
#             margin: 10px auto;
#             max-width: 50%;
#         }
#     </style>
# </head>
# <body>
#     <h1>{{ title }}</h1>
#     <p><strong>Date:</strong> {{ date }}</p>
    
#     <!-- Display the map -->
#     <h2>Strategic Tanker Routes</h2>
#     <img src="data:image/png;base64,{{ map_image }}" alt="Strategic Tanker Routes Map" style="width: 80%; max-width: 300px; margin: 20px auto;">

#     <h2>Dangote Refinery</h2>
#     <div class="section">
#         <div class="text">
#             <p><strong>Capacity & Impact:</strong> Operating at ~50%, the refinery processes 650,000 barrels/day, exporting petrol, diesel, and jet fuel. Key destinations include Europe and regional hubs like Ghana and South Africa, challenging traditional suppliers.</p>
#             <p><strong>Strategic Expansion:</strong> Plans include building 6.3 million liters of storage capacity to enhance export capabilities.</p>
#         </div>
#         <div class="charts">
#             <h3>Global Impact</h3>
#             <p><strong>Oil Price Dynamics:</strong> Increased local refining capacity reduces Nigeria’s import requirements, influencing global product tanker flows.</p>
#         </div>
#     </div>

#     <h2>Graphs</h2>
#     {% for image in sigc_graphs %}
#         <img src="data:image/png;base64,{{ image }}" alt="Refinery Graph" style="max-width:100%; margin: 20px auto;">
#     {% endfor %}
#     {% for image in bzcl_graphs %}
#         <img src="data:image/png;base64,{{ image }}" alt="Market Graph" style="max-width:100%; margin: 20px auto;">
#     {% endfor %}
# </body>
# </html>
# """

#Compact table HTML template
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
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: flex-start;
            gap: 15px;
            width: 100%;
            margin-bottom: 10px;
        }
        .text {
            flex: 3.5;
            margin-right: 5px;
        }
        .charts {
            flex: 3.5;
            margin-top: 0;
        }
        .charts-grid {
            display:grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 20px;
            }
        .charts-grid img {
            width: 100%;
            height: auto;
            border: 1px solid #ccc;
            object-fit: contain;}
        .charts h3 {
            margin-top: 0;
            font-size: 12px;
            color: #333;
            text-decoration: underline;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 0 auto;
            font-size: 8px;
            margin-top: 3px;
        }
        table, th, td {
            border: 1px solid #ccc;
        }
        th, td {
            padding: 2px;
            text-align: left;
            font-size: 8px;
        }
        th {
            background-color: #f4f4f4;
            font-size: 8px;
        }
        .routes th:nth-child(1),
        .routes td:nth-child(1) {
            width: 5%; /* Adjust column width for 'Route' */
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
            width: 8%; /* Adjust column width for numeric data */
        }
        .demarcation {
            margin-top: 0px;
            font-weight: bold;
            font-size: 10px;
            color: #222;
        }
        img {
            display: block;
            margin: 10px auto;
            max-width: 100%;
            max-height: 300px;
            object-fit: contain;
        }
        .cards {
            display: flex;
            gap: 15px;
            margin: 10px 0;
            justify-content: space-around;
            padding: 5px 0;}
        .card {
            flex: 1 1 calc(20% - 10px); /* Adjust width of each card */
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
            background-color: #f9f9f9;}
        .card h3 {
            font-size: 12px;
            margin-bottom: 5px;
            color: #444;}
        .card p {
            font-size: 10px;
            margin: 3px 0;}
        .card strong {
            font-size: 14px;
            color: #222;}
</style>
</head>
<body>
    <h1>{{ title }}</h1>

    <div class="section">
        <div class="text">
            <p><strong>Capacity & Impact:</strong> The Dangote Refinery, operational since December 2023, is the largest single-train refinery in the world, with a capacity of 650,000 barrels per day. Its production has significantly reduced Nigeria's reliance on imported refined products, particularly gasoline from Europe. This shift is disrupting traditional gasoline trade routes and challenging long-established suppliers.</p>
            <p><strong>Foreign Exchange & Export Earnings:</strong> Reducing refined product imports, the country can conserve foreign exchange. Additionally, with domestic demand met, Nigeria is positioned to export refined products, boosting foreign exchange earnings, improving the trade balance, and stabilizing the naira.</p>
            <p><strong>Strategic Expansion:</strong> Ongoing crude oil supply constraints due to limited availability from NNPC contributed to consturction of 6.3 million liters of additional storage capacity. Nigeria’s crude production has recovered from 931k bpd in 2022 to 1.5million bpd in 2024,  with the potential of 1.8m in 2025.</p>
            <p><strong>Energy Diversification:</strong> Achieving energy self-sufficiency within the next decade will require transitioning from petrol (PMS) to gas as the primary energy source, incorporating renewables, and leveraging resources like lithium for sustainability. Transparency in the downstream oil and gas sector remains a critical challenge.</p>
           
            <p>{{ overview }}</p> 

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

        <div class="demarcation"></div>
        <table class="routes">
            <thead>
                <tr>
                    <th>Route</th>
                    <th>Description - Dirty</th>
                    <th>Worldscale</th>
                    <th>TCE ($/day)</th>
                    <th>+/-</th>
                </tr>
            </thead>
            <tbody>
                {% for route in remaining_routes if route['Route'].startswith('TD') %}
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
        <div class="demarcation"></div>
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
                {% for route in remaining_routes if route['Route'].startswith('TC') %}
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

        <div class="cards">
        <div class="card">
            <h3>Suezmax TCE</h3>
            <p><strong>$30,422/day</strong></p>
            <p style="color: green;">+385 $/day &#9650;</p>
        </div>
        <div class="card">
            <h3>Aframax TCE</h3>
            <p><strong>$25,068/day</strong></p>
            <p style="color: green;">+355 $/day &#9650;</p>
        </div>
        <div class="card">
            <h3>VLCC TCE</h3>
            <p><strong>$57,025/day</strong></p>
            <p style="color: green;">+1717 $/day &#9650;</p>
        </div>
        <div class="card">
            <h3>VLCC OpEX</h3>
            <p><strong>$8,080/day</strong></p>
            <p style="color: green;">+102 $/day &#9650;</p>
        </div>
    </div>
    </div>
        <div class="charts">
            <p><strong>Regional & Global Dynamics. Decline in MR Tanker Imports:</strong> Reduced reliance on gasoline imports will impact traditional MR flows. Foreign refineries, especially in Europe, must explore new markets for their products, potentially leading to inventory buildup and price disruptions.</p>
            <p><strong>Rising Export Demand:</strong> Increased production capacity is driving regional exports to West-African Coast, South Africa, and abroad, boosting demand for Handysize and MR tankers. This dynamic enhances Nigeria's position as a regional energy hub.</p>
            <p><strong>Global Impact:</strong> New export routes will emerge as local refining capacity reduces Nigeria’s import dependency. This shift reshapes global tanker flows, increases competition in other markets, et al</p>
            <p><strong>Geopolitical Considerations:</strong> The Dangote Refinery strengthens Nigeria’s role in the global oil and gas ecosystem, supporting regional energy security and fostering trade ties. Resistance to this change is anticipated due to its disruption of long-established trade flows.</p>
            <h2>Global Bunker Prices</h2>
            <img src="data:image/png;base64,{{ map_image }}" 
             alt="Strategic Tanker Routes Map" 
             style="max-width: 90%; height: auto; margin: 10px auto; border: 1px solid #ccc;">

            {% for image in bzcl_graphs %}
                <img src="data:image/png;base64,{{ image }}" 
                    alt="Market Graph" 
                        style="width: 100%; max-width: 600px; max-height: 400px; object-fit: contain; margin: 5px auto; border: 1px solid #ccc;">
        {% endfor %}
        </div>
    </div>

</body>
</html>
"""

full_route_data = [
    {"Route": "TD2", "Description": "270K Middle East Gulf to Singapore", "Worldscale": 78.00, "TCE": 60_328, "Change (TCE)": 183, "OPEX": 8_080},
    {"Route": "TD3C", "Description": "270K Middle East Gulf to China (VLCC)", "Worldscale": 77.15, "TCE": 57_589, "Change (TCE)": 698, "OPEX": 8_080},
    {"Route": "TD6", "Description": "135K Black Sea to Mediterranean (Suezmax)", "Worldscale": 90.10, "TCE": 28_351, "Change (TCE)": 645, "OPEX": 7_321},
    {"Route": "TD7", "Description": "80K North Sea to Continent (Aframax)", "Worldscale": 110.00, "TCE": 20_317, "Change (TCE)": 1_294, "OPEX": 7_030},
    {"Route": "TD8", "Description": "80K Kuwait to Singapore", "Worldscale": 138.21, "TCE": 28_217, "Change (TCE)": 2_098, "OPEX": 7_030},
    {"Route": "TD9", "Description": "70K Caribbean to US Gulf (LR1)", "Worldscale": 131.56, "TCE": 22_821, "Change (TCE)": -2_063, "OPEX": 6_876},
    {"Route": "TD15", "Description": "260K West Africa to China (VLCC)", "Worldscale": 77.39, "TCE": 57_966, "Change (TCE)": 1_591, "OPEX": 8_080},
    {"Route": "TD20", "Description": "130K West Africa to UK-Continent (Suezmax)", "Worldscale": 85.67, "TCE": 32_492, "Change (TCE)": 125, "OPEX": 7_321},
    {"Route": "TD22", "Description": "270K US Gulf to China", "Worldscale": 6_820_000.00, "TCE": 29_834, "Change (TCE)": 2_399, "OPEX": 8_080},
    {"Route": "TD25", "Description": "70K US Gulf to UK-Continent", "Worldscale": 130.28, "TCE": 27_378, "Change (TCE)": -1_394, "OPEX": 7_030},
    {"Route": "TD27", "Description": "130K Guyana to ARA", "Worldscale": 79.33, "TCE": 28_226, "Change (TCE)": 162, "OPEX": 7_321},
    {"Route": "TC5", "Description": "55K CPP Middle East Gulf to Japan (LR1)", "Worldscale": 172.81, "TCE": 25_786, "Change (TCE)": -141, "OPEX": 6_876},
    {"Route": "TC8", "Description": "65K CPP Middle East Gulf to UK-Continent (LR1)", "Worldscale": 50.33, "TCE": 30_550, "Change (TCE)": -908, "OPEX": 6_876},
    {"Route": "TC12", "Description": "35K Naphtha West Coast India to Japan (MR)", "Worldscale": 160.31, "TCE": 13_201, "Change (TCE)": 236, "OPEX": 6_876},
    {"Route": "TC15", "Description": "80K Naphtha Mediterranean to Far East (Aframax)", "Worldscale": 3_094_167, "TCE": 8_946, "Change (TCE)": -605, "OPEX": 7_030},
    {"Route": "TC16", "Description": "60K ARA to Offshore Lome (LR1)", "Worldscale": 114.72, "TCE": 17_103, "Change (TCE)": 152, "OPEX": 6_876},
    {"Route": "TC17", "Description": "35K CPP Jubail to Dar es Salaam (MR)", "Worldscale": 216.07, "TCE": 20_319, "Change (TCE)": 777, "OPEX": 6_876},
    {"Route": "TC18", "Description": "37K CPP US Gulf to Brazil (MR)", "Worldscale": 185.00, "TCE": 20_728, "Change (TCE)": -2_818, "OPEX": 6_876},
    {"Route": "TC19", "Description": "37K CPP Amsterdam to Lagos (MR)", "Worldscale": 199.06, "TCE": 26_023, "Change (TCE)": 55, "OPEX": 6_876},
    {"Route": "TC20", "Description": "90K CPP Middle East Gulf to UK-Continent (Aframax)", "Worldscale": 3_956_250, "TCE": 36_279, "Change (TCE)": 2_492, "OPEX": 7_030},
]




# Update report data with absolute paths
updated_report_data_with_all_routes = {
    "title": "Maritime Per Week",
    "date": "21 01 2025",
    "overview": """
    The tanker market saw dynamic activity this week, with VLCC and Suezmax earnings on Middle East Gulf and West Africa routes experiencing significant gains. Aframax and MR tankers showed steadier movements, supported by balanced demand in the Atlantic and Asia-Pacific regions.

    Key Index Movements: The Baltic Dirty Tanker Index (BDTI) rose 34 points to 855, reflecting robust crude demand. The Baltic Clean Tanker Index (BCTI) gained 11 points to 640, underscoring resilience in clean product markets.

    """,
    "highest_changes": sorted(full_route_data, key=lambda x: x["Change (TCE)"], reverse=True)[:5],
    "remaining_routes": full_route_data,
    "sigc_graphs": [absolute_paths["SI"], absolute_paths["GC"],],
    "bzcl_graphs": [absolute_paths["BZ"], absolute_paths["CL"],],
    "map_image": base64_image,
    }

# Render the HTML
# updated_report_data_with_all_routes["map_image"] = encode_image_to_base64(os.path.abspath(map_image_path))  # Add map image path

template = Template(compact_table_template)
rendered_html = template.render(**updated_report_data_with_all_routes)


# Save to PDF
output_pdf_path = "Maritime_Per_Week_Compact_Tables.pdf"
HTML(string=rendered_html).write_pdf(output_pdf_path)

print(f"PDF generated: {output_pdf_path}")
