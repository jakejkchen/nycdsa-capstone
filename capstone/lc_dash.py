import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output

import numpy as np
import pandas as pd 
import plotly_express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app.config['suppress_callback_exceptions']=True


lc = pd.read_csv('./data/LC_data/complete_data/lending-club/accepted_2007_to_2018Q4.csv.gz', compression='gzip')

# preprocessing data
lc['issue_d'] = pd.to_datetime(lc['issue_d'])
lc = lc[pd.notnull(lc['issue_d'])]
lc['issue_year'] = lc['issue_d'].dt.year

#d_term_group = lc.groupby(['issue_d', 'term'])

app.layout = html.Div([
    dcc.Graph(id='graph-with-slider', style={"width": "50%", "display": "inline-block", 'float': 'left'}),
    dcc.Graph(id='int_rate', style={"width": "50%", "display": "inline-block", 'float': 'right'}),
    dcc.Slider(
        id='year-slider',
        min=lc['issue_year'].min(),
        max=lc['issue_year'].max(),
        value=2015,
        marks={str(year): str(year) for year in lc['issue_year'].unique()},
        step=None
    ),
])



@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value')])
def update_figure(selected_year):
	filtered_lc = lc[lc['issue_year']<=selected_year]

	return px.line(filtered_lc.groupby(['issue_d', 'term']).sum()[['loan_amnt']].reset_index(), x='issue_d', y='loan_amnt',
                   labels={'issue_d': 'Issue Date', 'loan_amnt': 'Origination Principal'}, color='term')

@app.callback(
    Output('int_rate', 'figure'),
    [Input('year-slider', 'value')])
def update_figure(selected_year):
    filtered_lc = lc[lc['issue_year']<=selected_year]

    return px.line(filtered_lc.groupby(['issue_d', 'term']).mean()[['int_rate']].reset_index(), x='issue_d', y='int_rate', 
        color='term', labels={'issue_d': 'Issue Date', 'int_rate': 'Interest Rate'})



if __name__ == '__main__':
	app.run_server(debug=False)