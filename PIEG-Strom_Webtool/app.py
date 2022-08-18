# Dash
from dash import Dash, html, dcc, Input, Output, State, callback_context,ctx
from dash.exceptions import PreventUpdate
# Dash community libraries
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
# Data management
import pandas as pd
# Plots
import plotly_express as px
# Eigene Funktionen
from functions.PLZtoWeatherRegion import getregion

##################################################
# TODOs ##########################################
##################################################
# TODO durchgängige Benennung der ids (Inhalt und Element) wie button_expert
# TODO durchgängig einfache Anführungszeichen
# Abstand zwisschen Container und Header
# Startbild, falls noch nichts fertig parametriert werden

# Dummy-Ergebnis-Dataframe
df_sfh=pd.read_pickle('PIEG-Strom_Webtool/dummy.pkl')

# App konfigurieren
# Icons via Iconify: siehe ps://icon-sets.iconify.design
app = Dash(__name__,
          suppress_callback_exceptions=True, 
          external_stylesheets=[dbc.themes.BOOTSTRAP,{'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css','rel': 'stylesheet','integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf','crossorigin': 'anonymous'}],
          meta_tags=[{'name': 'viewport', 'inhalt': 'width=device-width, initial-scale=1'},
          ],
          )

# Übersetzungstabelle (noch nicht durchgängig genutzt)
language=pd.read_csv('PIEG-Strom_Webtool/functions/translate.csv')

# PV-Größentabelle erstellen
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
                        dbc.Col(html.Div(id='results')),
                    ],align='top',
                    ),
                    dcc.Store(id='last_triggered_building')
                    
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
    return ([DashIconify(icon=flag, width=30,height=30,),language.loc[language['name']=='lang',lang].iloc[0]],lang,
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
                                html.Button(html.Div([DashIconify(icon='mdi:gas-burner',width=50,height=50,),html.Br(),language.loc[language['name']=='chp',lang].iloc[0]]),id='n_chp',n_clicks=0),
                                html.Button(html.Div([DashIconify(icon='mdi:heat-pump-outline',width=50,height=50,),html.Br(),language.loc[language['name']=='hp',lang].iloc[0]]),id='n_hp',n_clicks=0),
                                html.Button(html.Div([DashIconify(icon='material-symbols:mode-heat',width=50,height=50,),html.Br(),language.loc[language['name']=='gas',lang].iloc[0]]),id='n_gas',n_clicks=0),
                                html.Button(html.Div([DashIconify(icon='cil:battery-3',width=50,height=50,),html.Br(),language.loc[language['name']=='bat',lang].iloc[0]]),id='n_bat',n_clicks=0),
                                html.Button(html.Div([DashIconify(icon='iconoir:hydrogen',width=50,height=50,),html.Br(),language.loc[language['name']=='hyd',lang].iloc[0]]),id='n_hyd',n_clicks=0),
                                html.Div(id='technology')])
                            ),
                            ]),
        else:
            return html.Div(children='LSK')
    elif tab=='tab_econmics':
        return html.Div(children='economics')
    else:
        return html.Div()

# build parameter container
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
                                html.Div(language.loc[language['name']=='building_type_efh',lang].iloc[0]),
                                dcc.Dropdown(['kfW100','kfW50'],id='baustandart',value='kfW100',),
                                html.Div(language.loc[language['name']=='building_size',lang].iloc[0]),
                                dcc.Slider(50,250,50,value=150,id='wohnraum',persistence='local'),
                                html.H4(language.loc[language['name']=='usage',lang].iloc[0]),
                                html.Div(language.loc[language['name']=='inhabitants',lang].iloc[0]),
                                dcc.Slider(min=1,max=6,step=1,value=4,id='n_wohn',persistence='local'),
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
                                html.Div(language.loc[language['name']=='n_dwellings',lang].iloc[0]),
                                dcc.Slider(2,25,1,value=7,marks={2:'2',25:'25'},id='n_wohn',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),
                                html.Div(language.loc[language['name']=='building_size',lang].iloc[0]),
                                dcc.Slider(140,1750,70,value=700,marks={140:'140',1750:'1750'},id='wohnraum',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),
                                html.Div(language.loc[language['name']=='building_type_mfh',lang].iloc[0]),
                                dcc.Dropdown([25,75,200],value=75,id='baustandart'),
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
                                dcc.Slider(min=8000,max=74000,step=2000,marks={8000:'8000',74000:'74000'},id='stromverbrauch',tooltip={'placement': 'bottom', 'always_visible': False},persistence='local'),
                                dcc.Store(id='wohnraum'),
                                dcc.Store(id='n_wohn'),
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
    Input('n_chp', 'style'),
    Input('n_hp', 'style'),
    Input('n_gas', 'style'),
    Input('n_bat', 'style'),
    Input('n_hyd', 'style'),
    Input('button_language','value'))
