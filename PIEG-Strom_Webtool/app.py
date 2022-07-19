from turtle import width
import dash_trich_components as dtc
from dash.dependencies import Input, Output
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import plotly_express as px
from functions.PLZtoWeatherRegion import getregion

df_sfh=pd.read_pickle('PIEG-Strom_Webtool/dummy.pkl')
app = Dash(__name__,
          suppress_callback_exceptions=True, 
          external_stylesheets=[{'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css','rel': 'stylesheet','integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf','crossorigin': 'anonymous'}],
          meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"},
          ],
          )
region=['Nordseeküste','Ostseeküste','Nordwestdeutsches Tiefland','Nordostdeutsches Tiefland','Niederrheinisch-westfälische Bucht und Emsland','Nördliche und westliche Mittelgebirge, Randgebiete',
'Nördliche und westliche Mittelgebirge, zentrale Bereiche','Oberharz und Schwarzwald (mittlere Lagen)','Thüringer Becken und Sächsisches Hügelland','Südöstliche Mittelgebirge bis 1000 m',
'Erzgebirge, Böhmer- und Schwarzwald oberhalb 1000 m','Oberrheingraben und unteres Neckartal','Schwäbisch-fränkisches Stufenland und Alpenvorland','Schwäbische Alb und Baar',
'Alpenrand und -täler']
efh_content=html.Div(children=[
    html.H4('Einfamilienhaus'),
    html.Div('Standort'),
    dcc.Input(id='standort',placeholder='Postleitzahl oder Adresse',persistence='local'),
    html.Div('Nordsee',id='region'),
    html.Div('Baustandard'),
    dcc.Dropdown(['kfW100','kfW50'],id='baustandart_sfh',value='kfW100',),
    html.Div('Wohnraum in qm'),
    dcc.Slider(50,250,50,value=150,id='wohraum_efh',),
    html.H4('Verbrauchskennzahlen'),
    html.Div('Bewohneranzahl'),
    dcc.Slider(min=1,max=6,step=1,value=4,id='n_bewohner_efh'),
    html.Div('Stromverbrauch in kWh'),
    dcc.Slider(min=2000,max=8000,step=500,value=4000,id='stromverbrauch_efh'),
])
mfh_content=html.Div(children=[
    html.H4('Mehrfamilienhaus'),
    html.Div('Standort'),
    dcc.Input(id='standort',placeholder='Postleitzahl oder Adresse',persistence='local'),
    html.Div('Nordsee',id='region'),
    html.Div('Anzahl an Wohnungen'),
    dcc.Slider(2,25,1,value=7,id='n_wohnungen',),
    html.Div('Gebäudegröße in m²'),
    dcc.Slider(140,1750,70,value=140,id='wohraum_mfh',),
    html.Div('Baustandard in kWh/(m² Jahr)'),
    dcc.Dropdown([25,75,200],value=75,id='baustandard_mfh'),
    html.Div('Stromverbrauch in kWh'),
    dcc.Slider(min=8000,max=74000,step=2000,id='stromverbrauch_mfh'),
])
industrie_content=html.Div(children=[
    html.H4('Industriegebäude'),
    html.Div('Standort'),
    dcc.Input(id='standort',placeholder='Postleitzahl oder Adresse',persistence='local'),
    html.Div('Nordsee',id='region'),
    html.Div('Industriezweig'),
    dcc.Dropdown(['office','Schule'],value='office',id='industriezweig',),
    html.Div('Stromverbrauch in kWh'),
    dcc.Slider(min=8000,max=74000,step=2000,id='stromverbrauch_industrie'),
    html.Div('Batteriestrategie'),
    dcc.RadioItems(['Eigenverbrauchserhöhung', 'Lastspitzenkappung']),
])
pv_content=html.Div(children=[
    html.Div(html.H4('Photovoltaik')),
    dcc.Input(type='number',min=1,max=200)
])
EFH_container = dbc.Container(
                    [
                    dbc.Row(
                        [
                        dbc.Col(efh_content, md=12),
                        ],
                    align="top",
                    ),
                    ],
                    fluid=True,
                    )
MFH_container = dbc.Container(
                    [
                    dbc.Row(
                        [
                        dbc.Col(mfh_content, md=12),
                        ],
                    align="top",
                    ),
                    ],
                    fluid=True,
                    )
Industrie_container = dbc.Container(
                    [
                    dbc.Row(
                        [
                        dbc.Col(industrie_content, md=12),
                        ],
                    align="top",
                    ),
                    ],
                    fluid=True,
                    )
