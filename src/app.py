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
# Own functions
from utils.getregion import getregion
import utils.simulate as sim
import utils.economy as eco

##################################################
# TO DOs ##########################################
##################################################
# TODO Space between header and container
# TODO Translation
# TODO Save all inputs in a dataframe for import/export

# App configuration
# Icons from iconify, see https://icon-sets.iconify.design
app = Dash(__name__,
          suppress_callback_exceptions=True, 
          external_stylesheets=[dbc.themes.BOOTSTRAP,{'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css','rel': 'stylesheet','integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf','crossorigin': 'anonymous'}],
          meta_tags=[{'name': 'viewport', 'inhalt': 'width=device-width, initial-scale=1'},
          ],
          )

# Table for translation (work in progress)
language=pd.read_csv('src/utils/translate.csv')

# Weather information for all regions
weather_summary=pd.read_csv('src/assets/data/weather/TRJ-Tabelle.csv')

##################################################
# Definiton of graphical elements / content ######
##################################################

# Header #########################################

button_expert = dbc.Button(
    html.Div(id='button_expert_content',children=[DashIconify(icon='bi:toggle-off',width=50,height=30,),'Expert']),
    id='button_expert',
    outline=True,
    color='light',
    style={'textTransform': 'none'},
)

button_language = dbc.Button(
    html.Div(id='button_language_content',children=[DashIconify(icon='emojione:flag-for-germany',width=50,height=30,),'Sprache']),
    outline=True,
    color='light',
    id='button_language',
    style={'text-transform': 'none'},
    value='ger'
)

button_info = dbc.Button(
    html.Div(id='button_info_content',children=[DashIconify(icon='ph:info',width=50,height=30,),'Info']),
    outline=True,
    color='light',
    id='button_info',
    style={'text-transform': 'none'}
)
options_slp = [
    {"label": 'Gewerbe allgemein', "value": "LP_G0.csv"},
    {"label": "Gewerbe werktags 8–18 Uhr", "value": "LP_G1.csv"},
    {"label": "Gewerbe mit starkem bis überwiegendem Verbrauch in den Abendstunden", "value": "LP_G2.csv"},
    {"label": 'Gewerbe durchlaufend', "value": "LP_G3.csv"},
    {"label": 'Laden/Friseur', "value": "LP_G4.csv"},
    {"label": 'Bäckerei mit Backstube', "value": "LP_G5.csv"},
    {"label": 'Wochenendbetrieb', "value": "LP_G6.csv"},
    {"label": 'Landwirtschaftsbetriebe allgemein', "value": "LP_L0.csv"},
    {"label": 'Landwirtschaftsbetriebe mit Milchwirtschaft/Nebenerwerbs-Tierzucht', "value": "LP_L1.csv"},
    {"label": 'Übrige Landwirtschaftsbetriebe', "value": "LP_L2.csv"},
    {"label": 'Büro', "value": "LP_Ö_Büro"},
    {"label": 'Schule', "value": "LP_Ö_Schule"},
    {"label": 'Produzierendes Gewerbe / Metallverarbeitung', "value": "LP_G_MV.csv"},
    {"label": 'Produzierendes Gewerbe / Galvanisierung', "value": "LP_G_G.csv"},
    {"label": 'Möbelhaus', "value": "LP_G_MH.csv"},
]

header=dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H4('Auslegung von Batteriespeichern'),
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
            dcc.ConfirmDialog(
                id='info_dialog',
                message='Dummy text',
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
                                        dbc.NavItem(button_info,style={'width':'150'}),
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
# Main-Page

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
                    dcc.Store(id='n_clicks_pv'),
                    dcc.Store(id='n_clicks_chp'),
                    dcc.Store(id='n_clicks_hp'),
                    dcc.Store(id='p_el_hh'),
                    dcc.Store(id='p_th_load'),
                    dcc.Store(id='building'),
                    dcc.Store(id='pv_all'),
                    dcc.Store(id='c_pv1'),
                    dcc.Store(id='p_pv1'),
                    dcc.Store(id='power_heat_pump_W'),
                    dcc.Store(id='power_chp_W'),
                    dcc.Store(id='batteries'),
                    dcc.Store(id='price_electricity'),
                    #TODO: parameter dict
                    ],
                fluid=True)])

# Create layout
layout = html.Div(id='app-page-content',children=[header,content])
app.layout=layout

###################################################
# Callbacks #######################################
###################################################

