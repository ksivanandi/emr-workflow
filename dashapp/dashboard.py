import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import dash
from dash.dependencies import Input, Output
import plotly.figure_factory as ff
import base64

# for performance tuning using caching with Redis
# https://dash.plotly.com/performance

# use local css
##insert code here##


#multiple_admissions=pd.read_csv(r'data\multiple_admissions.csv')
summary=pd.read_csv(r'data\summary.csv')
readmission_charts=pd.read_csv(r'data\readmission_charts.csv')
#patient_pivot=pd.read_csv(r'data\patient_pivot.csv')
#patient_pivot.dropna()
readmission_scatter=pd.read_csv(r'data\readmission_scatter.csv')
diagnosis=pd.read_csv(r'data\diagnosis.csv')
#sort values and take top 15
diagnosis.sort_values('readmission', ascending=False)
diagnosis=diagnosis.nlargest(200,'readmission')
#readmissions_dict=readmissions.to_dict('records')
#multiple_admissions_table=ff.create_table(multiple_admissions)

# plotly template & formatting
template="plotly_dark"
LAYOUT = {'height': 600,
          'width': 1000}
config={'displaylogo': False,'displayModeBar': 'hover','autosizable': True,'showSources':True,'Zoom':True}
#initial graph
figure= px.histogram(diagnosis, x="diagnosis",nbins=75, color="insurance", marginal="rug",
                    template=template,title='Number of Readmissions by Initial Dx').update_layout(title_font_size=24,margin={'autoexpand':True,'b':240})
figure.update_xaxes(tickangle=45)
#figure=figure= px.box(patient_pivot, x="ethnicity", color="insurance",notched=True)

# set graph properties
figure.layout.autosize==True
figure.update_layout(title_font_color='#ffffff')


app = dash.Dash()
#app.css.append_css({'external_scripts': 'style.css'})

app.layout = html.Div(
    children=[
        html.H1(children=[
             "Baseline Report",
             ],
             style={'class':'right','color':'#ffffff','backgroundColor':'#00529b'}
             ),
             
        html.Div(className='row',  # Define the row element
            children=[
                html.Div(className='four columns div-user-controls',  # Define the left element
                        children = [
                            html.H3 ('Visualizing Readmissions Data'),
                            html.P('''The visualizations in this interactive report are based on data from your EMR.  They are designed to give you directional insight into your patient population.
                            You can change the visualization by selecting an option from the  dropdown below.'''),
                            html.Div(
                            # define dropdown
                            className='div-for-dropdown',
                            children=[
                                dcc.Dropdown(id='view', 
                                            options=[
                                                    
                                                    {'label': 'Patient Summary', 'value': 'Summary'},
                                                    {'label': 'Readmissions', 'value': 'Readmissions'},
                                                    {'label': 'Length of Stay', 'value': 'LOS'},
                                                    {'label': 'Readmission Scatter', 'value':'Readmission Scatter'},
                                                    {'label': 'Diagnosis', 'value': 'Diagnosis'},
                                                    ],multi=False, value='Diagnosis',
                                                      style={'backgroundColor': '#5bd9f0'},
                                                      className='view'
                                                      ),
                                     ],
                                     style={'color': '#292828','width':'250px'})
                                ]
                             ),
                             
                html.Div(className='eight columns div-for-charts bg-grey',
                        children=[
                                dcc.Graph(id='timeseries', animate=True,
                                config={'scrollZoom': True, 'autosizable':True,'responsive':False},
                                          figure= figure),
                                       
                                       
                                       ],
                        ),
                        
                    ]),
                
                
         html.Footer(children=[
             html.Img(src=app.get_asset_url('logo.png')),
             ],
             style={'color': '#00529b'}),    
                
                
                
                ],
)

# Callback for timeseries price
@app.callback(Output('timeseries', 'figure'),
              [Input('view', 'value')])
def update_graph(selected_dropdown_value):
        
        if (selected_dropdown_value=='Readmissions'):
            figure= px.histogram(readmission_charts, x="readmission", color="gender",nbins=200, marginal="rug",facet_col='insurance', 
                    title='Readmission Counts by Insurance Type', range_x= [1,100],template=template).update_layout(title_font_size=24)
            return figure
        
        elif (selected_dropdown_value=='Readmission Scatter'):
            figure= px.scatter(summary, x='los_avg', y='count',color='ethnicity',
                    title='Readmissions',template=template,hover_data=['patient_id','diagnosis','icd_codes','los']).update_layout(title_font_size=24)
            figure.update_xaxes(title='Length of Stay')
            figure.update_yaxes(title='Readmission Count')
            return figure
        
        elif (selected_dropdown_value=='LOS'):
             figure=px.histogram(summary, x="los",nbins=100, color="readmission", marginal="rug", template=template,title='Length of Stay', facet_col='insurance', range_x= [1,150]).update_layout(title_font_size=24)
             figure.update_xaxes(title='Length of Stay')
             return figure
            
        elif (selected_dropdown_value=='Diagnosis'):
            figure= px.histogram(diagnosis, x="diagnosis",nbins=75, color="insurance", marginal="rug",
                    template=template,title='Number of Readmissions by Initial Dx').update_layout(title_font_size=24,margin={'autoexpand':True,'b':240})
            figure.update_xaxes(tickangle=45)
            return figure
        
        elif (selected_dropdown_value=='Summary'):
            figure= px.histogram(summary, x="los", color="ethnicity",nbins=200, marginal="rug", 
                        title='Patient Summary', range_x= [1,100],template=template).update_layout(title_font_size=24)
            figure.update_xaxes(title='Length of Stay')
            return figure
        else:
            figure=px.scatter(readmission_scatter, x='los', y='readmission',color='readmission',
                    title='Readmission & Length of Stay',template=template).update_layout(title_font_size=24)
            return figure
            
if __name__ == '__main__':
    app.run_server(debug=True)