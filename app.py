# This is a Python script for the CCD Visualizer Dashboard.
# Copyright (c) 2023 Abhiraj Raundalkar
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import base64
import dash
import dash_html_components as html
import dash_core_components as dcc
import io
import pandas as pd
import dash_table
from dash.dependencies import Input, Output, State
import numpy as np
import dash_bootstrap_components as dbc


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Custom color palette
colors = {
    'background': '#ffffff',
    'text': '#000000',
    'accent': '#2C3539',
    'highlight': '#c44e52',
    'button': '#6495ED',
    'pie_colors': ['#FF0000', '#00FF00', '#FF7F50', '#0000FF', '#FFFF00']
}

# Read Excel function
def read_excel_contents(contents, columns_to_keep):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded), skiprows=8)
    df = df.iloc[:, columns_to_keep]
    df.columns = [
        'Index', 'Roll no', 'Names',
        'WEEK1', '1',
        'WEEK2', '2',
        'WEEK3', '3',
        'WEEK4', '4',
        'WEEK5', '5',
        'WEEK6', '6'
    ]
    return df

def update_output(contents, columns_to_keep):
    if contents is None:
        return html.Div(['']), {}, {}  # Added empty output for the new charts

    df = read_excel_contents(contents, columns_to_keep)

    # Convert columns to numeric if necessary
    numeric_columns = ['1', '2', '3', '4', '5', '6']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

    # Calculate the highest star count for each person
    df['Highest_Star'] = df[numeric_columns].apply(np.max, axis=1)

    # Calculate the percentage based on the Highest_Star column
    df['Percentage'] = ((df['Highest_Star'] / 5) * 100).apply(lambda x: f'{x:.2f}%' if not np.isnan(x) else '')

    # Create the DataTable
    table = dash_table.DataTable(
        columns=[{'name': col, 'id': col} for col in df.columns],
        data=df.to_dict('records'),
        style_table={'font-size': '12px', 'width': '90%', 'margin': 'auto'},
        style_cell={'textAlign': 'left'},
        page_size=len(df),
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ]
    )

    # Create the bar graph figure
    bar_graph = {
        'data': [
            {'x': df['Names'][2:], 'y': df['1'][2:], 'type': 'bar', 'name': 'Week 1'},
            {'x': df['Names'][2:], 'y': df['2'][2:], 'type': 'bar', 'name': 'Week 2'},
            {'x': df['Names'][2:], 'y': df['3'][2:], 'type': 'bar', 'name': 'Week 3'},
            {'x': df['Names'][2:], 'y': df['4'][2:], 'type': 'bar', 'name': 'Week 4'},
            {'x': df['Names'][2:], 'y': df['5'][2:], 'type': 'bar', 'name': 'Week 5'},
            {'x': df['Names'][2:], 'y': df['6'][2:], 'type': 'bar', 'name': 'Week 6'}
        ],
        'layout': {
            'title': 'Bar Graph: stars for Weeks 1 to 6',
            'xaxis': {'title': 'Student Names', 'tickangle': -45, 'automargin': True},
            'yaxis': {'title': 'stars in Hackerrank'},
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {'color': colors['text']},
            'margin': {'b': 100, 't': 50, 'l': 50, 'r': 50}  # Adjust margins
        }
    }

    # Create the pie chart figure for star count
    star_count_pie_chart = {
        'data': [
            {
                'labels': [f"{count} students = {star} stars" for star, count in df['Highest_Star'].value_counts().sort_index().items()],
                'values': df['Highest_Star'].value_counts().sort_index().values.tolist(),
                'type': 'pie',
                'marker': {'colors': colors['pie_colors']}
            }
        ],
        'layout': {
            'title': 'Pie Chart: Count of Students by Star Ratings',
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {'color': colors['text']}
        }
    }

    return table, bar_graph, star_count_pie_chart

app.layout = html.Div(style={'backgroundColor': colors['background'], 'height': '100vh'}, children=[
    dbc.Container(id="main-content", children=[
        html.H1("Login to CCD Visualizer", className="mt-5"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Username"),
                dbc.Input(id="username-input", type="text", placeholder="Enter username", className="mb-2"),
                dbc.Label("Password"),
                dbc.Input(id="password-input", type="password", placeholder="Enter password", className="mb-2"),
                dbc.Button("Login", id="login-button", color="primary", className="mt-3", n_clicks=0),
            ], width=4)
        ], className="mt-4"),
        html.Div([
            dbc.Button("Forgot Password", id="forgot-password-button", color="success", className="mt-2")
        ]),
        html.Div(id="login-output", className="mt-3")
    ])
])

