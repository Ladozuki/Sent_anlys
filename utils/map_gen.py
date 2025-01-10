import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

def create_tanker_routes_map(output_file="tanker_routes_map.png"):
    # Create a figure and axis for the map
    fig, ax = plt.subplots(figsize=(15, 10))

    # Initialize Basemap for a world map
    m = Basemap(projection='mill', resolution='c', llcrnrlat=-60, urcrnrlat=80, llcrnrlon=-180, urcrnrlon=180, ax=ax)
    m.drawcoastlines(color="white")
    m.drawcountries(color="white")
    m.fillcontinents(color='#2B3E50', lake_color='#1B2B34')
    m.drawmapboundary(fill_color='#1B2B34')

    # Add strategic route labels
    region_labels = {
        "Gulf of Guinea": (3.37, 5.52),
        "Black Sea": (28.75, 44.6),
        "North Sea": (4.2, 56.2),
        "Caribbean": (-61.22, 10.69),
        "Middle East": (50.58, 26.2),
        "East Africa": (39.2, -6.79),
    }

    for label, (lon, lat) in region_labels.items():
        x, y = m(lon, lat)
        plt.text(
            x, y, label, fontsize=10, color="white", ha="center",
            bbox=dict(facecolor="black", alpha=0.5, edgecolor="none")
        )

    # Add key ports and regions
    key_ports = {
        "Rotterdam": (4.47, 51.92),
        "Singapore": (103.85, 1.29),
        "Lagos": (3.38, 6.45),
        "Dar es Salaam": (39.28, -6.8),
        "Houston": (-95.37, 29.76),
    }

    for port, (lon, lat) in key_ports.items():
        x, y = m(lon, lat)
        m.plot(x, y, 'o', markersize=5, color='red', label="Key Port" if port == "Rotterdam" else "")  # Avoid duplicate labels
        plt.text(
            x, y, port, fontsize=8, color="yellow", ha="left", va="bottom",
            bbox=dict(facecolor="black", alpha=0.5, edgecolor="none")
        )

    # Annotate routes
    route_annotations = {
        "TC12": ["Naphtha exports", (78.96, 20.59), (139.69, 35.68)],
        "TD15": ["Nigeria crude to China", (3.37, 6.52), (116.40, 39.90)],
        "TD20": ["Bonny crude exports", (3.37, 6.52), (4.90, 52.37)],
    }

    for route, (desc, start, end) in route_annotations.items():
        x_start, y_start = m(start[0], start[1])
        x_end, y_end = m(end[0], end[1])
        mid_x, mid_y = (x_start + x_end) / 2, (y_start + y_end) / 2  # Midpoint for annotation
        plt.text(
            mid_x, mid_y, desc, fontsize=8, color="white", ha="center",
            bbox=dict(facecolor="black", alpha=0.7, edgecolor="none")
        )

    # Add a compass rose
    plt.text(
        0.92, 0.85, 'N', transform=ax.transAxes, fontsize=12, color="white", ha="center",
        bbox=dict(facecolor="black", alpha=0.5, edgecolor="none")
    )
    plt.arrow(0.92, 0.8, 0, 0.05, transform=ax.transAxes, color="white", head_width=0.02)

    # Add a scale bar
    scale_length = 5000  # Scale in km
    scale_x, scale_y = m(-170, -50)  # Bottom left corner
    m.drawmapscale(
        -170, -50, -170, -50, scale_length, barstyle='fancy', units='km',
        fontsize=8, yoffset=20, labelstyle='simple', fillcolor1='white', fillcolor2='black'
    )

    # Title and styling
    plt.title("Enhanced Strategic Tanker Routes", fontsize=16, color="white", pad=20)
    ax.set_facecolor("#1B2B34")

    # Save the map as an image file
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor="#1B2B34")
    plt.close()

# Call the function to create and save the map
if __name__ == "__main__":
    create_tanker_routes_map()
