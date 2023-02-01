import base64
import io
import warnings
warnings.filterwarnings("ignore")
# Dash
from dash import Dash, html, dcc, Input, Output, State, callback_context,ctx
from dash.exceptions import PreventUpdate
# Dash community libraries
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
# Data management
import pandas as pd
import numpy as np
import pathlib
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

# App configuration
# Icons from iconify, see https://icon-sets.iconify.design

app = Dash(__name__,
          suppress_callback_exceptions=True, 
          external_stylesheets=[dbc.themes.BOOTSTRAP,{'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css','rel': 'stylesheet','integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf','crossorigin': 'anonymous'}],
          meta_tags=[{'name': 'viewport', 'inhalt': 'width=device-width, initial-scale=1'},
          ],
          )
server = app.server

# Relative paths
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath('data').resolve()
ASSETS_PATH = PATH.joinpath('assets').resolve()

app.title = 'VDI 4657-3 Webtool'
# Table for translation (work in progress)
language=pd.read_csv(DATA_PATH.joinpath('translate.csv'))

# Weather information for all regions
weather_summary=pd.read_csv(DATA_PATH.joinpath('weather/TRJ-Tabelle.csv'))

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

button_download = dbc.Button(
    html.Div(id='button_download_content',children=[DashIconify(icon='ic:baseline-download',width=50,height=30,),html.Div('Parameter Download')]),
    id='button_download',
    outline=True,
    color="primary",
    active=True,
    style={'textTransform': 'none','color': '#023D6B','background-color': 'white',},
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

encoded_image=base64.b64encode(open(ASSETS_PATH.joinpath('logos/Logo_FZJ_200px.png'), 'rb').read())

options_building_type_ger=[
    {"label": html.Div([html.Span('Bestand, unsaniert',id='tooltip_building1'), dbc.Tooltip('Vorlauf: 35°C',target='tooltip_building1')]), "value": "Bestand, unsaniert"},
    {"label": html.Div([html.Span('Bestand, saniert',id='tooltip_building2'), dbc.Tooltip('Vorlauf: 45°C',target='tooltip_building2')]), "value": "Bestand, saniert"},
    {"label": html.Div([html.Span('Neubau, nach 2016',id='tooltip_building3'), dbc.Tooltip('Vorlauf: 55°C',target='tooltip_building3')]), "value": "Neubau, nach 2016"},
    ]
options_building_type_eng=[
    {"label": html.Div([html.Span('Existing building, unrenovated',id='tooltip_building1'), dbc.Tooltip('Heater temperature: 35°C',target='tooltip_building1')]), "value": "Bestand, unsaniert"},
    {"label": html.Div([html.Span('Existing building, renovated',id='tooltip_building2'), dbc.Tooltip('Heater temperature: 45°C',target='tooltip_building2')]), "value": "Bestand, saniert"},
    {"label": html.Div([html.Span('New building, after 2016',id='tooltip_building3'), dbc.Tooltip('Heater temperature: 55°C',target='tooltip_building3')]), "value": "Neubau, nach 2016"},
    ]
options_slp_ger = [
    {"label": 'G0: Gewerbe allgemein', "value": "LP_G0.csv"},
    {"label": "G1: Gewerbe werktags 8–18 Uhr", "value": "LP_G1.csv"},
    {"label": "G2: Gewerbe mit starkem bis überwiegendem Verbrauch in den Abendstunden", "value": "LP_G2.csv"},
    {"label": 'G3: Gewerbe durchlaufend', "value": "LP_G3.csv"},
    {"label": 'G4: Laden/Friseur', "value": "LP_G4.csv"},
    {"label": 'G5: Bäckerei mit Backstube', "value": "LP_G5.csv"},
    {"label": 'G6: Wochenendbetrieb', "value": "LP_G6.csv"},
    {"label": 'L0: Landwirtschaftsbetriebe allgemein', "value": "LP_L0.csv"},
    {"label": 'L1: Landwirtschaftsbetriebe mit Milchwirtschaft/Nebenerwerbs-Tierzucht', "value": "LP_L1.csv"},
    {"label": 'L2: Übrige Landwirtschaftsbetriebe', "value": "LP_L2.csv"},
    {"label": 'Büro', "value": "LP_Ö_Büro"},
    {"label": 'Schule', "value": "LP_Ö_Schule"},
    {"label": 'Produzierendes Gewerbe / Metallverarbeitung', "value": "LP_G_MV.csv"},
    {"label": 'Produzierendes Gewerbe / Galvanisierung', "value": "LP_G_G.csv"},
    {"label": 'Möbelhaus', "value": "LP_G_MH.csv"},
]
options_slp_eng = [
    {"label": 'G0: General trade', "value": "LP_G0.csv"},
    {"label": "G1: Trade during weekdays 8-18", "value": "LP_G1.csv"},
    {"label": "G2: Trade with strong to predominant consumption in the evening hours", "value": "LP_G2.csv"},
    {"label": 'G3: Continuous trade', "value": "LP_G3.csv"},
    {"label": 'G4: Store/hairdresser', "value": "LP_G4.csv"},
    {"label": 'G5: Bakery with bakery', "value": "LP_G5.csv"},
    {"label": 'G6: Weekend operation', "value": "LP_G6.csv"},
    {"label": 'L0: Farms in general', "value": "LP_L0.csv"},
    {"label": 'L1: Farms with dairy farming/part-time animal breeding', "value": "LP_L1.csv"},
    {"label": 'L2: Other farms', "value": "LP_L2.csv"},
    {"label": 'Office', "value": "LP_Ö_Büro"},
    {"label": 'School', "value": "LP_Ö_Schule"},
    {"label": 'Manufacturing trade/metal processing', "value": "LP_G_MV.csv"},
    {"label": 'Manufacturing trade/galvanization', "value": "LP_G_G.csv"},
    {"label": 'Furniture store', "value": "LP_G_MH.csv"},
]

header=dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4('Auslegung von Batteriespeichern'),
                    ],
                    id='app-title'
                    )
                ],
                align='center',
                ),
            ]),
        dbc.Row([
            dbc.Col([
                dbc.NavbarToggler(id='navbar-toggler'),
                dbc.Collapse(
                    dbc.Nav([
                        dbc.NavItem(button_language,style={'width':'150'}),
                        dbc.NavItem(button_info,style={'width':'150'}),
                        dcc.ConfirmDialog(id='info_dialog', message='Dummy text'),
                        ],
                        navbar=True,
                        ),
                    id='navbar-collapse',
                    navbar=True,
                    ),
                ],
                width=3,
                ),
            ],
            align='center',
            ),
        ],
        fluid=True,
        ),
    dark=True,
    color='#023D6B',
    sticky='top',
    )

################################################
# Main-Page

content = html.Div(children=[
    dbc.Container([
        dbc.Row([
            dbc.Col(html.Div(id='scroll',children=[
                dcc.Tabs(id='tabs',value='tab_info'),
                html.Div(id='tab-content'),
                ]
                ), width=12, md=5, lg=5, xl=4),
            dbc.Col(html.Div(
                children=[html.Div(id='bat_results'),
                    html.Div(id='bat_results_LSK'),
                    html.Div(id='cost_result'),
                    html.Div(id='cost_result_LSK'),
                    ]
                )),
            ]),
        ],fluid=True),
    dcc.Store(id='last_triggered_building'),
    dcc.Store(id='n_clicks_pv'),
    dcc.Store(id='n_clicks_chp'),
    dcc.Store(id='n_clicks_hp'),
    dcc.Store(id='parameter_include_heating'),
    dcc.Store(id='parameter_wohnfläche'),
    dcc.Store(id='parameter_building_type'),
    dcc.Store(id='p_el_hh'),
    dcc.Store(id='p_th_load'),
    dcc.Store(id='building'),
    dcc.Store(id='c_pv1'),
    dcc.Store(id='p_pv1'),
    dcc.Store(id='power_heat_pump_W'),
    dcc.Store(id='power_chp_W'),
    dcc.Store(id='batteries'),
    dcc.Store(id='price_electricity'),
    dcc.Store(id='price_electricity_peak'),
    dcc.Store(id='parameter_lang'),
    dcc.Store(id='parameter_use'),
    dcc.Loading(type='default',children=dcc.Store(id='parameter_location_int')),
    dcc.Store(id='parameter_location_string'),
    dcc.Store(id='parameter_pv'),
    dcc.Store(id='parameter_chp'),
    dcc.Store(id='parameter_hp'),
    dcc.Store(id='parameters_all'),
    dcc.Store(id='parameter_loadprofile'),
    dcc.Store('show_economic_results'),
    dcc.Store('show_bat_results'),
    dcc.Loading(type='default',children=dcc.Store(id='parameter_peak_shaving')),
    dcc.Store(id='parameter_economoy'),
    ],)

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
    Output('parameter_lang','data'),
    Input('button_language', 'n_clicks'),
    Input('parameters_all', 'data'),
)
def change_language(n_language,upload_data):
    if ctx.triggered_id=='parameters_all':
        lang=(upload_data['Language']['0'])
        if lang=='ger':
            flag='emojione:flag-for-germany'
        else:
            flag='emojione:flag-for-united-kingdom'
    else:
        if n_language==None or n_language%2==0:
            lang='ger'
            flag='emojione:flag-for-germany'
        else:
            lang='eng'
            flag='emojione:flag-for-united-kingdom'        
    return ([DashIconify(icon=flag, width=50,height=30,),language.loc[language['name']=='lang',lang].iloc[0]],
            lang,
            [html.H4(language.loc[language['name']=='header_p',lang])],
            [dcc.Tab(label=language.loc[language['name']=='use_case',lang].iloc[0],value='tab_info',children=[html.Div(children=[
                html.Br(),
                html.Div(language.loc[language['name']=='start',lang]),
                html.Br(),
                html.Div(language.loc[language['name']=='choose_use_case',lang], style={'textAlign': 'start'}),
                html.Br(),
                dbc.Container([
                    dbc.Row([
                        dbc.Col(html.Button(html.Div([DashIconify(icon='grommet-icons:optimize',width=75,height=75,),html.Br(),language.loc[language['name']=='increase_autarky',lang].iloc[0]]),id='autakie_click',n_clicks=0,
                            style={'background-color': 'white',
                            'color': 'black',
                            'font-size': '12px',
                            'width': '120px',
                            'display': 'inline-block',
                            'margin-bottom': '10px',
                            'margin-right': '5px',
                            'height':'100px',
                            'verticalAlign': 'top',
                            'textAlign': 'center'}),
                            width={'size':1,'offset': 2}),
                        dbc.Col(html.Button(html.Div([DashIconify(icon='grommet-icons:time',width=75,height=75,),html.Br(),language.loc[language['name']=='peak_shaving',lang].iloc[0]]),id='LSK_click',n_clicks=0,
                            style={'background-color': 'white',
                            'color': 'black',
                            'font-size': '12px',
                            'width': '120px',
                            'display': 'inline-block',
                            'margin-bottom': '10px',
                            'margin-right': '5px',
                            'height':'100px',
                            'verticalAlign': 'top',
                            'textAlign': 'center'}),
                            width={'size':1,'offset': 3},
                            )
                        ],
                        )
                ]),
                html.Br(),
                dcc.Upload(id='upload_parameters',children=html.Div(language.loc[language['name']=='upload_save',lang]),
                    style={'width': '90%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                ),
                html.Br(),
                html.Div(language.loc[language['name']=='developed',lang]),
                html.Br(),
                html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),style={'height':'67px'})
            ])]),
            dcc.Tab(label='System',value='tab_parameter',),
            dcc.Tab(label=language.loc[language['name']=='economics',lang].iloc[0], value='tab_econmics',)],
            lang
    )