@app.callback(
    Output("main-content", "children"),
    [Input("login-button", "n_clicks")],
    [State("username-input", "value"),
     State("password-input", "value")]
)
def handle_login(n_login_clicks, entered_username, entered_password):
    if n_login_clicks > 0:
        if entered_username == "mauli" and entered_password == "mauliccd":
            return html.Div([
                html.H1("Competitive Coding Development (CCD)", style={'textAlign': 'center', 'color': colors['text'], 'marginTop': '20px'}),
                dcc.Tabs(id='tabs', value='Page 1', children=[
                    dcc.Tab(label='2N, 2R, 3R', value='Page 1', children=[
                        dcc.Upload(
                            id='upload-data-page1',
                            children=html.Div([
                                html.B('Drag and Drop or '),
                                html.A(html.B('Select a File')),
                            ]),
                            style={
                                'width': '60%',
                                'height': '50px',
                                'lineHeight': '50px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': 'auto',
                                'marginTop': '20px',
                                'backgroundColor': colors['button'],
                                'color': colors['text'],
                            },
                            multiple=False
                        ),
                        html.Div(id='output-data-upload-page1', style={'margin': '20px'}),
                        dcc.Graph(id='bar-graph-page1', style={'width': '90%', 'margin': 'auto', 'marginTop': '20px'}),
                        dcc.Graph(id='star-count-pie-chart-page1', style={'width': '60%', 'margin': 'auto', 'marginTop': '20px'})
                        # ... (rest of the page 1 content)
                    ]),
                    dcc.Tab(label='4R', value='Page 2', children=[
                        dcc.Upload(
                            id='upload-data-page2',
                            children=html.Div([
                                html.B('Drag and Drop or '),
                                html.A(html.B('Select a File')),
                            ]),
                            style={
                                'width': '60%',
                                'height': '50px',
                                'lineHeight': '50px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': 'auto',
                                'marginTop': '20px',
                                'backgroundColor': colors['button'],
                                'color': colors['text'],
                            },
                            multiple=False
                        ),
                        html.Div(id='output-data-upload-page2', style={'margin': '20px'}),
                        dcc.Graph(id='bar-graph-page2', style={'width': '90%', 'margin': 'auto', 'marginTop': '20px'}),
                        dcc.Graph(id='star-count-pie-chart-page2', style={'width': '60%', 'margin': 'auto', 'marginTop': '20px'})
                        # ... (rest of the page 2 content)
                    ])
                ])
            ])
        else:
            return dbc.Alert("Login failed. Please check your credentials.", color="danger", dismissable=True)
    return app.layout
@app.callback(
    Output("login-output", "children"),
    [Input("forgot-password-button", "n_clicks")]
)
def show_contact_message(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        contact_message = html.Div([
            html.H4("Contact Us", style={'color': 'red'}),
            html.P("For password recovery, please contact us at juned44@gmail.com."),
        ])
        return contact_message
    return None


@app.callback(
    [Output('output-data-upload-page1', 'children'), Output('bar-graph-page1', 'figure'), Output('star-count-pie-chart-page1', 'figure'),
     Output('output-data-upload-page2', 'children'), Output('bar-graph-page2', 'figure'), Output('star-count-pie-chart-page2', 'figure')],
    [Input('upload-data-page1', 'contents'), Input('upload-data-page2', 'contents')],
    [State('tabs', 'value')]
)
def update_tab_contents(contents_page1, contents_page2, active_tab):
    columns_to_keep_page1 = [0, 1, 2, 6, 13, 16, 23, 26, 33, 36, 43, 46, 53, 56, 63]
    columns_to_keep_page2 = [0, 1, 2, 6, 15, 18, 27, 30, 39, 42, 51, 54, 63, 66, 75]
    
    outputs = []
    
    for contents, columns_to_keep in zip([contents_page1, contents_page2], [columns_to_keep_page1, columns_to_keep_page2]):
        if contents is None or active_tab is None:
            outputs.extend([html.Div(['']), {}, {}])  # Appending multiple outputs
        else:
            outputs.extend(update_output(contents, columns_to_keep))  # Appending multiple outputs
    
    return tuple(outputs)

if __name__ == '__main__':
    app.run_server(debug=True)



import base64
import dash
import dash_html_components as html
import dash_core_components as dcc
import io
import pandas as pd
import dash_table
from dash.dependencies import Input, Output, State
import numpy as np
import dash_bootstrap_components as dbc


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Custom color palette
colors = {
    'background': '#ffffff',
    'text': '#000000',
    'accent': '#2C3539',
    'highlight': '#c44e52',
    'button': '#6495ED',
    'pie_colors': ['#FF0000', '#00FF00', '#FF7F50', '#0000FF', '#FFFF00']
}

# Read Excel function
def read_excel_contents(contents, columns_to_keep):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded), skiprows=8)
    df = df.iloc[:, columns_to_keep]
    df.columns = [
        'Index', 'Roll no', 'Names',
        'WEEK1', '1',
        'WEEK2', '2',
        'WEEK3', '3',
        'WEEK4', '4',
        'WEEK5', '5',
        'WEEK6', '6'
    ]
    return df

