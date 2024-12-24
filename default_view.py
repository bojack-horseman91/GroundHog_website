<<<<<<< HEAD
import os
import json
from dash import dcc, html, Input, Output
import plotly.io as pio
import pandas as pd
import dash

# Load data
data = pd.read_csv('pseudo_data_with_recharge.csv')
json_dir = "figures_json"

# Set year to 2022
year = 2022

# Preload JSON data for the year 2022 as strings to avoid serialization issues
figures_cache = {
    'max_gwl': open(f"{json_dir}/max_gwl_{year}.json").read(),
    'min_gwl': open(f"{json_dir}/min_gwl_{year}.json").read(),
    'recharge': open(f"{json_dir}/recharge_{year}.json").read()
}

def default_layout():
    return html.Div([
        html.H1("Interactive Ground Water Level Map for the Year 2022", style={"textAlign": "center", "marginBottom": "20px"}),
        html.H3(
            "Click any point to show all the info (Scroll down to see) and you can also download data for that point for all years up to 2022",
            style={"textAlign": "center", "marginBottom": "20px"}
        ),
        dcc.Store(id='figures-cache', data=figures_cache),  # Store JSON strings
        html.Div(
            id='click-info',
            style={
                "padding": "10px",
                "fontSize": "16px",
                "margin": "20px auto",
                "maxWidth": "800px",
                "textAlign": "center"
            }
        ),
        html.Button(
            "Download Data for all years up to 2022",
            id="download-button",
            disabled=True,  # Initially disabled
            style={
                "display": "block",
                "padding": "10px",
                # "color": "#fff",
                # "backgroundColor": "#007BFF",
                "border": "none",
                "borderRadius": "5px",
                "marginTop": "10px",
                "marginLeft": "auto",
                "marginRight": "auto"
            }
        ),
        dcc.Loading(
            type="default",
            children=html.Div(
                [
                    dcc.Graph(id='max-gwl-plot', style={"flex": "1 1 300px", "minWidth": "300px"}),
                    dcc.Graph(id='min-gwl-plot', style={"flex": "1 1 300px", "minWidth": "300px"}),
                    dcc.Graph(id='recharge-plot', style={"flex": "1 1 300px", "minWidth": "300px"})
                ],
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "10px",
                    "justifyContent": "center",
                    "padding": "10px",
                    "marginTop": "5px"
                }
            )
        ),
        dcc.Download(id='point-data-download')  # Add the download component
    ], style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "padding": "10px",
        "margin": "0 auto",
        "maxWidth": "1200px"
    })