# Render tab content
@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value'),
    State('parameter_use','data'),
    Input('button_language','value'),
    State('n_clicks_pv','data'),
    State('n_clicks_chp','data'),
    State('n_clicks_hp','data'),
    Input('parameters_all', 'data'),
    Input('parameters_all', 'modified_timestamp'),
)
def render_tab_content(tab,LSK,lang,n_clicks_solar, n_clicks_chp, n_clicks_hp, upload_data, last_upload):
    if ctx.triggered_id=='parameters_all':
        n_clicks_timestamp_efh=None
        n_clicks_timestamp_mfh=None
        n_clicks_timestamp_indu=None
        building=upload_data['Building']['0']
        if building=='efh':
            n_clicks_timestamp_efh=1
        elif building=='mfh':
            n_clicks_timestamp_mfh=1
        elif building=='indu':
            n_clicks_timestamp_indu=1
        n_clicks_solar = upload_data['n_clicks_pv']['0']
        n_clicks_chp = upload_data['n_clicks_chp']['0']
        n_clicks_hp = upload_data['n_clicks_hp']['0']
        LSK = upload_data['use_case']['0']
        location = upload_data['location']['0']
        tab='tab_parameter'
        if upload_data['include_heating']['0']==0:
            choose_heating=[]
        else:
            choose_heating=['True']
    else:
        location=''
        choose_heating=[]
        n_clicks_timestamp_efh=None
        n_clicks_timestamp_mfh=None
        n_clicks_timestamp_indu=None
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
                dbc.Container([
                    dbc.Row(dbc.Col(html.H3(language.loc[language['name']=='location',lang].iloc[0])),),
                    dbc.Row([
                        dbc.Col(dcc.Input(id='standort',placeholder=language.loc[language['name']=='placeholder_location',lang].iloc[0],value=location,persistence='session',style=dict(width = '100%'))),
                        dbc.Col(dcc.Loading(type="default",children=html.Div(id='region')),align='start',width=12, lg=7),
                        ]),
                    html.Br(),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(html.H3(language.loc[language['name']=='choose_building',lang].iloc[0]), width=12),
                        ],
                        align='center',
                        ), 
                    dbc.Row([
                        dbc.Col(html.Button(html.Div([DashIconify(icon='clarity:home-solid',width=50,height=50,),html.Br(),language.loc[language['name']=='efh_name',lang].iloc[0]],style={'width':'120px'}),id='efh_click',n_clicks_timestamp=n_clicks_timestamp_efh), width=4),
                        dbc.Col(html.Button(html.Div([DashIconify(icon='bxs:building-house',width=50,height=50,),html.Br(),language.loc[language['name']=='mfh_name',lang].iloc[0]],style={'width':'120px'}),id='mfh_click',n_clicks_timestamp=n_clicks_timestamp_mfh), width=4),
                        dbc.Col(html.Button(html.Div([DashIconify(icon='la:industry',width=50,height=50,),html.Br(),language.loc[language['name']=='industry_name',lang].iloc[0]],style={'width':'120px'}),id='industry_click',n_clicks_timestamp=n_clicks_timestamp_indu), width=4),
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(id='include_heating_row'),
                    ]),
                    html.Br(),
                    ],
                    fluid=True,
                    ),
                    
                dbc.Container(id='bulding_container',fluid=True),
                dbc.Container([
                    html.Br(),
                    dbc.Row(dbc.Col(html.H3(language.loc[language['name']=='choose_technology',lang].iloc[0]))),
                    dbc.Row([
                        dbc.Col(html.Button(html.Div([DashIconify(icon='fa-solid:solar-panel',width=50,height=50,),html.Br(),language.loc[language['name']=='pv',lang].iloc[0]],style={'width':'120px'}),id='n_solar',n_clicks=n_clicks_solar),width=4),
                        dbc.Col(html.Button(html.Div([DashIconify(icon='mdi:gas-burner',width=50,height=50,),html.Br(),language.loc[language['name']=='chp',lang].iloc[0]],style={'width':'120px'}),id='n_chp',n_clicks=n_clicks_chp),width=4),
                        dbc.Col(html.Button(html.Div([DashIconify(icon='mdi:heat-pump-outline',width=50,height=50,),html.Br(),language.loc[language['name']=='hp',lang].iloc[0]],style={'width':'120px'}),id='n_hp',n_clicks=n_clicks_hp),width=4),
                    ])],
                    fluid=True
                    ),
                dbc.Container(html.Div([html.Div(id='hp_technology'),html.Div(id='chp_technology'),html.Div(id='hp_technology_value'),html.Div(id='chp_technology_value')],id='technology'),fluid=True)
                
            ])
        else:
            return html.Div(children=[html.Br(),
                dbc.Container(
                    [
                        dbc.Row(
                            [
                            dbc.Col(html.H3(language.loc[language['name']=='loadprofile',lang].iloc[0])),
                            ],
                        align='center',
                        ),
                    ],
                    fluid=True,
                ),
                dcc.Upload(id='upload_load_profile',children=html.Div([
                    html.Span(language.loc[language['name']=='upload_info',lang].iloc[0], id='tooltip_lp'),
                    dbc.Tooltip([html.Div(language.loc[language['name']=='upload_info1',lang].iloc[0]), 
                        html.Div(language.loc[language['name']=='upload_info2',lang].iloc[0]), 
                        html.Div(language.loc[language['name']=='upload_info3',lang].iloc[0])], 
                        target='tooltip_lp')]),
                    style={'width': '90%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                                    ),
                dcc.Loading(type="default",children=html.Div(id='kpi_LSK')),])
    elif tab=='tab_econmics':
        return html.Div(id='battery_cost_para')
    else:
        return html.Div(),None

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
    Output('include_heating_row','children'),
    Output('bulding_container','children'),
    Output('efh_click', 'style'), 
    Output('mfh_click', 'style'), 
    Output('industry_click', 'style'),    
    Output('last_triggered_building', 'data'),    
    Input('efh_click','n_clicks_timestamp'),
    Input('mfh_click','n_clicks_timestamp'),
    Input('industry_click','n_clicks_timestamp'),
    State('last_triggered_building','data'),
    Input('parameter_include_heating', 'data'),
    State('button_language','value'),
    State('parameters_all', 'data'),
    State('parameters_all', 'modified_timestamp'),
)
def getcontainer(efh_click,mfh_click,industry_click,choosebuilding,heating,lang, upload_data, last_upload):
    if (last_upload is not None) and ((ctx.timing_information['__dash_server']['dur']-last_upload/1000)<5):
        electricity_consumption_efh = (upload_data['electricicty_consumption']['0'])
        electricity_consumption_mfh = (upload_data['electricicty_consumption']['0'])
        electricity_consumption_indu = (upload_data['electricicty_consumption']['0'])
    else:
        electricity_consumption_efh = 4000
        electricity_consumption_mfh = 15_000
        electricity_consumption_indu = 50_000

    if (efh_click is None and mfh_click is None and industry_click is None):#changed_id = [0]
        if choosebuilding is None:
            return '',html.Div(language.loc[language['name']=='choose_building_type',lang].iloc[0],id='building_type_value'),{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'},None
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
    if lang=='eng':
        options_building_type=options_building_type_eng
    else:
        options_building_type=options_building_type_ger
    if (efh_click>mfh_click) and (efh_click>industry_click):
        if (heating is None) or (len(heating)==0): # for simulating without heating
            return (dcc.Checklist(options={'True': language.loc[language['name']=='heating',lang].iloc[0]},value=[], id='include_heating',persistence='session'),
                        [   
                        dbc.Row([
                            dbc.Col(language.loc[language['name']=='energy_cons',lang].iloc[0], width=6),
                            dbc.Col(html.Div(id='stromverbrauch_value'), width=4),
                            dbc.Col(dcc.Slider(min=2000,max=10000,step=500,value=electricity_consumption_efh,marks=None,id='stromverbrauch',tooltip={'placement': 'top', 'always_visible': False},persistence='session'), width=12),
                            html.Div(id='industry_type'),
                            dcc.Store(id='building_type_value'),
                            ],
                            align='center',
                            ),
                        ],
                    {'background-color': '#023D6B','color': 'white',},
                    {'background-color': 'white','color': 'black'},
                    {'background-color': 'white','color': 'black'},'efh')
        else: # with heating system
            return (dcc.Checklist(options={'True': language.loc[language['name']=='heating',lang].iloc[0]},value=['True'], id='include_heating',persistence='session'),
                        [
                            dbc.Row(
                                [
                                    dbc.Col(language.loc[language['name']=='energy_cons',lang].iloc[0], width=6),
                                    dbc.Col(html.Div(id='stromverbrauch_value'), width=4),
                                    dbc.Col(dcc.Slider(min=2000,max=8000,step=500,value=electricity_consumption_efh,marks=None,id='stromverbrauch',tooltip={'placement': 'top', 'always_visible': False},persistence='session'), width=12),
                                    html.Div(id='industry_type'),
                                ],
                                align='center',
                                ),
                            dbc.Row(
                                [
                                    dbc.Col(language.loc[language['name']=='building_size',lang].iloc[0], width=6),
                                    dbc.Col(html.Div(id='wohnfläche_value'), width=4),
                                    dbc.Col(dcc.Slider(min=50,max=250,step=10,value=150,marks=None,id='wohnfläche',tooltip={'placement': 'top', 'always_visible': False},persistence='session'), width=12),
                                ],
                                align='center',
                                ),
                            dbc.Row(
                                [
                                    dbc.Col(language.loc[language['name']=='building_type',lang].iloc[0], width=6),
                                    dbc.Col(html.Div(id='building_type_value'), width=6),
                                    dbc.Col(dcc.Dropdown(options_building_type, id='building_type',persistence='session'), width=11),
                                ],
                                align='center',
                                )
                        ],
                    {'background-color': '#023D6B','color': 'white',},
                    {'background-color': 'white','color': 'black'},
                    {'background-color': 'white','color': 'black'},'efh')
    if (mfh_click>efh_click) and (mfh_click>industry_click):
        if (heating is None) or (len(heating)==0): # for simulating without heating
            return (dcc.Checklist(options={'True': language.loc[language['name']=='heating',lang].iloc[0]},value=[], id='include_heating',persistence='session'),
                        [
                            dbc.Row(
                                [
                                    dbc.Col(language.loc[language['name']=='housing_units',lang].iloc[0], width=6),
                                    dbc.Col(html.Div(id='wohnfläche_value'), width=4),
                                    dbc.Col(dcc.Slider(min=2,max=50,step=1,value=12,marks=None,id='wohnfläche',tooltip={'placement': 'top', 'always_visible': False},persistence='session'), width=12),
                                ],
                                align='center'),
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='energy_cons',lang].iloc[0], width=6),
                                dbc.Col(html.Div(id='stromverbrauch_value'), width=4),
                                dbc.Col(dcc.Slider(min=5000,max=100000,step=1000,value=electricity_consumption_mfh,marks=None,id='stromverbrauch',tooltip={'placement': 'top', 'always_visible': False},persistence='session'), width=12),
                                dcc.Store(id='building_type_value'),
                                html.Div(id='industry_type'),
                                ],
                            align='center'),
                        ],
                    {'background-color': 'white','color': 'black'},
                    {'background-color': '#023D6B','color': 'white',},
                    {'background-color': 'white','color': 'black'},'mfh')
        else:
            return (dcc.Checklist(options={'True': language.loc[language['name']=='heating',lang].iloc[0]},value=['True'], id='include_heating',persistence='session'),
                        [
                            dbc.Row(
                                [
                                    dbc.Col(language.loc[language['name']=='housing_units',lang].iloc[0], width=6),
                                    dbc.Col(html.Div(id='wohnfläche_value'), width=4),
                                    dbc.Col(dcc.Slider(min=2,max=50,step=1,value=12,marks=None,id='wohnfläche',tooltip={'placement': 'top', 'always_visible': False},persistence='session'), width=12),
                                ],
                                align='center',
                                ),
                            dbc.Row(
                                [
                                    dbc.Col(language.loc[language['name']=='energy_cons',lang].iloc[0], width=6),
                                    dbc.Col(html.Div(id='stromverbrauch_value'), width=4),
                                    dbc.Col(dcc.Slider(min=5000,max=100000,step=1000,value=electricity_consumption_mfh,marks=None,id='stromverbrauch',tooltip={'placement': 'top', 'always_visible': False},persistence='session'), width=12),
                                    html.Div(id='industry_type'),
                                ],
                                align='center',
                                ),
                            dbc.Row(
                                [
                                    dbc.Col(language.loc[language['name']=='building_type',lang].iloc[0], width=6),
                                    dbc.Col(html.Div(id='building_type_value'), width=6),
                                    dbc.Col(dcc.Dropdown(options_building_type,id='building_type',persistence='session'), width=11),
                                ],
                                align='center',
                                )
                        ],
                {'background-color': 'white','color': 'black'},
                {'background-color': '#023D6B','color': 'white',},
                {'background-color': 'white','color': 'black'},'mfh')
    if (industry_click>efh_click) and (industry_click>mfh_click):
        if lang=='eng':
            options_slp=options_slp_eng
        else:
            options_slp=options_slp_ger
        return ('',
            [
            dbc.Row(
                [
                dbc.Col(language.loc[language['name']=='building_type_industry',lang].iloc[0], width=12),
                dbc.Col(dcc.Dropdown(options_slp,id='industry_type',persistence='session', optionHeight=100,maxHeight=400), width=11),
                ],
            align='center',
            ),
            dbc.Row(
                [
                dbc.Col(language.loc[language['name']=='energy_cons',lang].iloc[0], width=6),
                dbc.Col(html.Div(id='stromverbrauch_value'), width=4),
                dbc.Col(dcc.Slider(min=5_000,max=200_000,step=1000,marks=None,value=electricity_consumption_indu,id='stromverbrauch',tooltip={'placement': 'top', 'always_visible': False},persistence='session'), width=12),
                ],
            align='center',
            ),
            ],
            {'background-color': 'white','color': 'black'},
            {'background-color': 'white','color': 'black'},
            {'background-color': '#023D6B','color': 'white',},'indu')