def update_output(contents, columns_to_keep):
    if contents is None:
        return html.Div(['']), {}, {}  # Added empty output for the new charts

    df = read_excel_contents(contents, columns_to_keep)

    # Convert columns to numeric if necessary
    numeric_columns = ['1', '2', '3', '4', '5', '6']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

    # Calculate the highest star count for each person
    df['Highest_Star'] = df[numeric_columns].apply(np.max, axis=1)

    # Calculate the percentage based on the Highest_Star column
    df['Percentage'] = ((df['Highest_Star'] / 5) * 100).apply(lambda x: f'{x:.2f}%' if not np.isnan(x) else '')

    # Create the DataTable
    table = dash_table.DataTable(
        columns=[{'name': col, 'id': col} for col in df.columns],
        data=df.to_dict('records'),
        style_table={'font-size': '12px', 'width': '90%', 'margin': 'auto'},
        style_cell={'textAlign': 'left'},
        page_size=len(df),
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ]
    )

    # Create the bar graph figure
    bar_graph = {
        'data': [
            {'x': df['Names'][2:], 'y': df['1'][2:], 'type': 'bar', 'name': 'Week 1'},
            {'x': df['Names'][2:], 'y': df['2'][2:], 'type': 'bar', 'name': 'Week 2'},
            {'x': df['Names'][2:], 'y': df['3'][2:], 'type': 'bar', 'name': 'Week 3'},
            {'x': df['Names'][2:], 'y': df['4'][2:], 'type': 'bar', 'name': 'Week 4'},
            {'x': df['Names'][2:], 'y': df['5'][2:], 'type': 'bar', 'name': 'Week 5'},
            {'x': df['Names'][2:], 'y': df['6'][2:], 'type': 'bar', 'name': 'Week 6'}
        ],
        'layout': {
            'title': 'Bar Graph: stars for Weeks 1 to 6',
            'xaxis': {'title': 'Student Names', 'tickangle': -45, 'automargin': True},
            'yaxis': {'title': 'stars in Hackerrank'},
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {'color': colors['text']},
            'margin': {'b': 100, 't': 50, 'l': 50, 'r': 50}  # Adjust margins
        }
    }

    # Create the pie chart figure for star count
    star_count_pie_chart = {
        'data': [
            {
                'labels': [f"{count} students = {star} stars" for star, count in df['Highest_Star'].value_counts().sort_index().items()],
                'values': df['Highest_Star'].value_counts().sort_index().values.tolist(),
                'type': 'pie',
                'marker': {'colors': colors['pie_colors']}
            }
        ],
        'layout': {
            'title': 'Pie Chart: Count of Students by Star Ratings',
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {'color': colors['text']}
        }
    }

    return table, bar_graph, star_count_pie_chart

app.layout = html.Div(style={'backgroundColor': colors['background'], 'height': '100vh'}, children=[
    dbc.Container(id="main-content", children=[
        html.H1("Login to CCD Visualizer", className="mt-5"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Username"),
                dbc.Input(id="username-input", type="text", placeholder="Enter username", className="mb-2"),
                dbc.Label("Password"),
                dbc.Input(id="password-input", type="password", placeholder="Enter password", className="mb-2"),
                dbc.Button("Login", id="login-button", color="primary", className="mt-3", n_clicks=0),
            ], width=4)
        ], className="mt-4"),
        html.Div([
            dbc.Button("Forgot Password", id="forgot-password-button", color="success", className="mt-2")
        ]),
        html.Div(id="login-output", className="mt-3")
    ])
])

