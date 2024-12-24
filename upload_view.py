<<<<<<< HEAD
import base64
import io
import pandas as pd
import numpy as np
import torch
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from  joblib import load
import dash

# Load necessary model and scaler
fitted_scaler = load('model weights/fitted_scaler.pkl')
standard_scaler = load('model weights/standard_scaler.pkl')
rf_model = load('model weights/upsampling_model.joblib')

test_low=pd.read_csv('test_data/test_gldas_low_res_2008.csv').drop(columns=['Unnamed: 0'])
test_high=pd.read_csv('test_data/test_high_res_data_2008.csv').drop(columns=['Unnamed: 0','Max_GWL'])
# download_data=None
# Define color boundaries and color map
boundaries = [0, 5.3, 7.6, 9.8, 11.3, 15, 20.5, 26, 35.5, 58, 60, 70, 80, 90, 100, 150]
cmap_colors = [
    'blue', '#a8e1e0', '#66c18a', '#3b7a3d', '#f3d5a4', '#b299ca',
    '#e4a6a3', '#d35d60', '#a0322e', '#330e0f', '#4f4d4d', '#7d7b7b',
    '#a9a8a8', '#c2c0c0', '#dbdbdb', 'black'
]

# Function to assign colors based on boundaries
# Corrected function to assign colors based on boundaries
def get_discrete_color(val):
    for i in range(len(boundaries) - 1):
        # Check if value is within the current interval
        if boundaries[i] <= val < boundaries[i + 1]:
            return cmap_colors[i]
    # Assign last color if value is beyond final boundary
    return cmap_colors[-1]


# Layout for upload view
# Layout for upload view with dataset instructions
# Updated layout for upload view with spinners
def upload_layout():
    return html.Div([
        dcc.Store(id='prediction-data'),
        dcc.Download(id='download-prediction'),
        html.H1("Upload your low resolution (GLDAS Data) and High resolution data (ArcGIS) to our model to get downscaled results "),
        # Dataset instructions and upload buttons
        html.Div([
            html.H2("Please follow these Dataset Requirements:"),
            html.Ul([
                html.Li("Both High-Res and Low-Res CSVs must have the column 'GLDAS_SerialID' for merging."),
                html.Li("Both datasets must have the column 'Year' to ensure temporal alignment."),
                html.Li("High-Res dataset must include: "
                        f"{', '.join(test_high.columns)}."),
                html.Li("Low-Res dataset must include: "
                        f"{', '.join(test_low.columns)}."),
                html.Li("POINT_X is the longitude and POINT_Y is the latitude"),
                html.Li("The categorical columns are 'lithology' and 'lithology_MAJORITY'."),
                html.Li("Numerical columns should not contain missing (NaN) values."),
                html.Li("Categorical columns should not contain unexpected or invalid categories."),
            ]),
        ], style={'marginBottom': '20px'}),
        html.Div(
            [
                dcc.Upload(
                    id='upload-high-res',
                    children=html.Button(
                        'Upload High-Res CSV',
                        style={'background-color': '#4CAF50', 'color': 'white', 'padding': '10px 20px',
                               'border': 'none', 'border-radius': '5px', 'cursor': 'pointer', 'font-size': '16px'}
                    )
                ),
                dcc.Upload(
                    id='upload-low-res',
                    children=html.Button(
                        'Upload Low-Res CSV',
                        style={'background-color': '#2196F3', 'color': 'white', 'padding': '10px 20px',
                               'border': 'none', 'border-radius': '5px', 'cursor': 'pointer', 'font-size': '16px'}
                    )
                )
            ],
            style={'display': 'flex', 'justify-content': 'center', 'gap': '20px', 'margin': '20px 0'}
        ),
        html.Div(
            html.Button(
                'Show Min/Max GWL and Recharge',
                id='process-button',
                disabled=True,
                style={'padding': '10px 20px', 'fontSize': '16px', 'borderRadius': '5px', 'textAlign': 'center'}
            ),
            style={'display': 'flex', 'justify-content': 'center'}
        ),
        html.Div(id='upload-info'),
        html.Div(id='process-info'),

        # Graphs with spinners
        html.Div([
            dcc.Loading(
                id="loading-max-gwl",
                type="circle",
                children=dcc.Graph(id='max-gwl-plot-upload', style={'width': '450px', 'height': '600px'})
            ),
            dcc.Loading(
                id="loading-min-gwl",
                type="circle",
                children=dcc.Graph(id='min-gwl-plot-upload', style={'width': '450px', 'height': '600px'})
            ),
            dcc.Loading(
                id="loading-recharge",
                type="circle",
                children=dcc.Graph(id='recharge-plot-upload', style={'width': '450px', 'height': '600px'})
            )
        ], style={'display': 'flex', 'gap': '10px'}),
        html.Div(id='click-info-upload', style={'padding': '10px', 'fontSize': '16px'}),
        html.Div(
            html.Button(
                'Download Min, Max GWL and Recharge',
                id='download-upsampled-button',
                disabled=True,
                style={'padding': '10px 20px', 'fontSize': '16px', 'borderRadius': '5px', 'textAlign': 'center'}
            ),
            style={'display': 'flex', 'justify-content': 'center'}
        ),
    ])