def register_default_callbacks(app):
    @app.callback(
        [Output('max-gwl-plot', 'figure'), Output('min-gwl-plot', 'figure'), Output('recharge-plot', 'figure')],
        [Input('figures-cache', 'data')]
    )
    def update_plots(figures_cache):
        # Load figures from JSON strings
        max_gwl_fig = pio.from_json(figures_cache.get('max_gwl'))
        min_gwl_fig = pio.from_json(figures_cache.get('min_gwl'))
        recharge_fig = pio.from_json(figures_cache.get('recharge'))

        # Add POINT_X and POINT_Y to hover data directly
        max_gwl_fig.update_traces(hovertemplate="Latitude (POINT_X): %{x}<br>Longitude (POINT_Y): %{y}<br>")
        min_gwl_fig.update_traces(hovertemplate="Latitude (POINT_X): %{x}<br>Longitude (POINT_Y): %{y}<br>")
        recharge_fig.update_traces(hovertemplate="Latitude (POINT_X): %{x}<br>Longitude (POINT_Y): %{y}<br>")

        return max_gwl_fig, min_gwl_fig, recharge_fig

    @app.callback(
        [Output('click-info', 'children'), Output('download-button', 'disabled')],
        [Input('max-gwl-plot', 'clickData'), Input('min-gwl-plot', 'clickData'), Input('recharge-plot', 'clickData')]
    )
    def display_click_data_and_enable_button(max_click_data, min_click_data, recharge_click_data):
        click_data = max_click_data or min_click_data or recharge_click_data
        if click_data:
            point = click_data['points'][0]
            idx = point['pointIndex']
            max_gwl = data.iloc[idx]['Max_GWL']
            min_gwl = data.iloc[idx]['Min_GWL']
            recharge = data.iloc[idx]['recharge']
            point_x = data.iloc[idx]['POINT_X']
            point_y = data.iloc[idx]['POINT_Y']

            # Render click info
            click_info = html.Div(
                [
                    html.H2("Click Data Details", style={"marginBottom": "2px", "color": "#2C3E50"}),
                    html.Div(f"Max GWL: {max_gwl:.2f} m", style={"marginBottom": "5px"}),
                    html.Div(f"Min GWL: {min_gwl:.2f} m", style={"marginBottom": "5px"}),
                    html.Div(f"Recharge: {recharge:.2f} cm", style={"marginBottom": "5px"}),
                    html.Div(f"Latitude: {point_y:.2f} m", style={"marginBottom": "5px"}),
                    html.Div(f"Longitude: {point_x:.2f} m", style={"marginBottom": "5px"}),
                ],
                style={
                    "padding": "10px",
                    "border": "1px solid #ddd",
                    "borderRadius": "7px",
                    "backgroundColor": "#fff8dc",
                    "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
                    "textAlign": "center",
                    "width": "100%"
                }
            )
            return click_info, False  # Enable the button
        return html.Div("Click on a point to see Max GWL, Min GWL, and Recharge.", style={"padding": "2px"}), True

    @app.callback(
        Output('point-data-download', 'data'),
        [Input('download-button', 'n_clicks')],
        [Input('max-gwl-plot', 'clickData'), Input('min-gwl-plot', 'clickData'), Input('recharge-plot', 'clickData')]
    )
    def download_point_data(n_clicks, max_click_data, min_click_data, recharge_click_data):
        if n_clicks:
            click_data = max_click_data or min_click_data or recharge_click_data
            if click_data:
                point = click_data['points'][0]
                idx = point['pointIndex']
                point_x = data.iloc[idx]['POINT_X']
                point_y = data.iloc[idx]['POINT_Y']
                point_data = data[(data.POINT_X == point_x) & (data.POINT_Y == point_y)][['Max_GWL', 'Min_GWL', 'recharge', 'Year']]
                return dcc.send_data_frame(point_data.to_csv, f"data_for_lat_{point_y:.2f}_long_{point_x:.2f}.csv")
        return dash.no_update
=======
import os
import json
from dash import dcc, html, Input, Output
import plotly.io as pio
import pandas as pd
import dash

# Load data
data = pd.read_csv('pseudo_data_with_recharge.csv')
json_dir = "figures_json"

# Set year to 2022
year = 2022

# Preload JSON data for the year 2022 as strings to avoid serialization issues
figures_cache = {
    'max_gwl': open(f"{json_dir}/max_gwl_{year}.json").read(),
    'min_gwl': open(f"{json_dir}/min_gwl_{year}.json").read(),
    'recharge': open(f"{json_dir}/recharge_{year}.json").read()
}

def default_layout():
    return html.Div([
        html.H1("Interactive Ground Water Level Map for the Year 2022", style={"textAlign": "center", "marginBottom": "20px"}),
        html.H3(
            "Click any point to show all the info (Scroll down to see) and you can also download data for that point for all years up to 2022",
            style={"textAlign": "center", "marginBottom": "20px"}
        ),
        dcc.Store(id='figures-cache', data=figures_cache),  # Store JSON strings
        html.Div(
            id='click-info',
            style={
                "padding": "10px",
                "fontSize": "16px",
                "margin": "20px auto",
                "maxWidth": "800px",
                "textAlign": "center"
            }
        ),
        html.Button(
            "Download Data for all years up to 2022",
            id="download-button",
            disabled=True,  # Initially disabled
            style={
                "display": "block",
                "padding": "10px",
                # "color": "#fff",
                # "backgroundColor": "#007BFF",
                "border": "none",
                "borderRadius": "5px",
                "marginTop": "10px",
                "marginLeft": "auto",
                "marginRight": "auto"
            }
        ),
        dcc.Loading(
            type="default",
            children=html.Div(
                [
                    dcc.Graph(id='max-gwl-plot', style={"flex": "1 1 300px", "minWidth": "300px"}),
                    dcc.Graph(id='min-gwl-plot', style={"flex": "1 1 300px", "minWidth": "300px"}),
                    dcc.Graph(id='recharge-plot', style={"flex": "1 1 300px", "minWidth": "300px"})
                ],
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "10px",
                    "justifyContent": "center",
                    "padding": "10px",
                    "marginTop": "5px"
                }
            )
        ),
        dcc.Download(id='point-data-download')  # Add the download component
    ], style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "padding": "10px",
        "margin": "0 auto",
        "maxWidth": "1200px"
    })


