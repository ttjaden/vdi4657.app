# Dash
from dash import Dash, html, dcc, Input, Output, State, callback_context,ctx
from dash.exceptions import PreventUpdate
# Dash community libraries
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
# Data management
import pandas as pd
import numpy as np
# Plots
import plotly_express as px
# Additional informations
from datetime import datetime
# Eigene Funktionen
from utils.PLZtoWeatherRegion import getregion
import utils.simulate as sim

##################################################
# TODOs ##########################################
##################################################
# Abstand zwisschen Container und Header
# Startbild, falls noch nichts fertig parametriert werden

# App konfigurieren
# Icons via Iconify: siehe ps://icon-sets.iconify.design
app = Dash(__name__,
          suppress_callback_exceptions=True, 
          external_stylesheets=[dbc.themes.BOOTSTRAP,{'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css','rel': 'stylesheet','integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf','crossorigin': 'anonymous'}],
          meta_tags=[{'name': 'viewport', 'inhalt': 'width=device-width, initial-scale=1'},
          ],
          )

# Übersetzungstabelle (noch nicht durchgängig genutzt)
language=pd.read_csv('src/utils/translate.csv')

# PV-Größentabelle erstellen
# TODO Umbau auf Callback mit Gebäudestrombedarf
PV=[]
pv_dict=dict()
pv_dict[0]=str(0)
for i in range(0,10,1):
    PV.append(i)
pv_dict[len(PV)]=str(i+1)
for i in range(10,20,2):
    PV.append(i)
pv_dict[len(PV)]=str(i+2)
for i in range(20,50,5):
    PV.append(i)
pv_dict[len(PV)]=str(i+5)
for i in range(50,100,10):
    PV.append(i)
pv_dict[len(PV)]=str(i+10)
for i in range(100,220,20):
    PV.append(i)
pv_dict[len(PV)-1]=str(i)

##################################################
# Definiton grafischer Elemente / Inhalte ########
##################################################

# Header #########################################

button_expert = dbc.Button(
    html.Div(id='button_expert_content',children=[DashIconify(icon='bi:toggle-off',width=100,height=30,),'Expert']),
    id='button_expert',
    outline=True,
    color='info',
    style={'textTransform': 'none'},
)

button_language = dbc.Button(
    html.Div(id='button_language_content',children=[DashIconify(icon='emojione:flag-for-germany',width=30,height=30,),'Sprache']),
    outline=True,
    color='primary',
    id='button_language',
    style={'text-transform': 'none'},
    value='ger'
)

header=dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H4('PIEG-Strom Webtool'),
                                    html.P('Auslegung von Batteriespeichern'),
                                ],
                                id='app-title',
                            )
                        ],
                        md=True,
                        align='center',
                    ),
                ],
                align='center',
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.NavbarToggler(id='navbar-toggler'),
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavItem(button_expert,style={'width':'150'}),
                                        dbc.NavItem(button_language,style={'width':'150'}),
                                    ],
                                    navbar=True,
                                ),
                                id='navbar-collapse',
                                navbar=True,
                            ),
                        ],
                        md=3,
                    ),
                ],
                align='center',
            ),
        ],
        fluid=True,
    ),
    dark=True,
    color='#212529',
    sticky='top',
)

################################################
# Erstellung der Main-Page

content = html.Div(
                children=[dbc.Container(
                    [
                    dbc.Row(
                        [
                        dbc.Col(html.Div(id='scroll',children=[
                            dcc.Tabs(id='tabs',value='tab_info'),
                            html.Div(id='tab-content')
                        ]),md=4),
                        dbc.Col(html.Div(children=[html.Div(id='bat_results'),
                                                    html.Div(id='cost_result')])),
                    ],align='top',
                    ),
                    dcc.Store(id='last_triggered_building'),
                    dcc.Store(id='p_el_hh'),
                    dcc.Store(id='pv_all'),
                    dcc.Store(id='c_pv1'),
                    dcc.Store(id='c_pv2'),
                    dcc.Store(id='p_pv1'),
                    dcc.Store(id='p_pv2'),
                    dcc.Store(id='batteries'),
                    dcc.Store(id='E_gf'),
                    dcc.Store(id='E_gs'),
                    dcc.Store(id='electricity_price_buy'),
                    dcc.Store(id='electricity_price_sell'),
                    
                    ],
                fluid=True)])
