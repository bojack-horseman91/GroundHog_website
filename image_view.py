<<<<<<< HEAD
import dash
from dash import dcc, html
import os

# Function to list all image files for each year
def get_image_options(years):
    images = {}
    for year in years:
        images[year] = [
            {"label": f"Max GWL ({year})", "value": f"Upsampled_GWL/Upsample Max GWL (BGL) for the year {year} (meters).png"},
            {"label": f"Min GWL ({year})", "value": f"Upsampled_GWL/Upsample Min GWL (BGL) for the year {year} (meters).png"},
            {"label": f"Recharge ({year})", "value": f"Upsampled_Recharge/Upsample Recharge for the year {year} (centimeters).png"},
        ]
    return images

# List of years available for images
years = [str(year) for year in range(2003, 2023)]
image_options = get_image_options(years)

# Define the layout for the image view
def image_layout():
    return html.Div([
        html.H1("Yearly Ground Water Level Images", style={"textAlign": "center"}),
        dcc.Dropdown(
            id='image-year-dropdown',
            options=[{"label": year, "value": year} for year in years],
            value=years[0],
            clearable=False,
            style={"width": "50%", "margin": "0 auto"}
        ),
        html.Div(id='image-container', style={"textAlign": "center", "margin": "20px"}),
        dcc.Store(id='image-path-store')  # Store the image path
    ])

# Register callbacks to update the images based on dropdown selections
def register_image_callbacks(app):
    @app.callback(
        dash.dependencies.Output('image-container', 'children'),
        dash.dependencies.Input('image-year-dropdown', 'value')
    )
    def update_images(selected_year):
        # Create image paths for the selected year
        max_gwl_path = os.path.join("assets/figures_images", f"Upsampled_GWL/Upsample Max GWL (BGL) for the year {selected_year} (meters).png")
        min_gwl_path = os.path.join("assets/figures_images", f"Upsampled_GWL/Upsample Min GWL (BGL) for the year {selected_year} (meters).png")
        recharge_path = os.path.join("assets/figures_images", f"Upsampled_Recharge/Upsample Recharge for the year {selected_year} (centimeters).png")

        # Create a layout to display images side by side
        return html.Div(style={'display': 'flex', 'justifyContent': 'center'}, children=[
            html.Div(children=[
                html.H4(f"Max GWL ({selected_year})"),
                html.Img(src=max_gwl_path, style={"width": "100%", "height": "auto", "borderRadius": "10px"})
            ]),
            html.Div(children=[
                html.H4(f"Min GWL ({selected_year})"),
                html.Img(src=min_gwl_path, style={"width": "100%", "height": "auto", "borderRadius": "10px"})
            ]),
            html.Div(children=[
                html.H4(f"Recharge ({selected_year})"),
                html.Img(src=recharge_path, style={"width": "100%", "height": "auto", "borderRadius": "10px"})
            ])
        ])

# Create the Dash app
app = dash.Dash(__name__)

# Set the layout and register callbacks
app.layout = image_layout()
register_image_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
=======
import dash
from dash import dcc, html
import os

# Function to list all image files for each year
def get_image_options(years):
    images = {}
    for year in years:
        images[year] = [
            {"label": f"Max GWL ({year})", "value": f"Upsampled_GWL/Upsample Max GWL (BGL) for the year {year} (meters).png"},
            {"label": f"Min GWL ({year})", "value": f"Upsampled_GWL/Upsample Min GWL (BGL) for the year {year} (meters).png"},
            {"label": f"Recharge ({year})", "value": f"Upsampled_Recharge/Upsample Recharge for the year {year} (centimeters).png"},
        ]
    return images

# List of years available for images
years = [str(year) for year in range(2003, 2023)]
image_options = get_image_options(years)

# Define the layout for the image view
def image_layout():
    return html.Div([
        html.H1("Yearly Ground Water Level Images", style={"textAlign": "center"}),
        dcc.Dropdown(
            id='image-year-dropdown',
            options=[{"label": year, "value": year} for year in years],
            value=years[0],
            clearable=False,
            style={"width": "50%", "margin": "0 auto"}
        ),
        html.Div(id='image-container', style={"textAlign": "center", "margin": "20px"}),
        dcc.Store(id='image-path-store')  # Store the image path
    ])

# Register callbacks to update the images based on dropdown selections
def register_image_callbacks(app):
    @app.callback(
        dash.dependencies.Output('image-container', 'children'),
        dash.dependencies.Input('image-year-dropdown', 'value')
    )
    def update_images(selected_year):
        # Create image paths for the selected year
        max_gwl_path = os.path.join("assets/figures_images", f"Upsampled_GWL/Upsample Max GWL (BGL) for the year {selected_year} (meters).png")
        min_gwl_path = os.path.join("assets/figures_images", f"Upsampled_GWL/Upsample Min GWL (BGL) for the year {selected_year} (meters).png")
        recharge_path = os.path.join("assets/figures_images", f"Upsampled_Recharge/Upsample Recharge for the year {selected_year} (centimeters).png")

        # Create a layout to display images side by side
        return html.Div(style={'display': 'flex', 'justifyContent': 'center'}, children=[
            html.Div(children=[
                html.H4(f"Max GWL ({selected_year})"),
                html.Img(src=max_gwl_path, style={"width": "100%", "height": "auto", "borderRadius": "10px"})
            ]),
            html.Div(children=[
                html.H4(f"Min GWL ({selected_year})"),
                html.Img(src=min_gwl_path, style={"width": "100%", "height": "auto", "borderRadius": "10px"})
            ]),
            html.Div(children=[
                html.H4(f"Recharge ({selected_year})"),
                html.Img(src=recharge_path, style={"width": "100%", "height": "auto", "borderRadius": "10px"})
            ])
        ])

# Create the Dash app
app = dash.Dash(__name__)

# Set the layout and register callbacks
app.layout = image_layout()
register_image_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
>>>>>>> b0f3c7981bcd8173c0b97e07af51a9bb6efb166b
