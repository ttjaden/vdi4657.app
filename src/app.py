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
from utils.simulate import calc_pv
from utils.simulate import calc_bat

##################################################
# TODOs ##########################################
##################################################
# Abstand zwisschen Container und Header
# Startbild, falls noch nichts fertig parametriert werden

# Dummy-Ergebnis-Dataframe
df_sfh=pd.read_pickle('src/assets/data/dummy.pkl')

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
                        dbc.Col(html.Div(children=[html.Div(id='timeseries_results',children='To start go to Parameters'),
                                                    html.Div(id='bat_results'),
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
                [dcc.Tab(label='Info',value='tab_info',children=[html.Div(children=[
                                    html.H4(children='Was kann PIEG Strom Webtool?'),
                                    html.Div(children=language.loc[language['name']=='tab_info_1',lang].iloc[0]),
                                    html.Button(html.Div([DashIconify(icon='carbon:analytics',width=100,height=100,),html.Br(),language.loc[language['name']=='increase_autarky',lang].iloc[0]]),id='autakie_click',n_clicks=0,style={'background-color': 'white','color': 'black'}),
                                    html.Button(html.Div([DashIconify(icon='carbon:chart-multi-line',width=100,height=100,),html.Br(),language.loc[language['name']=='peak_shaving',lang].iloc[0]]),id='LSK_click',n_clicks=0,style={'background-color': 'white','color': 'black'}),
                                ])]),
                dcc.Tab(label='Parameter',value='tab_parameter',),
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
                            html.Div(html.H3(language.loc[language['name']=='choose_building',lang].iloc[0])),
                            html.Button(html.Div([DashIconify(icon='clarity:home-solid',width=50,height=50,),html.Br(),language.loc[language['name']=='efh_name',lang].iloc[0]],style={'width':'20vh'}),id='efh_click'),
                            html.Button(html.Div([DashIconify(icon='bxs:building-house',width=50,height=50,),html.Br(),language.loc[language['name']=='mfh_name',lang].iloc[0]],style={'width':'20vh'}),id='mfh_click'),
                            html.Button(html.Div([DashIconify(icon='la:industry',width=50,height=50,),html.Br(),language.loc[language['name']=='industry_name',lang].iloc[0]],style={'width':'20vh'}),id='industry_click'),
                            html.Div(id='bulding_container'),
                            html.Br(),
                            html.Div(html.H3(language.loc[language['name']=='efh_name',lang].iloc[0])),
                            html.Div(
                                html.Div(children=[html.Button(html.Div([DashIconify(icon='fa-solid:solar-panel',width=50,height=50,),html.Br(),language.loc[language['name']=='pv',lang].iloc[0]]),id='n_solar',n_clicks=0),
                                html.Button(html.Div([DashIconify(icon='fa-solid:solar-panel',width=50,height=50,),html.Br(),language.loc[language['name']=='pv',lang].iloc[0]]),id='n_solar2',n_clicks=0),
                                html.Button(html.Div([DashIconify(icon='mdi:gas-burner',width=50,height=50,),html.Br(),language.loc[language['name']=='chp',lang].iloc[0]]),id='n_chp',n_clicks=0),
                                html.Button(html.Div([DashIconify(icon='mdi:heat-pump-outline',width=50,height=50,),html.Br(),language.loc[language['name']=='hp',lang].iloc[0]]),id='n_hp',n_clicks=0),
                                html.Div(id='technology')])
                            ),
                            ]),
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
    State('button_language','value'),
)
def getcontainer(efh_click,mfh_click,industry_click,choosebuilding,lang):
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
        return (dbc.Container(
                    [
                        dbc.Row(
                            [
                            dbc.Col(html.Div(children=[
                                html.H4(language.loc[language['name']=='efh_name',lang].iloc[0]),
                                html.Div(language.loc[language['name']=='location',lang].iloc[0]),
                                dcc.Input(id='standort',placeholder=language.loc[language['name']=='placeholder_location',lang].iloc[0],persistence='local'),
                                html.Div(id='region'),
                                dcc.Store(id='baustandart'),
                                html.Div(language.loc[language['name']=='energy_cons',lang].iloc[0]),
                                dcc.Slider(min=2000,max=8000,step=500,value=4000,marks={2000:'2000',8000:'8000'},id='stromverbrauch',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),
                            ]), md=12),
                            ],
                        align='top',
                        ),
                    ],
                    fluid=True,
                    ),
                {'background-color': '#212529','color': 'white',},
                {'background-color': 'white','color': 'black'},
                {'background-color': 'white','color': 'black'},'efh')
    if (mfh_click>efh_click) and (mfh_click>industry_click):
        return (dbc.Container(
                    [
                        dbc.Row(
                            [
                            dbc.Col(html.Div(children=[
                                html.H4(language.loc[language['name']=='mfh_name',lang].iloc[0]),
                                html.Div(language.loc[language['name']=='location',lang].iloc[0]),
                                dcc.Input(id='standort',placeholder=language.loc[language['name']=='placeholder_location',lang].iloc[0],persistence='local'),
                                html.Div(id='region'),
                                dcc.Store(id='baustandart'),
                                html.Div(language.loc[language['name']=='energy_cons',lang].iloc[0]),
                                dcc.Slider(min=8000,max=74000,step=2000,value=10000,marks={8000:'8000',74000:'74000'},id='stromverbrauch',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),
                            ]), md=12),
                            ],
                        align='top',
                        ),
                        ],
                    fluid=True,
                    ),
                {'background-color': 'white','color': 'black'},
                {'background-color': '#212529','color': 'white',},
                {'background-color': 'white','color': 'black'},'mfh')
    if (industry_click>efh_click) and (industry_click>mfh_click):
        return (dbc.Container(
                    [
                        dbc.Row(
                            [
                            dbc.Col(html.Div(children=[
                                html.H4(language.loc[language['name']=='industry_name',lang].iloc[0]),
                                html.Div(language.loc[language['name']=='location',lang].iloc[0]),
                                dcc.Input(id='standort',placeholder=language.loc[language['name']=='placeholder_location',lang].iloc[0],persistence='local'),
                                html.Div(id='region'),
                                html.Div(language.loc[language['name']=='building_type_industry',lang].iloc[0]),
                                dcc.Dropdown(['office','Schule'],value='office',id='baustandart',persistence='local'),
                                html.Div(language.loc[language['name']=='energy_cons',lang].iloc[0]),
                                dcc.Slider(min=8000,max=74000,step=2000,value=16000,marks={8000:'8000',74000:'74000'},id='stromverbrauch',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),
                            ]), md=12),
                            ],
                        align='top',
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
    Input('n_solar2', 'style'),
    Input('n_chp', 'style'),
    Input('n_hp', 'style'),
    Input('button_language','value'),)
def built_technology(n_solar,n_solar2,n_chp,n_hp,lang):
    technology_list=[]
    if n_solar['color']=='white':
        technology_list.append(html.Div(children=[
                            html.Div(html.H4(language.loc[language['name']=='pv',lang].iloc[0])),
                            html.H6(language.loc[language['name']=='pv_power',lang].iloc[0]),
                            dcc.Slider(min=0,max=len(PV)-1,step=1,marks=pv_dict, id='pv_slider',value=10,persistence='local'),
                            html.H6((language.loc[language['name']=='pv_orientation',lang].iloc[0])),
                            dcc.Slider(min=0,max=360,step=5,marks={0:'0',360:'360'},tooltip={'placement': 'bottom', 'always_visible': False}, id='pv_orientation',value=180,persistence='local'),
                            html.H6((language.loc[language['name']=='pv_tilt',lang].iloc[0])),
                            dcc.Slider(min=0,max=90,step=1,marks={0:'0',90:'90'},tooltip={'placement': 'bottom', 'always_visible': False}, id='pv_tilt',value=35,persistence='local'),
                            html.Div(id='pv_value'),
                        ]))
    if n_solar2['color']=='white':
        technology_list.append(html.Div(children=[
                            html.Div(html.H4(language.loc[language['name']=='pv',lang].iloc[0])),
                            html.H6(language.loc[language['name']=='pv_power',lang].iloc[0]),
                            dcc.Slider(min=0,max=len(PV)-1,step=1,marks=pv_dict, id='pv_slider2',value=10,persistence='local'),
                            html.H6((language.loc[language['name']=='pv_orientation',lang].iloc[0])),
                            dcc.Slider(min=0,max=360,step=5,marks={0:'0',360:'360'},tooltip={'placement': 'bottom', 'always_visible': False}, id='pv_orientation2',value=180,persistence='local'),
                            html.H6((language.loc[language['name']=='pv_tilt',lang].iloc[0])),
                            dcc.Slider(min=0,max=90,step=1,marks={0:'0',90:'90'},tooltip={'placement': 'bottom', 'always_visible': False}, id='pv_tilt2',value=35,persistence='local'),
                            html.Div(id='pv_value2'),
                            ]))
    if n_chp['color']=='white':
        technology_list.append(html.Div(children=[
                            html.Div(html.H4(language.loc[language['name']=='chp',lang].iloc[0])),
                            html.H6(language.loc[language['name']=='chp_type',lang].iloc[0]),
                            dcc.RadioItems(options=language.loc[language['name']=='chp_type_options',lang],value=language.loc[language['name']=='chp_type_options',lang].iloc[0],id='chp_tech',),
                            html.Div(id='chp_elec',children=[html.Div(html.H6('Elektische Leistung')),dcc.Slider(min=0.5,max=2,step=0.1, id='chp_electric_slider',value=1,persistence='local')]),
                            html.H6(language.loc[language['name']=='chp_strategy',lang].iloc[0]),
                            dcc.RadioItems(options=language.loc[language['name']=='chp_strategy_options',lang],value=language.loc[language['name']=='chp_strategy_options',lang].iloc[2],id='chp_operation'),   
                            ]))
    if n_hp['color']=='white':
        technology_list.append(html.Div(children=[
                            html.Div(html.H4(language.loc[language['name']=='hp',lang].iloc[0])),
                            html.H6(language.loc[language['name']=='hp_type',lang].iloc[0]),
                            dcc.RadioItems(options=language.loc[language['name']=='hp_type_options',lang],value=language.loc[language['name']=='hp_type_options',lang].iloc[0],id='hp_typ')
                            ]))
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
@app.callback(
    Output('n_chp', 'style'), 
    Input('n_chp', 'n_clicks'),
    )
def change_chp_style(n_clicks):
    if (n_clicks%2)==1:
        return {'background-color': '#212529','color': 'white',}
    else:
        return {'background-color': 'white','color': 'black'}
@app.callback(
    Output('n_hp', 'style'), 
    Input('n_hp', 'n_clicks'),
    )
def change_hp_style(n_clicks):
    if (n_clicks%2)==1:
        return {'background-color': '#212529','color': 'white',}
    else:
        return {'background-color': 'white','color': 'black'}
@app.callback(
    Output('c_pv1', 'data'), 
    Input('pv_orientation','value'),
    Input('pv_tilt','value'),
    Input('standort','value'),)
def calc_pv_power1(orientation, tilt, location):
    pv1=calc_pv(trj=getregion(location)-1,year=2015,type='a',tilt=tilt,orientation=orientation)
    return pv1
@app.callback(
    Output('c_pv2', 'data'), 
    Input('pv_orientation2','value'),
    Input('pv_tilt2','value'),
    Input('standort','value'),)
def calc_pv_power2(orientation, tilt, location):
    pv2=calc_pv(trj=getregion(location)-1,year=2015,type='a',tilt=tilt,orientation=orientation)
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
    Output('E_bat_slider', 'children'),
    Input('stromverbrauch', 'value'),
    Input('button_expert','n_clicks'),)
def render_E_bat(efh,expertmode):
    if expertmode is None or expertmode%2==0:
        expertmode=False
    else:
        expertmode=True
    if int(efh/4000)==efh/4000:
        if expertmode:
            return html.Div(dcc.RangeSlider(efh/4000,efh/1000,efh/20000,value=[efh/4000,efh/1000],id='E_bat',marks={int(efh/4000):str(int(efh/4000)),int(efh/1000):str(int(efh/1000))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'))
        else:
            return html.Div(dcc.Slider(efh/4000,efh/1000,efh/20000,value=efh/2000,id='E_bat',marks={int(efh/4000):str(int(efh/4000)),int(efh/1000):str(int(efh/1000))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'))
    elif int(efh/1000)==efh/1000:
        if expertmode:
            return html.Div(dcc.RangeSlider(efh/4000,efh/1000,efh/20000,value=[efh/4000,efh/1000],id='E_bat',marks={(efh/4000):str((efh/4000)),int(efh/1000):str(int(efh/1000))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'))
        else:
            return html.Div(dcc.Slider(efh/4000,efh/1000,efh/20000,value=efh/2000,id='E_bat',marks={(efh/4000):str((efh/4000)),int(efh/1000):str(int(efh/1000))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'))
    else:
        if expertmode:
            return html.Div(dcc.RangeSlider(efh/4000,efh/1000,efh/20000,value=[efh/4000,efh/1000],id='E_bat',marks={(efh/4000):str((efh/4000)),(efh/1000):str((efh/1000))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'))
        else:
            return html.Div(dcc.Slider(efh/4000,efh/1000,efh/20000,value=efh/2000,id='E_bat',marks={(efh/4000):str((efh/4000)),(efh/1000):str((efh/1000))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'))
@app.callback(
    Output('P_bat_slider', 'children'),
    Input('E_bat', 'value'),
)
def render_P_bat(e_bat):
    if e_bat is None:
        raise PreventUpdate
    if isinstance(e_bat,list):
        return html.Div(dcc.RangeSlider(e_bat[0]/4,e_bat[1],value=[e_bat[0]/4,e_bat[1]],id='P_bat',marks={(e_bat[0]/4):str((e_bat[0]/4)),(e_bat[1]):str((e_bat[1]))},tooltip={'placement': 'bottom', 'always_visible': False}))
    return html.Div(dcc.Slider(e_bat/4,e_bat,e_bat/20,value=e_bat/2,id='P_bat',marks={(e_bat/4):str((e_bat/4)),(e_bat):str((e_bat))},tooltip={'placement': 'bottom', 'always_visible': False}))

@app.callback(
    Output('hyd_cap', 'children'),
    Input('stromverbrauch', 'value'),
    Input('button_expert','n_clicks'),)
def render_E_hyd(efh,expertmode):
    if expertmode is None or expertmode%2==0:
        expertmode=False
    else:
        expertmode=True
    if int(efh/8)==efh/8:
        if expertmode:
            return html.Div([dcc.RangeSlider(efh/8,efh/2,efh/40,value=[efh/8,efh/2],id='hyd_cap_slider',marks={int(efh/8):str(int(efh/8)),int(efh/2):str(int(efh/2))},tooltip={'placement': 'bottom', 'always_visible': False})])
        else:
            return html.Div(dcc.Slider(efh/8,efh/2,efh/40,value=efh/4,id='hyd_cap_slider',marks={int(efh/8):str(int(efh/8)),int(efh/2):str(int(efh/2))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'))
    else:
        if expertmode:
            return html.Div([dcc.RangeSlider(efh/8,efh/2,efh/40,value=[efh/8,efh/2],id='hyd_cap_slider',marks={(efh/8):str((efh/8)),int(efh/2):str(int(efh/2))},tooltip={'placement': 'bottom', 'always_visible': False})])
        else:
            return html.Div(dcc.Slider(efh/8,efh/2,efh/40,value=efh/4,id='hyd_cap_slider',marks={(efh/8):str((efh/8)),int(efh/2):str(int(efh/2))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'))
@app.callback(
    Output('electrolyseur_slider', 'children'),
    Input('hyd_cap_slider', 'value'),
)
def render_P_hyd(E_h2):
    if E_h2 is None:
        raise PreventUpdate
    try:
        E_h2_0=E_h2[0]
        E_h2_1=E_h2[1]
        if int(E_h2_0/200)==E_h2_0/200:
            if int(E_h2_1/50)==E_h2_1/50:
                return html.Div(children=[dcc.RangeSlider(E_h2_0/200,E_h2_1/50,id='electrolyseur_power',marks={int(E_h2_0/200):str(int(E_h2_0/200)),int(E_h2_1/50):str(int(E_h2_1/50))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),html.Br()])
            else:
                return html.Div(children=[dcc.RangeSlider(E_h2_0/200,E_h2_1/50,id='electrolyseur_power',marks={int(E_h2_0/200):str(int(E_h2_0/200)),(E_h2_1/50):str((E_h2_1/50))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),html.Br()])
        elif int(E_h2_1/50)==E_h2_1/50:
            return html.Div(children=[dcc.RangeSlider(E_h2_0/200,E_h2_1/50,id='electrolyseur_power',marks={(E_h2_0/200):str((E_h2_0/200)),int(E_h2_1/50):str(int(E_h2_1/50))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),html.Br()])
        else:
            return html.Div(children=[dcc.RangeSlider(E_h2_0/200,E_h2_1/50,id='electrolyseur_power',marks={(E_h2_0/200):str((E_h2_0/200)),(E_h2_1/50):str((E_h2_1/50))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),html.Br()])
    except:
        if int(E_h2/200)==E_h2/200:
            if int(E_h2/50)==E_h2/50:
                return html.Div(children=[dcc.Slider(E_h2/200,E_h2/50,E_h2/1000,value=E_h2/100,id='electrolyseur_power',marks={int(E_h2/200):str(int(E_h2/200)),int(E_h2/50):str(int(E_h2/50))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),html.Br()])
            else:
                return html.Div(children=[dcc.Slider(E_h2/200,E_h2/50,E_h2/1000,value=E_h2/100,id='electrolyseur_power',marks={int(E_h2/200):str(int(E_h2/200)),(E_h2/50):str((E_h2/50))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),html.Br()])
        elif int(E_h2/50)==E_h2/50:
            return html.Div(children=[dcc.Slider(E_h2/200,E_h2/50,E_h2/1000,value=E_h2/100,id='electrolyseur_power',marks={(E_h2/200):str((E_h2/200)),int(E_h2/50):str(int(E_h2/50))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),html.Br()])
        else:
            return html.Div(children=[dcc.Slider(E_h2/200,E_h2/50,E_h2/1000,value=E_h2/100,id='electrolyseur_power',marks={(E_h2/200):str((E_h2/200)),(E_h2/50):str((E_h2/50))},tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),html.Br()])


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
    Output('timeseries_results', 'children'),
    Input('p_el_hh','data'), 
    Input('p_pv1', 'data'),
    Input('p_pv2', 'data'),
    Input('n_solar', 'n_clicks'),
    Input('n_solar2', 'n_clicks'))
def graph_pv(p_el_hh,pv1,pv2,n_pv1,n_pv2):
    if p_el_hh is None: 
        return ('1. Click on a Building.')
    df=pd.DataFrame()
    year=datetime.now().date().year
    df.index=pd.date_range(start=str(year)+'-01-01', end=str(year+1)+'-01-01', periods=35041)[0:35040]
    if (pv1 is None) or ((n_pv1%2)!=1):
        pv1=np.zeros(35040).tolist()
    if (pv2 is None) or ((n_pv2%2)!=1):
        pv2=np.zeros(35040).tolist()
    df['p_el_hh']=p_el_hh
    df['p_PV']=np.array(pv1)+np.array(pv2)
    fig=px.line(df,title='Timeseries of Production and Consumption',labels={
                     "index": "Time",
                     "value": "Power [W]",
                     'variable': "Timeseries"
                 },)
    return dcc.Graph(figure=fig)

@app.callback(
    Output('bat_results', 'children'),
    Output('E_gs', 'data'),
    Output('E_gf', 'data'),
    Input('p_el_hh','data'), 
    Input('p_pv1', 'data'),
    Input('p_pv2', 'data'),
    Input('n_solar', 'n_clicks'),
    Input('n_solar2', 'n_clicks'))
def graph_pv(p_el_hh,pv1,pv2,n_pv1,n_pv2):
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
        return '2. Add Production of Electricity.',None , None
    batteries=calc_bat(df)
    fig1=px.line(data_frame=batteries,x='e_bat',y=['A','E'],labels={
                     "x": "Battery size [kWh]",
                     "y": "Autarkiegrad/Eigenverbrauch",
                 },title='Self-sufficiency and Self-consumption with different battery sizes')
    return dcc.Graph(figure=fig1),batteries['E_gs'].values.tolist(),batteries['E_gf'].values.tolist()

@app.callback(
    Output('cost_result', 'children'),
    Input('E_gs', 'data'),
    State('E_gf', 'data'),
    Input('electricity_price_buy','data'), 
    Input('electricity_price_sell', 'data'),
    )
def graph_pv(E_gs,E_gf,electricity_price_buy,electricity_price_sell):
    if (electricity_price_buy is None) or (E_gs is None): 
        return '3. Please change economic parameters in Economy Tab.'
    return dcc.Graph(figure=px.line(y=np.array(E_gs)*(-electricity_price_buy/100)-np.array(E_gf)*electricity_price_sell/100,title='Jahreskosten über Batteriegröße'))
if __name__ == '__main__':
    app.run_server(debug=True)