# Layout erstellen
layout = html.Div(id='app-page-content',children=[header,content])
app.layout=layout

###################################################
#Callbacks#########################################
###################################################

#create tabs and change language
@app.callback(
    Output('button_language_content', 'children'),
    Output('button_language', 'value'),
    Output('app-title','children'),
    Output('tabs','children'),
    Input('button_language', 'n_clicks'),
)
def change_language(n_language):
    if n_language==None or n_language%2==0:
        lang='ger'
        flag='emojione:flag-for-germany'
    else:
        lang='eng'
        flag='emojione:flag-for-united-kingdom'
    return ([DashIconify(icon=flag, width=30,height=30,),language.loc[language['name']=='lang',lang].iloc[0]],
                lang,
                [html.H4('PIEG-Strom Webtool'),html.P(language.loc[language['name']=='header_p',lang].iloc[0])],
                [dcc.Tab(label='Anwendung',value='tab_info',children=[html.Div(children=[
                                    html.H4(children='Was kann PIEG Strom Webtool?'),
                                    html.Div(children=language.loc[language['name']=='tab_info_1',lang].iloc[0]),
                                    html.Button(html.Div([DashIconify(icon='grommet-icons:optimize',width=100,height=100,),html.Br(),language.loc[language['name']=='increase_autarky',lang].iloc[0]]),id='autakie_click',n_clicks=0,style={'background-color': 'white','color': 'black'}),
                                    html.Button(html.Div([DashIconify(icon='grommet-icons:time',width=100,height=100,),html.Br(),language.loc[language['name']=='peak_shaving',lang].iloc[0]]),id='LSK_click',n_clicks=0,style={'background-color': 'white','color': 'black'}),
                                ])]),
                dcc.Tab(label='System',value='tab_parameter',),
                dcc.Tab(label=language.loc[language['name']=='economics',lang].iloc[0], value='tab_econmics',)]
        )

