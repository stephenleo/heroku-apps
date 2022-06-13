import os
import pandas as pd
import numpy as np
import re
from tensorflow.keras.models import load_model

import plotly.express as px
import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from utils.preprocess import preprocess

# Load the model
model_path = os.path.join(os.path.dirname(__file__), 'models/boyorgirl.h5')
pred_model = load_model(model_path)

# Setup the Dash App
external_stylesheets = [dbc.themes.LITERA]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Server
server = app.server

# FAQ section
with open('faq.md', 'r') as file:
    faq = file.read()

# App Layout
app.layout = html.Table([
    html.Tr([
        html.H1(html.Center(html.B('Boy or Girl?'))),
        html.Div(
            html.Center("Check if your names are Boy's names or Girl's names"),
            style={'fontSize': 20}),
        html.Br(),
        html.Div(
            dbc.Input(id='names',
                      value='Joe Biden, Kamala Harris',
                      placeholder='Enter names separated by space or comma',
                      style={'width': '700px'})),
        html.Br(),
        html.Center(children=[
            dbc.Button('Submit',
                       id='submit-button',
                       n_clicks=0,
                       color='primary',
                       type='submit'),
            dbc.Button('Reset',
                       id='reset-button',
                       color='secondary',
                       type='submit',
                       style={"margin-left": "50px"})
        ]),
        html.Br(),
        dcc.Loading(id='table-loading',
                    type='default',
                    children=html.Div(id='predictions',
                                      children=[],
                                      style={'width': '700px'})),
        dcc.Store(id='selected-names'),
        html.Br(),
        dcc.Loading(id='chart-loading',
                    type='default',
                    children=html.Div(id='bar-plot', children=[])),
        html.Br(),
        html.Div(html.Center(html.B('About "Boy or Girl?"')),
                 style={'fontSize': 20}),
        dcc.Markdown(faq, style={'width': '700px'})
    ])
],
                        style={
                            'marginLeft': 'auto',
                            'marginRight': 'auto'
                        })


# Callbacks
@app.callback([Output('submit-button', 'n_clicks'),
               Output('names', 'value')], Input('reset-button', 'n_clicks'),
              State('names', 'value'))
def update(n_clicks, value):
    return (-1, '') if n_clicks is not None and n_clicks > 0 else (0, value)


@app.callback(
    [Output('predictions', 'children'),
     Output('selected-names', 'data')], Input('submit-button', 'n_clicks'),
    State('names', 'value'))
def predict(n_clicks, value):
    if n_clicks < 0:
        return [], ''
    # Split on all non-alphabet characters
    names = re.findall(r"\w+", value)

    # Restrict to first 10 names only
    names = names[:10]

    # Convert to dataframe
    pred_df = pd.DataFrame({'name': names})

    # Preprocess
    pred_df = preprocess(pred_df, train=False)

    # Predictions
    result = pred_model.predict(np.asarray(
        pred_df['name'].values.tolist())).squeeze(axis=1)
    pred_df['Boy or Girl?'] = [
        'Boy' if logit > 0.5 else 'Girl' for logit in result
    ]
    pred_df['Probability'] = [
        logit if logit > 0.5 else 1.0 - logit for logit in result
    ]

    # Format the output
    pred_df['name'] = names
    pred_df.rename(columns={'name': 'Name'}, inplace=True)
    pred_df['Probability'] = pred_df['Probability'].round(2)
    pred_df.drop_duplicates(inplace=True)

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
                'fontFamily': 'Open Sans',
                'textAlign': 'center',
                'padding': '10px',
                'backgroundColor': 'rgb(255, 255, 204)',
                'height': 'auto',
                'font-size': '16px'
            },
            style_header={
                'backgroundColor': 'rgb(128, 128, 128)',
                'color': 'white',
                'textAlign': 'center'
            },
            export_format='csv')
    ], names


@app.callback(Output('bar-plot', 'children'), [
    Input('submit-button', 'n_clicks'),
    Input('predictions', 'children'),
    Input('selected-names', 'data')
])
def bar_plot(n_clicks, data, selected_names):
    if n_clicks >= 0:
        # Bar Chart
        data = pd.DataFrame(data[0]['props']['data'])
        fig = px.bar(data,
                     x="Probability",
                     y="Name",
                     color='Boy or Girl?',
                     orientation='h',
                     color_discrete_map={
                         'Boy': 'dodgerblue',
                         'Girl': 'lightcoral'
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
                          font={'size': 14},
                          width=700)

        return [dcc.Graph(figure=fig)]
    else:
        return []


if __name__ == '__main__':
    app.run_server()