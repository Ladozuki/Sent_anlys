import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

def create_fuel_prices_map(output_file="fuel_prices_map.png"):
    # Create a figure and axis for the map
    fig, ax = plt.subplots(figsize=(20, 14))  # Increased figure size for better clarity

    # Initialize Basemap for a world map
    m = Basemap(projection='mill', resolution='l', llcrnrlat=-60, urcrnrlat=80, llcrnrlon=-180, urcrnrlon=180, ax=ax)
    m.drawcoastlines(color="white", linewidth=0.5)
    m.drawcountries(color="gray", linewidth=0.5)
    m.fillcontinents(color='#6c757d', lake_color='#d4e4f7')
    m.drawmapboundary(fill_color='#d4e4f7')

    # Fuel prices for key locations
    fuel_prices = {
        "Fujairah": {"lat": 25.1, "lon": 56.3, "prices": {"HSFO": 488, "MGO": 795, "VLSFO": 594}},
        "Houston": {"lat": 29.76, "lon": -95.37, "prices": {"HSFO": 492, "MGO": 768, "VLSFO": 600}},
        "Rotterdam": {"lat": 51.92, "lon": 4.47, "prices": {"HSFO": 471, "MGO": 714, "VLSFO": 549}},
        "Singapore": {"lat": 1.29, "lon": 103.85, "prices": {"HSFO": 517, "MGO": 743, "VLSFO": 606}},
    }

    # Annotate fuel prices at their respective locations
    for location, details in fuel_prices.items():
        lat, lon = details["lat"], details["lon"]
        x, y = m(lon, lat)
        m.plot(x, y, 'o', markersize=15, color='red', alpha=0.9)  # Increased marker size
        prices_text = "\n".join([f"{key}: ${value}/mt" for key, value in details["prices"].items()])
        plt.text(
            x, y, f"{location}\n{prices_text}", fontsize=16, color="black", ha="left", va="bottom",
            bbox=dict(facecolor="white", alpha=0.85, edgecolor="black", linewidth=3, boxstyle="round,pad=1.2")
        )

    # Add a title and styling
    plt.title("Global Fuel Prices by Location (January 2025)", fontsize=16, color="black", pad=24)
    ax.set_facecolor("#f5f5f5")

    # Save the map as an image file
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

# Call the function to create and save the map
if __name__ == "__main__":
    create_fuel_prices_map()