#render tab content
@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value'),
    State('LSK_click','n_clicks'),
    Input('button_language','value'),
)
def render_content(tab,LSK,lang):
    if tab=='tab_parameter':
        if LSK==0:
            return html.Div(className='para',id='para',children=[
                html.Br(),
                dbc.Container(
                    [
                        dbc.Row(
                            [
                            dbc.Col(html.Div(children=[
                                html.H3(language.loc[language['name']=='location',lang].iloc[0]),
                                dcc.Input(id='standort',placeholder=language.loc[language['name']=='placeholder_location',lang].iloc[0],persistence='local'),
                            ]), md=6),
                            dbc.Col(html.Div(children=[
                                html.Div(id='region'),
                            ]), md=6),
                            ],
                        align='center',
                        ),
                    ],
                    fluid=True,
                ),
                html.Br(),
                dbc.Container(
                    [
                        dbc.Row(
                            [
                            dbc.Col(html.H3(language.loc[language['name']=='choose_building',lang].iloc[0]), md=4),
                            dbc.Col(dcc.Checklist(options={'True': 'Heizen und Warmwasser berücksichtigen?'},id='include_heating'), md=8),
                            ],
                        align='center',
                        ),
                    ],
                    fluid=True,
                ),
                html.Button(html.Div([DashIconify(icon='clarity:home-solid',width=50,height=50,),html.Br(),language.loc[language['name']=='efh_name',lang].iloc[0]],style={'width':'20vh'}),id='efh_click'),
                html.Button(html.Div([DashIconify(icon='bxs:building-house',width=50,height=50,),html.Br(),language.loc[language['name']=='mfh_name',lang].iloc[0]],style={'width':'20vh'}),id='mfh_click'),
                html.Button(html.Div([DashIconify(icon='la:industry',width=50,height=50,),html.Br(),language.loc[language['name']=='industry_name',lang].iloc[0]],style={'width':'20vh'}),id='industry_click'),
                html.Br(),
                html.Br(),
                html.Div(id='bulding_container'),
                html.Br(),
                html.Div(html.H3(language.loc[language['name']=='efh_name',lang].iloc[0])),
                html.Div(
                    html.Div(children=[html.Button(html.Div([DashIconify(icon='fa-solid:solar-panel',width=50,height=50,),html.Br(),language.loc[language['name']=='pv',lang].iloc[0]],style={'width':'20vh'}),id='n_solar',n_clicks=0),
                    html.Button(html.Div([DashIconify(icon='mdi:gas-burner',width=50,height=50,),html.Br(),language.loc[language['name']=='chp',lang].iloc[0]],style={'width':'20vh'}),id='n_chp',n_clicks=0),
                    html.Button(html.Div([DashIconify(icon='mdi:heat-pump-outline',width=50,height=50,),html.Br(),language.loc[language['name']=='hp',lang].iloc[0]],style={'width':'20vh'}),id='n_hp',n_clicks=0),
                    html.Div(id='technology')])
                ),])
        else:
            return html.Div(children='LSK')
    elif tab=='tab_econmics':
        return html.Div(children=[
            html.H4('Einspeisevergütung [ct/kWh]'),
            dcc.Slider(min=0,max=20,step=1,value=6,marks={0:'0',20:'20'},id='price_sell',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),
            html.H4('Strombezugspreis [ct/kWh]'),
            dcc.Slider(min=10,max=45,step=1,value=35,marks={10:'10',45:'45'},id='price_buy',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),
            ])
    else:
        return html.Div()