# No changes to callbacks needed as dcc.Loading automatically wraps the components

# Function to create scatter plot with discrete color coding
# Function to create scatter plot with discrete color coding and color bar legend
def create_discrete_color_plot(data, column, color_title):
    data[f"{column}_color"] = data[column].apply(get_discrete_color)
    fig = go.Figure(go.Scatter(
        x=data['POINT_X'], y=data['POINT_Y'], mode='markers',
        marker=dict(color=data[f"{column}_color"], size=8),
        text=data[column],
        hovertemplate="<br>Longitude: %{x:.2f}<br>Latitude: %{y:.2f}<br>" + color_title + ": %{text:.2f} <extra></extra>"

    ))
    fig.update_layout(
        title=f"{color_title} Map", xaxis_title="Longitude",
        yaxis_title="Latitude", height=600, width=450
    )

    # Add color bar legend
    for i, boundary in enumerate(boundaries[:-1]):
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode='markers',
            marker=dict(size=10, color=cmap_colors[i]),
            legendgroup=color_title,
            showlegend=True,
            name=f"{boundaries[i]} - {boundaries[i+1]} m"
        ))

    return fig

# Callbacks for upload view
def register_upload_callbacks(app):
    app.high_res_data = None
    app.low_res_data = None

    @app.callback(
        Output('upload-info', 'children'),
        Output('process-button', 'disabled'),  # Enable process button when both files are uploaded
        Input('upload-high-res', 'contents'),
        State('upload-high-res', 'filename'),
        prevent_initial_call=True
    )
    def upload_high_res(contents, filename):
        if contents:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            app.high_res_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            
            # Store the non-normalized Sy column
            app.high_res_data['original_Sy'] = app.high_res_data['Sy']
            
            # Apply scaling to numerical features (excluding Sy)
            app.high_res_data[fitted_scaler.feature_names_in_] = fitted_scaler.transform(app.high_res_data[fitted_scaler.feature_names_in_])
            process_button_disabled = app.low_res_data is None  # Disable until both files are uploaded
            return f"High-Res file '{filename}' uploaded and scaled successfully.", process_button_disabled
        return "No High-Res file uploaded.", True

    @app.callback(
        Output('upload-info', 'children', allow_duplicate=True),
        Output('process-button', 'disabled', allow_duplicate=True),
        Input('upload-low-res', 'contents'),
        State('upload-low-res', 'filename'),
        prevent_initial_call=True
    )
    def upload_low_res(contents, filename):
        if contents:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            app.low_res_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            
            process_button_disabled = app.high_res_data is None  # Disable until both files are uploaded
            return f"Low-Res file '{filename}' uploaded successfully.", process_button_disabled
        return "No Low-Res file uploaded.", True
    @app.callback(
        Output('download-prediction', 'data'),
        Input('download-upsampled-button', 'n_clicks'),
        State('prediction-data', 'data'),  # Access the prediction data
        prevent_initial_call=True
    )
    def download_the_prediction(n_clicks, data):
        if n_clicks and data:
            try:
                # Ensure the data is in a format suitable for DataFrame conversion
                df = pd.DataFrame(data)
                return dcc.send_data_frame(df.to_csv, "upsampled.csv", index=False)
            except Exception as e:
                return dash.no_update  # Log the error if needed
        return dash.no_update


    @app.callback(
        Output('process-info', 'children'),
        Output('max-gwl-plot-upload', 'figure'),
        Output('min-gwl-plot-upload', 'figure'),
        Output('recharge-plot-upload', 'figure'),
        Output('download-upsampled-button', 'disabled'),
        Output('prediction-data','data'),
        Input('process-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def process_data(n_clicks):
        if app.high_res_data is not None and app.low_res_data is not None:
            # Merge high- and low-resolution data
            data = app.high_res_data.merge(app.low_res_data, on=['GLDAS_SerialID', 'Year']).rename(columns={'POINT_X_x': 'POINT_X', 'POINT_Y_x': 'POINT_Y'})
            
            # Retrieve the stored original Sy for recharge calculation
            original_sy = data['original_Sy']
            
            # Scale numerical columns
            X_numerical_scaled = standard_scaler.transform(data[standard_scaler.feature_names_in_])
            
            # One-hot encode categorical columns
            X_cat = data[['lithology', 'lithology_MAJORITY']].astype('string')
            X_cat_encoded = pd.get_dummies(X_cat)
            
            # Prepare final input tensor for model
            X_final = torch.tensor(np.hstack([X_numerical_scaled, X_cat_encoded]).astype('float32'))
            
            # Predict Max_GWL and Min_GWL
            pred = rf_model.predict(X_final)
            data['Max_GWL'] = pred[:, 1]
            data['Min_GWL'] = pred[:, 0]

            
            # Calculate recharge using non-normalized Sy
            data['Recharge'] = (data['Max_GWL'].values - data['Min_GWL'].values) * 100 * original_sy.values

            # Generate plots
            max_gwl_fig = create_discrete_color_plot(data, 'Max_GWL', 'Max GWL (m)')
            min_gwl_fig = create_discrete_color_plot(data, 'Min_GWL', 'Min GWL (m)')
            recharge_fig = create_discrete_color_plot(data, 'Recharge', 'Recharge (cm)')
            prediction_data=data[['Min_GWL','Max_GWL','Recharge','POINT_X','POINT_Y']]
            
            
            # Show download link by changing the style to display
            return "Data processed successfully.", max_gwl_fig, min_gwl_fig, recharge_fig, False, prediction_data.to_dict()
        return "Please upload both high-res and low-res files.", None, None, None, None, {'display': 'none'},None
=======
import base64
import io
import pandas as pd
import numpy as np
import torch
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from  joblib import load
import dash

# Load necessary model and scaler
fitted_scaler = load('model weights/fitted_scaler.pkl')
standard_scaler = load('model weights/standard_scaler.pkl')
rf_model = load('model weights/upsampling_model.joblib')

test_low=pd.read_csv('test_data/test_gldas_low_res_2008.csv').drop(columns=['Unnamed: 0'])
test_high=pd.read_csv('test_data/test_high_res_data_2008.csv').drop(columns=['Unnamed: 0','Max_GWL'])
# download_data=None
# Define color boundaries and color map
boundaries = [0, 5.3, 7.6, 9.8, 11.3, 15, 20.5, 26, 35.5, 58, 60, 70, 80, 90, 100, 150]
cmap_colors = [
    'blue', '#a8e1e0', '#66c18a', '#3b7a3d', '#f3d5a4', '#b299ca',
    '#e4a6a3', '#d35d60', '#a0322e', '#330e0f', '#4f4d4d', '#7d7b7b',
    '#a9a8a8', '#c2c0c0', '#dbdbdb', 'black'
]

# Function to assign colors based on boundaries
# Corrected function to assign colors based on boundaries
def get_discrete_color(val):
    for i in range(len(boundaries) - 1):
        # Check if value is within the current interval
        if boundaries[i] <= val < boundaries[i + 1]:
            return cmap_colors[i]
    # Assign last color if value is beyond final boundary
    return cmap_colors[-1]


# Layout for upload view
# Layout for upload view with dataset instructions
# Updated layout for upload view with spinners
def upload_layout():
    return html.Div([
        dcc.Store(id='prediction-data'),
        dcc.Download(id='download-prediction'),
        html.H1("Upload your low resolution (GLDAS Data) and High resolution data (ArcGIS) to our model to get downscaled results "),
        # Dataset instructions and upload buttons
        html.Div([
            html.H2("Please follow these Dataset Requirements:"),
            html.Ul([
                html.Li("Both High-Res and Low-Res CSVs must have the column 'GLDAS_SerialID' for merging."),
                html.Li("Both datasets must have the column 'Year' to ensure temporal alignment."),
                html.Li("High-Res dataset must include: "
                        f"{', '.join(test_high.columns)}."),
                html.Li("Low-Res dataset must include: "
                        f"{', '.join(test_low.columns)}."),
                html.Li("POINT_X is the longitude and POINT_Y is the latitude"),
                html.Li("The categorical columns are 'lithology' and 'lithology_MAJORITY'."),
                html.Li("Numerical columns should not contain missing (NaN) values."),
                html.Li("Categorical columns should not contain unexpected or invalid categories."),
            ]),
        ], style={'marginBottom': '20px'}),
        html.Div(
            [
                dcc.Upload(
                    id='upload-high-res',
                    children=html.Button(
                        'Upload High-Res CSV',
                        style={'background-color': '#4CAF50', 'color': 'white', 'padding': '10px 20px',
                               'border': 'none', 'border-radius': '5px', 'cursor': 'pointer', 'font-size': '16px'}
                    )
                ),
                dcc.Upload(
                    id='upload-low-res',
                    children=html.Button(
                        'Upload Low-Res CSV',
                        style={'background-color': '#2196F3', 'color': 'white', 'padding': '10px 20px',
                               'border': 'none', 'border-radius': '5px', 'cursor': 'pointer', 'font-size': '16px'}
                    )
                )
            ],
            style={'display': 'flex', 'justify-content': 'center', 'gap': '20px', 'margin': '20px 0'}
        ),
        html.Div(
            html.Button(
                'Show Min/Max GWL and Recharge',
                id='process-button',
                disabled=True,
                style={'padding': '10px 20px', 'fontSize': '16px', 'borderRadius': '5px', 'textAlign': 'center'}
            ),
            style={'display': 'flex', 'justify-content': 'center'}
        ),
        html.Div(id='upload-info'),
        html.Div(id='process-info'),

        # Graphs with spinners
        html.Div([
            dcc.Loading(
                id="loading-max-gwl",
                type="circle",
                children=dcc.Graph(id='max-gwl-plot-upload', style={'width': '450px', 'height': '600px'})
            ),
            dcc.Loading(
                id="loading-min-gwl",
                type="circle",
                children=dcc.Graph(id='min-gwl-plot-upload', style={'width': '450px', 'height': '600px'})
            ),
            dcc.Loading(
                id="loading-recharge",
                type="circle",
                children=dcc.Graph(id='recharge-plot-upload', style={'width': '450px', 'height': '600px'})
            )
        ], style={'display': 'flex', 'gap': '10px'}),
        html.Div(id='click-info-upload', style={'padding': '10px', 'fontSize': '16px'}),
        html.Div(
            html.Button(
                'Download Min, Max GWL and Recharge',
                id='download-upsampled-button',
                disabled=True,
                style={'padding': '10px 20px', 'fontSize': '16px', 'borderRadius': '5px', 'textAlign': 'center'}
            ),
            style={'display': 'flex', 'justify-content': 'center'}
        ),
    ])

# No changes to callbacks needed as dcc.Loading automatically wraps the components

# Function to create scatter plot with discrete color coding
# Function to create scatter plot with discrete color coding and color bar legend
def create_discrete_color_plot(data, column, color_title):
    data[f"{column}_color"] = data[column].apply(get_discrete_color)
    fig = go.Figure(go.Scatter(
        x=data['POINT_X'], y=data['POINT_Y'], mode='markers',
        marker=dict(color=data[f"{column}_color"], size=8),
        text=data[column],
        hovertemplate="<br>Longitude: %{x:.2f}<br>Latitude: %{y:.2f}<br>" + color_title + ": %{text:.2f} <extra></extra>"

    ))
    fig.update_layout(
        title=f"{color_title} Map", xaxis_title="Longitude",
        yaxis_title="Latitude", height=600, width=450
    )

    # Add color bar legend
    for i, boundary in enumerate(boundaries[:-1]):
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode='markers',
            marker=dict(size=10, color=cmap_colors[i]),
            legendgroup=color_title,
            showlegend=True,
            name=f"{boundaries[i]} - {boundaries[i+1]} m"
        ))

    return fig

