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
# Own functions
from utils.getregion import getregion
import utils.simulate as sim
import utils.economy as eco

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

app.title = 'VDI 4657-3 | Webtool'

# Translation
language=pd.read_csv(DATA_PATH.joinpath('translate.csv'))

# Weather information for all regions
weather_summary=pd.read_csv(DATA_PATH.joinpath('weather/TRJ-Tabelle.csv'))

##################################################
# Definiton of graphical elements / content ######
##################################################

# predefine buttons and lists ####################

button_expert = dbc.Button(
    html.Div(id='button_expert_content',children=[DashIconify(icon='bi:toggle-off',width=50,height=30,),'Expert']),
    id='button_expert',
    outline=True,
    color='light',
    style={'textTransform': 'none'},
)

button_simulation = dbc.Button(
    html.Div(children=[DashIconify(icon='vaadin:start-cog'),html.Div('Start Simulation')]),
    id='button_simulation',
    outline=True,
    color="primary",#disabled=True,
    style={'textTransform': 'none','color': '#003da7','background-color': 'white',},
)

button_language = dbc.Button(
    html.Div(id='button_language_content',children=[DashIconify(icon='emojione:flag-for-germany'),html.Div('Sprache')]),
    id='button_language',
    style={'text-transform': 'none',
        'border': 'none',
        'background': 'none',
        'cursor': 'pointer',
        'color': 'white',
        },
    value='ger'
)

button_info = dbc.Button(
    html.Div(id='button_info_content',children=[DashIconify(icon='ph:info',width=50,height=30,),html.Div('Info')]),
    id='button_info',
    outline=False,
    color='light',
    style={'text-transform': 'none',
        'border': 'none',
        'background': 'none',
        'color': 'white',
        'cursor': 'pointer'
    },
)

encoded_image=base64.b64encode(open(ASSETS_PATH.joinpath('logos/Logo_BMWK_500px.png'), 'rb').read())

options_building_type_ger=[
    {"label":'Bestand, unsaniert', "value": '[2.6,15]'},
    {"label":'Bestand, saniert', "value": '[1.6,14]'},
    {"label":'Neubau, nach 2016', "value": '[0.8,12]'},
    ]
options_building_type_eng=[
    {"label": 'Existing building, unrenovated', "value": '[2.6,15]'},
    {"label": 'Existing building, renovated', "value": '[1.6,14]'},
    {"label": 'New building, after 2016', "value": '[0.8,12]'},
    ]
options_heatpump_ger=[
    {"label": 'Luft/Wasser (mittl. Effizienz)', "value": 'Luft/Wasser (mittl. Effizienz)'},
    {"label": 'Sole/Wasser (mittl. Effizienz)', "value": 'Sole/Wasser (mittl. Effizienz)'},
    ]
options_heatpump_eng=[
    {"label": 'Air/Water (average efficiency)', "value": 'Luft/Wdasser (mittl. Effizienz)'},
    {"label": 'Brine/water (average efficiency)', "value": 'Sole/Wasser (mittl. Effizienz)'},
    ]
options_slp_ger = [
    {"label": 'Eigenes Lastprofil', "value": "own_loadprofile"},
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
    {"label": 'Own load profile', "value": "own_loadprofile"},
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

################################################
# Header

header=dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                     html.Img(src="assets/favicon.ico"),
                    ],
                    )
                ],
                align='center',
                ),
            ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4('Auslegung von Stromspeichern'),
                    ],
                    id='app-title'
                    )
                ],
                align='left',
                ),
            ]),
        dbc.Row([
            dbc.Col([
                dbc.NavbarToggler(id='navbar-toggler'),
                dbc.Collapse(
                    dbc.Nav([
                        dbc.NavItem(button_language),
                        dbc.NavItem(button_info),
                        dcc.ConfirmDialog(id='info_dialog'),
                        ],
                        navbar=True,
                        ),
                    id='navbar-collapse',
                    navbar=True,
                    ),
                ],
                
                ),
            ],
            align='right',
            ),
        ],
        fluid=True,
        ),
    dark=True,
    color='#003da7',
    sticky='top'
    )

################################################
# Main-Page