def register_default_callbacks(app):
    @app.callback(
        [Output('max-gwl-plot', 'figure'), Output('min-gwl-plot', 'figure'), Output('recharge-plot', 'figure')],
        [Input('figures-cache', 'data')]
    )
    def update_plots(figures_cache):
        # Load figures from JSON strings
        max_gwl_fig = pio.from_json(figures_cache.get('max_gwl'))
        min_gwl_fig = pio.from_json(figures_cache.get('min_gwl'))
        recharge_fig = pio.from_json(figures_cache.get('recharge'))

        # Add POINT_X and POINT_Y to hover data directly
        max_gwl_fig.update_traces(hovertemplate="Latitude (POINT_X): %{x}<br>Longitude (POINT_Y): %{y}<br>")
        min_gwl_fig.update_traces(hovertemplate="Latitude (POINT_X): %{x}<br>Longitude (POINT_Y): %{y}<br>")
        recharge_fig.update_traces(hovertemplate="Latitude (POINT_X): %{x}<br>Longitude (POINT_Y): %{y}<br>")

        return max_gwl_fig, min_gwl_fig, recharge_fig

    @app.callback(
        [Output('click-info', 'children'), Output('download-button', 'disabled')],
        [Input('max-gwl-plot', 'clickData'), Input('min-gwl-plot', 'clickData'), Input('recharge-plot', 'clickData')]
    )
    def display_click_data_and_enable_button(max_click_data, min_click_data, recharge_click_data):
        click_data = max_click_data or min_click_data or recharge_click_data
        if click_data:
            point = click_data['points'][0]
            idx = point['pointIndex']
            max_gwl = data.iloc[idx]['Max_GWL']
            min_gwl = data.iloc[idx]['Min_GWL']
            recharge = data.iloc[idx]['recharge']
            point_x = data.iloc[idx]['POINT_X']
            point_y = data.iloc[idx]['POINT_Y']

            # Render click info
            click_info = html.Div(
                [
                    html.H2("Click Data Details", style={"marginBottom": "2px", "color": "#2C3E50"}),
                    html.Div(f"Max GWL: {max_gwl:.2f} m", style={"marginBottom": "5px"}),
                    html.Div(f"Min GWL: {min_gwl:.2f} m", style={"marginBottom": "5px"}),
                    html.Div(f"Recharge: {recharge:.2f} cm", style={"marginBottom": "5px"}),
                    html.Div(f"Latitude: {point_y:.2f} m", style={"marginBottom": "5px"}),
                    html.Div(f"Longitude: {point_x:.2f} m", style={"marginBottom": "5px"}),
                ],
                style={
                    "padding": "10px",
                    "border": "1px solid #ddd",
                    "borderRadius": "7px",
                    "backgroundColor": "#fff8dc",
                    "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
                    "textAlign": "center",
                    "width": "100%"
                }
            )
            return click_info, False  # Enable the button
        return html.Div("Click on a point to see Max GWL, Min GWL, and Recharge.", style={"padding": "2px"}), True

    @app.callback(
        Output('point-data-download', 'data'),
        [Input('download-button', 'n_clicks')],
        [Input('max-gwl-plot', 'clickData'), Input('min-gwl-plot', 'clickData'), Input('recharge-plot', 'clickData')]
    )
    def download_point_data(n_clicks, max_click_data, min_click_data, recharge_click_data):
        if n_clicks:
            click_data = max_click_data or min_click_data or recharge_click_data
            if click_data:
                point = click_data['points'][0]
                idx = point['pointIndex']
                point_x = data.iloc[idx]['POINT_X']
                point_y = data.iloc[idx]['POINT_Y']
                point_data = data[(data.POINT_X == point_x) & (data.POINT_Y == point_y)][['Max_GWL', 'Min_GWL', 'recharge', 'Year']]
                return dcc.send_data_frame(point_data.to_csv, f"data_for_lat_{point_y:.2f}_long_{point_x:.2f}.csv")
        return dash.no_update
>>>>>>> b0f3c7981bcd8173c0b97e07af51a9bb6efb166b