content_1 = """Hier stehen Details wofür das Tool ist und was gemacht werden kann!"""
content_2 = html.Div(html.Div(
        children=[
            html.Div(
                children=[
                    dcc.Tabs(children=[
                        dcc.Tab(label='Gebäude',
                        children=(
                            html.Div(html.H3('Gebäudewahl:'),
                            ),
                            html.Button(html.Div([DashIconify(icon="clarity:home-solid",width=230,height=230,),html.Br(),'Einfamilienhaus']),id='efh_click',n_clicks=0),
                            html.Button(html.Div([DashIconify(icon="bxs:building-house",width=230,height=230,),html.Br(),'Mehrfamilienhaus']),id='mfh_click',n_clicks=0),
                            html.Button(html.Div([DashIconify(icon="la:industry",width=230,height=230,),html.Br(),'Industrie']),id='industry_click',n_clicks=0),
                            html.Div(id='bulding_container'),
                            ),
                        ),
                        dcc.Tab(label='Technologie',
                        children=(
                            html.Div(html.H3('Technologiewahl')),
                            html.Button(html.Div([DashIconify(icon="fa-solid:solar-panel",width=230,height=230,),html.Br(),'Photovoltaik']),id='n_solar',n_clicks=0),
                            html.Button(html.Div([DashIconify(icon="mdi:gas-burner",width=230,height=230,),html.Br(),'KWK-Brenner']),id='n_chp',n_clicks=0),
                            html.Button(html.Div([DashIconify(icon="mdi:heat-pump-outline",width=230,height=230,),html.Br(),'Wärmepumpe']),id='n_hp',n_clicks=0),
                            html.Button(html.Div([DashIconify(icon="material-symbols:mode-heat",width=230,height=230,),html.Br(),'Gasheizung']),id='n_gas',n_clicks=0),
                            html.Button(html.Div([DashIconify(icon="cil:battery-3",width=230,height=230,),html.Br(),'Elektrische Batterie']),id='n_bat',n_clicks=0),#cc0
                            html.Button(html.Div([DashIconify(icon="iconoir:hydrogen",width=230,height=230,),html.Br(),'Wasserstoffspeicher']),id='n_hyd',n_clicks=0),#MIT
                            html.Div(id='technology')
                        )                                
                        ),
                    ]),
                
                ]
            
            ),
        ], 
))



content_3 = html.Div(
        id='main_page',
        children=[
            dcc.Location(id='url', refresh=False),
            html.Div(
                id='app-page-content',
                children=html.Div(
        children=[dbc.Container(
                    [
                    dbc.Row(
                        [
                        dbc.Col(html.Div(children=[
                        dcc.Tabs(id='forna-tabs', value='what-is', children=[
                        dcc.Tab(label='About',value='what-is',
                            children=html.Div(className='control-tab', children=[
                                html.H4(className='what-is', children='What is FornaContainer?'),
                                dcc.Markdown('''
                                FornaContainer is a force-directed graph that is
                                used to represent the secondary structure of nucleic
                                acids (i.e., DNA and RNA).
                                In the "Add New" tab, you can enter a sequence
                                by specifying the nucleotide sequence and the
                                dot-bracket representation of the secondary
                                structure.
                                In the "Sequences" tab, you can select which
                                sequences will be displayed, as well as obtain
                                information about the sequences that you have
                                already created.
                                In the "Colors" tab, you can choose to color each
                                nucleotide according to its base, the structural
                                feature to which it belongs, or its position in
                                the sequence; you can also specify a custom color
                                scheme.
                                '''),
                                html.Button(html.Div([DashIconify(icon="carbon:analytics",width=100,height=100,),html.Br(),'Autarkie erhöhen']),id='autakie_click',n_clicks=0,style={'background-color': 'white','color': 'black'}),
                                html.Button(html.Div([DashIconify(icon="carbon:chart-multi-line",width=100,height=100,),html.Br(),'Lastspitzenkappung']),id='LSK_click',n_clicks=0,style={'background-color': 'white','color': 'black'}),
                            ])
                        ),
                        dcc.Tab(label='Gebäude',className='parameter',value='parameter',
                        children=(
                            html.Div(html.H3('Gebäudewahl:'),
                            ),
                            html.Button(html.Div([DashIconify(icon="clarity:home-solid",width=100,height=100,),html.Br(),'Einfamilienhaus']),id='efh_click',n_clicks=0),
                            html.Button(html.Div([DashIconify(icon="bxs:building-house",width=100,height=100,),html.Br(),'Mehrfamilienhaus']),id='mfh_click',n_clicks=0),
                            html.Button(html.Div([DashIconify(icon="la:industry",width=100,height=100,),html.Br(),'Industrie']),id='industry_click',n_clicks=0),
                            html.Div(id='bulding_container'),
                            ),
                        ),
                        dcc.Tab(
                            label='Ökonomie',
                            value='show-sequences',
                            children=html.Div(className='control-tab', children=[
                                html.Div(
                                    className='app-controls-block',
                                    children=[
                                        html.Div(
                                            className='fullwidth-app-controls-name',
                                            children='Sequences to display'
                                        ),
                                        html.Div(
                                            className='app-controls-desc',
                                            children='Choose the sequences to display by ID.'
                                        ),
                                        html.Br(),
                                        dcc.Dropdown(
                                            id='forna-sequences-display',
                                            multi=True,
                                            clearable=True,
                                            value=['PDB_01019']
                                        )
                                    ]
                                ),
                                html.Hr(),
                                html.Div(
                                    className='app-controls-block',
                                    children=[
                                        html.Div(
                                            className='app-controls-block',
                                            children=[
                                                html.Div(
                                                    className='fullwidth-app-controls-name',
                                                    children='Sequence information by ID'
                                                ),
                                                html.Div(
                                                    className='app-controls-desc',
                                                    children='Search for a sequence by ID ' +
                                                    'to get more information.'
                                                ),
                                                html.Br(),
                                                dcc.Dropdown(
                                                    id='forna-sequences-info-search',
                                                    clearable=True
                                                ),
                                                html.Br(),
                                                html.Div(id='forna-sequence-info')
                                            ]
                                        )
                                    ]
                                )
                            ])
                        ),
                    ]),
            ]),md=4),
                    dbc.Col(html.Div(children=[html.Div(
                        dcc.Graph(id='forna-container')),
            dcc.Store(id='forna-custom-colors')]),md=8)#row
            ],align="top",
                    ),
                    ],
                    fluid=True,)]))])