# Add technology to the tab 'tab_parameter'
@app.callback(
    Output('technology','children'), 
    Input('n_solar', 'style'),
    Input('n_chp', 'style'),
    Input('n_hp', 'style'),
    Input('button_language','value'),
    Input('last_triggered_building','data'),
    State('parameters_all','modified_timestamp'),
    State('parameters_all','data'),
    )
def built_technology(n_solar,n_chp,n_hp,lang,building, last_upload, upload_data):
    pv_value=10
    chp_max_power=0.3
    chp_electric_heat_ratio=1
    hp_technology=''
    if last_upload is not None:
        if (ctx.timing_information['__dash_server']['dur']-last_upload/1000)<5:
            pv_value=(upload_data['pv_kwp']['0'])
            chp_electric_heat_ratio=(upload_data['chp_electric_heat_ratio']['0'])
            hp_technology=(upload_data['hp_technology']['0'])
    technology_list=[html.Br()]
    if n_solar['color']=='white':
        if building=='efh':
            technology_list.append(
                            dbc.Row(
                                [
                                dbc.Col(html.H6(language.loc[language['name']=='photovoltaik',lang].iloc[0]), width=6),
                                dbc.Col(html.Div(id='pv_slider_value'), width=4),
                                dbc.Col(dcc.Slider(min=0,max=20,step=1,marks=None, id='pv_slider',value=pv_value, tooltip={'placement': 'top', 'always_visible': False}, persistence='session'), width=12),
                                ],
                            align='center',
                            ))
        elif (building=='mfh') or (building=='indu'):
            technology_list.append(
                            dbc.Row(
                                [
                                dbc.Col(html.H6(language.loc[language['name']=='photovoltaik',lang].iloc[0]), width=6),
                                dbc.Col(html.Div(id='pv_slider_value'), width=4),
                                dbc.Col(dcc.Slider(min=0,max=200,step=5,marks=None, id='pv_slider',value=pv_value, tooltip={'placement': 'top', 'always_visible': False}, persistence='session'), width=12),
                                ],
                            align='center',
                            ))
        else:
            technology_list.append(html.Div(language.loc[language['name']=='choose_building_type',lang].iloc[0]))
    else:
        technology_list.append(
            dcc.Store(id='pv_slider')
        )
    if n_chp['color']=='white':
        technology_list.append(
                            dbc.Row(
                                [
                                dbc.Col(html.H6(language.loc[language['name']=='combined_heat_power',lang].iloc[0]), width=6),
                                dbc.Col(dcc.Loading(type="circle",children=html.Div(id="chp_load_hours"))),
                                ],
                            align='center',
                            ),)
        technology_list.append(
                            dbc.Row(
                                [
                                dbc.Col(language.loc[language['name']=='chp_peak_ratio',lang].iloc[0], width=6),
                                dbc.Col(id='chp_technology_value'),
                                dbc.Col(dcc.Slider(min=0.1,max=1,step=0.1,value=chp_max_power,marks=None,id='chp_max_power',tooltip={'placement': 'top', 'always_visible': False},persistence='session'), width=12),
                                dbc.Col(language.loc[language['name']=='chp_electric_number',lang].iloc[0], width=6),
                                dbc.Col(id='chp_technology_value2'),
                                dbc.Col(dcc.Slider(min=0.1,max=3,step=0.1,value=chp_electric_heat_ratio,marks=None,id='chp_technology',tooltip={'placement': 'top', 'always_visible': False},persistence='session'), width=12),
                                ],
                            align='center',
                            ),
                            )
    else:
        technology_list.append(
            html.Div([html.Div(id='chp_technology'),html.Div(id='chp_technology_value')])
        )
    if n_hp['color']=='white':
        technology_list.append(
                            dbc.Row(
                                [
                                dbc.Col(html.H6(language.loc[language['name']=='heatpump',lang].iloc[0]), width=6),
                                dbc.Col(dcc.Loading(type="circle",children=html.Div(id="hp_technology_value")), width=6),
                                dbc.Col(dcc.Dropdown(['Luft/Wasser (mittl. Effizienz)','Sole/Wasser (mittl. Effizienz)'],value=hp_technology, id='hp_technology',persistence='session', optionHeight=50), width=11),
                                ],
                            align='center',
                            )
                            )
    else:
        technology_list.append(
            html.Div([html.Div(id='hp_technology'),html.Div(id='hp_technology_value')])
        )
    return html.Div(children=technology_list)

# Change tabs with buttons on info tab (self-sufficiency or peak shaving)
@app.callback(
    Output('tabs', 'value'),
    Output('parameter_use','data'),
    Input('autakie_click', 'n_clicks'),
    Input('LSK_click', 'n_clicks'),
    Input('parameters_all', 'data'),
    State('tabs','value'),
    State('parameter_use','data')
    )
def next_Tab(autarkie, LSK, upload_data, tab, parameter_use):
    if ctx.triggered_id=='parameters_all':
        LSK=upload_data['use_case']['0']
    else:
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]#TODO
        if (autarkie==0) & (LSK==0):
            return tab,parameter_use
        elif changed_id.startswith('aut'):
            LSK=0
        elif changed_id.startswith('LSK'):
            LSK=1
    return 'tab_parameter', LSK

# Add investment cost for batteries
@app.callback(
    Output('battery_cost_para', 'children'),
    Output('parameter_economoy', 'data'),
    State('batteries','data'),
    Input('tabs','value'),
    State('parameter_use','data'),
    State('parameters_all','data'),
    State('parameters_all', 'modified_timestamp'),
    State('parameter_economoy', 'data'),
    State('parameter_peak_shaving', 'data'),
    Input('button_language', 'value'),
    )
