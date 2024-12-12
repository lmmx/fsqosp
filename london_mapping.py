import folium
import polars as pl
from folium.plugins import MarkerCluster
from IPython.display import HTML, display
from ipywidgets import Dropdown, Output, Text, VBox, interact

from london_analysis import load_london_places, load_places_geojson


def make_markers(places: pl.DataFrame) -> folium.GeoJson:
    return folium.GeoJsonTooltip(
        fields=list(places.columns),  # Display the "name" property on hover
        aliases=[
            k.title().replace("Po_", "PO_").replace("_", " ") for k in places.columns
        ],
    )


# Load and preprocess the data
london_places = load_london_places().select(pl.exclude("geom", "bbox"))

# Outputs for the map and the DataFrame
map_output = Output()
df_output = Output()


# Function to update both map and DataFrame
def update_map_and_df(category):
    with map_output:
        map_output.clear_output()  # Clear previous map
        m = folium.Map(location=[51.5, -0.06], zoom_start=12)

        cat_col = pl.col("fsq_category_labels")
        if category == "None":
            mask = cat_col.is_null()
        else:
            mask = cat_col.list.contains(category)
        filtered_places = london_places.filter(mask)

        # Display filtered places count
        print(f"{len(filtered_places):,} places")

        filtered_geojson = load_places_geojson(filtered_places)
        folium.GeoJson(
            filtered_geojson,
            name="Filtered London Places",
            tooltip=make_markers(filtered_places),
        ).add_to(m)
        display(m)  # Display map in the output widget

    with df_output:
        df_output.clear_output()  # Clear previous DataFrame
        display(HTML(filtered_places.to_pandas().to_html(index=False)))


# Create a list of unique categories
unique_categories = (
    london_places["fsq_category_labels"]
    .explode()
    .unique()
    .sort()
    .fill_null("None")
    .to_list()
)

# Create a text input widget for searching categories
search_box = Text(
    placeholder="Type to search...", description="Search:", continuous_update=True
)


# Function to filter categories based on search input
def filter_categories(change):
    search_text = change["new"].lower()
    filtered_options = [cat for cat in unique_categories if search_text in cat.lower()]
    category_dropdown.options = filtered_options


# Create a dropdown widget to select categories
category_dropdown = Dropdown(
    options=unique_categories,
    description="Category:",
    value=unique_categories[1],  # Default value
)

# Attach the filter function to the search box input
search_box.observe(filter_categories, names="value")

# Interactive widget for map and DataFrame
interact(update_map_and_df, category=category_dropdown)

# Arrange widgets and outputs in a layout
ui = VBox([search_box, category_dropdown, VBox([map_output, df_output])])

# Display the UI
display(ui)