# Create tabs and change language
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
    return ([DashIconify(icon=flag, width=50,height=30,),language.loc[language['name']=='lang',lang].iloc[0]],
                lang,
                [html.H4('Auslegung von Batteriespeichern')],
                [dcc.Tab(label='Anwendung',value='tab_info',children=[html.Div(children=[
                                    html.Br(),
                                    html.Div('Dies ist ein ergänzendes Webtool zur VDI 4657-3 "Planung und Integration von Energiespeichern in Gebäudeenergiesystemen - Elektrische Stromspeicher (ESS)"'),
                                    html.Br(),
                                    html.Div('Auswahl des Anwendungsfalls: '),
                                    html.Br(),
                                    html.Button(html.Div([DashIconify(icon='grommet-icons:optimize',width=75,height=75,),html.Br(),language.loc[language['name']=='increase_autarky',lang].iloc[0]]),id='autakie_click',n_clicks=0,
                                                                      style={'background-color': 'white','color': 'black', 'font-size': '12px', 'width': '100px', 'display': 'inline-block', 'margin-bottom': '10px', 'margin-right': '5px', 'height':'100px', 'verticalAlign': 'top'}),
                                    html.Button(html.Div([DashIconify(icon='grommet-icons:time',width=75,height=75,),html.Br(),language.loc[language['name']=='peak_shaving',lang].iloc[0]]),id='LSK_click',n_clicks=0,
                                                                      style={'background-color': 'white','color': 'black', 'font-size': '12px', 'width': '100px', 'display': 'inline-block', 'margin-bottom': '10px', 'margin-right': '5px', 'height':'100px', 'verticalAlign': 'top'}),
                                ])]),
                dcc.Tab(label='System',value='tab_parameter',),
                dcc.Tab(label=language.loc[language['name']=='economics',lang].iloc[0], value='tab_econmics',)]
        )

# Render tab content
@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value'),
    State('LSK_click','n_clicks'),
    Input('button_language','value'),
    State('n_clicks_pv','data'),
    State('n_clicks_chp','data'),
    State('n_clicks_hp','data'),
)
def render_tab_content(tab,LSK,lang,n_clicks_solar, n_clicks_chp, n_clicks_hp):
    if tab=='tab_parameter':
        if LSK==0:
            if n_clicks_solar is None:
                n_clicks_solar=0
            if n_clicks_chp is None:
                n_clicks_chp=0
            if n_clicks_hp is None:
                n_clicks_hp=0
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
                            dbc.Col(dcc.Checklist(options={'True': 'Heizen und Warmwasser berücksichtigen?'},id='include_heating',persistence='local'), md=8),
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
                html.Div([html.Div(id='wohnfläche'),html.Div(id='building_type'),html.Div(id='building_type_value')],id='bulding_container'),
                html.Br(),
                html.Div(html.H3(language.loc[language['name']=='efh_name',lang].iloc[0])),
                html.Div(
                    html.Div(children=[html.Button(html.Div([DashIconify(icon='fa-solid:solar-panel',width=50,height=50,),html.Br(),language.loc[language['name']=='pv',lang].iloc[0]],style={'width':'20vh'}),id='n_solar',n_clicks=n_clicks_solar),
                    html.Button(html.Div([DashIconify(icon='mdi:gas-burner',width=50,height=50,),html.Br(),language.loc[language['name']=='chp',lang].iloc[0]],style={'width':'20vh'}),id='n_chp',n_clicks=n_clicks_chp),
                    html.Button(html.Div([DashIconify(icon='mdi:heat-pump-outline',width=50,height=50,),html.Br(),language.loc[language['name']=='hp',lang].iloc[0]],style={'width':'20vh'}),id='n_hp',n_clicks=n_clicks_hp),
                    html.Div([html.Div(id='hp_technology'),html.Div(id='chp_technology'),html.Div(id='hp_technology_value'),html.Div(id='chp_technology_value')],id='technology')])
                ),])
        else:
            return html.Div(children=['LSK'])
    elif tab=='tab_econmics':
        return html.Div(children=[html.Div(id='battery_cost_para')])
    else:
        return html.Div()

# Info button content
@app.callback(
    Output('info_dialog', 'displayed'),
    Input('button_info','n_clicks'),
)
def display_info(n_clicks_info):
    if n_clicks_info is None:
        raise PreventUpdate
    return True

