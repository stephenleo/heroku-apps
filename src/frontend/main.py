import re
import requests
import pandas as pd
import plotly.express as px

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
name_gender_backend = 'https://name-gender-backend.herokuapp.com/predict'

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    html.H2(html.B('Boy or Girl?')),
    html.Div(
        dcc.Input(id='names',
                  placeholder='Enter names separated by space or comma',
                  value='Joe Biden, Kamala Harris',
                  style={'width': '100%'})),
    html.Br(),
    html.Button('Submit', id='submit-val', n_clicks=0),
    html.Br(),
    dcc.Store(id='api-response'),
    dash_table.DataTable(
        id='table',
        filter_action="native",
        sort_action="native",
        sort_mode="single",
        page_action="native",
        page_current=0,
        page_size=10,
        style_header={
            'backgroundColor': 'rgb(0, 0, 255)',
            'color': 'white'
        },
        style_cell={
            'textAlign': 'left',
            'backgroundColor': 'rgb(255, 255, 204)',
        },
        # style_cell_conditional=[
        #     {
        #         'if': {'column_id': 'Gender', 'filter_query': '{Gender}=="F"'},
        #         'backgroundColor': 'lightcoral'
        #     },
        #     {
        #         'if': {'filter_query': '{Gender}=="M"'},
        #         'backgroundColor': 'dodgerblue'
        #     },
        # ]
    ),
    dcc.Graph(id='bar-chart')
])


@app.callback(Output('api-response', 'data'),
              [Input('submit-val', 'n_clicks')], [State('names', 'value')])
def call_api(n_clicks, value):
    # Split on all non-alphabet characters
    names = re.findall(r"\w+", value)

    # Restrict to first 10 names only
    names = names[:10]

    # API requests
    response = requests.post(name_gender_backend, json=names)
    return response.json()


@app.callback([
    Output(component_id='table', component_property='data'),
    Output(component_id='table', component_property='columns')
], Input('api-response', 'data'))
def tabluar_results(value):
    # Convert values to Dataframe
    results_df = pd.DataFrame(value)

    # Uppercase the first letter of each column
    # TODO: Move this to the API
    results_df.columns = [col.title() for col in results_df.columns]

    # Return the data and columns for datatable display
    columns = [{'name': col, 'id': col} for col in results_df.columns]
    data = results_df.to_dict(orient='records')
    return data, columns


@app.callback(Output('bar-chart', 'figure'), [
    Input(component_id='table', component_property='data'),
    Input(component_id='table', component_property='columns')
])
def update_figure(data, columns):
    # Bar Chart
    fig = px.bar(data,
                 x="Probability",
                 y="Name",
                 color='Gender',
                 orientation='h',
                 color_discrete_map={
                     'M': 'dodgerblue',
                     'F': 'lightcoral'
                 })
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)