# build parameter container
# Gebäudeauswahl
@app.callback(
    Output('bulding_container','children'),
    Output('efh_click', 'style'), 
    Output('mfh_click', 'style'), 
    Output('industry_click', 'style'),    
    Output('last_triggered_building', 'data'),    
    Input('efh_click','n_clicks_timestamp'),
    Input('mfh_click','n_clicks_timestamp'),
    Input('industry_click','n_clicks_timestamp'),
    State('last_triggered_building','data'),
    Input('include_heating','value'),
    State('button_language','value'),
)
def getcontainer(efh_click,mfh_click,industry_click,choosebuilding,heating,lang):
    if (efh_click is None and mfh_click is None and industry_click is None):#changed_id = [0]
        if choosebuilding is None:
            return 'Ein Gebäudetyp wählen',{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'},None
        else:
            if choosebuilding=='efh':
                efh_click=1
            elif choosebuilding=='mfh':
                mfh_click=1
            else:
                industry_click=1
    if efh_click is None:
        efh_click=0
    if mfh_click is None:
        mfh_click=0
    if industry_click is None:
        industry_click=0
    if (efh_click>mfh_click) and (efh_click>industry_click):
        if (heating is None) or (len(heating)==0): # for simulating without heating
            return (dbc.Container(
                        [
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='energy_cons',lang].iloc[0], md=3),
                                dbc.Col(dcc.Slider(min=2000,max=8000,step=500,value=4000,marks=None,id='stromverbrauch',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'), md=5),
                                dbc.Col(html.Div(id='stromverbrauch_value'), md=4),
                                ],
                            align='center',
                            ),
                        ],
                        fluid=True,
                        ),
                    {'background-color': '#212529','color': 'white',},
                    {'background-color': 'white','color': 'black'},
                    {'background-color': 'white','color': 'black'},'efh')
        else: # with heating system
            return (dbc.Container(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(language.loc[language['name']=='energy_cons',lang].iloc[0], md=3),
                                    dbc.Col(dcc.Slider(min=2000,max=8000,step=500,value=4000,marks=None,id='stromverbrauch',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'), md=5),
                                    dbc.Col(html.Div(id='stromverbrauch_value'), md=4),
                                ],
                                align='center',
                                ),
                            dbc.Row(
                                [
                                    dbc.Col('Wohnfläche', md=3),
                                    dbc.Col(dcc.Slider(min=50,max=250,step=10,value=150,marks=None,id='wohnfläche',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'), md=5),
                                    dbc.Col(html.Div(id='wohnfläche_value'), md=4),
                                ],
                                align='center',
                                ),
                            dbc.Row(
                                [
                                    dbc.Col('Gebäudetyp', md=3),
                                    dbc.Col(dcc.Dropdown(['Bestand, unsaniert','Bestand, saniert', 'Neubau, nach 2016'],id='building_type'), md=5),
                                    dbc.Col(html.Div(id='building_type_value'), md=4),
                                ],
                                align='center',
                                )
                        ],
                        fluid=True,
                        ),
                    {'background-color': '#212529','color': 'white',},
                    {'background-color': 'white','color': 'black'},
                    {'background-color': 'white','color': 'black'},'efh')
    if (mfh_click>efh_click) and (mfh_click>industry_click):
        if (heating is None) or (len(heating)==0): # for simulating without heating
            return (dbc.Container(
                        [
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='energy_cons',lang].iloc[0], md=3),
                                dbc.Col(dcc.Slider(min=8000,max=74000,step=2000,value=16000,marks=None,id='stromverbrauch',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'), md=5),
                                dbc.Col(html.Div(id='stromverbrauch_value'), md=4),
                                ],
                            align='center',
                            ),
                        ],
                        fluid=True,
                        ),
                    {'background-color': 'white','color': 'black'},
                    {'background-color': '#212529','color': 'white',},
                    {'background-color': 'white','color': 'black'},'mfh')
        else:
            return (dbc.Container(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(language.loc[language['name']=='energy_cons',lang].iloc[0], md=3),
                                    dbc.Col(dcc.Slider(min=8000,max=74000,step=2000,value=16000,marks=None,id='stromverbrauch',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'), md=5),
                                    dbc.Col(html.Div(id='stromverbrauch_value'), md=4),
                                ],
                                align='center',
                                ),
                            dbc.Row(
                                [
                                    dbc.Col('Wohnfläche', md=3),
                                    dbc.Col(dcc.Slider(min=2,max=15,step=1,value=12,marks=None,id='wohneinheiten',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'), md=5),
                                    dbc.Col(html.Div(id='wohneinheiten_value'), md=4),
                                ],
                                align='center',
                                ),
                            dbc.Row(
                                [
                                    dbc.Col('Gebäudetyp', md=3),
                                    dbc.Col(dcc.Dropdown(['Bestand, unsaniert','Bestand, saniert', 'Neubau, nach 2016'],id='building_type'), md=5),
                                    dbc.Col(html.Div(id='building_type_value'), md=4),
                                ],
                                align='center',
                                )
                        ],
                        fluid=True,
                        ),
                {'background-color': 'white','color': 'black'},
                {'background-color': '#212529','color': 'white',},
                {'background-color': 'white','color': 'black'},'mfh')
    if (industry_click>efh_click) and (industry_click>mfh_click):
        if (heating is None) or (len(heating)==0): # for simulating without heating
            return (dbc.Container(
                        [
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='building_type_industry',lang].iloc[0], md=3),
                                dbc.Col(dcc.Dropdown(['office','Schule'],value='office',id='building_type',persistence='local'), md=5),
                                dbc.Col(html.Div(id='building_type'), md=3),
                                ],
                            align='center',
                            ),
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='energy_cons',lang].iloc[0], md=3),
                                dbc.Col(dcc.Slider(min=8000,max=74000,step=2000,value=16000,marks=None,id='stromverbrauch',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'), md=5),
                                dbc.Col(html.Div(id='stromverbrauch_value'), md=3),
                                ],
                            align='center',
                            ),
                        ],
                        fluid=True,
                        ),
                    {'background-color': 'white','color': 'black'},
                    {'background-color': 'white','color': 'black'},
                    {'background-color': '#212529','color': 'white',},'indu')
        else:
            return (dbc.Container(
                        [
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='building_type_industry',lang].iloc[0], md=3),
                                dbc.Col(dcc.Dropdown(['office','Schule'],value='office',id='building_type',persistence='local'), md=5),
                                dbc.Col(html.Div(id='building_type_value'), md=3),
                                ],
                            align='center',
                            ),
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='energy_cons',lang].iloc[0], md=3),
                                dbc.Col(dcc.Slider(min=8000,max=74000,step=2000,value=16000,marks=None,id='stromverbrauch',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'), md=5),
                                dbc.Col(html.Div(id='stromverbrauch_value'), md=3),
                                ],
                            align='center',
                            ),
                            dbc.Row(
                                [
                                dbc.Col('Normheizlast', md=3),
                                dbc.Col(dcc.Slider(min=5,max=150,step=5,value=125,marks=None,id='normheizlast',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'), md=5),
                                dbc.Col(html.Div(id='normheizlast_value'), md=3),
                                ],
                            align='center',
                            ),
                        ],
                        fluid=True,
                        ),
                    {'background-color': 'white','color': 'black'},
                    {'background-color': 'white','color': 'black'},
                    {'background-color': '#212529','color': 'white',},'indu')