# Build parameter container
# Building selection
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
            return 'Einen Gebäudetyp wählen',{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'},None
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
                                dbc.Col(dcc.Slider(min=2000,max=10000,step=500,value=4000,marks=None,id='stromverbrauch',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'), md=5),
                                dbc.Col(html.Div(id='stromverbrauch_value'), md=4),
                                html.Div(id='industry_type'),
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
                                    html.Div(id='industry_type'),
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
                                    dbc.Col(dcc.Dropdown(['Bestand, unsaniert','Bestand, saniert', 'Neubau, nach 2016'],id='building_type',persistence='local'), md=5),
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
                                dbc.Col(dcc.Slider(min=5000,max=100000,step=5000,value=15000,marks=None,id='stromverbrauch',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'), md=5),
                                dbc.Col(html.Div(id='stromverbrauch_value'), md=4),
                                html.Div(id='industry_type'),
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
                                    dbc.Col(dcc.Slider(min=5000,max=100000,step=5000,value=15000,marks=None,id='stromverbrauch',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'), md=5),
                                    dbc.Col(html.Div(id='stromverbrauch_value'), md=4),
                                    html.Div(id='industry_type'),
                                ],
                                align='center',
                                ),
                            dbc.Row(
                                [
                                    dbc.Col('Wohneinheiten', md=3),
                                    dbc.Col(dcc.Slider(min=2,max=49,step=1,value=12,marks=None,id='wohnfläche',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'), md=5),
                                    dbc.Col(html.Div(id='wohnfläche_value'), md=4),
                                ],
                                align='center',
                                ),
                            dbc.Row(
                                [
                                    dbc.Col('Gebäudetyp', md=3),
                                    dbc.Col(dcc.Dropdown(['Bestand, unsaniert','Bestand, saniert', 'Neubau, nach 2016'],id='building_type',persistence='local'), md=5),
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
                                dbc.Col(dcc.Dropdown(options_slp,id='industry_type',persistence='local', optionHeight=100,maxHeight=400), md=5),
                                ],
                            align='center',
                            ),
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='energy_cons',lang].iloc[0], md=3),
                                dbc.Col(dcc.Input(min=5_000,max=1_000_000,step=1000,value=50_000,type='number',style=dict(width = '100%'),id='stromverbrauch',persistence='local'), md=5),
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
                                dbc.Col(dcc.Dropdown(options_slp,id='industry_type',persistence='local', optionHeight=100,maxHeight=400), md=5),
                                ],
                            align='center',
                            ),
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='energy_cons',lang].iloc[0], md=3),
                                dbc.Col(dcc.Input(min=5_000,max=1_000_000,step=1000,value=50_000,type='number',style=dict(width = '100%'),id='stromverbrauch',persistence='local'), md=5),
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
    Input('button_language','value'),
    Input('last_triggered_building','data'),
    )
def built_technology(n_solar,n_chp,n_hp,lang,building):
    technology_list=[]
    if n_solar['color']=='white':
        if building=='efh':
            technology_list.append(dbc.Container(
                        [
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='pv',lang].iloc[0], md=3),
                                dbc.Col(dcc.Slider(min=0,max=20,step=1,marks=None, id='pv_slider',value=10,persistence='local'), md=5),
                                dbc.Col(html.Div(id='pv_slider_value'), md=4),
                                ],
                            align='center',
                            ),
                        ],
                        fluid=True,
                        ))
        elif (building=='mfh') or (building=='indu'):
            technology_list.append(dbc.Container(
                        [
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='pv',lang].iloc[0], md=3),
                                dbc.Col(dcc.Slider(min=0,max=200,step=5,marks=None, id='pv_slider',value=10,persistence='local'), md=5),
                                dbc.Col(html.Div(id='pv_slider_value'), md=4),
                                ],
                            align='center',
                            ),
                        ],
                        fluid=True,
                        ))
        else:
            technology_list.append(html.Div('Einen Gebäudetyp wählen'))
    else:
        technology_list.append(
            dcc.Store(id='pv_slider')
        )
    if n_chp['color']=='white':
        technology_list.append(dbc.Container(
                        [
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='chp',lang].iloc[0], md=3),
                                dbc.Col(dcc.Slider(min=0.1,max=3,step=0.1,value=0.5,marks=None,id='chp_technology',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'), md=5),
                                dbc.Col(html.Div(id='chp_technology_value'), md=4),
                                ],
                            align='center',
                            ),
                        ],
                        fluid=True,
                        ))
    else:
        technology_list.append(
            html.Div([html.Div(id='chp_technology'),html.Div(id='chp_technology_value')])
        )
    if n_hp['color']=='white':
        technology_list.append(dbc.Container(
                        [
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='hp',lang].iloc[0], md=3),
                                dbc.Col(dcc.Dropdown(['Luft/Wasser (mittl. Effizienz)','Sole/Wasser (mittl. Effizienz)'], id='hp_technology',value=10,persistence='local', optionHeight=50), md=5),
                                dbc.Col(html.Div(id='hp_technology_value'), md=4),
                                ],
                            align='center',
                            ),
                        ],
                        fluid=True,
                        ))
    else:
        technology_list.append(
            html.Div([html.Div(id='hp_technology'),html.Div(id='hp_technology_value')])
        )
    return html.Div(children=technology_list)

