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
            line-height: 1.3;
            font-size: 10px;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-top: 5px 0;
            font-size: 20px;
        }
        h2 {
            color: #444;
            border-bottom: 1px solid #ccc;
            margin-top: 10px;
            font-size: 13px;
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
            margin-bottom: 5px;
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
            font-size: 10px;
            margin-top: 3px;
        }
        table, th, td {
            border: 1px solid #;
        }
        th, td {
            padding: 2px;
            text-align: left;
            font-size: 8px;
        }
        th {
            background-color: #f4f4f4;
            font-weight: bold;
            font-size: 10px;
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
            gap: 10px;
            margin: 5px 0;
            justify-content: space-around;
            padding: 5px 0;}
        .card {
            flex: 1 1 calc(15% - 8px); /* Adjust width of each card */
            flex-wrap: wrap;
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            text-align: center;
            background-color: #000;
            color: #fff}
        .card h3 {
            font-size: 10px;
            margin-bottom: 4px;
            color: #fff;}
        .card p {
            font-size: 8px;
            margin: 3px 0;
            color: #ccc;}
        .card strong {
            font-size: 10px;
            color: #fff;}
</style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p style="text-align: left; font-size: 10px; font-weight: bold;">22 January 2025 </p>

    <div class="section">
        <div class="text">
            <p><strong>Capacity & Impact:</strong> The <strong>Dangote Refinery</strong>, operational since December 2023, is the <strong>largest single-train refinery in the world</strong>, with a capacity of <strong>650,000 barrels per day</strong>. Its production has significantly reduced Nigeria's reliance on <strong>imported refined products</strong>, particularly gasoline from Europe. This shift is <strong>disrupting traditional gasoline trade routes</strong> and challenging long-established suppliers.</p>

            <p><strong>Foreign Exchange & Export Earnings:</strong> Reducing refined product imports, the country can <strong>conserve foreign exchange</strong>. Additionally, with <strong>domestic demand met</strong>, Nigeria is positioned to export refined products, <strong>stabilizing the naira</strong> in the process.</p>

            <p><strong>Strategic Expansion:</strong> Ongoing crude oil supply constraints due to limited availability from NNPC contributed to the construction of <strong>6.3 million liters of additional storage capacity</strong>. Nigeria’s crude production has recovered from <strong>931k bpd in 2022</strong> to <strong>1.5 million bpd in 2024</strong>, with the potential of <strong>1.8m in 2025</strong>.</p>
            
            <h2 style="text-align: center; margin-top: 20px;">Market Overview</h2>

            <p>The tanker market saw varied activity this week. <strong>VLCC</strong> and <strong>Suezmax</strong> earnings rose on <strong>Middle East Gulf</strong> and <strong>West Africa routes</strong>, while <strong>Aframax</strong> and <strong>MR tankers</strong> remained steady with balanced demand in the <strong>Atlantic</strong> and <strong>Asia-Pacific regions</strong>.</p>

            <p><strong>Key Indices:</strong> The <strong>Baltic Dirty Tanker Index (BDTI)</strong> gained <strong>34 points</strong> to <strong>855</strong>, while the <strong>Baltic Clean Tanker Index (BCTI)</strong> rose <strong>11 points</strong> to <strong>640</strong>. <strong>Sale and purchase activity softened</strong>, <strong>asset and recycling prices declined</strong>, and <strong>bunker prices saw moderate increases</strong> across major hubs. <strong>FFA volumes contracted</strong> in both <strong>clean</strong> and <strong>dirty segments</strong>.</p>

            <table class="routes">
            <h3 style="text-align: center; margin-top: 10px;">Largest changess</h3>
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
        <h3 style="text-align: center; margin-top: 16px;">Dirty Routes</h3>
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
        <h3 style="text-align: center; margin-top: 10px;">Clean Routes</h3>
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
            <h3>Tanker Recycling Index </h3>
            <p><strong>11,437</strong></p>
            <p style="color: red;">-73 &#9660;</p>
        </div>
        <div class="card">
            <h3>Tanker Sale and Purchase Index </h3>
            <p><strong>7,623</strong></p>
            <p style="color: red;">-3 &#9660;</p>
        </div>
        <div class="card">
            <h3>Tanker New Building Index </h3>
            <p><strong>7,753</strong></p>
            <p style="color: red;">-37 &#9660;</p>
        </div>
        
        
        
    </div>
    </div>
    
        <div class="charts">
           <p><strong>Regional & Global Dynamics:</strong> Reduced reliance on gasoline imports will <strong>impact traditional MR flows</strong>. Foreign refineries, especially in Europe, must <strong>explore new markets</strong> for their products, potentially leading to <strong>inventory buildup</strong> and price disruptions.</p>
            <p><strong>Rising Export Demand:</strong> Increased production capacity is <strong>driving regional exports</strong> to the West-African Coast, South Africa, and abroad, boosting demand for <strong>Handysize</strong> and <strong>MR tankers</strong>. This dynamic enhances Nigeria's position as a <strong>regional energy hub</strong>.</p>
            <p><strong>Global Impact:</strong> New export routes will emerge as local refining capacity reduces Nigeria’s <strong>import dependency</strong>. This shift reshapes <strong>global tanker flows</strong>, increases competition in other markets, and more.</p>
            <p><strong>Energy Diversification:</strong> Achieving energy self-sufficiency within the next decade will require transitioning from <strong>petrol (PMS)</strong> to <strong>gas</strong> as the primary energy source, incorporating <strong>renewables</strong>, and leveraging resources like <strong>lithium</strong> for sustainability.</p>
            
            <h2 style="text-align: center; margin-top: 10px;">Global Bunker Prices</h2>
            <img src="data:image/png;base64,{{ map_image }}" 
             alt="Strategic Tanker Routes Map" 
             style="max-width: 100%; height: auto; margin: 20px auto; border: 1px solid #ccc;">

            {% for image in bzcl_graphs %}
                <img src="data:image/png;base64,{{ image }}" 
                    alt="Market Graph" 
                        style="width: 100%; max-width: 600px; max-height: 300px; object-fit: contain; margin: 5px auto; border: 1px solid #ccc;">
        {% endfor %}
        
        </div>
    </div>


    <footer style="text-align: center; font-size: 8px; color: #555; margin-top: px; border-top: 1px solid #ccc; padding-top: 5px;">
        <p>© 2025 Lado Limited. All Rights Reserved.</p>
    </footer>

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