def next_Tab(batteries, tab, LSK, upload_data, last_upload, parameter_economy, df_peak_shaving_results, lang):
    if (LSK is None):
        return 'Zunächst System definieren.', last_upload

    if (batteries is None) & (LSK==0):
        return 'Zunächst System definieren.', last_upload
        
    I_0,exp=eco.invest_params_default()
    if LSK==0:
        if len(batteries)==3:
            return 'Bitte Erzeuger im System-Tab auswählen.', last_upload
        capacity_bat_small = batteries['e_bat']['1']
        capacity_bat_big = batteries['e_bat']['5']
        specific_bat_cost_small,_ = eco.invest_costs(capacity_bat_small, I_0, exp)
        specific_bat_cost_big, _ = eco.invest_costs(capacity_bat_big, I_0, exp)
    else:
        df=(pd.DataFrame().from_dict(df_peak_shaving_results))
        try:
            df=(df.loc[(df['Entladerate']>0.5) &  (df['Entladerate']<2.5)])
            capacity_bat_small=round(df['nutzbare Speicherkapazität in kWh'].values[0],1)
            capacity_bat_big=round(df['nutzbare Speicherkapazität in kWh'].values[-1],1)
        except:
            df=(df.loc[(df['Discharge rate']>0.5) &  (df['Discharge rate']<2.5)])
            capacity_bat_small=round(df['Usable storage capacity in kWh'].values[0],1)
            capacity_bat_big=round(df['Usable storage capacity in kWh'].values[-1],1)
        specific_bat_cost_small,_ = eco.invest_costs(capacity_bat_small, I_0, exp)
        specific_bat_cost_big, _ = eco.invest_costs(capacity_bat_big, I_0, exp)
        
    if tab=='tab_econmics':
        if (last_upload!=parameter_economy):
            specific_bat_cost_small = upload_data['specific_bat_cost_small']['0']
            specific_bat_cost_big = upload_data['specific_bat_cost_big']['0']
            price_sell = int(upload_data['Electricity_price']['0'].split(',')[1][:-1])
            price_buy = int(upload_data['Electricity_price']['0'].split(',')[0][1:])
        else:
            specific_bat_cost_small=int(round(float(specific_bat_cost_small)/50)*50)
            specific_bat_cost_big=int(round(float(specific_bat_cost_big)/50)*50)
            price_sell=6
            price_buy=35
        if LSK==0:
            cost_use_case=dbc.Row(
                [
                dbc.Col(language.loc[language['name']=='price_buy',lang].iloc[0], width=12),
                dbc.Col([dcc.Input(id='price_buy',min=0,value=price_buy,placeholder='ct/kWh',type='number',style=dict(width = '50%'),persistence='session'),'ct/kWh'], width=6),
                dbc.Col(language.loc[language['name']=='price_sell',lang].iloc[0], width=12),
                dbc.Col([dcc.Input(id='price_sell',min=0,value=price_sell,placeholder='ct/kWh',type='number',style=dict(width = '50%'),persistence='session'),'ct/kWh',html.Div(id='energy_price_below2500'),html.Div(id='energy_price_above2500'),html.Div(id='power_price_below2500'),html.Div(id='power_price_above2500')], width=6),
                ],
                align='center',
                )
            download_parameter_button=dbc.Col([dbc.NavItem(button_download,style={'width':'100%'}),dcc.Download(id="download-parameters-xlsx")], width=6)
        else:
            energy_tariff_below2500, energy_tariff_above2500, power_tariff_below2500, power_tariff_above2500=eco.grid_costs_default()
            cost_use_case=dbc.Row(
                [
                dbc.Col('Arbeitspreis bei unter 2500 Volllaststunden: ', width=12),
                dbc.Col([dcc.Input(id='energy_price_below2500',min=0,value=energy_tariff_below2500*100,placeholder='ct/kWh',type='number',style=dict(width = '50%'),persistence='session'),'ct/kWh'], width=6),
                dbc.Col('Arbeitspreis bei über 2500 Volllaststunden: ', width=12),
                dbc.Col([dcc.Input(id='energy_price_above2500',min=0,value=energy_tariff_above2500*100,placeholder='ct/kWh',type='number',style=dict(width = '50%'),persistence='session'),'ct/kWh'], width=6),
                dbc.Col('Leistungspreis bei unter 2500 Volllaststunden: ', width=12),
                dbc.Col([dcc.Input(id='power_price_below2500',min=0,value=power_tariff_below2500,placeholder='€/kW',type='number',style=dict(width = '50%'),persistence='session'),'€/kW'], width=6),
                dbc.Col('Leistungspreis bei über 2500 Volllaststunden: ', width=12),
                dbc.Col([dcc.Input(id='power_price_above2500',min=0,value=power_tariff_above2500,placeholder='€/kW',type='number',style=dict(width = '50%'),persistence='session'),'€/kW', html.Div(id='price_buy'),html.Div(id='price_sell')], width=6),
                ],
                align='center',
                )
            download_parameter_button=html.Div()
        
        return html.Div(
            [html.Br(),
            html.H4(language.loc[language['name']=='invest_cost',lang].iloc[0]),
            dbc.Container(
                        [
                            dbc.Row(
                                [
                                dbc.Col(html.Div([language.loc[language['name']=='small_battery',lang].iloc[0]]), width=6),
                                dbc.Col(html.Div([str(capacity_bat_small)+' kWh']), width=6),
                                ],
                            align='center',
                            ),
                            dbc.Row(
                                [
                                dbc.Col([dcc.Input(id='specific_bat_cost_small',value=specific_bat_cost_small,type='number',style=dict(width = '50%'), persistence='session'),'€/kWh'], width=6),
                                dbc.Col(html.Div(id='absolut_bat_cost_small'), width=6),
                                ],
                            align='center',
                            ),
                            dbc.Row(
                                [
                                dbc.Col(html.Div([language.loc[language['name']=='large_battery',lang].iloc[0]]), width=6),
                                dbc.Col(html.Div([str(capacity_bat_big)+' kWh']), width=6),
                                ],
                            align='center',
                            ),
                            dbc.Row(
                                [
                                dbc.Col([dcc.Input(id='specific_bat_cost_big', value=specific_bat_cost_big,type='number', style=dict(width = '50%'),persistence='session'),'€/kWh'], width=6),
                                dbc.Col(html.Div(id='absolut_bat_cost_big'), width=6),
                                ],
                            align='center',
                            ),
                        ]),
            html.Br(),
            html.H4(language.loc[language['name']=='tariff',lang].iloc[0]),
            dbc.Container(cost_use_case),
            html.Br(),
            html.H4(language.loc[language['name']=='eco_help',lang].iloc[0]),
            dbc.Container([
                dbc.Row(dbc.Col(language.loc[language['name']=='eco_help_info',lang].iloc[0])),
                html.Br(),
                html.Br(),
                dbc.Row(
                    [
                    dbc.Col(dbc.Button(
                        html.Div(children=[DashIconify(icon='system-uicons:reset',width=50,height=30,),html.Div(language.loc[language['name']=='default',lang].iloc[0])],),
                        id='button_reset_price',
                        outline=True,
                        color="primary",
                        active=True,
                        style={'textTransform': 'none','color': '#023D6B','background-color': 'white',},
                        ), width=6),
                    download_parameter_button
                    ]
                )
            ]),
            ]
        ), last_upload

# Specific functions for a certain purpose ################
# Weather information
@app.callback(
    Output('parameter_location_int','data'),
    Output('parameter_location_string','data'),
    Input('standort', 'value'),
    )
def standorttoregion(standort):
    if (standort==''):
        raise PreventUpdate
    else:
        region=getregion(standort)
    return region, standort

@app.callback(
    Output('region', 'children'), 
    Input('parameter_location_int', 'data'),
    Input('button_language','value'))
def standorttoregion(region,lang):
    if region is None:
        raise PreventUpdate
    weather=pd.read_csv(DATA_PATH.joinpath('weather/TRY_'+str(region)+'_a_2015_15min.csv'))
    average_temperature_C=weather['temperature [degC]'].mean()
    global_irradiance_kWh_m2a=weather['synthetic global irradiance [W/m^2]'].mean()*8.76
    return ['DWD Region: ',language.loc[language['name']==str(region),lang].iloc[0]]

# Electric load profile information
@app.callback(
    Output('p_el_hh', 'data'),
    Output('stromverbrauch_value', 'children'),
    Input('stromverbrauch', 'value'),
    State('last_triggered_building','data'),
    Input('industry_type','value'))
def get_p_el_hh(e_hh,building,building_type):
    if building=='efh':
        p_el=pd.read_csv(DATA_PATH.joinpath('electrical_loadprofiles/LP_W_EFH.csv'))
    elif building=='mfh':
        if e_hh<15000:
            p_el=pd.read_csv(DATA_PATH.joinpath('electrical_loadprofiles/LP_W_MFH_k.csv'))

        elif e_hh<45000:
            p_el=pd.read_csv(DATA_PATH.joinpath('electrical_loadprofiles/LP_W_MFH_m.csv'))
        elif e_hh>45000:
            p_el=pd.read_csv(DATA_PATH.joinpath('electrical_loadprofiles/LP_W_MFH_g.csv'))
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
        p_el=pd.read_csv(DATA_PATH.joinpath('electrical_loadprofiles/'+building_type))
    return (p_el.iloc[:,1].values*e_hh/1000).tolist(), str(e_hh) + ' kWh'

# Change button style
@app.callback(
    Output('n_solar', 'style'),
    Output('n_clicks_pv', 'data'),
    Input('n_solar', 'n_clicks'),
    )
def change_solar_style(n_clicks):
    if (n_clicks%2)==1:
        return {'background-color': '#023D6B','color': 'white',},1
    else:
        return {'background-color': 'white','color': 'black'},0
@app.callback(
    Output('n_solar2', 'style'), 
    Input('n_solar2', 'n_clicks'),
    )
def change_solar2_style(n_clicks):
    if (n_clicks%2)==1:
        return {'background-color': '#023D6B','color': 'white',}
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
    Input('parameter_include_heating', 'data'),
    Input('last_triggered_building', 'data'),
    )
def change_hp_chp_style(n_chp,n_hp,heating, building):
    if (heating is None) or (len(heating)==0) or (building=='indu'):
        return {'background-color': 'white','color': 'grey'},0,{'background-color': 'white','color': 'grey'},0,0,0
    if ((n_hp%2==0) and (n_chp%2==0)) or (n_chp>=3) or (n_hp>=3):
        return {'background-color': 'white','color': 'black'},0,{'background-color': 'white','color': 'black'},0,0,0
    elif (n_chp%2)==1:
        return {'background-color': '#023D6B','color': 'white'},2,{'background-color': 'white','color': 'black'},0,1,0
    elif n_hp%2==1:
        return {'background-color': 'white','color': 'black'},0,{'background-color': '#023D6B','color': 'white'},2,0,1

# Calculation of photovoltaic output time series
@app.callback(
    Output('c_pv1', 'data'),
    Input('parameter_location_int','data'), 
    )