# Change tabs with buttons on info tab (self-sufficiency or peak shaving)
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

# Add investment cost for batteries
@app.callback(
    Output('battery_cost_para', 'children'),
    State('batteries','data'),
    Input('tabs','value'),
    )
def next_Tab(batteries,tab):
    if batteries is None:
        return 'Zunächst System definieren.'
    I_0,exp=eco.invest_params_default()
    specific_bat_cost_small, absolut_bat_cost_small = eco.invest_costs(batteries['e_bat']['1'],I_0,exp)
    specific_bat_cost_big, absolut_bat_cost_big = eco.invest_costs(batteries['e_bat']['5'],I_0,exp)
    if tab=='tab_econmics':
        return html.Div(
            [html.H4('Investitionskosten für Batteriespeicher'),
            dbc.Container(
                        [
                            dbc.Row(
                                [
                                dbc.Col(html.Div(['Kleinste Batterie', html.Br(), str(batteries['e_bat']['1'])+' kWh']), md=4),
                                dbc.Col([dcc.Input(id='specific_bat_cost_small',value=int(round(float(specific_bat_cost_small)/50)*50),type='number',style=dict(width = '50%')),'€/kWh'], md=5),
                                dbc.Col(html.Div(id='absolut_bat_cost_small'), md=3),
                                ],
                            align='center',
                            ),
                            html.Br(),
                            dbc.Row(
                                [
                                dbc.Col(html.Div(['Größte Batterie', html.Br(), str(batteries['e_bat']['5'])+' kWh']), md=4),
                                dbc.Col([dcc.Input(id='specific_bat_cost_big', value=int(round(float(specific_bat_cost_big)/50)*50),type='number',style=dict(width = '50%')),'€/kWh'], md=5),
                                dbc.Col(html.Div(id='absolut_bat_cost_big'), md=3),
                                ],
                            align='center',
                            ),
                        ]),
            html.H4('Stromtarif'),
            dbc.Container(
                        [                           
                            dbc.Row(
                                [
                                dbc.Col('Einspeisevergütung', md=4),
                                dbc.Col([dcc.Input(id='price_sell',min=0,max=20,value=6,placeholder='ct/kWh',type='number',style=dict(width = '50%',persistence='local')),'ct/kWh'], md=5),
                                dbc.Col(html.Div(), md=4),
                                ],
                            align='center',
                            ),
                            dbc.Row(
                                [
                                dbc.Col('Strombezugspreis', md=4),
                                dbc.Col([dcc.Input(id='price_buy',min=10,max=60,value=40,placeholder='ct/kWh',type='number',style=dict(width = '50%'),persistence='local'),'ct/kWh'], md=5),
                                dbc.Col(html.Div(), md=3),
                                ],
                            align='center',
                            ),
                        ],
                        fluid=True,
                        ),
            ]
        )

# Specific functions for a certain purpose ################
# Weather information
@app.callback(
    Output('region', 'children'),
    Input('standort', 'value'),
    Input('button_language','value'))
def standorttoregion(standort,lang):
    region=str(getregion(standort))
    weather=pd.read_csv('src/assets/data/weather/TRY_'+region+'_a_2015_15min.csv')
    average_temperature_C=weather['temperature [degC]'].mean()
    global_irradiance_kWh_m2a=weather['synthetic global irradiance [W/m^2]'].mean()*8.76
    return html.Div(children=['DWD Region: '+language.loc[language['name']==str(getregion(standort)),lang].iloc[0],html.Br(),
                    'Durchschnittstemperatur: ' + str(round(average_temperature_C ,1)) + ' °C',html.Br(),
                    'Globalstrahlung: '+ str(int(global_irradiance_kWh_m2a)) + ' kWh/(m²a)'])

# Electric load profile information
@app.callback(
    Output('p_el_hh', 'data'),
    Input('stromverbrauch', 'value'),
    State('last_triggered_building','data'),
    Input('industry_type','value'))
def get_p_el_hh(e_hh,building,building_type):
    if building=='efh':
        p_el=pd.read_csv('src/assets/data/electrical_loadprofiles/LP_W_EFH.csv')
    elif building=='mfh':
        if e_hh<15000:
            p_el=pd.read_csv('src/assets/data/electrical_loadprofiles/LP_W_MFH_k.csv')

        elif e_hh<45000:
            p_el=pd.read_csv('src/assets/data/electrical_loadprofiles/LP_W_MFH_m.csv')
        elif e_hh>45000:
            p_el=pd.read_csv('src/assets/data/electrical_loadprofiles/LP_W_MFH_g.csv')
    else:
        if building_type==None:
            raise PreventUpdate
        if building_type=='LP_Ö_Schule':
            if e_hh<100_000:
                building_type='LP_Ö_Schule_k.csv'
            elif e_hh<300_000:
                building_type='LP_Ö_Schule_m.csv'
            else:
                building_type='LP_Ö_Schule_g.csv'
        elif building_type=='LP_Ö_Büro':
            if e_hh<100_000:
                building_type='LP_Ö_Büro_k.csv'
            else:
                building_type='LP_Ö_Büro_m.csv'
        p_el=pd.read_csv('src/assets/data/electrical_loadprofiles/'+building_type)
    return (p_el.iloc[:,1].values*e_hh/1000).tolist()