layout = html.Div([
    dtc.SideBar([
        dtc.SideBarItem(id='id_1', label="Info", icon="fas fa-info"),
        dtc.SideBarItem(id='id_2', label="Gebäude", icon="fas fa-home"),
        dtc.SideBarItem(id='id_3', label="Ergebnis", icon="far fa-list-alt"),
    ]),
    html.Div([
    ], id="page_content"),
])
app.layout=layout

@app.callback(
    Output('forna-tabs', 'value'), 
    Input('autakie_click', 'n_clicks'),
    Input('LSK_click', 'n_clicks'),
    )
def next_Tab(autarkie,LSK):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if changed_id.startswith('aut'):
        return 'parameter'
    elif changed_id.startswith('LSK'):
        return 'parameter'
    else:
        return 'what-is'

@app.callback(
    Output('region', 'children'),
    Input('standort', 'value'))
def standorttoregion(standort):
    return html.Div(str(region[getregion(standort)-1]))

@app.callback(
    Output('n_solar', 'style'), 
    Input('n_solar', 'n_clicks'),
    )
def change_solar_style(n_clicks):
    if (n_clicks%2)==1:
        return {'background-color': 'green','color': 'white',}
    else:
        return {'background-color': 'white','color': 'black'}
@app.callback(
    Output('n_chp', 'style'), 
    Output('n_chp', 'n_clicks'), 
    Input('n_chp', 'n_clicks'),
    State('n_hp','style'),
    State('n_gas','style'))
def change_chp_style(n_clicks,hp,gas):
    if (n_clicks%2)==1:
        if (hp['color']=='black') & (gas['color']=='black'):
            return {'background-color': 'white','color': 'black'},2
        return {'background-color': 'green','color': 'white',},1
    else:
        return {'background-color': 'white','color': 'black'},2
@app.callback(
    Output('n_hp', 'style'), 
    Output('n_hp', 'n_clicks'), 
    Input('n_hp', 'n_clicks'),
    State('n_chp', 'style'),
    State('n_gas', 'style'),
    )
def change_hp_style(n_clicks,n_chp,n_gas):
    if (n_clicks%2)==1:
        return {'background-color': 'green','color': 'white',},1
    else:
        if None!=n_chp:
            if (n_chp['color']=='white')&(n_gas['color']=='black'):
                return {'background-color': 'green','color': 'white',},1
        return {'background-color': 'white','color': 'black'},2