# Add technology to the tab 'tab_parameter'
@app.callback(
    Output('technology','children'), 
    Input('n_solar', 'style'),
    Input('n_chp', 'style'),
    Input('n_hp', 'style'),
    Input('button_language','value'),)
def built_technology(n_solar,n_chp,n_hp,lang):
    technology_list=[]
    if n_solar['color']=='white':
        technology_list.append(dbc.Container(
                        [
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='pv',lang].iloc[0], md=3),
                                dbc.Col(dcc.Slider(min=0,max=len(PV)-1,step=1,marks=pv_dict, id='pv_slider',value=10,persistence='local'), md=5),
                                dbc.Col(html.Div(id='pv_slider_value'), md=4),
                                ],
                            align='center',
                            ),
                        ],
                        fluid=True,
                        ))
    if n_chp['color']=='white':
        technology_list.append(dbc.Container(
                        [
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='chp',lang].iloc[0], md=3),
                                dbc.Col(dcc.Dropdown([1,2], id='chp_technology',value=10,persistence='local'), md=5),
                                dbc.Col(html.Div(id='chp_technology_value'), md=4),
                                ],
                            align='center',
                            ),
                        ],
                        fluid=True,
                        ))
    if n_hp['color']=='white':
        technology_list.append(dbc.Container(
                        [
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='hp',lang].iloc[0], md=3),
                                dbc.Col(dcc.Dropdown(['Luft/Wasser (mittl. Effizienz)','Sole/Wasser (mittl. Effizienz)'], id='hp_technology',value=10,persistence='local'), md=5),
                                dbc.Col(html.Div(id='hp_technology_value'), md=4),
                                ],
                            align='center',
                            ),
                        ],
                        fluid=True,
                        ))
    return html.Div(children=technology_list)

#change tabs with buttons on Info-Tab (Autarky or Peak shaving)
@app.callback(
    Output('tabs', 'value'),
    Output('autakie_click', 'n_clicks'),
    Output('LSK_click', 'n_clicks'),
    Input('autakie_click', 'n_clicks'),
    Input('LSK_click', 'n_clicks'),
    State('tabs','value')
    )
def next_Tab(autarkie,LSK,tab):
    if (autarkie==0) & (LSK==0):
        return tab,0,0
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if changed_id.startswith('aut'):
        return 'tab_parameter',1,0
    elif changed_id.startswith('LSK'):
        return 'tab_parameter',0,1
    else:
        return tab,0,0
        
#specific functions for a certain purpose##################

@app.callback(
    Output('region', 'children'),
    Input('standort', 'value'),
    Input('button_language','value'))