# Change button style
@app.callback(
    Output('n_solar', 'style'),
    Output('n_clicks_pv', 'data'),
    Input('n_solar', 'n_clicks'),
    )
def change_solar_style(n_clicks):
    if (n_clicks%2)==1:
        return {'background-color': '#212529','color': 'white',},1
    else:
        return {'background-color': 'white','color': 'black'},0
@app.callback(
    Output('n_solar2', 'style'), 
    Input('n_solar2', 'n_clicks'),
    )
def change_solar2_style(n_clicks):
    if (n_clicks%2)==1:
        return {'background-color': '#212529','color': 'white',}
    else:
        return {'background-color': 'white','color': 'black'}
@app.callback(
    Output('n_chp', 'style'),
    Output('n_chp','n_clicks'), 
    Output('n_hp','style'), 
    Output('n_hp','n_clicks'),
    Output('n_clicks_chp','data'),
    Output('n_clicks_hp','data'),
    Input('n_chp', 'n_clicks'),
    Input('n_hp','n_clicks'), 
    Input('include_heating','value'),
    )
def change_hp_chp_style(n_chp,n_hp,heating):
    if (heating is None) or (len(heating)==0):
        return {'background-color': 'white','color': 'grey'},0,{'background-color': 'white','color': 'grey'},0,0,0
    if ((n_hp%2==0) and (n_chp%2==0)) or (n_chp>=3) or (n_hp>=3):
        return {'background-color': 'white','color': 'black'},0,{'background-color': 'white','color': 'black'},0,0,0
    elif (n_chp%2)==1:
        return {'background-color': '#212529','color': 'white'},2,{'background-color': 'white','color': 'black'},0,1,0
    elif n_hp%2==1:
        return {'background-color': 'white','color': 'black'},0,{'background-color': '#212529','color': 'white'},2,0,1

# Calculation of photovoltaic output time series
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
    Output('p_pv1', 'data'), 
    Input('pv_slider','value'),
    Input('c_pv1','data'),)
def scale_pv1(pv_slider1, pv1):
    if pv_slider1 is None:
        raise PreventUpdate
    pv1=np.array(pv1) * pv_slider1
    return list(pv1)

# Calculation of thermal building and hot water demand time series
@app.callback(
    Output('p_th_load', 'data'), 
    Output('building', 'data'),
    Output('building_type_value','children'), 
    Input('include_heating','value'),
    Input('standort','value'),
    Input('wohnfläche','value'),
    Input('building_type','value'),)
def calc_heating_timeseries(heating,location,Area,building_type):
    if (heating is None) or (location is None) or (Area is None) or(building_type is None):
        return None, None, None
    # 1 person for every 50m² in a SFH
    inhabitants = round(Area/50,0)
    if Area<50: # in that case its the amount of residential units in a MFH
        inhabitants=Area*2 # 2 persons per residential unit
        Area=Area*70 # (70 m² per residential unit)
    # Definintion and selection of building types
    buildings = pd.DataFrame([[0.8, 12, 35, 28, 1.1],
                            [1.6, 14, 45, 35, 1.2],
                            [2.6, 15, 55, 45, 1.3]],
                            columns=['Q_sp', 'T_limit', 'T_vl_max', 'T_rl_max', 'f_hs_exp'],
                            index=['new','renovated','old'])  
    if building_type.endswith('unsaniert'):
        building=buildings.loc['old',:]
    elif building_type.startswith('Bestand'):
        building=buildings.loc['renovated',:]
    elif building_type.startswith('Neubau'):
        building=buildings.loc['new',:]
    building=building.to_dict()
    t_room = 20
    region=getregion(location)
    # Get min temp. for location
    TRJ=pd.read_csv('src/assets/data/weather/TRJ-Tabelle.csv')
    building['T_min_ref'] = TRJ['T_min_ref'][region-1]
    building['Area']=Area
    building['Inhabitants']=inhabitants
    building['location']=str(region)
    t_room=20
    P_tww = 1000+200*building['Inhabitants']    # additional heating load for DHW in W 1000 W + 200 W/person
    P_th_max=(t_room - building['T_min_ref']) * building['Q_sp'] * building['Area'] + P_tww
    # Calc heating load time series with 24h average outside temperature
    weather = pd.read_csv('src/assets/data/weather/TRY_'+str(region)+'_a_2015_15min.csv', header=0, index_col=0)
    weather.loc[weather['temperature 24h [degC]']<building['T_limit'],'p_th_heating']=(t_room-weather.loc[weather['temperature 24h [degC]']<building['T_limit'],'temperature 24h [degC]'])* building['Q_sp'] * Area
    weather.loc[weather['temperature 24h [degC]']>=building['T_limit'],'p_th_heating']=0
    # Load domestic hot water load profile
    load = pd.read_csv('src/assets/data/thermal_loadprofiles/dhw_'+str(int(inhabitants)) +'_15min.csv', header=0, index_col=0)
    load['p_th_heating [W]']=weather['p_th_heating'].values
    load_dict=load[['load [W]','p_th_heating [W]']].to_dict()
    return load_dict, building, 'Max. Heizlast: '+str(int(round(P_th_max)))+' W'