content = dbc.Container([
    dbc.Row([
        dbc.Col(html.Div(id='scroll',children=[
            dcc.Tabs(id='tabs',value='tab_info',mobile_breakpoint=400),
            html.Div(id='tab-content'),
            ]), 
            width=12,xs=12, sm=12, md=12, lg=12, xl=12, xxl=4),
        dbc.Col(html.Div(
            children=[html.Div(id='bat_results'),
                html.Div(id='bat_results_LSK'),
                html.Div(id='cost_result'),
                ]
            )),
        ],style={'padding': '15px'}),
    dcc.Store(id='last_triggered_building', storage_type='memory'),                                     # welches Gebäude ausgewählt war-> df                                     
    dcc.Store(id='n_clicks_pv', storage_type='memory'),                                                 # ob PV ausgewählt war -> df                         
    dcc.Store(id='n_clicks_pv2', storage_type='memory'),                                                 # ob PV ausgewählt war -> df                         
    dcc.Store(id='n_clicks_chp', storage_type='memory'),                                                # ob KWK ausgewählt war -> df                             
    dcc.Store(id='n_clicks_hp', storage_type='memory'),                                                 # ob Wärmepumpe ausgewählt war -> df                         
    dcc.Store(id='parameter_include_heating', storage_type='memory'),                                   # ob Heating ausgewählt war -> df                                         
    dcc.Store(id='parameter_wohnfläche', storage_type='memory'),                                        # Wohnfläche -> df                                     
    dcc.Store(id='parameter_building'),                                                                 # Gebäudetyp -> df                               
    dcc.Store(id='building', storage_type='memory'),                                                    # Gebäudewerte                                       
    dcc.Store(id='batteries', storage_type='memory'),                                                   # ERGEBNIS                         
    dcc.Store(id='chp_max_power_data', storage_type='memory'),                                          # chp sachen                                 
    dcc.Store(id='chp_technology_data', storage_type='memory'),                                         # chp sachen                             
    dcc.Store(id='price_electricity', storage_type='memory'),                                           # Preis                                 
    dcc.Store(id='price_electricity_peak', storage_type='memory'),                                      # Preis                                     
    dcc.Store(id='parameter_lang', storage_type='memory'),                                              # Sprache                             
    dcc.Store(id='parameter_use', storage_type='memory'),                                               # Anwendung                             
    dcc.Loading(type='default',children=dcc.Store(id='parameter_location_int', storage_type='memory')), # Standort -> df                                                                         
    dcc.Store(id='parameter_location_string', storage_type='memory'),                                   # Standort
    dcc.Store(id='weather_typ', storage_type='memory'),                                   # Standort                                          
    dcc.Store(id='parameter_pv', storage_type='memory'),                                                # PV-Größe -> df                             
    dcc.Store(id='parameter_chp', storage_type='memory'),                                               # KWK-Größe -> df                             
    dcc.Store(id='parameter_hp', storage_type='memory'),                                                # Wärmepumpe auswahl -> df                             
    dcc.Store(id='parameters_all'),                                                                     # alle Parameter beim Upload     
    dcc.Store(id='parameter_loadprofile', storage_type='memory'),                                       # Lastprofil beim Upload                                     
    dcc.Store('show_economic_results', storage_type='memory'),                                          # ausgeählten Graphen                                 
    dcc.Store('show_bat_results', storage_type='memory'),                                               # ausgeählten Graphen                             
    dcc.Loading(type='default',children=dcc.Store(id='parameter_peak_shaving', storage_type='memory')), #                                                                         
    dcc.Store(id='parameter_economoy', storage_type='memory'),                                          #                                 
    ],fluid=True)

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
    Input('button_language', 'n_clicks')
)
def change_language(n_language):
    if n_language==None or n_language%2==0:
        lang='ger'
        flag='emojione:flag-for-germany'
    else:
        lang='eng'
        flag='emojione:flag-for-united-kingdom'        
    return ([DashIconify(icon=flag, width=50,height=30,),html.Div(language.loc[language['name']=='lang',lang].iloc[0])],
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
                            'font-size': '10px',
                            'width': '100px',
                            'display': 'inline-block',
                            'margin-bottom': '10px',
                            'margin-right': '5px',
                            'height':'100px',
                            'verticalAlign': 'top',
                            'textAlign': 'center'}),
                            width={'size':1,'offset': 2}),
                        dbc.Tooltip(
                            language.loc[language['name']=='increase_autarky_tooltip',lang].iloc[0],
                            target="autakie_click",
                            placement='bottom'),

                        dbc.Col(html.Button(html.Div([DashIconify(icon='grommet-icons:time',width=75,height=75,),html.Br(),language.loc[language['name']=='peak_shaving',lang].iloc[0]]),id='LSK_click',n_clicks=0,
                            style={'background-color': 'white',
                            'color': 'black',
                            'font-size': '12px',
                            'width': '100px',
                            'display': 'inline-block',
                            'margin-bottom': '10px',
                            'margin-right': '5px',
                            'height':'100px',
                            'verticalAlign': 'top',
                            'textAlign': 'center'}),
                            width={'size':1,'offset': 3},
                            ),
                        dbc.Tooltip(
                            language.loc[language['name']=='peak_shaving_tooltip',lang].iloc[0],
                            target="LSK_click",
                            placement='bottom'),
                        ],
                        )
                ]),
                html.Br(),
                html.Div(language.loc[language['name']=='developed',lang]),
                html.Br(),
                html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),style={'height':'200px'})
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
    State('n_clicks_pv2','data'),
    State('n_clicks_chp','data'),
    State('n_clicks_hp','data'),
)
def render_tab_content(tab,LSK,lang,n_clicks_solar, n_clicks_solar2, n_clicks_chp, n_clicks_hp):
    location=''
    n_clicks_timestamp_efh=None
    n_clicks_timestamp_mfh=None
    n_clicks_timestamp_indu=None
    if tab=='tab_parameter':
        if LSK==0:
            if n_clicks_solar is None:
                n_clicks_solar=0
            if n_clicks_solar2 is None:
                n_clicks_solar2=0
            if n_clicks_chp is None:
                n_clicks_chp=0
            if n_clicks_hp is None:
                n_clicks_hp=0
            return html.Div(className='para',id='para',children=[
                html.Br(),
                dbc.Accordion([
                    dbc.AccordionItem([
                        dbc.Row([
                            dbc.Col(dbc.Accordion([
                                # Standort
                                dbc.AccordionItem([
                                    dbc.Row([
                                        dbc.Col(dcc.Input(
                                            id='standort',
                                            placeholder=language.loc[language['name'] == 'placeholder_location', lang].iloc[0],
                                            value=location,
                                            persistence='memory',
                                            style=dict(width='100%')
                                        )),
                                        dbc.Col([
                                            html.Span('DWD Region: '),
                                            DashIconify(icon='ph:info', width=20, height=20, id='dwd_info',
                                                        style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'}),
                                            dcc.Loading(type="default", children=html.Div(id='region'))
                                        ], align='start', width=12, lg=7),
                                        dbc.Tooltip(language.loc[language['name'] == 'dwd_info', lang].iloc[0], target="dwd_info", placement='bottom'),
                                    ])
                                ], title=language.loc[language['name'] == 'location', lang].iloc[0], item_id='accordion_location'),

                                # Wetterjahr
                                dbc.AccordionItem([
                                    dbc.Row([
                                        dbc.Col(dcc.RadioItems(
                                            options=[
                                                {'label': language.loc[language['name'] == 'weather_year_text1', lang].iloc[0], 'value': '2015'},
                                                {'label': language.loc[language['name'] == 'weather_year_text2', lang].iloc[0], 'value': '2045'}
                                            ],
                                            value='2015',
                                            inline=True,
                                            id='weather_year',
                                            labelStyle={'margin-right': '30px'}
                                        ))
                                    ])
                                ], title=language.loc[language['name'] == "weather_year", lang].iloc[0], item_id='accordion_weather_year'),

                                # Wettertyp
                                dbc.AccordionItem([
                                    dbc.Row([
                                        dbc.Col(dcc.RadioItems(
                                            options=[
                                                {'label': language.loc[language['name'] == 'weather_typ_text1', lang].iloc[0], 'value': 'a'},
                                                {'label': language.loc[language['name'] == 'weather_typ_text2', lang].iloc[0], 'value': 'w'},
                                                {'label': language.loc[language['name'] == 'weather_typ_text3', lang].iloc[0], 'value': 's'}
                                            ],
                                            value='a',
                                            inline=True,
                                            id='weather_typ',
                                            labelStyle={'margin-right': '20px'}
                                        ))
                                    ])
                                ], title=language.loc[language['name'] == "weather_type", lang].iloc[0], item_id='accordion_weather_typ')
                            ], id='accordion_simulate_weather')
                            )
                            
                            ])
                    ],
                    title=language.loc[language['name']=='weather_data',lang].iloc[0],
                    id='accordion_simulate_1',
                    ),
                    dbc.AccordionItem([
                        dbc.Row([
                            dbc.Col(html.Button(html.Div([DashIconify(icon='clarity:home-solid',width=50,height=50,),html.Br(),language.loc[language['name']=='efh_name',lang].iloc[0]],style={'width':'80px'}),id='efh_click',n_clicks_timestamp=n_clicks_timestamp_efh), width=4),
                            dbc.Tooltip(language.loc[language['name']=='efh_tooltip',lang].iloc[0], target="efh_click", placement='bottom'),
                            dbc.Col(html.Button(html.Div([DashIconify(icon='bxs:building-house',width=50,height=50,),html.Br(),language.loc[language['name']=='mfh_name',lang].iloc[0]],style={'width':'80px'}),id='mfh_click',n_clicks_timestamp=n_clicks_timestamp_mfh), width=4),
                            dbc.Tooltip(language.loc[language['name']=='mfh_tooltip',lang].iloc[0], target="mfh_click", placement='bottom'),
                            dbc.Col(html.Button(html.Div([DashIconify(icon='la:industry',width=50,height=50,),html.Br(),language.loc[language['name']=='industry_name',lang].iloc[0]],style={'width':'80px'}),id='industry_click',n_clicks_timestamp=n_clicks_timestamp_indu), width=4),
                            dbc.Tooltip(language.loc[language['name']=='industry_tooltip',lang].iloc[0], target="industry_click", placement='bottom'),
                        ]),
                        dbc.Row(dbc.Col(id='include_heating_row')),
                        dbc.Container(id='bulding_container',fluid=True),
                    ],
                    title=language.loc[language['name']=='choose_building',lang].iloc[0],
                    id='accordion_simulate_2',
                    ),
                    dbc.AccordionItem([
                        dbc.Row([
                            dbc.Col(html.Button(html.Div([DashIconify(icon='fa-solid:solar-panel',width=50,height=50,),html.Br(),language.loc[language['name']=='pv1',lang].iloc[0]],style={'width':'80px'}),id='n_solar',n_clicks=n_clicks_solar),width=3),
                            dbc.Tooltip(language.loc[language['name']=='pv_tooltip',lang].iloc[0],target="n_solar",placement='bottom'),
                            dbc.Col(html.Button(html.Div([DashIconify(icon='fa-solid:solar-panel',width=50,height=50,),html.Br(),language.loc[language['name']=='pv2',lang].iloc[0]],style={'width':'80px'}),id='n_solar2',n_clicks=n_clicks_solar2),width=3),
                            dbc.Tooltip(language.loc[language['name']=='pv_tooltip',lang].iloc[0],target="n_solar2",placement='bottom'),
                            dbc.Col(html.Button(html.Div([DashIconify(icon='mdi:gas-burner',width=50,height=50,),html.Br(),language.loc[language['name']=='chp',lang].iloc[0]],style={'width':'80px'}),id='n_chp',n_clicks=n_clicks_chp),width=3),
                            dbc.Tooltip(language.loc[language['name']=='chp_tooltip',lang].iloc[0],target="n_chp",placement='bottom'),
                            dbc.Col(html.Button(html.Div([DashIconify(icon='mdi:heat-pump-outline',width=50,height=50,),html.Br(),language.loc[language['name']=='hp',lang].iloc[0]],style={'width':'80px'}),id='n_hp',n_clicks=n_clicks_hp),width=3),
                            dbc.Tooltip(language.loc[language['name']=='hp_tooltip',lang].iloc[0],target="n_hp",placement='bottom'),
                        ]),
                        dbc.Container(html.Div([html.Div(id='hp_technology'),html.Div(id='chp_technology'),html.Div(id='hp_technology_value'),html.Div(id='chp_technology_value'), html.Div(id='chp_max_power'), html.Div(id='chp_load_hours')],id='technology'),fluid=True)
                    ],
                    title=language.loc[language['name']=='choose_technology',lang].iloc[0],
                    id='accordion_simulate_3',
                    ),
                    dbc.AccordionItem([
                        dbc.Row([                                
                                dbc.Col([html.Span(language.loc[language['name'] == 'feed_in_limit', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='text_feed_in_limit',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})], width=6),
                                dbc.Tooltip(language.loc[language['name']=='feed_in_limit_info',lang].iloc[0],target="text_feed_in_limit",placement='bottom'),
                                dbc.Col(dcc.Loading(type="circle",children=html.Div(id="feed_in_limit_text")), width=3),
                                dbc.Col(dcc.Slider(0,1,0.05,value=0.6,marks=None, tooltip={'placement': 'top', 'always_visible': False}, id='feed_in_limit',persistence='memory'), width=11),

                                dbc.Col(dcc.Checklist(options={'True': language.loc[language['name']=='bat_prog',lang].iloc[0]},value=[], id='bat_prog',persistence='memory'), width='auto'),
                                dbc.Col([DashIconify(icon='ph:info',width=20,height=20,id='text_bat_prog',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})], width=6),
                                dbc.Tooltip(language.loc[language['name']=='bat_prog_info',lang].iloc[0],target="text_bat_prog",placement='bottom'),

                                dbc.Row(html.Div(style={'height': '20px'})),

                                dbc.Col([html.Span(language.loc[language['name'] == 'p_bat', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='text_p_bat',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})], width=6),
                                dbc.Tooltip(language.loc[language['name']=='p_bat_info',lang].iloc[0],target="text_p_bat",placement='bottom'),
                                dbc.Col(dcc.Loading(type="circle",children=html.Div(id="p_bat_text")), width=6),
                                dbc.Col(dcc.Slider(0.1,2,0.1,value=0.5,marks=None, tooltip={'placement': 'top', 'always_visible': False}, id='p_bat',persistence='memory'), width=11),
                        ],align='center'),
                        dbc.Container(html.Div(id='battery_storage'),fluid=True)
                    ],
                    title=language.loc[language['name']=='battery_storage',lang].iloc[0],
                    id='accordion_simulate_4',
                    ),
                
                ],
                always_open=False,
                id='accordion_simulate',
                ),
            html.Br(),
            html.Div(
                [
                    button_simulation,
                    html.Div(
                        dcc.Loading(
                            id="simulation_info",
                            type="circle",
                            children=language.loc[language['name']=='simulation_info1',lang].iloc[0]
                        ),
                        style={'marginLeft': '1em', 'display': 'inline-block', 'maxWidth': '70%'}
                    )
                ],
                style={'display': 'flex', 'alignItems': 'center'}
            )
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
    Output('info_dialog','message'),
    Input('button_info','n_clicks'),
    State('button_language', 'value'),
)
def display_info(n_clicks_info, lang):
    if n_clicks_info is None:
        raise PreventUpdate
    return True, language.loc[language['name']=='info_text',lang].iloc[0]

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
)
def getcontainer(efh_click,mfh_click,industry_click,choosebuilding,heating,lang):
    electricity_consumption_efh = 4000
    electricity_consumption_mfh = 15_000
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
            return (html.Div(dcc.Checklist(options={'True': language.loc[language['name']=='heating',lang].iloc[0]},value=[], id='include_heating',persistence='memory'),style={'textAlign': 'center','marginTop': '5px', 'marginBottom': '0px'}),
                        [   
                        dbc.Row([
                            dbc.Col([html.Span(language.loc[language['name'] == 'energy_cons', lang].iloc[0]),
                            DashIconify(icon='ph:info',width=20,height=20,id='text_energy_cons',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})],style={'marginTop': '1rem'}),
                            dbc.Tooltip(language.loc[language['name']=='energy_cons_tooltip',lang].iloc[0],target="text_energy_cons",placement='bottom'),
                            dbc.Col(html.Div(id='stromverbrauch_value'), width=4),
                            dbc.Col(dcc.Slider(min=1000,max=10000,step=500,value=electricity_consumption_efh,marks=None,id='stromverbrauch',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                            html.Div(id='industry_type'),
                            dcc.Store(id='building_type_value', storage_type='memory'),
                            ],
                            align='center',
                            ),
                        ],
                    {'background-color': '#003da7','color': 'white',},
                    {'background-color': 'white','color': 'black'},
                    {'background-color': 'white','color': 'black'},'efh')
        else: # efh with heating system
            return (html.Div(dcc.Checklist(options={'True': language.loc[language['name']=='heating',lang].iloc[0]},value=['True'], id='include_heating',persistence='memory'),style={'textAlign': 'center','marginTop': '5px', 'marginBottom': '0px'}),
                        [
                            dbc.Row(
                                [
                                    dbc.Col([html.Span(language.loc[language['name'] == 'energy_cons', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='text_energy_cons',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})], style={'marginTop': '1rem'}),
                                    dbc.Tooltip(language.loc[language['name']=='energy_cons_tooltip',lang].iloc[0],target="text_energy_cons",placement='bottom'),
                                    dbc.Col(html.Div(id='stromverbrauch_value'), width=4),
                                    dbc.Col(dcc.Slider(min=2000,max=8000,step=500,value=electricity_consumption_efh,marks=None,id='stromverbrauch',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                                    html.Div(id='industry_type'),
                                ],
                                align='center',
                                ),
                            dbc.Row(
                                [
                                    dbc.Col([html.Span(language.loc[language['name'] == 'building_size', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='text_building_size',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                    dbc.Tooltip(language.loc[language['name']=='building_size_tooltip',lang].iloc[0],target="text_building_size",placement='bottom'),
                                    dbc.Col(html.Div(id='wohnfläche_value'), width=4),
                                    dbc.Col(dcc.Slider(min=50,max=250,step=10,value=150,marks=None,id='wohnfläche',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                                ],
                                align='center',
                                ),
                            dbc.Row(
                                [
                                    dbc.Col([html.Span(language.loc[language['name'] == 'inhabitants', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='text_inhabitants',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                    dbc.Tooltip(language.loc[language['name']=='inhabitants_tooltip',lang].iloc[0],target="text_inhabitants",placement='bottom'),
                                    dbc.Col(dcc.Input(id='inhabitants_efh',
                                                      value=4,
                                                      min=0,
                                                      max=10,
                                                      type='number'), width=11)
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col([html.Span(language.loc[language['name'] == 'building_type', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='text_building_type',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                    dbc.Tooltip(language.loc[language['name']=='building_type_tooltip',lang].iloc[0],target="text_building_type",placement='bottom'),
                                    dbc.Col(html.Div(id='building_type_value'), width=6),
                                    dbc.Col(dcc.Dropdown(options_building_type, id='building_type',persistence='memory'), width=11),
                                    dbc.Col(language.loc[language['name']=='heating_temperature',lang].iloc[0], width=6),
                                    dbc.Col(dcc.RadioItems(options=[
                                                            {"label": '35 °C / 28 °C', "value": '[35, 28, 1.1]'},
                                                            {"label": '45 °C / 35 °C', "value": '[45, 35, 1.2]'},
                                                            {"label": '55 °C / 45 °C', "value": '[55, 45, 1.3]'}
                                                        ],
                                                        labelStyle={'margin-right': '30px'},
                                                        value='[55, 45, 1.3]',
                                                        id='heating_distribution_temperatures',
                                                        persistence='memory'
                                                    ), width=12),
                                ],
                                align='center',
                                )
                        ],
                    {'background-color': '#003da7','color': 'white',},
                    {'background-color': 'white','color': 'black'},
                    {'background-color': 'white','color': 'black'},'efh')
    if (mfh_click>efh_click) and (mfh_click>industry_click): #mfh
        if (heating is None) or (len(heating)==0): # mfh for simulating without heating
            return (html.Div(dcc.Checklist(options={'True': language.loc[language['name']=='heating',lang].iloc[0]},value=[], id='include_heating',persistence='memory'),style={'textAlign': 'center','marginTop': '5px', 'marginBottom': '0px'}),
                        [
                            dbc.Row(
                                [
                                    dbc.Col([html.Span(language.loc[language['name'] == 'housing_units', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='text_housing_units',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})],style={'marginTop': '1rem'}),
                                    dbc.Tooltip(language.loc[language['name']=='housing_units_tooltip',lang].iloc[0],target="text_housing_units",placement='bottom'),
                                    dbc.Col(html.Div(id='wohnfläche_value'), width=4),
                                    dbc.Col(dcc.Slider(min=2,max=50,step=1,value=12,marks=None,id='wohnfläche',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                                ],
                                align='center'),
                            dbc.Row(
                                [
                                dbc.Col([html.Span(language.loc[language['name'] == 'energy_cons', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='text_energy_cons',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                dbc.Tooltip(language.loc[language['name']=='energy_cons_tooltip',lang].iloc[0],target="text_energy_cons",placement='bottom'),
                                dbc.Col(html.Div(id='stromverbrauch_value'), width=4),
                                dbc.Col(dcc.Slider(min=5000,max=100000,step=1000,value=electricity_consumption_mfh,marks=None,id='stromverbrauch',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                                dcc.Store(id='building_type_value', storage_type='memory'),
                                html.Div(id='industry_type'),
                                ],
                            align='center'),
                        dcc.Store(id='inhabitants_efh')
                        ],
                    {'background-color': 'white','color': 'black'},
                    {'background-color': '#003da7','color': 'white',},
                    {'background-color': 'white','color': 'black'},'mfh')
        else: #mfh with heating
            return (html.Div(dcc.Checklist(options={'True': language.loc[language['name']=='heating',lang].iloc[0]},value=['True'], id='include_heating',persistence='memory'),style={'textAlign': 'center','marginTop': '5px', 'marginBottom': '0px'}),
                        [
                            dbc.Row(
                                [
                                    dbc.Col([html.Span(language.loc[language['name'] == 'housing_units', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='text_housing_units',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})],style={'marginTop': '1rem'}),
                                    dbc.Tooltip(language.loc[language['name']=='housing_units_tooltip',lang].iloc[0],target="text_housing_units",placement='bottom'),
                                    dbc.Col(html.Div(id='wohnfläche_value'), width=4),
                                    dbc.Col(dcc.Slider(min=2,max=50,step=1,value=12,marks=None,id='wohnfläche',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                                ],
                                align='center',
                                ),
                            dbc.Row(
                                [
                                    dbc.Col([html.Span(language.loc[language['name'] == 'energy_cons', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='text_energy_cons',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                    dbc.Tooltip(language.loc[language['name']=='energy_cons_tooltip',lang].iloc[0],target="text_energy_cons",placement='bottom'),
                                    dbc.Col(html.Div(id='stromverbrauch_value'), width=4),
                                    dbc.Col(dcc.Slider(min=5000,max=100000,step=1000,value=electricity_consumption_mfh,marks=None,id='stromverbrauch',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                                    html.Div(id='industry_type'),
                                ],
                                align='center',
                                ),
                            dbc.Row(
                                [
                                    dbc.Col([html.Span(language.loc[language['name'] == 'building_type', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='text_building_type',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                    dbc.Tooltip(language.loc[language['name']=='building_type_tooltip',lang].iloc[0],target="text_building_type",placement='bottom'),
                                    dbc.Col(html.Div(id='building_type_value'), width=6),
                                    dbc.Col(dcc.Dropdown(options_building_type,id='building_type',persistence='memory'), width=11),
                                    dbc.Col(language.loc[language['name']=='heating_temperature',lang].iloc[0], width=6),
                                    dbc.Col(dcc.RadioItems(options=[
                                                            {"label": '35 °C / 28 °C', "value": '[35, 28, 1.1]'},
                                                            {"label": '45 °C / 35 °C', "value": '[45, 35, 1.2]'},
                                                            {"label": '55 °C / 45 °C', "value": '[55, 45, 1.3]'}
                                                        ],
                                                        labelStyle={'margin-right': '30px'},
                                                        value='[55, 45, 1.3]',
                                                        id='heating_distribution_temperatures',
                                                        persistence='memory'
                                                    ), width=12),
                                ],
                                align='center',
                                ),
                            dcc.Store(id='inhabitants_efh')
                        ],
                {'background-color': 'white','color': 'black'},
                {'background-color': '#003da7','color': 'white',},
                {'background-color': 'white','color': 'black'},'mfh')
    if (industry_click>efh_click) and (industry_click>mfh_click): #industry no heating
        if lang=='eng':
            options_slp=options_slp_eng
        else:
            options_slp=options_slp_ger
        if (heating is None) or (len(heating)==0): # for simulating without heating
            return (html.Div(dcc.Checklist(options={'True': language.loc[language['name']=='heating',lang].iloc[0][0:15]},value=[], id='include_heating',persistence='memory'),style={'textAlign': 'center','marginTop': '5px', 'marginBottom': '0px'}),
                [
                dbc.Row(
                    [
                    dbc.Col(language.loc[language['name']=='building_type_industry',lang].iloc[0], width=12, style={'marginTop': '1rem'}),
                    dbc.Col(dcc.Dropdown(options_slp,id='industry_type',persistence='memory', optionHeight=100,maxHeight=400), width=11),
                    ],
                align='center',
                ),
                dbc.Row(id='slp_choosen',
                align='center',
                ),
                ],
                {'background-color': 'white','color': 'black'},
                {'background-color': 'white','color': 'black'},
                {'background-color': '#003da7','color': 'white',},'indu')
        else: #industry with heating
            return (html.Div(dcc.Checklist(options={'True': language.loc[language['name']=='heating',lang].iloc[0][0:15]},value=['True'], id='include_heating',persistence='memory'),style={'textAlign': 'center','marginTop': '5px', 'marginBottom': '0px'}),
                [
                dbc.Row(
                    [
                    dbc.Col(language.loc[language['name']=='building_type_industry',lang].iloc[0], width=12),
                    dbc.Col(dcc.Dropdown(options_slp,id='industry_type',persistence='memory', optionHeight=100,maxHeight=400), width=11),
                    ],
                
                
                align='center',
                ),
                dbc.Row(id='slp_choosen',
                align='center',
                ),
                dbc.Row(
                    [
                    dbc.Col(
                        html.Div([
                            html.Span(language.loc[language['name'] == 'max_heatload', lang].iloc[0]),
                            DashIconify(icon='ph:info',width=20,height=20,id='text_building_type',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})
                        ]),
                        width=6
                    ),
                    dbc.Col(html.Div(id='heat_load_indu_value'), width=4),
                    dbc.Tooltip(language.loc[language['name']=='max_heatload_tooltip',lang].iloc[0],target="text_building_type",placement='bottom'),
                    dbc.Col(dcc.Slider(min=1,max=500,step=1,value=100,marks=None,id='building_type',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                    dbc.Col(language.loc[language['name']=='heating_temperature',lang].iloc[0], width=6),
                    dbc.Col(dcc.RadioItems(options=[
                                            {"label": '35 °C / 28 °C', "value": '[35, 28, 1.1]'},
                                            {"label": '45 °C / 35 °C', "value": '[45, 35, 1.2]'},
                                            {"label": '55 °C / 45 °C', "value": '[55, 45, 1.3]'}
                                            ],
                                        labelStyle={'margin-right': '30px'},
                                        value='[55, 45, 1.3]',
                                        id='heating_distribution_temperatures',
                                        persistence='memory'
                                    ), width=12),
                    ],
                    align='center',
                    ),
                ],
                {'background-color': 'white','color': 'black'},
                {'background-color': 'white','color': 'black'},
                {'background-color': '#003da7','color': 'white',},'indu')

# Add technology to the tab 'tab_parameter'
@app.callback(
    Output('technology','children'), 
    Input('n_solar', 'style'),
    Input('n_solar2', 'style'),
    Input('n_chp', 'style'),
    Input('n_hp', 'style'),
    Input('button_language','value'),
    Input('last_triggered_building','data'),
    )
def built_technology(n_solar, n_solar2,n_chp,n_hp,lang,building):
    pv_value=10.0
    chp_max_power=30
    chp_electric_heat_ratio=100
    hp_technology=''
    technology_list=[html.Br()]
    if building=='efh':
        if n_solar['color']!='white':
            technology_list.append(
                            dbc.Row(
                                [
                                dcc.Store(id='pv_slider'),
                                dcc.Store(id='pv1_inclination'),
                                dcc.Store(id='pv1_azimut'),
                                
                                ]))
        else:
            technology_list.append(
                            dbc.Row(
                                [
                                dbc.Col([html.H6(language.loc[language['name'] == 'photovoltaik', lang].iloc[0],style={'display': 'inline-block', 'margin': 0}),DashIconify(icon='ph:info',width=20,height=20,id='photovoltaik_text',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                dbc.Tooltip(language.loc[language['name']=='photovoltaik_tooltip',lang].iloc[0], target="photovoltaik_text", placement='bottom'),
                                dbc.Col(html.Div(id='pv_slider_value'), width=4),
                                dbc.Col(dcc.Slider(min=0,max=20,step=0.1,marks=None, id='pv_slider',value=pv_value, tooltip={'placement': 'top', 'always_visible': False}, persistence='memory'), width=12),
                                dbc.Col([html.Span(language.loc[language['name'] == 'pv_tilt', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='pv_tilt_text',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                dbc.Tooltip(language.loc[language['name']=='pv_tilt_tooltip',lang].iloc[0], target="pv_tilt_text", placement='bottom'),
                                dbc.Col(html.Div(), width=4),
                                dbc.Col(dcc.Slider(min=0,max=90,step=5, value=35,
                                    marks={0: '0°', 90: '90°'},
                                    tooltip={'placement': 'top', 'always_visible': False}, persistence='memory', id='pv1_inclination'), width=12),
                                dbc.Col([html.Span('Azimut'),DashIconify(icon='ph:info',width=20,height=20,id='azimut_text',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                dbc.Tooltip(language.loc[language['name']=='pv_orientation_tooltip',lang].iloc[0], target="azimut_text", placement='bottom'),
                                dbc.Col(dcc.Slider(
                                    id='pv1_azimut',
                                    min=0,
                                    max=315,
                                    marks={0:'Nord',45: 'Nord-Ost',90: 'Ost', 135: 'Süd-Ost', 180: 'Süd', 225: 'Süd-West', 270: 'West', 315: 'Nord-West'},
                                    step=None,  # Setze step auf None für diskrete Werte
                                    value=180,  # Standardwert
                                    persistence='memory'), width=12),
                                ]))
        if n_solar2['color']!='white':
            technology_list.append(
                            dbc.Row(
                                [
                                dcc.Store(id='pv2_slider'),
                                dcc.Store(id='pv2_inclination'),
                                dcc.Store(id='pv2_azimut'),                    
                                ]))
        else:
            technology_list.append(
                            dbc.Row(
                                [
                                dbc.Col([html.H6(language.loc[language['name'] == 'photovoltaik', lang].iloc[0],style={'display': 'inline-block', 'margin': 0}),DashIconify(icon='ph:info',width=20,height=20,id='photovoltaik_text2',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                dbc.Tooltip(language.loc[language['name']=='photovoltaik_tooltip',lang].iloc[0], target="photovoltaik_text2", placement='bottom'),
                                dbc.Col(html.Div(id='pv2_slider_value'), width=4),
                                dbc.Col(dcc.Slider(min=0,max=20,step=0.1,marks=None, id='pv2_slider',value=0.0, tooltip={'placement': 'top', 'always_visible': False}, persistence='memory'), width=12),
                                dbc.Col([html.Span(language.loc[language['name'] == 'pv_tilt', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='pv_tilt_text2',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                dbc.Tooltip(language.loc[language['name']=='pv_tilt_tooltip',lang].iloc[0], target="pv_tilt_text2", placement='bottom'),
                                dbc.Col(html.Div(), width=4),
                                dbc.Col(dcc.Slider(min=0,max=90,step=5, value=35,
                                    marks={0: '0°', 90: '90°'},
                                    tooltip={'placement': 'top', 'always_visible': False}, persistence='memory', id='pv2_inclination'), width=12),
                                dbc.Col([html.Span('Azimut'),DashIconify(icon='ph:info',width=20,height=20,id='azimut_text2',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                dbc.Tooltip(language.loc[language['name']=='pv_orientation_tooltip',lang].iloc[0], target="azimut_text2", placement='bottom'),
                                dbc.Col(dcc.Slider(
                                    id='pv2_azimut',
                                    min=0,
                                    max=315,
                                    marks={0:'Nord',45: 'Nord-Ost',90: 'Ost', 135: 'Süd-Ost', 180: 'Süd', 225: 'Süd-West', 270: 'West', 315: 'Nord-West'},
                                    step=None,  # Setze step auf None für diskrete Werte
                                    value=180,  # Standardwert
                                    persistence='memory'), width=12),
                                html.Br(),
                                html.Br(),
                                ],
                            align='center',
                            ))
    elif (building=='mfh') or (building=='indu'):
        if n_solar['color']!='white':
            technology_list.append(
                            dbc.Row(
                                [
                                dcc.Store(id='pv_slider'),
                                dcc.Store(id='pv1_inclination'),
                                dcc.Store(id='pv1_azimut'),
                                
                                ]))
        else:
            technology_list.append(
                            dbc.Row(
                                [
                                dbc.Col([html.H6(language.loc[language['name'] == 'photovoltaik', lang].iloc[0],style={'display': 'inline-block', 'margin': 0}),DashIconify(icon='ph:info',width=20,height=20,id='photovoltaik_text',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                dbc.Tooltip(language.loc[language['name']=='photovoltaik_tooltip',lang].iloc[0], target="photovoltaik_text", placement='bottom'),
                                dbc.Col(html.Div(id='pv_slider_value'), width=4),
                                dbc.Col(dcc.Slider(min=0,max=200,step=1,marks=None, id='pv_slider',value=pv_value, tooltip={'placement': 'top', 'always_visible': False}, persistence='memory'), width=12),
                                dbc.Col([html.Span(language.loc[language['name'] == 'pv_tilt', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='pv_tilt_text',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                dbc.Tooltip(language.loc[language['name']=='pv_tilt_tooltip',lang].iloc[0], target="pv_tilt_text", placement='bottom'),
                                dbc.Col(html.Div(), width=4),
                                dbc.Col(dcc.Slider(min=0,max=90,step=5, value=35,
                                    marks={0: '0°', 90: '90°'},
                                    tooltip={'placement': 'top', 'always_visible': False}, persistence='memory', id='pv1_inclination'), width=12),
                                dbc.Col([html.Span('Azimut'),DashIconify(icon='ph:info',width=20,height=20,id='azimut_text',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                dbc.Tooltip(language.loc[language['name']=='pv_orientation_tooltip',lang].iloc[0], target="azimut_text", placement='bottom'),
                                dbc.Col(dcc.Slider(
                                    id='pv1_azimut',
                                    min=0,
                                    max=315,
                                    marks={0:'Nord',45: 'Nord-Ost',90: 'Ost', 135: 'Süd-Ost', 180: 'Süd', 225: 'Süd-West', 270: 'West', 315: 'Nord-West'},
                                    step=None,  # Setze step auf None für diskrete Werte
                                    value=180,  # Standardwert
                                    persistence='memory'), width=12),
                                
                                html.Br(),
                                html.Br(),
                                ],
                            align='center',
                            ))
        if n_solar2['color']!='white':
            technology_list.append(
                            dbc.Row(
                                [
                                dcc.Store(id='pv2_slider'),
                                dcc.Store(id='pv2_inclination'),
                                dcc.Store(id='pv2_azimut'),                    
                                ]))
        else:
            technology_list.append(dbc.Row(
                                [
                                dbc.Col([html.H6(language.loc[language['name'] == 'photovoltaik', lang].iloc[0],style={'display': 'inline-block', 'margin': 0}),DashIconify(icon='ph:info',width=20,height=20,id='photovoltaik_text2',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                dbc.Tooltip(language.loc[language['name']=='photovoltaik_tooltip',lang].iloc[0], target="photovoltaik_text2", placement='bottom'),
                                dbc.Col(html.Div(id='pv2_slider_value'), width=4),
                                dbc.Col(dcc.Slider(min=0,max=200,step=1,marks=None, id='pv2_slider',value=0, tooltip={'placement': 'top', 'always_visible': False}, persistence='memory'), width=12),
                                dbc.Col([html.Span(language.loc[language['name'] == 'pv_tilt', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='pv_tilt_text2',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                dbc.Tooltip(language.loc[language['name']=='pv_tilt_tooltip',lang].iloc[0], target="pv_tilt_text2", placement='bottom'),
                                dbc.Col(html.Div(), width=4),
                                dbc.Col(dcc.Slider(min=0,max=90,step=5, value=35,
                                    marks={0: '0°', 90: '90°'},
                                    tooltip={'placement': 'top', 'always_visible': False}, persistence='memory', id='pv2_inclination'), width=12),
                                dbc.Col([html.Span('Azimut'),DashIconify(icon='ph:info',width=20,height=20,id='azimut_text2',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})]),
                                dbc.Tooltip(language.loc[language['name']=='pv_orientation_tooltip',lang].iloc[0], target="azimut_text2", placement='bottom'),
                                dbc.Col(dcc.Slider(
                                    id='pv2_azimut',
                                    min=0,
                                    max=315,
                                    marks={0:'Nord',45: 'Nord-Ost',90: 'Ost', 135: 'Süd-Ost', 180: 'Süd', 225: 'Süd-West', 270: 'West', 315: 'Nord-West'},
                                    step=None,  # Setze step auf None für diskrete Werte
                                    value=180,  # Standardwert
                                    persistence='memory'), width=12),
                                html.Br(),
                                html.Br(),
                                ],
                            align='center',
                            ))
    else:
        technology_list.append(html.Div(language.loc[language['name']=='choose_building_type',lang].iloc[0]))
    
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
                                dbc.Col([html.Span(language.loc[language['name'] == 'chp_peak_ratio', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='chp_peak_ratio_text',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})],width=6),
                                dbc.Col(id='chp_technology_value'),
                                dbc.Tooltip(language.loc[language['name']=='chp_peak_ratio_tooltip',lang].iloc[0], target="chp_peak_ratio_text", placement='bottom'),
                                dbc.Col(dcc.Slider(min=10 ,max=100,step=10,value=chp_max_power,marks=None,id='chp_max_power',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                                dbc.Col([html.Span(language.loc[language['name'] == 'chp_electric_number', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='chp_electric_number_text',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})],width=6),
                                dbc.Col(id='chp_technology_value2'),
                                dbc.Tooltip(language.loc[language['name']=='chp_electric_number_tooltip',lang].iloc[0], target="chp_electric_number_text", placement='bottom'),
                                dbc.Col(dcc.Slider(min=10,max=300,step=10,value=chp_electric_heat_ratio,marks=None,id='chp_technology',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                                ],
                            align='center',
                            ),
                            )
    else:
        technology_list.append(
            html.Div([html.Div(id='chp_technology'),html.Div(id='chp_technology_value'),html.Div(id='chp_technology_value2'), html.Div(id='chp_load_hours')])
        )
    if n_hp['color']=='white':
        if lang=='eng':
            options_hp_technology=options_heatpump_eng
        else:
            options_hp_technology=options_heatpump_ger
        technology_list.append(
                            dbc.Row(
                                [
                                dbc.Col([html.Span(language.loc[language['name'] == 'heatpump', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='hp_text',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})],width=6),
                                dbc.Tooltip(language.loc[language['name']=='hp_text',lang].iloc[0], target="hp_text", placement='bottom'),
                                dbc.Col(dcc.Loading(type="circle",children=html.Div(id="hp_technology_value")), width=6),
                                dbc.Col(dcc.Dropdown(options_hp_technology,value=hp_technology, id='hp_technology',persistence='memory', optionHeight=50), width=11),
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
    State('tabs','value'),
    State('parameter_use','data')
    )
def next_Tab(autarkie, LSK, tab, parameter_use):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
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
            absolut_bat_cost_small = upload_data['specific_bat_cost_small']['0']
            absolut_bat_cost_big = upload_data['specific_bat_cost_big']['0'] #TODO
            price_sell = int(upload_data['Electricity_price']['0'].split(',')[1][:-1])
            price_buy = int(upload_data['Electricity_price']['0'].split(',')[0][1:])
        else:
            absolut_bat_cost_small=int(round(float(specific_bat_cost_small*capacity_bat_small)/50)*50)
            absolut_bat_cost_big=int(round(float(specific_bat_cost_big*capacity_bat_big)/50)*50)
            price_sell=6
            price_buy=30
        if LSK==0:
            cost_use_case=[
                dbc.Row(
                    [
                    dbc.Col(html.Div(language.loc[language['name']=='price_buy',lang].iloc[0]), width=6),
                    dbc.Col(html.Div(id='price_buy_text'), width=6),
                    ]),
                dbc.Row(
                    [
                    dbc.Col(dcc.Slider(min=0, max=50,step=1,value=price_buy,marks=None,id='price_buy',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                    ]),
                dbc.Row(
                    [
                    dbc.Col(html.Div(language.loc[language['name']=='price_increase',lang].iloc[0]), width=6),
                    dbc.Col(html.Div(id='price_increase_text'), width=6),
                    ]),
                dbc.Row(
                    [
                    dbc.Col(dcc.Slider(min=0, max=10,step=0.5,value=1.5,marks=None,id='price_increase',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                    ]),
                dbc.Row(
                    [
                    dbc.Col(html.Div(language.loc[language['name']=='price_sell',lang].iloc[0]), width=6),
                    dbc.Col(html.Div(id='price_sell_text'), width=6),
                    ]),
                dbc.Row(
                    [
                    dbc.Col(dcc.Slider(min=0, max=30,step=1,value=price_sell,marks=None,id='price_sell',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                    ]),
                ]
        else:
            energy_tariff_below2500, energy_tariff_above2500, power_tariff_below2500, power_tariff_above2500=eco.grid_costs_default()
            cost_use_case=dbc.Row(
                [
                dbc.Col(html.Div(language.loc[language['name']=='energy_price_2499',lang].iloc[0]), width=8),
                dbc.Col(html.Div(id='energy_price_below2500_text'), width=4),
                dbc.Col(dcc.Slider(min=0, max=50,step=1,value=energy_tariff_below2500*100,marks=None,id='energy_price_below2500',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),

                dbc.Col(html.Div(language.loc[language['name']=='energy_price_2500',lang].iloc[0]), width=8),
                dbc.Col(html.Div(id='energy_price_above2500_text'), width=4),
                dbc.Col(dcc.Slider(min=0, max=50,step=1,value=energy_tariff_above2500*100,marks=None,id='energy_price_above2500',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),

                dbc.Col(html.Div(language.loc[language['name']=='power_price_2499',lang].iloc[0]), width=8),
                dbc.Col(html.Div(id='power_price_below2500_text'), width=4),
                dbc.Col(dcc.Slider(min=0, max=100,step=5,value=power_tariff_below2500,marks=None,id='power_price_below2500',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),

                dbc.Col(html.Div(language.loc[language['name']=='power_price_2500',lang].iloc[0]), width=8),
                dbc.Col(html.Div(id='power_price_above2500_text'), width=4),
                dbc.Col(dcc.Slider(min=0, max=200,step=10,value=power_tariff_above2500,marks=None,id='power_price_above2500',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                dcc.Store(id='price_increase')
                ],
                align='center',
                )
        
        return html.Div(
            [html.Br(),dbc.Accordion([
                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col(html.Div([str(capacity_bat_small) + language.loc[language['name']=='battery_cost_func',lang].iloc[0]]), width=6),
                        dbc.Col(html.Div(id='absolut_bat_cost_small_text'), width=3),
                        dbc.Col(html.Div('(xxx €/kWh)',id='specific_bat_cost_small_text'), width=3),]),
                    dbc.Row(
                        [
                        dbc.Col(dcc.Slider(min=0, max=absolut_bat_cost_small*2,step=50,value=absolut_bat_cost_small,marks=None,id='absolut_bat_cost_small',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                        ],),
                    dbc.Row(
                        [
                        dbc.Col(html.Div([str(capacity_bat_big) + language.loc[language['name']=='battery_cost_func',lang].iloc[0]]), width=6),
                        dbc.Col(html.Div(id='absolut_bat_cost_big_text'), width=3),
                        dbc.Col(html.Div('(xxx €/kWh)', id='specific_bat_cost_big_text'), width=3),]),
                    dbc.Row(
                        [
                        dbc.Col(dcc.Slider(min=0, max=absolut_bat_cost_big*2,step=50,value=absolut_bat_cost_big,marks=None,id='absolut_bat_cost_big',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                        ]),
                ],
                title=language.loc[language['name']=='invest_cost',lang].iloc[0],
                ),
                dbc.AccordionItem(
                    cost_use_case
                ,
                title=language.loc[language['name']=='tariff',lang].iloc[0],
                ),
                dbc.AccordionItem([
                    #dbc.Row(dbc.Col(language.loc[language['name']=='eco_help_info',lang].iloc[0])),
                    dbc.Row(
                        [
                        dbc.Col([html.Span(language.loc[language['name'] == 'text_imputed_interest_rate', lang].iloc[0]),DashIconify(icon='ph:info',width=20,height=20,id='tooltip_imputed_interest_rate',style={'marginLeft': '8px', 'cursor': 'pointer', 'verticalAlign': 'middle'})],width=6),
                        dbc.Col(html.Div(id='text_imputed_interest_rate'), width=4),
                        dbc.Tooltip(language.loc[language['name']=='tooltip_imputed_interest_rate',lang].iloc[0],target="tooltip_imputed_interest_rate",placement='bottom'),
                        dbc.Col(dcc.Slider(min=0, max=15,step=1,value=3,marks=None,id='imputed_interest_rate',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),

                        ]),
                    dbc.Row(
                        [
                        dbc.Col(language.loc[language['name']=='life_exp',lang].iloc[0], width=6, id='tooltip_life_exp'),
                        dbc.Col(html.Div(id='text_life_exp'), width=4),
                        dbc.Col(dcc.Slider(min=5,max=25,step=1,value=15,marks=None,id='life_exp',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
                        ],
                    align='center',
                    ),
                ],
                title=language.loc[language['name']=='eco_help',lang].iloc[0],
                ),
            ],always_open=True,
            active_item=['item-0', 'item-1']),
            html.Br(),
                dbc.Row(
                    [
                    dbc.Col(dbc.Button(
                        html.Div(children=[DashIconify(icon='system-uicons:reset',width=50,height=30,),html.Div(language.loc[language['name']=='default',lang].iloc[0])],),
                        id='button_reset_price',
                        outline=True,
                        color="primary",
                        active=True,
                        style={'textTransform': 'none','color': '#003da7','background-color': 'white',},
                        ), width={'offset':1,'size':4}),
                    ]
                )
            ]), last_upload

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
    Output('weather_typ', 'data'), 
    Input('parameter_location_int', 'data'),
    Input('weather_year', 'value'),
    Input('weather_typ', 'value'),
    Input('button_language','value'))
def standorttoregion(region, weather_year, weather_typ,lang):
    if region is None:
        raise PreventUpdate
    weather=pd.read_csv(DATA_PATH.joinpath('weather/TRY_'+str(region)+'_'+weather_typ+'_'+weather_year+'_15min.csv'))
    average_temperature_C=weather['temperature [degC]'].mean()
    global_irradiance_kWh_m2a=weather['synthetic global irradiance [W/m^2]'].mean()*8.76
    return html.Div(language.loc[language['name']==str(region),lang].iloc[0]), [weather_typ,weather_year]

# Electric load profile information
@app.callback(
    Output('stromverbrauch_value', 'children'),
    Input('stromverbrauch', 'value'),
    Input('tabs','value'))
def get_p_el_hh(e_hh, tab):
    return str(e_hh) + ' kWh'

# Electric load profile information
@app.callback(
    Output('heat_load_indu_value', 'children'),
    Input('building_type', 'value'),
    Input('tabs','value'))
def get_p_el_hh(e_hh, tab):
    return str(e_hh) + ' kW'

@app.callback(
    Output('text_life_exp', 'children'),
    Input('life_exp', 'value'),
    Input('tabs','value'),
    Input('button_language', 'value'),)
def get_p_el_hh(e_hh, tab, lang):
    return str(e_hh) +' '+ language.loc[language['name']=='year',lang].iloc[0]

@app.callback(
    Output('text_imputed_interest_rate', 'children'),
    Input('imputed_interest_rate', 'value'),
    Input('tabs','value'))
def get_p_el_hh(e_hh, tab):
    return str(e_hh) + ' %'

# Change button style
@app.callback(
    Output('n_solar', 'style'),
    Output('n_clicks_pv', 'data'),
    Output('n_solar2', 'style'),
    Output('n_clicks_pv2', 'data'),
    Input('n_solar', 'n_clicks'),
    Input('n_solar2', 'n_clicks'),
)
def change_solar_style(n_solar_clicks, n_solar2_clicks):
    ctx_id = ctx.triggered_id if hasattr(ctx, "triggered_id") else None

    # Default values if None
    n_solar_clicks = n_solar_clicks or 0
    n_solar2_clicks = n_solar2_clicks or 0

    # Determine styles and states
    if ctx_id == 'n_solar2':
        # If n_solar2 is triggered, set both to blue if odd
        if n_solar2_clicks % 2 == 1:
            return (
                {'background-color': '#003da7', 'color': 'white'}, 1,
                {'background-color': '#003da7', 'color': 'white'}, 1
            )
        else:
            return (
                {'background-color': '#003da7', 'color': 'white'}, 1,
                {'background-color': 'white', 'color': 'black'}, 0
            )
    else:
        # n_solar triggered or initial
        n_solar_style = {'background-color': '#003da7', 'color': 'white'} if n_solar_clicks % 2 == 1 else {'background-color': 'white', 'color': 'black'}
        n_solar2_style = {'background-color': '#003da7', 'color': 'white'} if n_solar2_clicks % 2 == 1 else {'background-color': 'white', 'color': 'black'}
        n_clicks_pv = 1 if n_solar_clicks % 2 == 1 else 0
        n_clicks_pv2 = 1 if n_solar2_clicks % 2 == 1 else 0
        return n_solar_style, n_clicks_pv, n_solar2_style, n_clicks_pv2
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
    if (heating is None) or (len(heating)==0): #or (building=='indu')
        return {'background-color': 'white','color': 'grey'},0,{'background-color': 'white','color': 'grey'},0,0,0
    if ((n_hp%2==0) and (n_chp%2==0)) or (n_chp>=3) or (n_hp>=3):
        return {'background-color': 'white','color': 'black'},0,{'background-color': 'white','color': 'black'},0,0,0
    elif (n_chp%2)==1:
        return {'background-color': '#003da7','color': 'white'},2,{'background-color': 'white','color': 'black'},0,1,0
    elif n_hp%2==1:
        return {'background-color': 'white','color': 'black'},0,{'background-color': '#003da7','color': 'white'},2,0,1

@app.callback(
    Output('parameter_pv','data'),
    Input('pv_slider','value'),
    )
def scale_pv1(pv_slider1):
    if pv_slider1 is None:
        raise PreventUpdate
    return pv_slider1


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
    Input('inhabitants_efh', 'value'),
    State('last_triggered_building', 'data'),
    State('stromverbrauch', 'value'),
    )
def print_wohnfläche_value(wohnfläche, inhabitants_efh, building, electricity_consumption):
    if building is None: 
        raise PreventUpdate
    if building=='mfh':
        return [wohnfläche*2,wohnfläche*70], wohnfläche*1500
    return [inhabitants_efh, wohnfläche], electricity_consumption

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
    Output('parameter_building', 'data'),
    Input('building_type', 'value'),
    Input('heating_distribution_temperatures', 'value'),
    State('last_triggered_building','data'),
    )
def save_parameter_building(building_type, heating_distribution_temperatures, building):
    if building_type is None:
        raise PreventUpdate
    if building=='indu':
        building_type_data=[building_type*1000,15]
    else:
        building_type_data=eval(building_type)
    heating_distribution_temperatures=eval(heating_distribution_temperatures)
    building={'Q_sp':building_type_data[0], 'T_limit':building_type_data[1], 'T_vl_max':heating_distribution_temperatures[0],'T_rl_max':heating_distribution_temperatures[1],'f_hs_exp':heating_distribution_temperatures[2]}
    return building

@app.callback(
    Output('slp_choosen', 'children'),
    Input('industry_type', 'value'),
    Input('button_language', 'value'),
)
def save_parameter_chp_max_power(industry_type, lang):
    if industry_type=='own_loadprofile':
        return dcc.Upload(id='upload_load_profile',children=html.Div([
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
                ), html.Div(id='kpi_LSK'), dcc.Store('stromverbrauch'), dcc.Store(id='building_type_value')
    return [dbc.Col(language.loc[language['name']=='energy_cons',lang].iloc[0], width=6,style={'marginTop': '1rem'}),
            dbc.Col(html.Div(id='stromverbrauch_value'), width=4, style={'marginTop': '1rem'}),
            dbc.Col(dcc.Slider(min=5_000,max=200_000,step=1000,marks=None,value=50_000,id='stromverbrauch',tooltip={'placement': 'top', 'always_visible': False},persistence='memory'), width=12),
            dcc.Store(id='building_type_value', storage_type='memory')]
@app.callback(
    Output('chp_max_power_data', 'data'),
    Input('chp_max_power', 'value'),
)
def save_parameter_chp_max_power(chp_max_power):
    if chp_max_power is None:
        raise PreventUpdate
    return chp_max_power

@app.callback(
    Output('chp_technology_data', 'data'),
    Input('chp_technology', 'value'),
)
def save_parameter_chp_technology_value(chp_technology):
    if chp_technology is None:
        raise PreventUpdate
    return chp_technology

# Show photovoltaic power
@app.callback(
    Output('pv_slider_value', 'children'),
    Input('pv_slider', 'value'),
    )
def print_pv_slider_value(pv_slider):
    return html.Div(str(pv_slider)+ ' kWp')

@app.callback(
    Output('pv2_slider_value', 'children'),
    Input('pv2_slider', 'value'),
    )
def print_pv_slider_value2(pv_slider):
    return html.Div(str(pv_slider)+ ' kWp')

# Show battery power
@app.callback(
    Output('p_bat_text', 'children'),
    Input('p_bat', 'value'),
    )
def print_pbat_text(p_bat):
    return html.Div(str(p_bat)+ ' kW/KWh')

# Show Feed-in limitation power
@app.callback(
    Output('feed_in_limit_text', 'children'),
    Input('feed_in_limit', 'value'),
    )
def print_pbat_text(p_bat):
    return html.Div(str(int(p_bat*100))+ ' %')

# Show investment cost batteries
@app.callback(
    Output('absolut_bat_cost_small_text', 'children'),
    Output('absolut_bat_cost_big_text', 'children'),
    Output('specific_bat_cost_small_text','children'),
    Output('specific_bat_cost_big_text','children'),
    Input('absolut_bat_cost_small', 'value'),
    Input('absolut_bat_cost_big', 'value'),
    State('parameter_use', 'data'),
    State('batteries','data'),
    State('parameter_peak_shaving', 'data'),
    Input('tabs','value')
    )
def show_investmentcost_small(absolut_bat_cost_small, absolut_bat_cost_big, LSK, batteries, df_peak_shaving_results, tabs):
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
    return (html.Div([str(round(absolut_bat_cost_small))+ ' €']),
            html.Div([str(round(absolut_bat_cost_big))+ ' €']),
            str(round((absolut_bat_cost_small / capacity_bat_small))) + ' €/kWh',  str(round((absolut_bat_cost_big / capacity_bat_big))) + ' €/kWh')

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
        decoded_split=decoded.decode('utf-8', errors='ignore').split('\n')
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
    State('parameter_use', 'data'),
)
def calculate_peak_shaving(loadprofile, lang, use_case):
    if use_case==0:
        raise PreventUpdate
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
    fig=px.scatter(data_frame=df,x=language.loc[language['name']=='cut_peak',lang].iloc[0],y=language.loc[language['name']=='usable_battery_size',lang].iloc[0],color=language.loc[language['name']=='e_rate',lang].iloc[0],size=language.loc[language['name']=='load_hours',lang].iloc[0], color_continuous_scale='turbo')
    colorbar=dict(tickmode='array',tickvals=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],len=1.05,ticklabeloverflow='allow',outlinewidth=0)
    fig.update_layout(coloraxis = {'cmin':0,'cmax':3.0,'colorbar':colorbar,'autocolorscale':False},)
    fig.update_layout(margin=dict(l=20, r=20, b=20),)
    return [
            html.Br(),
            html.Br(),dcc.Graph(figure=fig, config={'displayModeBar': False})]


# reset bat_cost
@app.callback(
    Output('absolut_bat_cost_small', 'value'),
    Output('absolut_bat_cost_big', 'value'),
    Input('button_reset_price', 'n_clicks'),
    State('parameter_use', 'data'),
    State('batteries','data'),
    State('parameter_peak_shaving', 'data'),
)
def reset_bat_price(n_reset, LSK, batteries, df_peak_shaving_results):
    if n_reset is None:
        raise PreventUpdate
    I_0,exp=eco.invest_params_default()
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
    specific_bat_cost_small,_ = eco.invest_costs(capacity_bat_small, I_0, exp)
    specific_bat_cost_big, _ = eco.invest_costs(capacity_bat_big, I_0, exp)
    return int(round(float(specific_bat_cost_small*capacity_bat_small)/50)*50),int(round(float(specific_bat_cost_big*capacity_bat_big)/50)*50)

# reset electricity_tariff (Use Case increase self-sufficiency)
@app.callback(
    Output('energy_price_below2500', 'value'),
    Output('energy_price_above2500', 'value'),
    Output('power_price_below2500', 'value'),
    Output('power_price_above2500', 'value'),
    Input('button_reset_price', 'n_clicks'),
)
def reset_economy(n):
    if n is None:
        raise PreventUpdate
    energy_price_below2500, energy_price_above2500, power_price_below2500, power_price_above2500=eco.grid_costs_default()
    energy_price_below2500=energy_price_below2500*100
    energy_price_above2500=energy_price_above2500*100
    return energy_price_below2500, energy_price_above2500, power_price_below2500, power_price_above2500

# Save electricity price autarky
@app.callback(
    Output('price_electricity', 'data'),
    Output('price_buy_text', 'children'),
    Output('price_increase_text', 'children'),
    Output('price_sell_text', 'children'),
    Output('price_sell', 'value'),
    Output('price_buy', 'value'),
    Output('price_increase', 'value'),
    Output('imputed_interest_rate', 'value'),
    Output('life_exp', 'value'),
    Input('price_buy', 'value'),
    Input('price_increase', 'value'),
    Input('price_sell', 'value'),
    Input('button_reset_price', 'n_clicks'),
    )
def save_price_buy(price_buy,price_increase,price_sell, tabs):
    if ctx.triggered_id=='button_reset_price':
        price_buy=30
        price_sell=6
        price_increase=1.5
    return [price_buy, price_sell], str(price_buy)+ ' ct/kWh',str(price_increase)+' %', str(price_sell)+ ' ct/kWh', price_sell, price_buy, price_increase, 3, 15

# Save electricity price peak shaving
@app.callback(
    Output('price_electricity_peak', 'data'),
    Output('energy_price_below2500_text', 'children'),
    Output('energy_price_above2500_text', 'children'),
    Output('power_price_below2500_text', 'children'),
    Output('power_price_above2500_text', 'children'),
    Input('energy_price_below2500', 'value'),
    Input('energy_price_above2500', 'value'),
    Input('power_price_below2500', 'value'),
    Input('power_price_above2500', 'value'),
    Input('button_reset_price', 'n_clicks'),
    )
def save_price_buy_peak(energy_tariff_below2500, energy_tariff_above2500, power_tariff_below2500, power_tariff_above2500, tabs):
    return [energy_tariff_below2500/100, energy_tariff_above2500/100, power_tariff_below2500, power_tariff_above2500], str(energy_tariff_below2500)+ ' ct/kWh', str(energy_tariff_above2500)+' ct/kWh', str(power_tariff_below2500)+' €/kW', str(power_tariff_above2500)+' €/kW'


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

# suchen
@app.callback(
    Output('accordion_simulate', 'active_item'),
    Input('button_simulation', 'n_clicks'),
)
def collapse_accordion(n):
    if n == None:
        raise PreventUpdate
    return []

#create results

# Calculate self sufficiency with different battery sizes # suchen

@app.callback(
    Output('batteries', 'data'),
    Output('hp_technology_value', 'children'), 
    Output('parameter_hp','data'),
    Output('building_type_value','children'), 
    Output('chp_load_hours', 'children'), 
    Output('chp_technology_value', 'children'), 
    Output('chp_technology_value2', 'children'),
    Output('accordion_simulate_1','title'),
    Output('accordion_simulate_2','title'),
    Output('accordion_simulate_3','title'),
    Output('accordion_simulate_4','title'),
    Output('simulation_info','children'),
    State('stromverbrauch', 'value'),
    State('last_triggered_building','data'),
    State('industry_type','value'),
    State('parameter_include_heating', 'data'),
    State('parameter_location_int','data'),
    State('parameter_wohnfläche','data'),
    State('parameter_building','data'),
    State('hp_technology','value'),
    State('chp_max_power_data','data'),
    State('chp_technology_data','data'),
    State('pv_slider','value'),
    State('n_chp', 'style'),
    State('n_hp', 'style'),
    State('n_solar', 'style'),
    State('n_solar2', 'style'),
    State('weather_typ','data'),
    State('pv1_inclination', 'value'),
    State('pv1_azimut', 'value'),
    State('pv2_slider','value'),
    State('pv2_inclination', 'value'),
    State('pv2_azimut', 'value'),
    State('p_bat', 'value'),
    State('feed_in_limit', 'value'),
    State('bat_prog', 'value'),
    Input('button_simulation', 'n_clicks'),
    State('parameter_loadprofile', 'data'),
    State('button_language', 'value')
)
def calc_bat_results(e_hh,building_name,building_type, heating,region,Area,building, choosen_hp, chp_max_ratio, choosen_chp, pv_size, chp_active, hp_active, pv_active, pv_active2, weather_typ, pv1_inclination, pv1_azimut, pv2_slider, pv2_inclination, pv2_azimut, p_bat, feed_in_limit, bat_prog, n, load_profile ,lang):
    if n is None:
        raise PreventUpdate
    ## Electrica loadprofile
    if (building_name=='indu')&(building_type=='own_loadprofile'):
        p_el=load_profile
    else:    
        if building_name=='efh':
            p_el=pd.read_csv(DATA_PATH.joinpath('electrical_loadprofiles/LP_W_EFH.csv'))
            
        elif building_name=='mfh':
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
        p_el=(p_el.iloc[:,1].values*e_hh/1000)
    tech_title=''
    P_stc=0
    ## Photovoltaic
    if pv_active['color']=='white':
        if pv_active2['color']=='white':
            P_stc=pv_size+pv2_slider
            tech_title+='PV: ' + str(P_stc)+ ' kWp'
            c_pv=sim.calc_pv(trj=region-1,year=str(weather_typ[1]),type=weather_typ[0],tilt=pv1_inclination,orientation=pv1_azimut)
            p_pv1=np.array(c_pv)*pv_size
            if pv2_slider>0:
                c_pv=sim.calc_pv(trj=region-1,year=str(weather_typ[1]),type=weather_typ[0],tilt=pv2_inclination,orientation=pv2_azimut)
                p_pv2=np.array(c_pv)*pv2_slider
                p_pv=p_pv1+p_pv2
            else:
                p_pv=p_pv1
        else:
            P_stc=pv_size
            tech_title+='PV: ' + str(pv_size)+ ' kWp'
            c_pv=sim.calc_pv(trj=region-1,year=str(weather_typ[1]),type=weather_typ[0],tilt=pv1_inclination,orientation=pv1_azimut)
            p_pv=np.array(c_pv)*pv_size
    elif pv_active2['color']=='white':
        P_stc=pv2_slider
        tech_title+='PV: ' + str(pv2_slider)+ ' kWp'
        c_pv=sim.calc_pv(trj=region-1,year=str(weather_typ[1]),type=weather_typ[0],tilt=pv2_inclination,orientation=pv2_azimut)
        p_pv=np.array(c_pv)*pv2_slider
    else:
        p_pv=0
    ## heating system
    if (heating is None) or (heating==[]) or (region is None) or ((Area is None) and (building_name!='indu')) or(building is None):
        p_hp = 0
        p_chp = 0
        hp_summary=None
        p_chp = 0
        building_type_value = ''
        chp_th = None
        chp_el = None
        chp_runtime = None
        sim_error_info=language.loc[language['name']=='simulation_info2',lang].iloc[0]
    else:
        if building_name=='indu':
            inhabitants=-5
            Area=1
        else:
            inhabitants = Area[0]
            Area=Area[1]
        # Definintion and selection of building type
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
        building_type_value = language.loc[language['name']=='max_heatload',lang].iloc[0]+' '+str(round(P_th_max/1000,1))+' kW'
        # Calc heating load time series with 24h average outside temperature
        weather = pd.read_csv(DATA_PATH.joinpath('weather/TRY_'+str(region)+'_'+weather_typ[0]+'_'+weather_typ[1]+'_15min.csv'), header=0, index_col=0)
        weather.loc[weather['temperature 24h [degC]']<building['T_limit'],'p_th_heating']=(t_room-weather.loc[weather['temperature 24h [degC]']<building['T_limit'],'temperature 24h [degC]'])* building['Q_sp'] * Area
        weather.loc[weather['temperature 24h [degC]']>=building['T_limit'],'p_th_heating']=0
        # Load domestic hot water load profile
        if building_name=='indu':
            load = pd.read_csv(DATA_PATH.joinpath('thermal_loadprofiles/dhw_1_15min.csv'), header=0, index_col=0)*0
        else:
            load = pd.read_csv(DATA_PATH.joinpath('thermal_loadprofiles/dhw_'+str(int(inhabitants)) +'_15min.csv'), header=0, index_col=0)
        load['p_th_heating [W]']=weather['p_th_heating'].values
        load_dict=load[['load [W]','p_th_heating [W]']].to_dict()

        ## Heat pump
        if (choosen_hp is None) or hp_active['color']!='white':
            p_hp=0
            hp_summary=None
        else:
            if choosen_hp.startswith('Sole'):
                group_id=5
            elif choosen_hp.startswith('Luft'):
                group_id=1
            else:
                raise PreventUpdate
            P_hp_el , results_summary, t_in, t_out = sim.calc_hp(weather, building,load_dict,group_id)
            p_hp= P_hp_el.values
            hp_summary=(html.Div('SJAZ: '+str((round(results_summary['SJAZ'],2)))+ ', ' +str(int(round(results_summary['Energy_consumption_kWh'],0)))+' kWh'))
            tech_title+='; '+language.loc[language['name']=='hp',lang].iloc[0]+': '+'SJAZ: '+str((round(results_summary['SJAZ'],2)))+ ', ' +str(int(round(results_summary['Energy_consumption_kWh'],0)))+' kWh'

        ## CHP
        sim_error_info=language.loc[language['name']=='simulation_info2',lang].iloc[0]
        if (choosen_chp is None) or chp_active['color']!='white':
            p_chp = 0
            chp_th = None
            chp_el = None
            chp_runtime = None
            P_el_chp=0
            if hp_active['color']!='white' and (len(heating)==1):
                sim_error_info=language.loc[language['name']=='error_heating_missing',lang].iloc[0]
        else:
            results_timeseries, _, P_th_chp, P_el_chp, runtime = sim.calc_chp(weather, building,load_dict,choosen_chp/100,chp_to_peak_ratio=chp_max_ratio/100)
            p_chp = results_timeseries['P_chp_h_el'].values
            chp_runtime=html.Div(str(int(round(runtime)))+' '+ language.loc[language['name']=='load_hours',lang].iloc[0])
            chp_th = html.Div([str(chp_max_ratio)+ '% (' + str((round(P_th_chp/1000,1)))+' kW', html.Sub('th'), ')'])
            chp_el = html.Div([str(choosen_chp)+ '% (' + str((round(P_el_chp/1000,1))) + ' kW', html.Sub('el'), ')'])
            tech_title+='; '+language.loc[language['name']=='chp',lang].iloc[0]+': '+str(int(round(runtime)))+' '+ language.loc[language['name']=='load_hours',lang].iloc[0]+', ' + str((round(P_el_chp/1000,1))) + ' kWel,' + str((round(P_th_chp/1000,1)))+' kWth'


    ## Calculation
    df=pd.DataFrame()
    df.index=pd.date_range(start='2022-01-01', end='2023-01-01', periods=35041)[0:35040]
    df['p_el_hh']=p_el
    df['p_el_hp']=p_hp
    df['p_chp']=p_chp
    df['p_el_hh']=df['p_el_hh']+df['p_el_hp']
    df['p_PV'] = p_pv
    if (df['p_PV'].mean()==0) and df['p_chp'].mean()==0:
        return (None, hp_summary,None,  building_type_value, chp_runtime, chp_th, chp_el,language.loc[language['name']=='location',lang].iloc[0],language.loc[language['name']=='choose_building',lang].iloc[0],language.loc[language['name']=='choose_technology',lang].iloc[0], language.loc[language['name']=='simulation_info3',lang].iloc[0])
    E_el_MWH = df['p_el_hh'].mean()*8.76/1000
    E_pv_kwp = df['p_PV'].mean()*8.76/1000
    E_chp = df['p_chp'].mean()*8.76/1000
    if building_name!='efh':
        if (E_chp>0):
            max_battery_size = np.ceil(round(E_el_MWH,0)/5)*5
        else:
            max_battery_size = np.ceil(np.minimum(round(E_el_MWH,0)*2,E_pv_kwp*2)/5)*5
    else:
        if (E_chp>0):
            max_battery_size = np.ceil(round(E_el_MWH,0)*1.5/5)*5#TODO: CHP battery sizing?
        else:
            max_battery_size = np.ceil(np.minimum(round(E_el_MWH,0)*2,E_pv_kwp*2)/5)*5 #TODO: CHP battery sizing?
    if bat_prog == []:
        bat_prog=['']
        bat_title=language.loc[language['name']=='bat_prog_negativ',lang].iloc[0]
    else:
        bat_title=language.loc[language['name']=='bat_prog_positiv',lang].iloc[0]
    batteries=sim.calc_bs(df, np.maximum(10,max_battery_size), p_bat, feed_in_limit, bat_prog[0],P_stc=P_stc)
    if building_name=='efh':
        building_name=language.loc[language['name']=='efh_name',lang].iloc[0]
    elif building_name=='mfh':
        building_name=language.loc[language['name']=='mfh_name',lang].iloc[0]
    elif building_name=='indu':
        building_name=language.loc[language['name']=='industry_name',lang].iloc[0]
    return (batteries.to_dict(), 
        hp_summary,
        choosen_hp,
        building_type_value,
        chp_runtime,
        chp_th,
        chp_el,
        language.loc[language['name']=='weather_data',lang].iloc[0]+' ' + language.loc[language['name']==str(region),lang].iloc[0], 
        language.loc[language['name']=='choose_building',lang].iloc[0] +' '+building_name+ ' ' + building_type_value, 
        language.loc[language['name']=='choose_technology',lang].iloc[0]+ ' '+tech_title,
        language.loc[language['name']=='battery_storage',lang].iloc[0] + ' ' + str(int(feed_in_limit*100)) + ' %, ' + bat_title,
        sim_error_info)

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
    if (batteries is None): #or ((building!='indu') & (include_heating is None))
        raise PreventUpdate
    elif (len(batteries)==3) or (tab!='tab_parameter') or (parameter_use!=0):
        return html.Div()
    #elif building != 'indu':
    elif(len(include_heating)==1) and (n_hp==0) and (n_chp==0):
        return html.Div()
    return html.Div(children=[html.Br(),
    dbc.Container([
        dbc.Row([
            dbc.Col(dbc.Button(language.loc[language['name']=='self_sufficiency',lang].iloc[0],id='Autarkiegrad',color="primary", active=True)),
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
        return show_graph, {'background-color': '#003da7','color': 'white',},{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'}
    elif show_graph=='Eigenverbrauch':
        return show_graph,{'background-color': 'white','color': 'black'},{'background-color': '#003da7','color': 'white',},{'background-color': 'white','color': 'black'}
    elif show_graph=='Energiebilanz':
        return show_graph, {'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'},{'background-color': '#003da7','color': 'white',}

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
    batteries['Autarkiegrad ohne Stromspeicher'] = batteries['Autarkiegrad ohne Stromspeicher'].round(0).astype(int)
    batteries['Erhöhung der Autarkie durch Stromspeicher'] = batteries['Erhöhung der Autarkie durch Stromspeicher'].round(0).astype(int)
    batteries['Eigenverbrauch ohne Stromspeicher'] = batteries['Eigenverbrauch ohne Stromspeicher'].round(0).astype(int)
    batteries['Erhöhung des Eigenverbrauchs durch Stromspeicher'] = batteries['Erhöhung des Eigenverbrauchs durch Stromspeicher'].round(0).astype(int)
    batteries['Gesamter Autarkiegrad'] = (batteries['Autarkiegrad ohne Stromspeicher'] + batteries['Erhöhung der Autarkie durch Stromspeicher']).astype(str) + ' %'
    batteries['Gesamter Eigenverbrauchsgrad'] = (batteries['Eigenverbrauch ohne Stromspeicher'] + batteries['Erhöhung des Eigenverbrauchs durch Stromspeicher']).round(1).astype(str) + ' %'
    batteries['Netzbezug [kWh/a]']=batteries['Netzbezug'].astype(int)
    batteries['Netzeinspeisung [kWh/a]']=batteries['Netzeinspeisung'].astype(int)
    # Set axis font size and disable zoom
    axis_font = dict(size=16)

    if lang=='ger':
        if results_id=='Autarkiegrad':
            fig=px.bar(data_frame=batteries,x='e_bat',y=['Autarkiegrad ohne Stromspeicher','Erhöhung der Autarkie durch Stromspeicher'],
                color_discrete_map={'Autarkiegrad ohne Stromspeicher': '#ffe43b', 'Erhöhung der Autarkie durch Stromspeicher' : '#ffbd29'},
                labels={"e_bat": "nutzbare Speicherkapazität in kWh",
                        "value": "%",
                        'variable': ''
                        },
                hover_data={'Gesamter Autarkiegrad': True,
                        'e_bat': False,  # wenn du die x-Achse im Hover nicht doppelt willst
                        }
                )
        elif results_id=='Eigenverbrauch':
            fig=px.bar(data_frame=batteries,x='e_bat',y=['Eigenverbrauch ohne Stromspeicher','Erhöhung des Eigenverbrauchs durch Stromspeicher'],
                color_discrete_map={'Eigenverbrauch ohne Stromspeicher': '#ffe43b', 'Erhöhung des Eigenverbrauchs durch Stromspeicher' : '#ffbd29'},
                labels={"e_bat": "nutzbare Speicherkapazität in kWh",
                        "value": "%",
                        'variable': ''
                        },
                hover_data={'Gesamter Eigenverbrauchsgrad': True,
                        'e_bat': False,  # wenn du die x-Achse im Hover nicht doppelt willst
                        }

                )
        elif results_id=='Energiebilanz':
            fig=px.bar(data_frame=batteries,x='e_bat',y=['Netzeinspeisung [kWh/a]','Netzbezug [kWh/a]', 'Abregelungsverluste'],
                color_discrete_map={'Netzeinspeisung [kWh/a]': '#c8c8c8', 'Netzbezug [kWh/a]' : '#646464', 'Abregelungsverluste' : '#000000'},
                labels={"e_bat": "nutzbare Speicherkapazität in kWh",
                        #"value": "Netzbezug/Netzeinspeisung in kWh/a",
                        'variable': ''
                        },
                hover_data={
                        'e_bat': False,  # wenn du die x-Achse im Hover nicht doppelt willst
                        }
                )
            fig.update_yaxes(title="Netzbezug/Netzeinspeisung in kWh/a")
    else:
        batteries.rename(columns = {'Autarkiegrad ohne Stromspeicher':'Degree of self-sufficiency without battery',
                                    'Erhöhung der Autarkie durch Stromspeicher':'Increasing self-sufficiency battery',
                                    'Eigenverbrauch ohne Stromspeicher':'Self-consumption without battery',
                                    'Erhöhung des Eigenverbrauchs durch Stromspeicher':'Increase of self-consumption by battery',
                                    'Netzeinspeisung':'Grid feed-in',
                                    'Netzbezug': 'Grid supply',
                                    'Abregelungsverluste' : 'curtailment loss'
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
            fig=px.bar(data_frame=batteries,x='e_bat',y=['Grid feed-in','Grid supply', 'curtailment loss'],
                color_discrete_map={'Grid feed-in': '#c8c8c8', 'Grid supply' : '#646464', 'curtailment loss' : '#000000'},
                labels={"e_bat": "usable battery size in kWh",
                        "value": "Grid supply/Grid feed-in in kWh/a",
                        'variable': ''
                        }
            )
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=16)  # Set legend font size larger
        ),
        margin=dict(l=20, r=20, b=20),
        xaxis=dict(title_font=axis_font, tickfont=axis_font),
        yaxis=dict(title_font=axis_font, tickfont=axis_font),
        dragmode=False  # disables zoom and pan
    )
    # Also disable scroll/zoom via config
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
        return show_graph, {'background-color': '#003da7','color': 'white',},{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'}
    elif show_graph=='NetPresentValue':
        return show_graph,{'background-color': 'white','color': 'black'},{'background-color': '#003da7','color': 'white',},{'background-color': 'white','color': 'black'}
    elif show_graph=='InternalRateOfReturn':
        return show_graph, {'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'},{'background-color': '#003da7','color': 'white',}

# Show choosen graph (economy tab)
@app.callback(
    Output('cost_result_graph', 'children'),
    State('batteries', 'data'),
    State('parameter_peak_shaving', 'data'),
    Input('price_electricity','data'),
    Input('price_electricity_peak','data'),
    Input('price_increase', 'value'),
    Input('absolut_bat_cost_small','value'),
    Input('absolut_bat_cost_big','value'),
    Input('tabs', 'value'),
    Input('life_exp','value'),
    Input('imputed_interest_rate','value'),
    Input('show_economic_results', 'data'),
    State('parameter_use', 'data'),
    Input('button_language', 'value'),
    )
def economic_results_graph(batteries,batteries_peak,electricity_price,electricity_price_peak,price_increase_rate,absolut_bat_cost_small,absolut_bat_cost_big,tab,lifetime,interest_rate,results_id, LSK, lang):
    if ((electricity_price is None) and (LSK==0)) or ((electricity_price_peak is None) and (LSK==1)): 
        raise PreventUpdate
    if (LSK==0):
        batteries=(pd.DataFrame(batteries))
        if (electricity_price[0] is None) or (electricity_price[1] is None) or (batteries is None) or (tab!='tab_econmics'): 
            return html.Div()
        years=lifetime
        interest_rate=interest_rate/100
        Invest_cost=[]
        NetPresentValue=[]
        Amortisation=[]
        InternalRateOfReturn=[]
        I_0, exp = eco.invest_params([batteries['e_bat'].values[1],batteries['e_bat'].values[-1]],[absolut_bat_cost_small/batteries['e_bat'].values[1],absolut_bat_cost_big/batteries['e_bat'].values[-1]])
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
                            price_increase_rate/100,
                            years,
                            lifetime)
            NetPresentValue.append(round(eco.net_present_value(cashflow, interest_rate),0))
            Amortisation.append(eco.amortisation(cashflow, interest_rate))
            InternalRateOfReturn.append(round(eco.internal_rate_of_return(cashflow),4))
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
                    color_discrete_sequence=['#003da7'], 
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
                    color_discrete_sequence=['#003da7'], 
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
                title = language.loc[language['name']=='eco_text_9',lang].iloc[0] + best_value_battery + language.loc[language['name']=='eco_text_10',lang].iloc[0] + str(round(InternalRateOfReturn_max*100,1)) + ' %.'
            else:
                title = language.loc[language['name']=='eco_text_8',lang].iloc[0]
            fig=px.bar(data_frame=batteries, x='e_bat', y='InternalRateOfReturn', hover_data=['Investitionskosten'],
                    color_discrete_sequence=['#003da7'], 
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
        years=lifetime
        interest_rate=interest_rate/100
        Invest_cost=[]
        NetPresentValue=[]
        Amortisation=[]
        InternalRateOfReturn=[]
        I_0, exp = eco.invest_params([capacity_bat_small,capacity_bat_big],[absolut_bat_cost_small/capacity_bat_small,absolut_bat_cost_big/capacity_bat_big])
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
            NetPresentValue.append(round(eco.net_present_value(cashflow, interest_rate),0))
            Amortisation.append(eco.amortisation(cashflow,interest_rate))
            InternalRateOfReturn.append(round(eco.internal_rate_of_return(cashflow),4))
        df[language.loc[language['name']=='invest_cost',lang].iloc[0]]=Invest_cost
        df['NetPresentValue']=NetPresentValue
        df['Amortisation']=np.where(np.array(Amortisation)==0,lifetime,np.array(Amortisation))
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
                    title = language.loc[language['name']=='eco_text_3',lang].iloc[0]+ str(round(fastest_amort_battery,1)) + language.loc[language['name']=='eco_text_4',lang].iloc[0]
                else:
                    title= language.loc[language['name']=='eco_text_5',lang].iloc[0]
            else:
                title = language.loc[language['name']=='eco_text_6',lang].iloc[0]
            fig=px.line(data_frame=df, x=language.loc[language['name']=='usable_battery_size',lang].iloc[0], y='Amortisation', hover_data=[language.loc[language['name']=='invest_cost',lang].iloc[0]], 
                    labels={
                        "Amortisation": language.loc[language['name']=='payback_years',lang].iloc[0],
                        })
            fig.update_layout(margin=dict(l=20, r=20, b=20),)
            return [dbc.Col(html.H6(title), width={'offset':2}),dbc.Col(dcc.Graph(figure=fig,config={'displayModeBar': False}),width=12)]
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
                title = language.loc[language['name']=='eco_text_9',lang].iloc[0] + str(round(best_value_battery,1)) + language.loc[language['name']=='eco_text_10',lang].iloc[0] + str(round(InternalRateOfReturn_max*100,1)) + ' %.'
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
    app.run_server(debug=False, port=8050)