def standorttoregion(standort,lang):
    return html.Div(language.loc[language['name']==str(getregion(standort)),lang].iloc[0])

@app.callback(
    Output('p_el_hh', 'data'),
    Input('stromverbrauch', 'value'),
    State('last_triggered_building','data'))
def get_p_el_hh(e_hh,building):
    if building=='efh':
        p_el=pd.read_csv('src/assets/data/electrical_loadprofiles/LP_W_EFH.csv')
    elif building=='mfh':
        if e_hh>8000:
            p_el=pd.read_csv('src/assets/data/electrical_loadprofiles/LP_W_MFH_k.csv')

        elif e_hh>15000:
            p_el=pd.read_csv('src/assets/data/electrical_loadprofiles/LP_W_MFH_m.csv')
        elif e_hh>45000:
            p_el=pd.read_csv('src/assets/data/electrical_loadprofiles/LP_W_MFH_g.csv')
    else:
        p_el=pd.read_csv('src/assets/data/electrical_loadprofiles/LP_G_G.csv')
    return (p_el.iloc[:,1].values*e_hh/1000).tolist()

@app.callback(
    Output('n_solar', 'style'),
    Input('n_solar', 'n_clicks'),
    )
def change_solar_style(n_clicks):
    if (n_clicks%2)==1:
        return {'background-color': '#212529','color': 'white',}
    else:
        return {'background-color': 'white','color': 'black'}
@app.callback(
    Output('n_solar2', 'style'), 
    Input('n_solar2', 'n_clicks'),
    )
def change_gas_style(n_clicks):
    if (n_clicks%2)==1:
        return {'background-color': '#212529','color': 'white',}
    else:
        return {'background-color': 'white','color': 'black'}
"""@app.callback(
    Output('n_hp', 'style'), 
    Output('n_hp', 'n_clicks'), 
    Input('n_hp', 'n_clicks'),
    State('n_chp', 'style'),
    State('n_gas', 'style'),
    )
def change_hp_style(n_clicks,n_chp,n_gas):
    if (n_clicks%2)==1:
        return {'background-color': '#212529','color': 'white',},1
    else:
        if None!=n_chp:
            if (n_chp['color']=='white')&(n_gas['color']=='black'):
                return {'background-color': '#212529','color': 'white',},1
        return {'background-color': 'white','color': 'black'},2"""
@app.callback(
    Output('n_chp', 'style'),
    Output('n_chp','n_clicks'), 
    Output('n_hp','style'), 
    Output('n_hp','n_clicks'), 
    Input('n_chp', 'n_clicks'),
    Input('n_hp','n_clicks'), 
    )
def change_chp_style(n_chp,n_hp):
    if ((n_hp%2==0) and (n_chp%2==0)) or (n_chp>=3) or (n_hp>=3):
        return {'background-color': 'white','color': 'black'},0,{'background-color': 'white','color': 'black'},0
    elif (n_chp%2)==1:
        return {'background-color': '#212529','color': 'white'},2,{'background-color': 'white','color': 'black'},0
    elif n_hp%2==1:
        return {'background-color': 'white','color': 'black'},0,{'background-color': '#212529','color': 'white'},2

@app.callback(
    Output('c_pv1', 'data'), 
    Input('standort','value'),)
def calc_pv_power1(location):
    orientation=180
    tilt=35
    type='a'
    year=2015
    pv1=sim.calc_pv(trj=getregion(location)-1,year=year,type=type,tilt=tilt,orientation=orientation)
    return pv1
@app.callback(
    Output('c_pv2', 'data'), 
    Input('standort','value'),)
def calc_pv_power2(location):
    orientation=180
    tilt=35
    type='a'
    year=2015
    pv2=sim.calc_pv(trj=getregion(location)-1,year=year,type=type,tilt=tilt,orientation=orientation)
    return pv2
@app.callback(
    Output('p_pv1', 'data'), 
    Input('pv_slider','value'),
    Input('c_pv1','data'),)
