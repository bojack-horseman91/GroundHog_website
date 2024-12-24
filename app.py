import dash 
from dash import dcc, html
from default_view import default_layout, register_default_callbacks
from upload_view import upload_layout, register_upload_callbacks
from image_view import image_layout, register_image_callbacks  # Import the new image view

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the navbar
def navbar():
    return html.Div(
        [
            html.Div(
                [
                   # Groundhog icon (image served from assets/images folder)
                    html.Img(
                        src="/assets/images/groundhog.jpg",  # Path to the local image
                        alt="Groundhog Icon",
                        style={
                            "height": "50px",
                            "width": "50px",
                            "marginRight": "10px",
                            "borderRadius": "50%",
                        },
                    ),

                    html.Div(
                        [
                            html.H1(
                                "GroundHog",
                                style={
                                    "margin": "0",
                                    "fontSize": "44px",
                                    "color": "#2C3E50",
                                },
                            ),
                            html.P(
                                "Revolutionizing Groundwater Downscaling",
                                style={
                                    "margin": "0",
                                    "fontSize": "14px",
                                    "color": "#7F8C8D",
                                },
                            ),
                        ],
                        style={"display": "flex", "flexDirection": "column"},
                    ),
                ],
                style={"display": "flex", "alignItems": "center"},
            )
        ],
        style={
            "padding": "10px",
            "backgroundColor": "#ECF0F1",
            "borderBottom": "1px solid #BDC3C7",
            "display": "flex",
            "justifyContent": "center",
        },
    )

# Define app layout
app.layout = html.Div([
    navbar(),  # Add the navbar
    dcc.Tabs([
        dcc.Tab(label='Default View', children=default_layout()),
        dcc.Tab(label='Upload GLDAS to Model to downscale', children=upload_layout()),
        dcc.Tab(label='Image of downscaled GLDAS data', children=image_layout())  # Add the image view tab
    ])
])

# Register callbacks
register_default_callbacks(app)
register_upload_callbacks(app)
register_image_callbacks(app)  # Register image callbacks

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