# Calculation of heat pump power and efficiency time series
@app.callback(
    Output('hp_technology_value', 'children'), 
    Output('power_heat_pump_W', 'data'),
    Input('building','data'),
    Input('p_th_load','data'),
    Input('hp_technology','value'),
    State('n_hp', 'style'),
    )
def sizing_of_heatpump(building, p_th_load, choosen_hp, hp_active):
    if (choosen_hp is None) or hp_active['color']!='white':
        raise PreventUpdate
    if choosen_hp.startswith('Sole'):
        group_id=5
    elif choosen_hp.startswith('Luft'):
        group_id=1
    P_hp_el , results_summary, t_in, t_out = sim.calc_hp(building,p_th_load,group_id)
    print(results_summary['JAZ'],results_summary['SJAZ'])
    return (html.Div('(' + str(t_in)+ '° / ' + str(t_out) + '°)'), \
            html.Div('SJAZ: '+str((round(results_summary['SJAZ'],2)))), \
            html.Div('Heizstab: ' + str(int(round(results_summary['percent_heating_rod_el'])))+' % el')), \
            P_hp_el.values.tolist()

# Calculation of heat pump power and efficiency time series
@app.callback(
    Output('chp_technology_value', 'children'), 
    Output('power_chp_W', 'data'),
    Input('building','data'),
    Input('p_th_load','data'),
    Input('chp_technology','value'),
    State('n_chp', 'style'),
    )
def sizing_of_chp(building, p_th_load, choosen_chp, chp_active):
    if (choosen_chp is None) or chp_active['color']!='white':
        raise PreventUpdate
    results_timeseries, P_th_max, P_th_chp, P_el_chp, runtime = sim.calc_chp(building,p_th_load,choosen_chp,)
    return html.Div([html.Div(str(int(round(P_el_chp))) + ' kWel / ' + str(int(round(P_th_chp)))+' kWth'),\
                    html.Div(str(int(round(runtime)))+ ' Volllaststunden')]), \
                    results_timeseries['P_chp_h_el'].values.tolist()

# Show electric energy demand
@app.callback(
    Output('stromverbrauch_value', 'children'),
    Input('stromverbrauch', 'value'),
    )
def print_stromverbrauch_value(stromverbrauch):
    return html.Div(str(stromverbrauch)+ ' kWh/a')

# Show living area in m² or residential units
@app.callback(
    Output('wohnfläche_value', 'children'),
    Input('wohnfläche', 'value'),
    )
def print_wohnfläche_value(wohnfläche):
    if wohnfläche<50:
        return html.Div(str(wohnfläche)+ ' WE')
    return html.Div(str(wohnfläche)+ ' m²')

# Show maximum heating load
@app.callback(
    Output('normheizlast_value', 'children'),
    Input('normheizlast', 'value'),
    )
def print_normheizlast_value(normheizlast):
    return html.Div(str(normheizlast)+ ' kW')
    
# Show photovoltaic power
@app.callback(
    Output('pv_slider_value', 'children'),
    Input('pv_slider', 'value'),
    )
def print_pv_slider_value(pv_slider):
    return html.Div(str(pv_slider)+ ' kWp')

# Save electricity price
@app.callback(
    Output('price_electricity', 'data'),
    Input('price_buy', 'value'),
    Input('price_sell', 'value'),
    )
def save_price_buy(price_buy,price_sell):
    return [price_buy, price_sell]

# Show investment cost batteries
@app.callback(
    Output('absolut_bat_cost_small', 'children'),
    Output('absolut_bat_cost_big', 'children'),
    Input('specific_bat_cost_small', 'value'),
    Input('specific_bat_cost_big', 'value'),
    State('batteries', 'data')
    )