def scale_pv1(pv_slider1, pv1):
    pv1=np.array(pv1) * PV[pv_slider1]
    return list(pv1)
@app.callback(
    Output('p_pv2', 'data'), 
    Input('pv_slider2','value'),
    Input('c_pv2','data'),)
def scale_pv2(pv_slider2, pv2):
    pv2=np.array(pv2) * PV[pv_slider2]
    return list(pv2)

@app.callback(
    Output('hp_technology_value', 'children'), 
    Input('hp_technology','value'),
    Input('standort','value'),
    Input('wohnfläche','value'),
    Input('building_type','value'),
    )
def sizing_of_heatpump(choosen_hp,location,Area,building_type):
    if choosen_hp.startswith('Sole'):
        group_id=5
    elif choosen_hp.startswith('Luft'):
        group_id=1
    buildings = pd.DataFrame([[0.6, 12, 35, 28, 1.1], [1.2, 15, 55, 45, 1.3]],
                            columns=['Q_sp', 'T_limit', 'T_vl_max',
                                    'T_rl_max', 'f_hs_exp'],
                            index=['new', 'old'])
    if building_type.endswith('unsaniert'):
        building=buildings.loc['old',:]
    elif building_type.startswith('Bestand'):
        building=buildings.loc['old',:]
    elif building_type.startswith('Neubau'):
        building=buildings.loc['new',:]
    results_timeseries, P_th_max, t_in, t_out = sim.sim_hp(getregion(location),Area,building,group_id)
    return (html.Div(str(round(P_th_max/1000,1))+' kWth'),html.Div('(' + str(t_in)+ '° / ' + str(t_out) + '°)'))


@app.callback(
    Output('stromverbrauch_value', 'children'),
    Input('stromverbrauch', 'value'),
    )
def print_stromverbrauch_value(stromverbrauch):
    return html.Div(str(stromverbrauch)+ ' kWh/a')
@app.callback(
    Output('wohnfläche_value', 'children'),
    Input('wohnfläche', 'value'),
    )
def print_wohnfläche_value(wohnfläche):
    return html.Div(str(wohnfläche)+ ' m²')
@app.callback(
    Output('wohneinheiten_value', 'children'),
    Input('wohneinheiten', 'value'),
    )
def print_wohneinheiten_value(wohneinheiten):
    return html.Div(str(wohneinheiten)+ ' WE')
@app.callback(
    Output('normheizlast_value', 'children'),
    Input('normheizlast', 'value'),
    )
def print_normheizlast_value(normheizlast):
    return html.Div(str(normheizlast)+ ' kW')
@app.callback(
    Output('pv_slider_value', 'children'),
    Input('pv_slider', 'value'),
    )
def print_pv_slider_value(pv_slider):
    return html.Div(str(PV[pv_slider])+ ' kWp')

@app.callback(
    Output('electricity_price_buy', 'data'),
    Input('price_buy', 'value'),
    )
def change_price_buy(price_buy):
    return price_buy
@app.callback(
    Output('electricity_price_sell', 'data'),
    Input('price_sell', 'value'),
    )
def change_price_buy(price_sell):
    return price_sell

@app.callback(
    Output('button_expert', 'children'),
    Input('button_expert', 'n_clicks'),
)
def expertmode(n1):
    if n1 is None:
        raise PreventUpdate
    if n1%2==1:
        return [DashIconify(icon='bi:toggle-on',width=100,height=30,),'Expert']
    else: 
        return [DashIconify(icon='bi:toggle-off',width=100,height=30,),'Expert']