# Callbacks for upload view
def register_upload_callbacks(app):
    app.high_res_data = None
    app.low_res_data = None

    @app.callback(
        Output('upload-info', 'children'),
        Output('process-button', 'disabled'),  # Enable process button when both files are uploaded
        Input('upload-high-res', 'contents'),
        State('upload-high-res', 'filename'),
        prevent_initial_call=True
    )
    def upload_high_res(contents, filename):
        if contents:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            app.high_res_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            
            # Store the non-normalized Sy column
            app.high_res_data['original_Sy'] = app.high_res_data['Sy']
            
            # Apply scaling to numerical features (excluding Sy)
            app.high_res_data[fitted_scaler.feature_names_in_] = fitted_scaler.transform(app.high_res_data[fitted_scaler.feature_names_in_])
            process_button_disabled = app.low_res_data is None  # Disable until both files are uploaded
            return f"High-Res file '{filename}' uploaded and scaled successfully.", process_button_disabled
        return "No High-Res file uploaded.", True

    @app.callback(
        Output('upload-info', 'children', allow_duplicate=True),
        Output('process-button', 'disabled', allow_duplicate=True),
        Input('upload-low-res', 'contents'),
        State('upload-low-res', 'filename'),
        prevent_initial_call=True
    )
    def upload_low_res(contents, filename):
        if contents:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            app.low_res_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            
            process_button_disabled = app.high_res_data is None  # Disable until both files are uploaded
            return f"Low-Res file '{filename}' uploaded successfully.", process_button_disabled
        return "No Low-Res file uploaded.", True
    @app.callback(
        Output('download-prediction', 'data'),
        Input('download-upsampled-button', 'n_clicks'),
        State('prediction-data', 'data'),  # Access the prediction data
        prevent_initial_call=True
    )
    def download_the_prediction(n_clicks, data):
        if n_clicks and data:
            try:
                # Ensure the data is in a format suitable for DataFrame conversion
                df = pd.DataFrame(data)
                return dcc.send_data_frame(df.to_csv, "upsampled.csv", index=False)
            except Exception as e:
                return dash.no_update  # Log the error if needed
        return dash.no_update


    @app.callback(
        Output('process-info', 'children'),
        Output('max-gwl-plot-upload', 'figure'),
        Output('min-gwl-plot-upload', 'figure'),
        Output('recharge-plot-upload', 'figure'),
        Output('download-upsampled-button', 'disabled'),
        Output('prediction-data','data'),
        Input('process-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def process_data(n_clicks):
        if app.high_res_data is not None and app.low_res_data is not None:
            # Merge high- and low-resolution data
            data = app.high_res_data.merge(app.low_res_data, on=['GLDAS_SerialID', 'Year']).rename(columns={'POINT_X_x': 'POINT_X', 'POINT_Y_x': 'POINT_Y'})
            
            # Retrieve the stored original Sy for recharge calculation
            original_sy = data['original_Sy']
            
            # Scale numerical columns
            X_numerical_scaled = standard_scaler.transform(data[standard_scaler.feature_names_in_])
            
            # One-hot encode categorical columns
            X_cat = data[['lithology', 'lithology_MAJORITY']].astype('string')
            X_cat_encoded = pd.get_dummies(X_cat)
            
            # Prepare final input tensor for model
            X_final = torch.tensor(np.hstack([X_numerical_scaled, X_cat_encoded]).astype('float32'))
            
            # Predict Max_GWL and Min_GWL
            pred = rf_model.predict(X_final)
            data['Max_GWL'] = pred[:, 1]
            data['Min_GWL'] = pred[:, 0]

            
            # Calculate recharge using non-normalized Sy
            data['Recharge'] = (data['Max_GWL'].values - data['Min_GWL'].values) * 100 * original_sy.values

            # Generate plots
            max_gwl_fig = create_discrete_color_plot(data, 'Max_GWL', 'Max GWL (m)')
            min_gwl_fig = create_discrete_color_plot(data, 'Min_GWL', 'Min GWL (m)')
            recharge_fig = create_discrete_color_plot(data, 'Recharge', 'Recharge (cm)')
            prediction_data=data[['Min_GWL','Max_GWL','Recharge','POINT_X','POINT_Y']]
            
            
            # Show download link by changing the style to display
            return "Data processed successfully.", max_gwl_fig, min_gwl_fig, recharge_fig, False, prediction_data.to_dict()
        return "Please upload both high-res and low-res files.", None, None, None, None, {'display': 'none'},None
>>>>>>> b0f3c7981bcd8173c0b97e07af51a9bb6efb166b