def show_investmentcost_small(specific_bat_cost_small, specific_bat_cost_big, batteries):
    return html.Div([str(round(specific_bat_cost_small * batteries['e_bat']['1']))+ ' €']),\
            html.Div([str(round(specific_bat_cost_big * batteries['e_bat']['5']))+ ' €'])

# Change button expert style
@app.callback(
    Output('button_expert', 'children'),
    Input('button_expert', 'n_clicks'),
)
def expertmode(n1):
    if n1 is None:
        raise PreventUpdate
    if n1%2==1:
        return [DashIconify(icon='bi:toggle-on',width=50,height=30,),'Expert']
    else: 
        return [DashIconify(icon='bi:toggle-off',width=50,height=30,),'Expert']

# Open Navbar (Burger-Button on small screens)
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

# Calculate self sufficiency with different battery sizes
@app.callback(
    Output('batteries', 'data'),
    Input('p_el_hh','data'), 
    Input('power_heat_pump_W','data'), 
    Input('power_chp_W','data'), 
    Input('p_pv1', 'data'),
    Input('n_solar', 'n_clicks'),
    State('n_hp','style'),
    State('n_chp','style'),
    )
def calc_bat_results(p_el_hh,power_heat_pump_W,power_chp_W,pv1,n_pv1,n_hp_style,n_chp_style):
    if p_el_hh is None:
        raise PreventUpdate
    df=pd.DataFrame()
    df.index=pd.date_range(start='2022-01-01', end='2023-01-01', periods=35041)[0:35040]
    if (pv1 is None) or ((n_pv1%2)!=1):
        pv1=np.zeros(35040).tolist()
    if (power_heat_pump_W is None) or n_hp_style['color']!='white':
        power_heat_pump_W=np.zeros(35040).tolist()
    if (power_chp_W is None) or n_chp_style['color']!='white':
        power_chp_W=np.zeros(35040).tolist()
    df['p_el_hh']=p_el_hh
    df['p_el_hp']=power_heat_pump_W
    df['p_chp']=power_chp_W
    df['p_el_hh']=df['p_el_hh']+df['p_el_hp']
    df['p_PV']=np.array(pv1)
    if (df['p_PV'].mean()==0) and df['p_chp'].mean()==0:
        return None, None , None
    E_el_MWH = df['p_el_hh'].mean()*8.76/1000
    E_pv_kwp = df['p_PV'].mean()*8.76/1000
    E_chp = df['p_chp'].mean()*8.76/1000
    if (E_chp>0):
        batteries=sim.calc_bs(df, round(E_el_MWH*2,1)) #TODO: CHP battery sizing?
    else:
        batteries=sim.calc_bs(df, round(np.minimum(E_el_MWH*2.5,E_pv_kwp*2.5),1)) #TODO: CHP battery sizing?
    return batteries.to_dict()

# Show selection for different graphs (self sufficiency, self consumption or energy balance)
@app.callback(
    Output('bat_results', 'children'),
    Input('batteries', 'data'),
    Input('tabs', 'value'),
    State('include_heating','value'),
    State('n_hp', 'style'),
    State('n_chp', 'style'),
    )
def bat_results(batteries,tab,include_heating,n_hp,n_chp):
    if (batteries is None) or (include_heating is None):
        raise PreventUpdate
    elif (len(batteries)==3) or (tab!='tab_parameter'):
        return html.Div()
    elif (len(include_heating)==1) and (n_hp['color']=='black') and (n_chp['color']=='black'):
        return html.Div()
    return html.Div(children=[html.Br(),dcc.RadioItems(['Autarkiegrad','Eigenverbrauchsanteil','Energiebilanz'],'Autarkiegrad',id='show_bat_results',persistence='local'),html.Div(id='bat_result_graph')])

# show choosen graph    
@app.callback(
    Output('bat_result_graph', 'children'),
    Input('batteries', 'data'),
    Input('tabs', 'value'),
    Input('show_bat_results', 'value'),
    )
