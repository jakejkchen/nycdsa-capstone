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
lc.sort_values('issue_year', inplace=True)
lc['fico'] = (lc['fico_range_low'].values + lc['fico_range_high'].values)/2
lc['fico_band'] = pd.cut(lc['fico'].values, bins=[300, 580, 670, 740, 800, 850], labels=['300-580', '580-670', '670-740', '740-800', '800-850'])
lc['int_rate_band'] = pd.cut(lc['int_rate'].values, bins=[0, 8, 12, 16, 20, 24, 28, 32], 
       labels=['0-8%', '8-12%', '12-16%', '16-20%', '20-24%', '24-28%', '28-32%'])
lc.loc[lc.dti<0, 'dti']=0
lc['dti_band'] = pd.cut(lc['dti'].values, bins=[0,10,20,30, 40, 50, 1000], 
       labels=['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '>50%'])

#d_term_group = lc.groupby(['issue_d', 'term'])

app.layout = html.Div([
    html.Div([
        html.Div([dcc.Graph(id='graph-with-slider')], className='five columns'),
        html.Div([dcc.Graph(id='int_rate')], className='five columns'),
        html.Div([dcc.Slider(
            id='year-slider',
            min=lc['issue_year'].min(),
            max=lc['issue_year'].max(),
            value=2015,
            marks={str(year): str(year) for year in lc['issue_year'].unique()},
            step=None
             )], className='row')
        ], className='row'
           ),
    html.Div([
        html.Div([
            html.Div([html.H3('Loan Grade'), dcc.Graph(figure=px.bar(lc.groupby(['grade']).sum()[['loan_amnt']].reset_index(), x='grade', color='grade',category_orders={'grade':['A', 'B', 'C', 'D', 'E', 'F', 'G']},
                      y='loan_amnt', opacity=0.75,labels={'grade': 'Grade', 'loan_amnt':'Origination Principal', 'issue_year': 'Issue Year'}))], className='four columns'),
            html.Div([html.H3('FICO Band'), dcc.Graph(figure=px.bar(lc.groupby(['fico_band']).sum()[['loan_amnt']].reset_index(), x='fico_band', color='fico_band',
                      y='loan_amnt', opacity=0.75,labels={'fico_band': 'FICO Band', 'loan_amnt':'Origination Principal', 'issue_year': 'Issue Year'}))], className='four columns')], className='row'),
        html.Div([
            html.Div([html.H3('Int Rate Band'), dcc.Graph(figure=px.bar(lc.groupby(['int_rate_band']).sum()[['loan_amnt']].reset_index(), x='int_rate_band', color='int_rate_band',
                      y='loan_amnt', opacity=0.75,labels={'int_rate_band': 'Int Rate', 'loan_amnt':'Origination Principal', 'issue_year': 'Issue Year'}))], className='four columns'),
            html.Div([html.H3('DTI Band'), dcc.Graph(figure=px.bar(lc.groupby(['dti_band']).sum()[['loan_amnt']].reset_index(), x='dti_band', color='dti_band',
                      y='loan_amnt', opacity=0.75,labels={'dti_band': 'DTI Band', 'loan_amnt':'Origination Principal', 'issue_year': 'Issue Year'}))], className='four columns')], className='row')
        ], className='row'),
    html.Div([
        html.Div([dcc.Graph(id='loan_grade_by_year', className='nine columns')
             ]),
        html.Div([
            dcc.Dropdown(id='issue_year_drop_down',
                        options=[
                                  {'label': str(year), 'value': str(year)} for year in lc['issue_year'].unique()
                                 ],
                        value='2017',
                        ),
                ], className='two columns')
        
        ], className='row')
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

@app.callback(
    Output('loan_grade_by_year', 'figure'),
    [Input('issue_year_drop_down', 'value')]
    )
def update_figure(selected_year):
    filtered_lc = lc[lc['issue_year']==int(selected_year)]
    return px.box(filtered_lc, x='grade', category_orders={'grade':['A', 'B', 'C', 'D', 'E', 'F', 'G']},
        y='loan_amnt', labels={'grade': 'Grade', 'loan_amnt':'Origination Principal', 'issue_year': 'Issue Year'})



if __name__ == '__main__':
	app.run_server(debug=False)