@app.callback(
    Output("main-content", "children"),
    [Input("login-button", "n_clicks")],
    [State("username-input", "value"),
     State("password-input", "value")]
)
def handle_login(n_login_clicks, entered_username, entered_password):
    if n_login_clicks > 0:
        if entered_username == "mauli" and entered_password == "mauliccd":
            return html.Div([
                html.H1("Competitive Coding Development (CCD)", style={'textAlign': 'center', 'color': colors['text'], 'marginTop': '20px'}),
                dcc.Tabs(id='tabs', value='Page 1', children=[
                    dcc.Tab(label='2N, 2R, 3R', value='Page 1', children=[
                        dcc.Upload(
                            id='upload-data-page1',
                            children=html.Div([
                                html.B('Drag and Drop or '),
                                html.A(html.B('Select a File')),
                            ]),
                            style={
                                'width': '60%',
                                'height': '50px',
                                'lineHeight': '50px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': 'auto',
                                'marginTop': '20px',
                                'backgroundColor': colors['button'],
                                'color': colors['text'],
                            },
                            multiple=False
                        ),
                        html.Div(id='output-data-upload-page1', style={'margin': '20px'}),
                        dcc.Graph(id='bar-graph-page1', style={'width': '90%', 'margin': 'auto', 'marginTop': '20px'}),
                        dcc.Graph(id='star-count-pie-chart-page1', style={'width': '60%', 'margin': 'auto', 'marginTop': '20px'})
                        # ... (rest of the page 1 content)
                    ]),
                    dcc.Tab(label='4R', value='Page 2', children=[
                        dcc.Upload(
                            id='upload-data-page2',
                            children=html.Div([
                                html.B('Drag and Drop or '),
                                html.A(html.B('Select a File')),
                            ]),
                            style={
                                'width': '60%',
                                'height': '50px',
                                'lineHeight': '50px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': 'auto',
                                'marginTop': '20px',
                                'backgroundColor': colors['button'],
                                'color': colors['text'],
                            },
                            multiple=False
                        ),
                        html.Div(id='output-data-upload-page2', style={'margin': '20px'}),
                        dcc.Graph(id='bar-graph-page2', style={'width': '90%', 'margin': 'auto', 'marginTop': '20px'}),
                        dcc.Graph(id='star-count-pie-chart-page2', style={'width': '60%', 'margin': 'auto', 'marginTop': '20px'})
                        # ... (rest of the page 2 content)
                    ])
                ])
            ])
        else:
            return dbc.Alert("Login failed. Please check your credentials.", color="danger", dismissable=True)
    return app.layout
@app.callback(
    Output("login-output", "children"),
    [Input("forgot-password-button", "n_clicks")]
)
def show_contact_message(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        contact_message = html.Div([
            html.H4("Contact Us", style={'color': 'red'}),
            html.P("For password recovery, please contact us at juned44@gmail.com."),
        ])
        return contact_message
    return None


@app.callback(
    [Output('output-data-upload-page1', 'children'), Output('bar-graph-page1', 'figure'), Output('star-count-pie-chart-page1', 'figure'),
     Output('output-data-upload-page2', 'children'), Output('bar-graph-page2', 'figure'), Output('star-count-pie-chart-page2', 'figure')],
    [Input('upload-data-page1', 'contents'), Input('upload-data-page2', 'contents')],
    [State('tabs', 'value')]
)
def update_tab_contents(contents_page1, contents_page2, active_tab):
    columns_to_keep_page1 = [0, 1, 2, 6, 13, 16, 23, 26, 33, 36, 43, 46, 53, 56, 63]
    columns_to_keep_page2 = [0, 1, 2, 6, 15, 18, 27, 30, 39, 42, 51, 54, 63, 66, 75]
    
    outputs = []
    
    for contents, columns_to_keep in zip([contents_page1, contents_page2], [columns_to_keep_page1, columns_to_keep_page2]):
        if contents is None or active_tab is None:
            outputs.extend([html.Div(['']), {}, {}])  # Appending multiple outputs
        else:
            outputs.extend(update_output(contents, columns_to_keep))  # Appending multiple outputs
    
    return tuple(outputs)

if __name__ == '__main__':
    app.run_server(debug=True)