@app.callback(
    Output('n_gas', 'style'), 
    Output('n_gas', 'n_clicks'), 
    Input('n_gas', 'n_clicks'),
    State('n_chp', 'style'),
    State('n_hp', 'style'),)
def change_gas_style(n_clicks,n_chp,n_hp):
    if (n_clicks%2)==1:
        return {'background-color': 'green','color': 'white',},1
    else:
        if None!=n_chp:
            if (n_chp['color']=='white')&(n_hp['color']=='black'):
                return {'background-color': 'green','color': 'white',},1
        return {'background-color': 'white','color': 'black'},2
@app.callback(
    Output('n_bat', 'style'), 
    Input('n_bat', 'n_clicks'),)
def change_bat_style(n_clicks):
    if (n_clicks%2)==1:
        return {'background-color': 'green','color': 'white',}
    else:
        return {'background-color': 'white','color': 'black'}
@app.callback(
    Output('n_hyd', 'style'), 
    Input('n_hyd', 'n_clicks'),)
def change_hyd_style(n_clicks):
    if (n_clicks%2)==1:
        return {'background-color': 'green','color': 'white',}
    else:
        return {'background-color': 'white','color': 'black'}

@app.callback(
    Output('technology','children'), 
    Input('n_solar', 'style'),
    Input('n_chp', 'style'),
    Input('n_hp', 'style'),
    Input('n_gas', 'style'),
    Input('n_bat', 'style'),
    Input('n_hyd', 'style'),)
def built_technology(n_solar,n_chp,n_hp,n_gas,n_bat,n_hyd):
    technology_list=[]
    if n_solar['color']=='white':
        technology_list.append(pv_content)
    if n_chp['color']=='white':
        technology_list.append(html.Div('n_chp'))
    if n_hp['color']=='white':
        technology_list.append(html.Div('n_hp'))
    if n_gas['color']=='white':
        technology_list.append(html.Div('n_gas'))
    if n_bat['color']=='white':
        technology_list.append(html.Div('n_bat'))
    if n_hyd['color']=='white':
        technology_list.append(html.Div('n_hyd'))
    return html.Div(children=technology_list)

@app.callback(
    Output('forna-container','figure'),
    State('standort','value'),
    Input('baustandart_sfh','value'),
    Input('wohraum_efh','value'),
    Input('n_bewohner_efh','value'),
    Input('stromverbrauch_efh','value'),
)
def show_results(standort,baustandart_sfh,wohraum_efh,n_bewohner_efh,stromverbrauch_efh):
    #print(region[getregion(standort)-1])
    dff=df_sfh.loc[(df_sfh['personen']==n_bewohner_efh)&(df_sfh['stromverbrauch']==stromverbrauch_efh)&(df_sfh['size']==wohraum_efh)&(df_sfh['baustand']==baustandart_sfh)]
    fig=px.scatter(dff,x='personen',y='Kosten')
    return fig


@app.callback(
    Output('bulding_container','children'),
    Output('efh_click', 'style'), 
    Output('mfh_click', 'style'), 
    Output('industry_click', 'style'), 
    Input('efh_click','n_clicks'),
    Input('mfh_click','n_clicks'),
    Input('industry_click','n_clicks'),
)
def getcontainer(efh_click,mfh_click,industy_click):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if changed_id.startswith('efh'):
        return EFH_container,{'background-color': 'green','color': 'white',},{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'}
    elif changed_id.startswith('mfh'):
        return MFH_container,{'background-color': 'white','color': 'black'},{'background-color': 'green','color': 'white',},{'background-color': 'white','color': 'black'}
    elif changed_id.startswith('industry'):
        return Industrie_container,{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'},{'background-color': 'green','color': 'white',}
    else:
        return 'Press a Housing option',{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'}

"""@app.callback(
    Output("page_content", "children"),
    Input("forna-tabs", "value"),
)"""

@app.callback(
    Output("page_content", "children"),
    Input("id_1", "n_clicks_timestamp"),
    Input("id_2", "n_clicks_timestamp"),
    Input("id_3", "n_clicks_timestamp"),
    
)
def toggle_collapse(input1, input2, input3):
    btn_df = pd.DataFrame({"input1": [input1], "input2": [input2],
                           "input3": [input3]})
    
    btn_df = btn_df.fillna(0)

    if btn_df.idxmax(axis=1).values == "input1":
        return content_1
    if btn_df.idxmax(axis=1).values == "input2":
        return content_2
    if btn_df.idxmax(axis=1).values == "input3":
        return content_3

if __name__ == '__main__':
    app.run_server(debug=True)