def built_technology(n_solar,n_chp,n_hp,n_gas,n_bat,n_hyd,lang):
    technology_list=[]
    if n_solar['color']=='white':
        technology_list.append(html.Div(children=[
                            html.Div(html.H4(language.loc[language['name']=='pv',lang].iloc[0])),
                            html.H6('PV-Leistung in kWp: '),
                            dcc.Slider(min=0,max=len(PV)-1,step=1,marks=pv_dict, id='pv_slider',value=10,persistence='local'),
                            #html.Div(id='pv_value'),
                            html.H6('PV-Ausrichtung: '),
                            dcc.RadioItems(options={'Ost-West':'Ost-West','Süd':'Süd'},value='Süd',id='pv_ausrichtung',inline=False)
                        ]))
    if n_chp['color']=='white':
        technology_list.append(html.Div(children=[
                            html.Div(html.H4(language.loc[language['name']=='chp',lang].iloc[0])),
                            html.H6('Technologie: '),
                            dcc.RadioItems(options={'Gas':'Erdas','PEM':'Brennstoffzelle (PEM)','SOFC':'Brennstoffzelle (SOFC)'},id='chp_tech',),
                            html.Div(id='chp_elec',children=[html.Div(html.H6('Elektische Leistung')),dcc.Slider(min=0.5,max=2,step=0.1, id='chp_electric_slider',value=1,persistence='local')]),
                            html.H6('Betriebsstrategie: '),
                            dcc.RadioItems(options={'el':'elektisch','heat':'Wärme','el_heat':'elektisch & Wärme'},value='el_heat',id='chp_operation'),   
                            ]))
    if n_hp['color']=='white':
        technology_list.append(html.Div(children=[
                            html.Div(html.H4(language.loc[language['name']=='hp',lang].iloc[0])),
                            html.H6('Wärmepumpen-Typ: '),
                            dcc.RadioItems(options={'air':'Luft/Wasser','brine':'Sole/Wasser'},value='air',id='hp_typ')
                            ]))
    if n_gas['color']=='white':
        technology_list.append(html.Div(children=[
                            html.Div(html.H4(language.loc[language['name']=='gas',lang].iloc[0])),
                            html.Div(id='gas_power',children=[html.Div('bsp: Thermische Leistung: 500 kW')]),
                            ]))
    if n_bat['color']=='white':
        technology_list.append(html.Div(children=[
                            html.Div(html.H4(language.loc[language['name']=='bat',lang].iloc[0])),
                            html.H6('Batterie-Größe in kWh: '),
                            html.Div(id='E_bat_slider',children=dcc.Slider(min=0.5,max=2,step=0.1,marks=pv_dict, id='E_bat',persistence='local')),
                            html.H6('Batterieleistung in kW: '),
                            html.Div(id='P_bat_slider',children=dcc.Slider(min=0.5,max=2,step=0.1, id='P_bat',persistence='local')),
                            html.H6('Einspeisegrenze in kW/kWp: '),
                            html.Div(dcc.Slider(min=0,max=1,step=0.1, id='bat_lim',persistence='local')),
                            ]))
    if n_hyd['color']=='white':
        technology_list.append(html.Div(children=[
                            html.Div(html.H4(language.loc[language['name']=='hyd',lang].iloc[0])),
                            html.H6('H2-Speicherkapazität in kWhel: '),
                            html.Div(id='hyd_cap',children=[dcc.Slider(0.5,2,0.1,id='hyd_cap_slider',persistence='local')]),
                            html.H6('Elektolyseur-Leistung in kW: '),
                            html.Div(id='electrolyseur_slider',children=dcc.Slider(min=0.5,max=2,step=0.1, id='electrolyseur_power',value=10,persistence='local')),
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
    Output('n_solar', 'style'), 
    Input('n_solar', 'n_clicks'),
    )
def change_solar_style(n_clicks):
    if (n_clicks%2)==1:
        return {'background-color': '#212529','color': 'white',}
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
        return {'background-color': '#212529','color': 'white',},1
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
        return {'background-color': '#212529','color': 'white',},1
    else:
        if None!=n_chp:
            if (n_chp['color']=='white')&(n_gas['color']=='black'):
                return {'background-color': '#212529','color': 'white',},1
        return {'background-color': 'white','color': 'black'},2
@app.callback(
    Output('n_gas', 'style'), 
    Output('n_gas', 'n_clicks'), 
    Input('n_gas', 'n_clicks'),
    State('n_chp', 'style'),
    State('n_hp', 'style'),)
def change_gas_style(n_clicks,n_chp,n_hp):
    if (n_clicks%2)==1:
        return {'background-color': '#212529','color': 'white',},1
    else:
        if None!=n_chp:
            if (n_chp['color']=='white')&(n_hp['color']=='black'):
                return {'background-color': '#212529','color': 'white',},1
        return {'background-color': 'white','color': 'black'},2
@app.callback(
    Output('n_bat', 'style'), 
    Input('n_bat', 'n_clicks'),)
def change_bat_style(n_clicks):
    if (n_clicks%2)==1:
        return {'background-color': '#212529','color': 'white',}
    else:
        return {'background-color': 'white','color': 'black'}
@app.callback(
    Output('n_hyd', 'style'), 
    Input('n_hyd', 'n_clicks'),)
def change_hyd_style(n_clicks):
    if (n_clicks%2)==1:
        return {'background-color': '#212529','color': 'white',}
    else:
        return {'background-color': 'white','color': 'black'}
@app.callback(
    Output('pv_value', 'children'), 
    Input('pv_slider', 'value'),)
def change_hyd_style(pv_slider):
    return (PV[pv_slider])

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
    Output('results','children'),
    State('standort','value'),
    Input('baustandart','value'),
    Input('wohnraum','value'),
    Input('n_wohn','value'),
    Input('stromverbrauch','value'),
    State('bulding_container','children')
)
def show_results(standort,baustandart_sfh,wohnraum,n_wohn,stromverbrauch,info):
    gebäude=(info['props']['children'][0]['props']['children'][0]['props']['children']['props']['children'][0]['props']['children'])
    dff=df_sfh.loc[(df_sfh['personen']==n_wohn)&(df_sfh['stromverbrauch']==stromverbrauch)&(df_sfh['size']==wohnraum)&(df_sfh['baustand']==baustandart_sfh)]
    fig=px.scatter(dff,x='personen',y='Kosten')
    return dcc.Graph(figure=fig)

if __name__ == '__main__':
    app.run_server(debug=True)