def bat_results(batteries,tab,results_id):
    if (batteries is None) or (tab!='tab_parameter'):
        return html.Div()
    elif (len(batteries)==3) or (tab!='tab_parameter'):
        return html.Div()
    batteries=pd.DataFrame.from_dict(batteries)
    if results_id=='Autarkiegrad':
        fig=px.bar(data_frame=batteries,x='e_bat',y=['Autarkiegrad ohne Stromspeicher','Erhöhung der Autarkie durch Stromspeicher'],
            color_discrete_map={'Autarkiegrad ohne Stromspeicher': '#fecda4', 'Erhöhung der Autarkie durch Stromspeicher' : '#90da9d'},
            labels={"e_bat": "nutzbare Speicherkapazität in kWh",
                    "value": "%",
                    'variable': ''
                    }
            )
    elif results_id=='Eigenverbrauchsanteil':
        fig=px.bar(data_frame=batteries,x='e_bat',y=['Eigenverbrauch ohne Stromspeicher','Erhöhung des Eigenverbrauchs durch Stromspeicher'],
            color_discrete_map={'Eigenverbrauch ohne Stromspeicher': '#fecda4', 'Erhöhung des Eigenverbrauchs durch Stromspeicher' : '#90da9d'},
            labels={"e_bat": "nutzbare Speicherkapazität in kWh",
                    "value": "%",
                    'variable': ''
                    }
            )
    elif results_id=='Energiebilanz':
        fig=px.bar(data_frame=batteries,x='e_bat',y=['Netzeinspeisung','Netzbezug'],
            color_discrete_map={'Netzeinspeisung': '#fae0a4', 'Netzbezug' : '#a7adb4'},
            labels={"e_bat": "nutzbare Speicherkapazität in kWh",
                    "value": "Netzeinspeisung/Netzbezug in kWh/a",
                    'variable': ''
                    }
            )
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
        ))
    return dcc.Graph(figure=fig)

# Show selection for different graphs (economy tab)
@app.callback(
    Output('cost_result', 'children'),
    State('batteries', 'data'),
    Input('price_electricity','data'), 
    Input('tabs', 'value'),
    )
def economic_results(batteries,electricity_price, tab):
    if electricity_price is None: 
        raise PreventUpdate
    if (electricity_price[0] is None) or (electricity_price[1] is None) or (batteries is None) or (tab!='tab_econmics'): 
        return html.Div()
    return html.Div(children=[dcc.RadioItems(['Amortisationszeit','NetPresentValue','InternalRateOfReturn'],value='Amortisationszeit',id='show_economic_results',persistence='local'),html.Div(id='cost_result_graph')])

# Show choosen graph (economy tab)
@app.callback(
    Output('cost_result_graph', 'children'),
    State('batteries', 'data'),
    Input('price_electricity','data'),
    Input('specific_bat_cost_small','value'),
    Input('specific_bat_cost_big','value'),
    Input('tabs', 'value'),
    Input('show_economic_results', 'value'),
    )
def economic_results_graph(batteries,electricity_price,specific_bat_cost_small,specific_bat_cost_big,tab,results_id):
    if electricity_price is None: 
        raise PreventUpdate
    batteries=(pd.DataFrame(batteries))
    if (electricity_price[0] is None) or (electricity_price[1] is None) or (batteries is None) or (tab!='tab_econmics'): 
        return html.Div()
    years=20
    lifetime=15
    interest_rate=0.015
    NetPresentValue=[]
    Amortisation=[]
    InternalRateOfReturn=[]
    I_0, exp = eco.invest_params([batteries['e_bat'].values[1],batteries['e_bat'].values[-1]],[specific_bat_cost_small,specific_bat_cost_big])
    for battery in batteries.index[1:]:
        i, I = eco.invest_costs(batteries.loc[battery]['e_bat'], I_0,exp)
        cashflow = eco.cash_flow(I,
                        batteries.loc['0']['Netzeinspeisung'],
                        batteries.loc[battery]['Netzeinspeisung'],
                        -batteries.loc['0']['Netzbezug'],
                        -batteries.loc[battery]['Netzbezug'],
                        electricity_price[1]/100,
                        electricity_price[0]/100,
                        years,
                        lifetime)
        NetPresentValue.append(eco.net_present_value(cashflow, interest_rate))
        Amortisation.append(eco.amortisation(cashflow))
        InternalRateOfReturn.append(eco.internal_rate_of_return(cashflow))
    if results_id.startswith('Amortisationszeit'):
        return dcc.Graph(figure=px.bar(x=batteries['e_bat'][1:], y=Amortisation,title='Amortisationszeit'))
    elif results_id.startswith('NetPresentValue'):
        fig=px.bar(x=batteries['e_bat'][1:], y=NetPresentValue,title='NetPresentValue')
        fig.update_yaxes(ticksuffix = " €")
        return dcc.Graph(figure=fig)
    elif results_id.startswith('InternalRateOfReturn'):
        fig=px.bar(x=batteries['e_bat'][1:], y=np.array(InternalRateOfReturn)*100,title='InternalRateOfReturn')
        fig.update_yaxes(ticksuffix = " %")
        return dcc.Graph(figure=fig)
if __name__ == '__main__':
    app.run_server(debug=True)