def calc_pv_power1(location):
    if location is None:
        raise PreventUpdate
    orientation=180
    tilt=35
    type='a'
    year=2015
    pv1=sim.calc_pv(trj=location-1,year=year,type=type,tilt=tilt,orientation=orientation)
    return pv1
@app.callback(
    Output('p_pv1', 'data'),
    Output('parameter_pv','data'),
    Input('pv_slider','value'),
    Input('c_pv1','data'),)
def scale_pv1(pv_slider1, pv1):
    if pv_slider1 is None:
        raise PreventUpdate
    pv1=np.array(pv1) * pv_slider1
    return list(pv1),pv_slider1

# Calculation of thermal building and hot water demand time series
@app.callback(
    Output('p_th_load', 'data'), 
    Output('building', 'data'),
    Output('building_type_value','children'), 
    Input('parameter_include_heating', 'data'),
    Input('parameter_location_int','data'),
    Input('parameter_wohnfläche','data'),
    Input('parameter_building_type','data'),
    Input('button_language','value'))
def calc_heating_timeseries(heating,region,Area,building_type, lang):
    if (heating is None) or (region is None) or (Area is None) or(building_type is None):
        return None, None, None
    # 1 person for every 50m² in a SFH
    inhabitants = Area[0]
    Area=Area[1]
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
    # Get min temp. for location
    TRJ=pd.read_csv(DATA_PATH.joinpath('weather/TRJ-Tabelle.csv'))
    building['T_min_ref'] = TRJ['T_min_ref'][region-1]
    building['Area']=Area
    building['Inhabitants']=inhabitants
    building['location']=str(region)
    t_room=20
    P_tww = 1000+200*building['Inhabitants']    # additional heating load for DHW in W 1000 W + 200 W/person
    P_th_max=(t_room - building['T_min_ref']) * building['Q_sp'] * building['Area'] + P_tww
    # Calc heating load time series with 24h average outside temperature
    weather = pd.read_csv(DATA_PATH.joinpath('weather/TRY_'+str(region)+'_a_2015_15min.csv'), header=0, index_col=0)
    weather.loc[weather['temperature 24h [degC]']<building['T_limit'],'p_th_heating']=(t_room-weather.loc[weather['temperature 24h [degC]']<building['T_limit'],'temperature 24h [degC]'])* building['Q_sp'] * Area
    weather.loc[weather['temperature 24h [degC]']>=building['T_limit'],'p_th_heating']=0
    # Load domestic hot water load profile
    load = pd.read_csv(DATA_PATH.joinpath('thermal_loadprofiles/dhw_'+str(int(inhabitants)) +'_15min.csv'), header=0, index_col=0)
    load['p_th_heating [W]']=weather['p_th_heating'].values
    load_dict=load[['load [W]','p_th_heating [W]']].to_dict()
    return load_dict, building, language.loc[language['name']=='max_heatload',lang].iloc[0]+str(int(round(P_th_max)))+' W'

# Calculation of heat pump power and efficiency time series
@app.callback(
    Output('hp_technology_value', 'children'), 
    Output('power_heat_pump_W', 'data'),
    Output('parameter_hp','data'),
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
    else:
        raise PreventUpdate
    P_hp_el , results_summary, t_in, t_out = sim.calc_hp(building,p_th_load,group_id)
    return (html.Div('SJAZ: '+str((round(results_summary['SJAZ'],2)))+ ', ' +str(int(round(results_summary['Energy_consumption_kWh'],0)))+' kWh')), \
            P_hp_el.values.tolist(),\
            choosen_hp

# Calculation of heat pump power and efficiency time series
@app.callback(
    Output('chp_load_hours', 'children'), 
    Output('chp_technology_value', 'children'), 
    Output('chp_technology_value2', 'children'), 
    Output('power_chp_W', 'data'),
    Output('parameter_chp','data'),
    Input('building','data'),
    Input('p_th_load','data'),
    Input('chp_max_power','value'),
    Input('chp_technology','value'),
    State('n_chp', 'style'),
    Input('button_language', 'value')
    )
def sizing_of_chp(building, p_th_load,chp_max_ratio, choosen_chp, chp_active, lang):
    if (choosen_chp is None) or chp_active['color']!='white':
        raise PreventUpdate
    results_timeseries, P_th_max, P_th_chp, P_el_chp, runtime = sim.calc_chp(building,p_th_load,choosen_chp,chp_to_peak_ratio=chp_max_ratio)
    return (html.Div(str(int(round(runtime)))+' '+ language.loc[language['name']=='load_hours',lang].iloc[0]),
            html.Div(str((round(P_th_chp/1000,1)))+' kWth'),
            html.Div(str((round(P_el_chp/1000,1))) + ' kWel'),
            results_timeseries['P_chp_h_el'].values.tolist(), \
            choosen_chp)

# Save parameter 'include heating'
@app.callback(
    Output('parameter_include_heating', 'data'),
    Input('include_heating', 'value'),
    )
def save_state_heating(include_heating):
    if include_heating is None:
        raise PreventUpdate
    return include_heating

# Save living area and inhabitants
@app.callback(
    Output('parameter_wohnfläche', 'data'),
    Output('stromverbrauch', 'value'),
    Input('wohnfläche', 'value'),
    State('last_triggered_building', 'data'),
    State('stromverbrauch', 'value'),
    )
def print_wohnfläche_value(wohnfläche, building, electricity_consumption):
    if building is None: 
        raise PreventUpdate
    if building=='mfh':
        return [wohnfläche*2,wohnfläche*70], wohnfläche*1500
    return [wohnfläche/50, wohnfläche], electricity_consumption

#Show living area in m² or residential units
@app.callback(
    Output('wohnfläche_value', 'children'),
    Input('parameter_wohnfläche', 'data'),
    State('last_triggered_building', 'data'),
    )
def print_wohnfläche_value(wohnfläche, building):
    if building is None: 
        raise PreventUpdate
    if building=='mfh':
        return html.Div(str(int(wohnfläche[1]/70))+ ' WE')
    return html.Div(str(wohnfläche[1])+ ' m²')

# Save parameter 'building_type'
@app.callback(
    Output('parameter_building_type', 'data'),
    Input('building_type', 'value'),
    )
def save_parameter_building_type(building_type):
    if building_type is None:
        raise PreventUpdate
    return building_type

# Show photovoltaic power
@app.callback(
    Output('pv_slider_value', 'children'),
    Input('pv_slider', 'value'),
    )
def print_pv_slider_value(pv_slider):
    return html.Div(str(pv_slider)+ ' kWp')

# Save electricity price autarky
@app.callback(
    Output('price_electricity', 'data'),
    Input('price_buy', 'value'),
    Input('price_sell', 'value'),
    Input('button_reset_price', 'n_clicks'),
    )
def save_price_buy(price_buy,price_sell, tabs):
    return [price_buy, price_sell]

# Save electricity price peak shaving
@app.callback(
    Output('price_electricity_peak', 'data'),
    Input('energy_price_below2500', 'value'),
    Input('energy_price_above2500', 'value'),
    Input('power_price_below2500', 'value'),
    Input('power_price_above2500', 'value'),
    Input('button_reset_price', 'n_clicks'),
    )
def save_price_buy_peak(energy_tariff_below2500, energy_tariff_above2500, power_tariff_below2500, power_tariff_above2500, tabs):
    return [energy_tariff_below2500/100, energy_tariff_above2500/100, power_tariff_below2500, power_tariff_above2500]

# Show investment cost batteries
@app.callback(
    Output('absolut_bat_cost_small', 'children'),
    Output('absolut_bat_cost_big', 'children'),
    Input('specific_bat_cost_small', 'value'),
    Input('specific_bat_cost_big', 'value'),
    State('parameter_use', 'data'),
    State('batteries', 'data'),
    State('parameter_peak_shaving', 'data'),
    Input('button_reset_price', 'n_clicks'),
    )
def show_investmentcost_small(specific_bat_cost_small, specific_bat_cost_big, LSK, batteries, df_peak_shaving_results, tabs):
    if LSK==0:
        capacity_bat_small = batteries['e_bat']['1']
        capacity_bat_big = batteries['e_bat']['5']
    else:
        df=(pd.DataFrame().from_dict(df_peak_shaving_results))
        try:
            df=(df.loc[(df['Entladerate']>0.5) &  (df['Entladerate']<2.5)])
            capacity_bat_small=round(df['nutzbare Speicherkapazität in kWh'].values[0],1)
            capacity_bat_big=round(df['nutzbare Speicherkapazität in kWh'].values[-1],1)
        except:
            df=(df.loc[(df['Discharge rate']>0.5) &  (df['Discharge rate']<2.5)])
            capacity_bat_small=round(df['Usable storage capacity in kWh'].values[0],1)
            capacity_bat_big=round(df['Usable storage capacity in kWh'].values[-1],1)
    return html.Div([str(round(specific_bat_cost_small * capacity_bat_small))+ ' €']),\
            html.Div([str(round(specific_bat_cost_big * capacity_bat_big))+ ' €'])

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

# Download
@app.callback(
    Output('download-parameters-xlsx', 'data'),
    Input('button_download', 'n_clicks'),
    State('last_triggered_building', 'data'),
    State('p_el_hh','data'),
    State('n_clicks_pv', 'data'),
    State('n_clicks_chp', 'data'),
    State('n_clicks_hp', 'data'),
    State('building', 'data'),
    State('price_electricity', 'data'),
    State('specific_bat_cost_small', 'value'),
    State('specific_bat_cost_big', 'value'),
    State('parameter_lang', 'data'),
    State('parameter_use', 'data'),
    State('parameter_location_string', 'data'),
    State('parameter_pv', 'data'),
    State('parameter_chp', 'data'),
    State('parameter_hp', 'data'),
    prevent_initial_call=True,
)
def download(n1, last_triggered_building, p_el_hh, n_clicks_pv, n_clicks_chp, n_clicks_hp, building, price_electricity,specific_bat_cost_small, specific_bat_cost_big, parameter_lang, parameter_use, parameter_location_string, parameter_pv, parameter_chp, parameter_hp):
    df=pd.DataFrame()
    df['Language']=[parameter_lang]
    df['use_case']=[parameter_use]
    df['location']=[parameter_location_string]
    df['Building']=[last_triggered_building]
    df['electricicty_consumption']=[int(round(np.array(p_el_hh).mean()*8.76,0))]
    df['n_clicks_pv']=[n_clicks_pv]
    df['pv_kwp']=[parameter_pv]
    df['n_clicks_chp']=[n_clicks_chp]
    df['chp_electric_heat_ratio']=[parameter_chp]
    df['n_clicks_hp']=[n_clicks_hp]
    df['hp_technology']=[parameter_hp]
    if building is not None:
        include_heating=1
        Area=building['Area']
        if building['T_vl_max']==55:
            building='Bestand, unsaniert'
        elif building['T_vl_max']==45:
            building='Bestand, saniert'
        else:
            building='Neubau, nach 2016'
    else:
        include_heating=0
        building=0
        Area=0
    df['include_heating']=[include_heating]
    df['Building_type']=[building]
    df['Building_size']=[Area]
    df['Electricity_price']=[price_electricity]
    df['specific_bat_cost_small']=[specific_bat_cost_small]
    df['specific_bat_cost_big']=[specific_bat_cost_big]
    df['Building_size']=[Area]
    
    return dcc.send_data_frame(df.to_excel, "VDI_4657_parameter.xlsx", sheet_name="Sheet_name_1")

# Upload
@app.callback(
    Output('parameters_all', 'data'),
    Output('parameters_all', 'modified_timestamp'),
    Input('upload_parameters', 'contents'),
)
def upload(file):
    if file is None:
        raise PreventUpdate
    content_type, content_string = file.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded))
    return df.to_dict(),ctx.timing_information['__dash_server']['dur']*1000

