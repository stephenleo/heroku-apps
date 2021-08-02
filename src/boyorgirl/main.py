from model import CustomOpTfPredictor as Model

import re
import pandas as pd
import plotly.express as px

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

# Load the Model
model_dir = 'models/1'
pred_model = Model(model_dir)

# Setup the Dash App
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# App Layout
app.layout = html.Table([
    html.Tr([
        html.H2(html.B('Boy or Girl?')),
        html.Div(
            dcc.Input(id='names',
                      placeholder='Enter names separated by space or comma',
                      value='Joe Biden, Kamala Harris',
                      style={
                          'width': '500px',
                          'font-size': '14px'
                      })),
        html.Br(),
        html.Center(
            html.Button('Submit',
                        id='submit-button',
                        n_clicks=0,
                        style={'font-size': '14px'})),
        html.Br(),
        html.Div(id='predictions', children=[], style={'width': '500px'}),
        dcc.Store(id='selected-names'),
        html.Br(),
        html.Div(id='bar-plot', children=[])
    ])
],
                        style={
                            'marginLeft': 'auto',
                            'marginRight': 'auto'
                        })


# Callbacks
@app.callback(
    [Output('predictions', 'children'),
     Output('selected-names', 'children')], Input('submit-button', 'n_clicks'),
    State('names', 'value'))
def predict(n_clicks, value):
    # Split on all non-alphabet characters
    names = re.findall(r"\w+", value)

    # Restrict to first 10 names only
    names = names[:10]

    # Predictions
    pred_df = pd.DataFrame(pred_model.predict(names)).drop_duplicates()

    return [
        dash_table.DataTable(
            id='pred-table',
            columns=[{
                'name': col,
                'id': col,
            } for col in pred_df.columns],
            data=pred_df.to_dict('records'),
            filter_action="native",
            filter_options={"case": "insensitive"},
            sort_action="native",  # give user capability to sort columns
            sort_mode="single",  # sort across 'multi' or 'single' columns
            page_current=0,  # page number that user is on
            page_size=10,  # number of rows visible per page
            style_cell={
                'textAlign': 'center',
                'padding': '10px',
                'backgroundColor': 'rgb(255, 255, 204)',
                'height': 'auto',
                'font-size': '14px',
                'width': '100px',
                'minWidth': '100px',
                'maxWidth': '100px'
            },
            style_header={
                'backgroundColor': 'rgb(0, 0, 255)',
                'color': 'white',
                'textAlign': 'center'
            },
        )
    ], names


@app.callback(
    Output('bar-plot', 'children'),
    [Input('predictions', 'children'),
     Input('selected-names', 'children')])
def bar_plot(data, selected_names):
    # Bar Chart
    data = pd.DataFrame(data[0]['props']['data'])
    fig = px.bar(data,
                 x="Probability",
                 y="Name",
                 color='Gender',
                 orientation='h',
                 color_discrete_map={
                     'M': 'dodgerblue',
                     'F': 'lightcoral'
                 })

    fig.update_layout(title={
        'text': 'Confidence in Prediction',
        'x': 0.5
    },
                      yaxis={
                          'categoryorder': 'array',
                          'categoryarray': selected_names,
                          'autorange': 'reversed',
                      },
                      xaxis={'range': [0, 1]},
                      width=500)

    return html.Div(children=[dcc.Graph(figure=fig)])


if __name__ == '__main__':
    app.run_server(debug=True)