@app.callback(
    Output('navbar-collapse', 'is_open'),
    [Input('navbar-toggler', 'n_clicks')],
    [State('navbar-collapse', 'is_open')],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

#create results

@app.callback(
    Output('batteries', 'data'),
    Output('E_gs', 'data'),
    Output('E_gf', 'data'),
    Input('p_el_hh','data'), 
    Input('p_pv1', 'data'),
    Input('p_pv2', 'data'),
    Input('n_solar', 'n_clicks'),
    State('p_el_hh','data'),)
def calc_bat_results(p_el_hh,pv1,pv2,n_pv1,p_el):
    df=pd.DataFrame()
    year=datetime.now().date().year
    df.index=pd.date_range(start=str(year)+'-01-01', end=str(year+1)+'-01-01', periods=35041)[0:35040]
    if (pv1 is None) or ((n_pv1%2)!=1):
        pv1=np.zeros(35040).tolist()
    if (pv2 is None) or ((n_pv2%2)!=1):
        pv2=np.zeros(35040).tolist()
    df['p_el_hh']=p_el_hh
    df['p_PV']=np.array(pv1)+np.array(pv2)
    if df['p_PV'].mean()==0:
        return None, None , None
    E_el_MWH = np.array(p_el).mean()*8.76/1000
    E_pv_kwp = df['p_PV'].mean()*8.76/1000
    batteries=sim.calc_bat(df, round(np.minimum(E_el_MWH*1.5,E_pv_kwp*1.5),1))
    return batteries.to_dict(),batteries['E_gs'].values.tolist(),batteries['E_gf'].values.tolist()

@app.callback(
    Output('bat_results', 'children'),
    Input('batteries', 'data'),
    Input('tabs', 'value'),
    )
def bat_results(batteries,tab):
    if (batteries is None) or (tab!='tab_parameter'):
        return html.Div()
    return html.Div(children=[html.Br(),dcc.RadioItems(['Autarkiegrad','Eigenverbrauchsanteil','Energiebilanz'],'Autarkiegrad',id='show_bat_results'),html.Div(id='bat_result_graph')])
@app.callback(
    Output('bat_result_graph', 'children'),
    Input('batteries', 'data'),
    Input('tabs', 'value'),
    Input('show_bat_results', 'value'),
    )
def bat_results(batteries,tab,results_id):
    if (batteries is None) or (tab!='tab_parameter'):
        return html.Div()
    batteries=pd.DataFrame.from_dict(batteries)
    if results_id=='Autarkiegrad':
        fig=px.line(data_frame=batteries,x='e_bat',y='A',title='Autarkiegrad with different battery sizes')
    elif results_id=='Eigenverbrauchsanteil':
        fig=px.line(data_frame=batteries,x='e_bat',y='E',title='Eigenverbrauchsanteil with different battery sizes')
    elif results_id=='Energiebilanz':
        fig=px.line(data_frame=batteries,x='e_bat',y=['A','E'],title='Self-sufficiency and Self-consumption with different battery sizes')
    return dcc.Graph(figure=fig)

@app.callback(
    Output('cost_result', 'children'),
    State('E_gs', 'data'),
    State('E_gf', 'data'),
    Input('electricity_price_buy','data'), 
    Input('electricity_price_sell', 'data'),
    Input('tabs', 'value'),
    )
def economic_results(E_gs,E_gf,electricity_price_buy,electricity_price_sell,tab):
    if (electricity_price_buy is None) or (E_gs is None) or (tab!='tab_econmics'): 
        return html.Div()
    return html.Div(children=[dcc.RadioItems([1,2,3],id='show_economic_results'),html.Div(id='cost_result_graph')])
@app.callback(
    Output('cost_result_graph', 'children'),
    State('E_gs', 'data'),
    State('E_gf', 'data'),
    Input('electricity_price_buy','data'), 
    Input('electricity_price_sell', 'data'),
    Input('tabs', 'value'),
    Input('show_economic_results', 'value'),
    )
def economic_results_graph(E_gs,E_gf,electricity_price_buy,electricity_price_sell,tab,results_id):
    if (electricity_price_buy is None) or (E_gs is None) or (tab!='tab_econmics'): 
        return html.Div()
    return dcc.Graph(figure=px.line(y=np.array(E_gs)*(-electricity_price_buy/100)-np.array(E_gf)*electricity_price_sell/100,title='Jahreskosten über Batteriegröße'))
if __name__ == '__main__':
    app.run_server(debug=True)