# Upload load profile
@app.callback(
    Output('kpi_LSK', 'children'),
    Output('parameter_loadprofile', 'data'),
    Input('upload_load_profile', 'contents'),
    Input('upload_load_profile', 'filename'),
    Input('button_language', 'value'),
)
def upload_loadprofile(file, name, lang):
    if file is None:
        raise PreventUpdate
    content_type, content_string = file.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in name:
        # Assume that the user uploaded a CSV file
        decoded_split=decoded.decode('utf-8').split('\n')
        if decoded_split[-1:]=='':
            decoded_split=(decoded_split[:-1])
        try:
            df = pd.read_csv(io.StringIO('\n'.join(decoded_split[-35042:])), sep=',')
            sep=','
        except:
            pass
        if len(df.columns)==1:
            sep=';'
        df = pd.read_csv(io.StringIO('\n'.join(decoded_split[-35042:])), sep=sep)
        if(len(df.mean())==0):
            df = pd.read_csv(io.StringIO('\n'.join(decoded_split[-35042:])),decimal=',', sep=sep)
    elif 'xls' in name:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(io.BytesIO(decoded), decimal='.')
        if (len(df))>35040:
            df = pd.read_excel(io.BytesIO(decoded),header=len(df)-35040, decimal='.')
        if len(df.columns)==1:
            df = pd.read_excel(io.BytesIO(decoded), header=len(df)-35040, decimal=',')
    biggest_column=(df.mean().sort_values(ascending=False).index[0])
    E_gs, P_gs_max, t_util_a = sim.calc_gs_kpi(df.loc[:,biggest_column]*1000)
    return html.Div([language.loc[language['name']=='choosen_column',lang].iloc[0] + biggest_column,html.Br(),
        language.loc[language['name']=='grid_supply',lang].iloc[0] + str(int(round(E_gs/1000,0)))+ ' kWh',html.Br(),
        language.loc[language['name']=='max_grid_supply',lang].iloc[0]+ str(round(P_gs_max/1000,2))+ ' kW',html.Br(),
        language.loc[language['name']=='load_hours',lang].iloc[0] + ': ' + str(t_util_a) + ' h']), (df.loc[:,biggest_column]*1000).to_list()

# Calculate Peak-shaving
@app.callback(
    Output('parameter_peak_shaving', 'data'),
    Input('parameter_loadprofile', 'data'),
    Input('button_language', 'value'),
)
def calculate_peak_shaving(loadprofile, lang):
    loadprofile=pd.DataFrame({'LP' : loadprofile}) #W
    df = sim.calc_bs_peakshaving(loadprofile['LP'])
    df['P_bs_discharge_max'] = df['P_bs_discharge_max']/1000    #kW
    df['C_bs'] = df['C_bs']/1000                                #kWh
    df.rename(columns={'P_bs_discharge_max':language.loc[language['name']=='cut_peak',lang].iloc[0], 'C_bs':language.loc[language['name']=='usable_battery_size',lang].iloc[0], 't_util':language.loc[language['name']=='load_hours',lang].iloc[0], 'E_rate': language.loc[language['name']=='e_rate',lang].iloc[0]}, inplace=True)
    return df.to_dict()

# Show Peak-Shaving
@app.callback(
    Output('bat_results_LSK', 'children'),
    Input('parameter_peak_shaving', 'data'),
    Input('tabs', 'value'),
    State('parameter_use', 'data'),
    State('button_language', 'value')
)
def upload_loadprofile(df, tab, use_case, lang):
    if (use_case==0) or (tab!='tab_parameter'):
        return html.Div()
    df= pd.DataFrame().from_dict(df)
    fig=px.scatter(data_frame=df,x=language.loc[language['name']=='cut_peak',lang].iloc[0],y=language.loc[language['name']=='usable_battery_size',lang].iloc[0],color=language.loc[language['name']=='e_rate',lang].iloc[0],size=language.loc[language['name']=='load_hours',lang].iloc[0])
    colorscale=[[0, "#ff0000"],[0.05, "#ff3300"],[0.1, "#ff6600"],[0.15, "#ff9900"],[0.2, "#ffcc00"],[0.25, "#ffff00"],[0.3, "#cdee0a"],[0.35, "#9add14"],[0.4, "#67cc1e"],[0.45, "#34bb28"],[0.5, "#00a933"],[0.55, "#34bb28"],[0.6, "#67cc1e"],[0.65, "#9add14"],[0.7, "#cdee0a"],[0.75, "#ffff00"],[0.8, "#ffcc00"],[0.85, "#ff9900"],[0.9, "#ff6600"],[0.95, "#ff3300"],[1, "#ff0000"]]
    colorbar=dict(tickmode='array',tickvals=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],len=1.05,ticklabeloverflow='allow',outlinewidth=0)
    fig.update_layout(coloraxis = {'cmin':0,'cmax':3.0,'colorscale':colorscale,'colorbar':colorbar,'autocolorscale':False},)
    fig.update_layout(margin=dict(l=20, r=20, b=20),)
    return dcc.Graph(figure=fig, config={'displayModeBar': False})


# reset price
@app.callback(
    Output('price_sell', 'value'),
    Output('price_buy', 'value'),
    Output('energy_price_below2500', 'value'),
    Output('energy_price_above2500', 'value'),
    Output('power_price_below2500', 'value'),
    Output('power_price_above2500', 'value'),
    Output('specific_bat_cost_small', 'value'),
    Output('specific_bat_cost_big', 'value'),
    Input('button_reset_price', 'n_clicks'),
    State('parameter_use', 'data'),
    State('batteries','data'),
    State('parameter_peak_shaving', 'data'),
)
def reset_economy(n,LSK,batteries,df_peak_shaving_results):
    if n is None:
        raise PreventUpdate
    I_0,exp=eco.invest_params_default()
    if LSK==0:
        capacity_bat_small = batteries['e_bat']['1']
        capacity_bat_big = batteries['e_bat']['5']
        price_sell=6
        price_buy=35
        energy_price_below2500 = ''
        energy_price_above2500 = ''
        power_price_below2500 = ''
        power_price_above2500 = ''
    else:
        price_sell=''
        price_buy=''
        energy_price_below2500, energy_price_above2500, power_price_below2500, power_price_above2500=eco.grid_costs_default()
        energy_price_below2500=energy_price_below2500*100
        energy_price_above2500=energy_price_above2500*100
        df=(pd.DataFrame().from_dict(df_peak_shaving_results))
        try:
            df=(df.loc[(df['Entladerate']>0.5) &  (df['Entladerate']<2.5)])
            capacity_bat_small=round(df['nutzbare Speicherkapazität in kWh'].values[0],1)
            capacity_bat_big=round(df['nutzbare Speicherkapazität in kWh'].values[-1],1)
        except:
            df=(df.loc[(df['Discharge rate']>0.5) &  (df['Discharge rate']<2.5)])
            capacity_bat_small=round(df['Usable storage capacity in kWh'].values[0],1)
            capacity_bat_big=round(df['Usable storage capacity in kWh'].values[-1],1)
    specific_bat_cost_small,_ = eco.invest_costs(capacity_bat_small, I_0, exp)
    specific_bat_cost_big, _ = eco.invest_costs(capacity_bat_big, I_0, exp)
    return price_sell,price_buy,energy_price_below2500, energy_price_above2500, power_price_below2500, power_price_above2500,int(round(float(specific_bat_cost_small)/50)*50),int(round(float(specific_bat_cost_big)/50)*50)

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
    State('n_solar', 'n_clicks'),
    State('n_hp','style'),
    State('n_chp','style'),
    State('last_triggered_building', 'data'),
    )
def calc_bat_results(p_el_hh,power_heat_pump_W,power_chp_W,pv1,n_pv1,n_hp_style,n_chp_style, building):
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
    if building!='efh':
        if (E_chp>0):
            max_battery_size = np.ceil(round(E_el_MWH,0)/5)*5
        else:
            max_battery_size = np.ceil(np.minimum(round(E_el_MWH,0)*1.5,E_pv_kwp*1.5)/5)*5
    else:
        if (E_chp>0):
            max_battery_size = np.ceil(round(E_el_MWH,0)*1.5/5)*5#TODO: CHP battery sizing?
        else:
            max_battery_size = np.ceil(np.minimum(round(E_el_MWH,0)*2.5,E_pv_kwp*2.5)/5)*5 #TODO: CHP battery sizing?
    batteries=sim.calc_bs(df, np.maximum(10,max_battery_size))
    return batteries.to_dict()

# Show selection for different graphs (self sufficiency, self consumption or energy balance)
@app.callback(
    Output('bat_results', 'children'),
    Input('batteries', 'data'),
    Input('tabs', 'value'),
    State('parameter_include_heating', 'data'),
    State('n_clicks_hp', 'data'),
    State('n_clicks_chp', 'data'),
    State('last_triggered_building', 'data'),
    State('parameter_use', 'data'),
    Input('button_language', 'value'),
    )
def bat_results(batteries,tab,include_heating,n_hp,n_chp, building, parameter_use, lang):
    if n_hp is None:
        n_hp=0
    if n_chp is None:
        n_chp=0
    if (batteries is None) or ((building!='indu') & (include_heating is None)):
        raise PreventUpdate
    elif (len(batteries)==3) or (tab!='tab_parameter') or (parameter_use!=0):
        return html.Div()
    elif building != 'indu':
        if(len(include_heating)==1) and (n_hp==0) and (n_chp==0):
            return html.Div()
    return html.Div(children=[html.Br(),
    dbc.Container([
        dbc.Row([
            dbc.Col(width=1),
            dbc.Col(dbc.Button(language.loc[language['name']=='self_sufficiency',lang].iloc[0],id='Autarkiegrad',color="primary", active=True)),#,style={'color':'#023D6B'}
            dbc.Col(dbc.Button(language.loc[language['name']=='self_consumption',lang].iloc[0],id='Eigenverbrauch',color="primary", active=True)),
            dbc.Col(dbc.Button(language.loc[language['name']=='energy_balance',lang].iloc[0],id='Energiebilanz',color="primary", active=True))
            ]),html.Br()
        ], fluid=True),html.Div(id='bat_result_graph')])

# return choosen value for bat_results    
@app.callback(
    Output('show_bat_results', 'data'),
    Output('Autarkiegrad', 'style'),
    Output('Eigenverbrauch', 'style'),
    Output('Energiebilanz', 'style'),
    Input('Autarkiegrad', 'n_clicks'),
    Input('Eigenverbrauch', 'n_clicks'),
    Input('Energiebilanz', 'n_clicks'),
    State('show_bat_results', 'data'),
    )
def bat_choosen_results(aut, eig, energy, data):
    show_graph=ctx.triggered_id
    if ((ctx.triggered_id=='Autarkiegrad')and(aut==0))or ((ctx.triggered_id=='Eigenverbrauch')and(eig==0)) or ((ctx.triggered_id=='Energiebilanz')and(energy==0)):
        show_graph=data
    if data is None: 
        show_graph='Autarkiegrad'
    if show_graph=='Autarkiegrad':
        return show_graph, {'background-color': '#023D6B','color': 'white',},{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'}
    elif show_graph=='Eigenverbrauch':
        return show_graph,{'background-color': 'white','color': 'black'},{'background-color': '#023D6B','color': 'white',},{'background-color': 'white','color': 'black'}
    elif show_graph=='Energiebilanz':
        return show_graph, {'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'},{'background-color': '#023D6B','color': 'white',}

# show choosen graph    
@app.callback(
    Output('bat_result_graph', 'children'),
    Input('batteries', 'data'),
    Input('tabs', 'value'),
    Input('show_bat_results', 'data'),
    Input('button_language', 'value'),
    )
def bat_results(batteries,tab,results_id, lang):
    if (batteries is None) or (tab!='tab_parameter'):
        return html.Div()
    elif (len(batteries)==3) or (tab!='tab_parameter'):
        return html.Div('Bitte Erzeuger auswählen!')
    batteries=pd.DataFrame.from_dict(batteries)
    batteries['e_bat']=batteries['e_bat'].astype('str')
    if lang=='ger':
        if results_id=='Autarkiegrad':
            fig=px.bar(data_frame=batteries,x='e_bat',y=['Autarkiegrad ohne Stromspeicher','Erhöhung der Autarkie durch Stromspeicher'],
                color_discrete_map={'Autarkiegrad ohne Stromspeicher': '#ffe43b', 'Erhöhung der Autarkie durch Stromspeicher' : '#ffbd29'},
                labels={"e_bat": "nutzbare Speicherkapazität in kWh",
                        "value": "%",
                        'variable': ''
                        }
                )
        elif results_id=='Eigenverbrauch':
            fig=px.bar(data_frame=batteries,x='e_bat',y=['Eigenverbrauch ohne Stromspeicher','Erhöhung des Eigenverbrauchs durch Stromspeicher'],
                color_discrete_map={'Eigenverbrauch ohne Stromspeicher': '#ffe43b', 'Erhöhung des Eigenverbrauchs durch Stromspeicher' : '#ffbd29'},
                labels={"e_bat": "nutzbare Speicherkapazität in kWh",
                        "value": "%",
                        'variable': ''
                        }
                )
        elif results_id=='Energiebilanz':
            fig=px.bar(data_frame=batteries,x='e_bat',y=['Netzeinspeisung','Netzbezug'],
                color_discrete_map={'Netzeinspeisung': '#c8c8c8', 'Netzbezug' : '#646464'},
                labels={"e_bat": "nutzbare Speicherkapazität in kWh",
                        "value": "Netzbezug/Netzeinspeisung in kWh/a",
                        'variable': ''
                        }
                )
    else:
        batteries.rename(columns = {'Autarkiegrad ohne Stromspeicher':'Degree of self-sufficiency without battery',
                                    'Erhöhung der Autarkie durch Stromspeicher':'Increasing self-sufficiency battery',
                                    'Eigenverbrauch ohne Stromspeicher':'Self-consumption without battery',
                                    'Erhöhung des Eigenverbrauchs durch Stromspeicher':'Increase of self-consumption by battery',
                                    'Netzeinspeisung':'Grid feed-in',
                                    'Netzbezug': 'Grid supply'
                                    }, inplace = True)
        if results_id=='Autarkiegrad':
            fig=px.bar(data_frame=batteries,x='e_bat',y=['Degree of self-sufficiency without battery','Increasing self-sufficiency battery'],
                color_discrete_map={'Degree of self-sufficiency without battery': '#ffe43b', 'Increasing self-sufficiency battery' : '#ffbd29'},
                labels={"e_bat": "usable battery size in kWh",
                        "value": "%",
                        'variable': ''
                        }
                )
        elif results_id=='Eigenverbrauch':
            fig=px.bar(data_frame=batteries,x='e_bat',y=['Self-consumption without battery','Increase of self-consumption by battery'],
                color_discrete_map={'Self-consumption without battery': '#ffe43b', 'Increase of self-consumption by battery' : '#ffbd29'},
                labels={"e_bat": "usable battery size in kWh",
                        "value": "%",
                        'variable': ''
                        }
                )
        elif results_id=='Energiebilanz':
            fig=px.bar(data_frame=batteries,x='e_bat',y=['Grid feed-in','Grid supply'],
                color_discrete_map={'Grid feed-in': '#c8c8c8', 'Grid supply' : '#646464'},
                labels={"e_bat": "usable battery size in kWh",
                        "value": "Grid supply/Grid feed-in in kWh/a",
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
    fig.update_layout(margin=dict(l=20, r=20, b=20),)
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

# Show selection for different graphs (economy tab)
@app.callback(
    Output('cost_result', 'children'),
    State('batteries', 'data'), 
    Input('tabs', 'value'),
    State('parameter_use', 'data'),
    Input('button_language', 'value'),
    )
def economic_results(batteries, tab, parameter_use, lang):
    if tab!='tab_econmics': 
        return html.Div()
    if parameter_use==0:
        if batteries is None:
            return html.Div()
    return html.Div(children=[html.Br(),
    dbc.Container([
        dbc.Row([
            dbc.Col(width=1),
            dbc.Col(dbc.Button(language.loc[language['name']=='payback',lang].iloc[0],id='Amortisationszeit',color="primary", active=True)),
            dbc.Col(dbc.Button(language.loc[language['name']=='NPV',lang].iloc[0],id='NetPresentValue',color="primary", active=True)),
            dbc.Col(dbc.Button(language.loc[language['name']=='IROR',lang].iloc[0],id='InternalRateOfReturn',color="primary", active=True))
            ]),html.Br(),html.Br(),
        dbc.Row(id='cost_result_graph')
        ])])

# return choosen value for economy_results    
@app.callback(
    Output('show_economic_results', 'data'),
    Output('Amortisationszeit', 'style'),
    Output('NetPresentValue', 'style'),
    Output('InternalRateOfReturn', 'style'),
    Input('Amortisationszeit', 'n_clicks'),
    Input('NetPresentValue', 'n_clicks'),
    Input('InternalRateOfReturn', 'n_clicks'),
    State('show_economic_results', 'data')
    )
def eco_results(aut, eig, energy, data):
    show_graph=ctx.triggered_id
    if ((ctx.triggered_id=='Amortisationszeit')and(aut==0))or ((ctx.triggered_id=='NetPresentValue')and(eig==0)) or ((ctx.triggered_id=='InternalRateOfReturn')and(energy==0)):
        show_graph=data
    if data is None: 
        show_graph='Amortisationszeit'
    if show_graph=='Amortisationszeit':
        return show_graph, {'background-color': '#023D6B','color': 'white',},{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'}
    elif show_graph=='NetPresentValue':
        return show_graph,{'background-color': 'white','color': 'black'},{'background-color': '#023D6B','color': 'white',},{'background-color': 'white','color': 'black'}
    elif show_graph=='InternalRateOfReturn':
        return show_graph, {'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'},{'background-color': '#023D6B','color': 'white',}

# Show choosen graph (economy tab)
@app.callback(
    Output('cost_result_graph', 'children'),
    State('batteries', 'data'),
    State('parameter_peak_shaving', 'data'),
    Input('price_electricity','data'),
    Input('price_electricity_peak','data'),
    Input('specific_bat_cost_small','value'),
    Input('specific_bat_cost_big','value'),
    Input('tabs', 'value'),
    Input('show_economic_results', 'data'),
    State('parameter_use', 'data'),
    Input('button_language', 'value'),
    )
def economic_results_graph(batteries,batteries_peak,electricity_price,electricity_price_peak,specific_bat_cost_small,specific_bat_cost_big,tab,results_id, LSK, lang):
    if ((electricity_price is None) and (LSK==0)) or ((electricity_price_peak is None) and (LSK==1)): 
        raise PreventUpdate
    if (LSK==0):
        batteries=(pd.DataFrame(batteries))
        if (electricity_price[0] is None) or (electricity_price[1] is None) or (batteries is None) or (tab!='tab_econmics'): 
            return html.Div()
        years=15
        lifetime=15
        interest_rate=0.015
        Invest_cost=[]
        NetPresentValue=[]
        Amortisation=[]
        InternalRateOfReturn=[]
        I_0, exp = eco.invest_params([batteries['e_bat'].values[1],batteries['e_bat'].values[-1]],[specific_bat_cost_small,specific_bat_cost_big])
        for battery in batteries.index[1:]:
            i, I = eco.invest_costs(batteries.loc[battery]['e_bat'], I_0,exp)
            Invest_cost.append(str(round(I))+ ' €')
            cashflow = eco.cash_flow_self_consumption(I,
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
        batteries=batteries.iloc[1:,:]
        batteries['e_bat']=batteries['e_bat'].astype('str')
        batteries['Investitionskosten']=Invest_cost
        batteries['NetPresentValue']=NetPresentValue
        batteries['Amortisation']=Amortisation
        batteries['InternalRateOfReturn']=np.array(InternalRateOfReturn)*100
        if results_id.startswith('Amortisationszeit'):
            Amortisation0=np.array(Amortisation)[np.where(np.array(Amortisation)>0)]
            if len(Amortisation0)==1:
                Amortisation_min=np.where(np.array(Amortisation)==(min(Amortisation0)))[0]
                title = language.loc[language['name']=='eco_text_1',lang].iloc[0] + batteries['e_bat'].values[Amortisation_min[0]] + language.loc[language['name']=='eco_text_2',lang].iloc[0]
            elif len(Amortisation0)>0:
                Amortisation_min=np.where(np.array(Amortisation)==(min(Amortisation0)))[0]
                if len(Amortisation_min)==1:
                    fastest_amort_battery = batteries['e_bat'].values[Amortisation_min[0]]
                    title = language.loc[language['name']=='eco_text_3',lang].iloc[0]+ fastest_amort_battery + language.loc[language['name']=='eco_text_4',lang].iloc[0]
                else:
                    title= language.loc[language['name']=='eco_text_5',lang].iloc[0]
            else:
                title = language.loc[language['name']=='eco_text_6',lang].iloc[0]
            fig=px.bar(data_frame=batteries, x='e_bat', y='Amortisation', hover_data=['Investitionskosten'],
                    color_discrete_sequence=['#023D6B'], 
                    labels={"e_bat": language.loc[language['name']=='usable_battery_size',lang].iloc[0],
                        "Amortisation": language.loc[language['name']=='payback_years',lang].iloc[0],
                        })
            fig.update_layout(margin=dict(l=20, r=20, b=20),)
            return [dbc.Col(html.H6(title),width={'offset':2}),dbc.Col(dcc.Graph(figure=fig,config={'displayModeBar': False}),width=12)]
        elif results_id.startswith('NetPresentValue'):
            NetPresentValue_max=max(NetPresentValue)
            best_value_battery = batteries['e_bat'].values[NetPresentValue.index(NetPresentValue_max)]
            if NetPresentValue_max>0:
                title = language.loc[language['name']=='eco_text_3',lang].iloc[0] + best_value_battery + language.loc[language['name']=='eco_text_7',lang].iloc[0]
            else:
                title = language.loc[language['name']=='eco_text_8',lang].iloc[0]
            fig=px.bar(data_frame=batteries, x='e_bat', y='NetPresentValue', hover_data=['Investitionskosten'],
                    color_discrete_sequence=['#023D6B'], 
                    labels={"e_bat": language.loc[language['name']=='usable_battery_size',lang].iloc[0],
                        "NetPresentValue": language.loc[language['name']=='NPV',lang].iloc[0],
                        })
            fig.update_yaxes(ticksuffix = " €")
            fig.update_layout(margin=dict(l=20, r=20, b=20),)
            return [dbc.Col(html.H6(title),width={'offset':2}),dbc.Col(dcc.Graph(figure=fig,config={'displayModeBar': False}),width=12)]
        elif results_id.startswith('InternalRateOfReturn'):
            InternalRateOfReturn_max=max(InternalRateOfReturn)
            best_value_battery = batteries['e_bat'].values[InternalRateOfReturn.index(InternalRateOfReturn_max)]
            if InternalRateOfReturn_max>0:
                title = language.loc[language['name']=='eco_text_9',lang].iloc[0] + best_value_battery + language.loc[language['name']=='eco_text_10',lang].iloc[0] + str(round(InternalRateOfReturn_max*100,2)) + ' %.'
            else:
                title = language.loc[language['name']=='eco_text_8',lang].iloc[0]
            fig=px.bar(data_frame=batteries, x='e_bat', y='InternalRateOfReturn', hover_data=['Investitionskosten'],
                    color_discrete_sequence=['#023D6B'], 
                    labels={"e_bat": language.loc[language['name']=='usable_battery_size',lang].iloc[0],
                        "InternalRateOfReturn": language.loc[language['name']=='IROR',lang].iloc[0],
                        })
            fig.update_yaxes(ticksuffix = " %")
            fig.update_layout(margin=dict(l=20, r=20, b=20),)
            return [dbc.Col(html.H6(title),width={'offset':2}),dbc.Col(dcc.Graph(figure=fig,config={'displayModeBar': False}),width=12)]
    else:
        df=pd.DataFrame().from_dict(batteries_peak)
        try:
            df=(df.loc[(df['Entladerate']>0.5) &  (df['Entladerate']<2.5)])
            capacity_bat_small=round(df['nutzbare Speicherkapazität in kWh'].values[0],1)
            capacity_bat_big=round(df['nutzbare Speicherkapazität in kWh'].values[-1],1)
        except:
            df=(df.loc[(df['Discharge rate']>0.5) &  (df['Discharge rate']<2.5)])
            capacity_bat_small=round(df['Usable storage capacity in kWh'].values[0],1)
            capacity_bat_big=round(df['Usable storage capacity in kWh'].values[-1],1)
        years=15
        lifetime=15
        interest_rate=0.015
        Invest_cost=[]
        NetPresentValue=[]
        Amortisation=[]
        InternalRateOfReturn=[]
        I_0, exp = eco.invest_params([capacity_bat_small,capacity_bat_big],[specific_bat_cost_small,specific_bat_cost_big])
        for battery in df.index:
            i, I = eco.invest_costs(df.loc[battery][language.loc[language['name']=='usable_battery_size',lang].iloc[0]], I_0,exp)
            Invest_cost.append(str(round(I))+ ' €')
            cashflow = eco.cash_flow_peak_shaving(I,
                batteries_peak['E_gs']['0']/1000,
                df.loc[battery]['E_gs']/1000,
                batteries_peak[language.loc[language['name']=='load_hours',lang].iloc[0]]['0'],
                df.loc[battery][language.loc[language['name']=='load_hours',lang].iloc[0]],
                batteries_peak['P_gs_max']['0']/1000,
                df.loc[battery]['P_gs_max']/1000,
                electricity_price_peak[0],
                electricity_price_peak[1],
                electricity_price_peak[2],
                electricity_price_peak[3],
                years,
                lifetime,
                )
            NetPresentValue.append(eco.net_present_value(cashflow, interest_rate))
            Amortisation.append(eco.amortisation(cashflow))
            InternalRateOfReturn.append(eco.internal_rate_of_return(cashflow))
        df[language.loc[language['name']=='invest_cost',lang].iloc[0]]=Invest_cost
        df['NetPresentValue']=NetPresentValue
        df['Amortisation']=np.where(np.array(Amortisation)==0,15,np.array(Amortisation))
        df['InternalRateOfReturn']=np.array(InternalRateOfReturn)*100
        if results_id.startswith('Amortisationszeit'):
            Amortisation0=np.array(Amortisation)[np.where(np.array(Amortisation)>0)]
            if len(Amortisation0)==1:
                Amortisation_min=np.where(np.array(Amortisation)==(min(Amortisation0)))[0]
                title = language.loc[language['name']=='eco_text_1',lang].iloc[0] + str(round(df[language.loc[language['name']=='usable_battery_size',lang].iloc[0]].values[Amortisation_min[0]],1)) + language.loc[language['name']=='eco_text_2',lang].iloc[0]
            elif len(Amortisation0)>0:
                Amortisation_min=np.where(np.array(Amortisation)==(min(Amortisation0)))[0]
                if len(Amortisation_min)==1:
                    fastest_amort_battery = df[language.loc[language['name']=='usable_battery_size',lang].iloc[0]].values[Amortisation_min[0]]
                    title = language.loc[language['name']=='eco_text_3',lang].iloc[0]+ str(round(fastest_amort_battery),1) + language.loc[language['name']=='eco_text_4',lang].iloc[0]
                else:
                    title= language.loc[language['name']=='eco_text_5',lang].iloc[0]
            else:
                title = language.loc[language['name']=='eco_text_6',lang].iloc[0]
            fig=px.line(data_frame=df, x=language.loc[language['name']=='usable_battery_size',lang].iloc[0], y='Amortisation', hover_data=[language.loc[language['name']=='invest_cost',lang].iloc[0]], 
                    labels={
                        "Amortisation": language.loc[language['name']=='payback_years',lang].iloc[0],
                        })
            fig.update_layout(margin=dict(l=20, r=20, b=20),)
            return [dbc.Col(html.H6(title),width={'offset':2}),dbc.Col(dcc.Graph(figure=fig,config={'displayModeBar': False}),width=12)]
        elif results_id.startswith('NetPresentValue'):
            NetPresentValue_max=max(NetPresentValue)
            best_value_battery = df[language.loc[language['name']=='usable_battery_size',lang].iloc[0]].values[NetPresentValue.index(NetPresentValue_max)]
            if NetPresentValue_max>0:
                title = language.loc[language['name']=='eco_text_3',lang].iloc[0] + str(round(best_value_battery,1)) + language.loc[language['name']=='eco_text_7',lang].iloc[0]
            else:
                title = language.loc[language['name']=='eco_text_8',lang].iloc[0]
            fig=px.line(data_frame=df, x=language.loc[language['name']=='usable_battery_size',lang].iloc[0], y='NetPresentValue', hover_data=[language.loc[language['name']=='invest_cost',lang].iloc[0]],
                    labels={
                        "NetPresentValue": language.loc[language['name']=='NPV',lang].iloc[0],
                        })
            fig.update_yaxes(ticksuffix = " €")
            fig.update_layout(margin=dict(l=20, r=20, b=20),)
            return [dbc.Col(html.H6(title),width={'offset':2}),dbc.Col(dcc.Graph(figure=fig,config={'displayModeBar': False}),width=12)]
        elif results_id.startswith('InternalRateOfReturn'):
            InternalRateOfReturn_max=max(InternalRateOfReturn)
            best_value_battery = df[language.loc[language['name']=='usable_battery_size',lang].iloc[0]].values[InternalRateOfReturn.index(InternalRateOfReturn_max)]
            if InternalRateOfReturn_max>0:
                title = language.loc[language['name']=='eco_text_9',lang].iloc[0] + str(round(best_value_battery,1)) + language.loc[language['name']=='eco_text_10',lang].iloc[0] + str(round(InternalRateOfReturn_max*100,2)) + ' %.'
            else:
                title = language.loc[language['name']=='eco_text_8',lang].iloc[0]
            fig=px.line(data_frame=df, x=language.loc[language['name']=='usable_battery_size',lang].iloc[0], y='InternalRateOfReturn', hover_data=[language.loc[language['name']=='invest_cost',lang].iloc[0]],
                    labels={
                        "InternalRateOfReturn": language.loc[language['name']=='IROR',lang].iloc[0],
                        })
            fig.update_yaxes(ticksuffix = " %")
            fig.update_layout(margin=dict(l=20, r=20, b=20),)
            return [dbc.Col(html.H6(title),width={'offset':2}),dbc.Col(dcc.Graph(figure=fig,config={'displayModeBar': False}),width=12)]
        
if __name__ == '__main__':
    app.run_server(debug=True)
