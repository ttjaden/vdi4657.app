from tkinter import E
from dash.dependencies import Input, Output
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import plotly_express as px
from dash.exceptions import PreventUpdate

from functions.PLZtoWeatherRegion import getregion



df_sfh=pd.read_pickle('PIEG-Strom_Webtool/dummy.pkl')
app = Dash(__name__,
          suppress_callback_exceptions=True, 
          external_stylesheets=[dbc.themes.BOOTSTRAP,{'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css','rel': 'stylesheet','integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf','crossorigin': 'anonymous'}],
          meta_tags=[{"name": "viewport", "inhalt": "width=device-width, initial-scale=1"},
          ],
          )
language=pd.read_csv('PIEG-Strom_Webtool/functions/translate.csv')
region=['Nordseeküste','Ostseeküste','Nordwestdeutsches Tiefland','Nordostdeutsches Tiefland','Niederrheinisch-westfälische Bucht und Emsland','Nördliche und westliche Mittelgebirge, Randgebiete',
'Nördliche und westliche Mittelgebirge, zentrale Bereiche','Oberharz und Schwarzwald (mittlere Lagen)','Thüringer Becken und Sächsisches Hügelland','Südöstliche Mittelgebirge bis 1000 m',
'Erzgebirge, Böhmer- und Schwarzwald oberhalb 1000 m','Oberrheingraben und unteres Neckartal','Schwäbisch-fränkisches Stufenland und Alpenvorland','Schwäbische Alb und Baar',
'Alpenrand und -täler']

button_howto = dbc.Button(
    html.Div(id='button_expert',children=[DashIconify(icon="bi:toggle-off",width=100,height=30,),'Expert']),
    id="expert",
    outline=True,
    color="info",
    style={"textTransform": "none"},
)

button_github = dbc.Button(
    html.Div(id='button_language',children=[DashIconify(icon="emojione:flag-for-united-kingdom",width=30,height=30,),'Language']),
    outline=True,
    color="primary",
    id="language",
    style={"text-transform": "none"},
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
                                    html.H4("PIEG-Strom Webtool"),
                                    html.P("Auslegung von Batteriespeichern"),
                                ],
                                id="app-title",
                            )
                        ],
                        md=True,
                        align="center",
                    ),
                ],
                align="center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.NavbarToggler(id="navbar-toggler"),
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavItem(button_howto,style={'width':'150'}),
                                        dbc.NavItem(button_github,style={'width':'150'}),
                                    ],
                                    navbar=True,
                                ),
                                id="navbar-collapse",
                                navbar=True,
                            ),
                        ],
                        md=3,
                    ),
                ],
                align="center",
            ),
        ],
        fluid=True,
    ),
    dark=True,
    color="#212529",
    sticky="top",
)
efh_inhalt=html.Div(children=[
    html.H4(language.loc[language['name']=='efh_name','ger']),
    html.Div('Standort'),
    dcc.Input(id='standort',placeholder='Postleitzahl oder Adresse',persistence='local'),
    html.Div(id='region'),
    html.Div('Baustandard'),
    dcc.Dropdown(['kfW100','kfW50'],id='baustandart',value='kfW100',),
    html.Div('Wohnraum in qm'),
    dcc.Slider(50,250,50,value=150,id='wohnraum',persistence='local'),
    html.H4('Verbrauchskennzahlen'),
    html.Div('Bewohneranzahl'),
    dcc.Slider(min=1,max=6,step=1,value=4,id='n_wohn',persistence='local'),
    html.Div('Stromverbrauch in kWh'),
    dcc.Slider(min=2000,max=8000,step=500,value=4000,marks={2000:'2000',8000:'8000'},id='stromverbrauch',tooltip={"placement": "bottom", "always_visible": False},persistence='local'),
])
efh_content=html.Div(children=[
    html.H4(language.loc[language['name']=='efh_name','eng']),
    html.Div(language.loc[language['name']=='location','eng']),
    dcc.Input(id='standort',placeholder=language.loc[language['name']=='placeholder_location','eng'].values[0],persistence='local'),
    html.Div(id='region'),
    html.Div(language.loc[language['name']=='building_type','eng']),
    dcc.Dropdown(['kfW100','kfW50'],id='baustandart',value='kfW100',),
    html.Div(language.loc[language['name']=='Building size in sqm','eng']),
    dcc.Slider(50,250,50,value=150,id='wohnraum',persistence='local'),
    html.H4(language.loc[language['name']=='usage','eng']),
    html.Div(language.loc[language['name']=='inhabitants','eng']),
    dcc.Slider(min=1,max=6,step=1,value=4,id='n_wohn',persistence='local'),
    html.Div(language.loc[language['name']=='energy_cons','eng']),
    dcc.Slider(min=2000,max=8000,step=500,value=4000,marks={2000:'2000',8000:'8000'},id='stromverbrauch',tooltip={"placement": "bottom", "always_visible": False},persistence='local'),
])
mfh_inhalt=html.Div(children=[
    html.H4('Mehrfamilienhaus'),
    html.Div('Standort'),
    dcc.Input(id='standort',placeholder='Postleitzahl oder Adresse',persistence='local'),
    html.Div('Nordsee',id='region'),
    html.Div('Anzahl an Wohnungen'),
    dcc.Slider(2,25,1,value=7,marks={2:'2',25:'25'},id='n_wohn',tooltip={"placement": "bottom", "always_visible": False},persistence='local'),
    html.Div('Gebäudegröße in m²:'),
    dcc.Slider(140,1750,70,value=700,marks={140:'140',1750:'1750'},id='wohnraum',tooltip={"placement": "bottom", "always_visible": False},persistence='local'),
    html.Div('Baustandard in kWh/(m² Jahr)'),
    dcc.Dropdown([25,75,200],value=75,id='baustandart'),
    html.Div('Stromverbrauch in kWh:'),
    dcc.Slider(min=8000,max=74000,step=2000,value=10000,marks={8000:'8000',74000:'74000'},id='stromverbrauch',tooltip={"placement": "bottom", "always_visible": False},persistence='local'),
])
industrie_inhalt=html.Div(children=[
    html.H4('Industriegebäude'),
    html.Div('Standort'),
    dcc.Input(id='standort',placeholder='Postleitzahl oder Adresse',persistence='local'),
    html.Div('Nordsee',id='region'),
    html.Div('Industriezweig'),
    dcc.Dropdown(['office','Schule'],value='office',id='baustandart',persistence='local'),
    html.Div('Stromverbrauch in kWh'),
    dcc.Slider(min=8000,max=74000,step=2000,marks={8000:'8000',74000:'74000'},id='stromverbrauch',tooltip={"placement": "bottom", "always_visible": False},persistence='local'),
    dcc.Store(id='wohnraum'),
    dcc.Store(id='n_wohn'),
])
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
pv_inhalt=html.Div(children=[
    html.Div(html.H4('Photovoltaik')),
    html.H6('PV-Leistung in kWp: '),
    dcc.Slider(min=0,max=len(PV)-1,step=1,marks=pv_dict, id='pv_slider',value=10,persistence='local'),
    #html.Div(id='pv_value'),
    html.H6('PV-Ausrichtung: '),
    dcc.RadioItems(options={'Ost-West':'Ost-West','Süd':'Süd'},value='Süd',id='pv_ausrichtung',inline=False)
    ])
chp_inhalt=html.Div(children=[
    html.Div(html.H4('KWK-Anlage')),
    html.H6('Technologie: '),
    dcc.RadioItems(options={'Gas':'Erdas','PEM':'Brennstoffzelle (PEM)','SOFC':'Brennstoffzelle (SOFC)'},id='chp_tech',),
    html.Div(id='chp_elec',children=[html.Div(html.H6('Elektische Leistung')),dcc.Slider(min=0.5,max=2,step=0.1, id='chp_electric_slider',value=1,persistence='local')]),
    html.H6('Betriebsstrategie: '),
    dcc.RadioItems(options={'el':'elektisch','heat':'Wärme','el_heat':'elektisch & Wärme'},value='el_heat',id='chp_operation'),   
    ])
hp_inhalt=html.Div(children=[
    html.Div(html.H4('Wärmepumpe')),
    html.H6('Wärmepumpen-Typ: '),
    dcc.RadioItems(options={'air':'Luft/Wasser','brine':'Sole/Wasser'},value='air',id='hp_typ')
    ])
gas_inhalt=html.Div(children=[
    html.Div(html.H4('Gasheizung')),
    html.Div(id='gas_power',children=[html.Div('bsp: Thermische Leistung: 500 kW')]),
    ])
bat_inhalt=html.Div(children=[
    html.Div(html.H4('Batterie')),
    html.H6('Batterie-Größe in kWh: '),
    html.Div(id='E_bat_slider',children=dcc.Slider(min=0.5,max=2,step=0.1,marks=pv_dict, id='E_bat',persistence='local')),
    html.H6('Batterieleistung in kW: '),
    html.Div(id='P_bat_slider',children=dcc.Slider(min=0.5,max=2,step=0.1, id='P_bat',persistence='local')),
    html.H6('Einspeisegrenze in kW/kWp: '),
    html.Div(dcc.Slider(min=0,max=1,step=0.1, id='bat_lim',persistence='local')),
    ])
hyd_inhalt=html.Div(children=[
    html.Div(html.H4('H2-Speicher')),
    html.H6('H2-Speicherkapazität in kWhel: '),
    html.Div(id='hyd_cap',children=[dcc.Slider(0.5,2,0.1,id='hyd_cap_slider',persistence='local')]),
    html.H6('Elektolyseur-Leistung in kW: '),
    html.Div(id='electrolyseur_slider',children=dcc.Slider(min=0.5,max=2,step=0.1, id='electrolyseur_power',value=10,persistence='local')),
    #html.Div(id='pv_value'),
    ])
hyd_inhalt_expert=html.Div(children=[
    html.Div(html.H4('H2-Speicher')),
    html.H6('H2-Speicherkapazität in kWhel: '),
    html.Div(id='hyd_cap',children=[dcc.RangeSlider(0.5,2,0.1,id='hyd_cap_slider',persistence='local')]),
    html.H6('Elektolyseur-Leistung in kW: '),
    html.Div(id='electrolyseur_slider',children=dcc.Slider(min=0.5,max=2,step=0.1, id='electrolyseur_power',value=10,persistence='local')),
    #html.Div(id='pv_value'),
    ])
EFH_container_ger = dbc.Container(
                    [
                    dbc.Row(
                        [
                        dbc.Col(efh_inhalt, md=12),
                        ],
                    align="top",
                    ),
                    ],
                    fluid=True,
                    )
EFH_container_eng = dbc.Container(
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
                        dbc.Col(mfh_inhalt, md=12),
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
                        dbc.Col(industrie_inhalt, md=12),
                        ],
                    align="top",
                    ),
                    ],
                    fluid=True,
                    )

technology=html.Div(children=[html.Button(html.Div([DashIconify(icon="fa-solid:solar-panel",width=50,height=50,),html.Br(),'Photovoltaik']),id='n_solar',n_clicks=0),
        html.Button(html.Div([DashIconify(icon="mdi:gas-burner",width=50,height=50,),html.Br(),'KWK-Brenner']),id='n_chp',n_clicks=0),
        html.Button(html.Div([DashIconify(icon="mdi:heat-pump-outline",width=50,height=50,),html.Br(),'Wärmepumpe']),id='n_hp',n_clicks=0),
        html.Button(html.Div([DashIconify(icon="material-symbols:mode-heat",width=50,height=50,),html.Br(),'Gasheizung']),id='n_gas',n_clicks=0),
        html.Button(html.Div([DashIconify(icon="cil:battery-3",width=50,height=50,),html.Br(),'Batterie']),id='n_bat',n_clicks=0),
        html.Button(html.Div([DashIconify(icon="iconoir:hydrogen",width=50,height=50,),html.Br(),'H2-Speicher']),id='n_hyd',n_clicks=0),
        html.Div(id='technology')])
inhalt = html.Div(
        id='main_page',
        children=[
            dcc.Location(id='url', refresh=False),
            html.Div(
                id='app-page',
                children=html.Div(
        children=[dbc.Container(
                    [
                    dbc.Row(
                        [
                        dbc.Col(html.Div(id='scroll',className='scroll',children=[
                        dcc.Tabs(id='forna-tabs',className='forna-tabs',value='what-is', children=[
                            dcc.Tab(label='Info',value='what-is',children=[html.Div(className='control-tab', children=[
                                    html.H4(className='what-is', children='Was kann PIEG Strom Webtool?'),
                                    dcc.Markdown('''
                                    Das PIEG-Strom Webtool dient zur Hilfe bei der 
                                    Auslegung von Batteriespeichern. Nach Eingabe verschiedener
                                    Parametern werden Aussagen über die Wirtschaftlichkeit
                                    und die effektivste Speichergröße getroffen.
                                    In the "Sequences" tab, you can select which
                                    sequences will be displayed, as well as obtain
                                    information about the sequences that you have
                                    already created.
                                    In the "Colors" tab, you can choose to color each
                                    nucleotide according to its base, the structural
                                    feature to which it belongs, or its position in
                                    the sequence; you can also specify a custom color
                                    scheme.
                                    ''',id='what_is'),
                                    html.Button(html.Div([DashIconify(icon="carbon:analytics",width=100,height=100,),html.Br(),'Autarkie erhöhen']),id='autakie_click',n_clicks=0,style={'background-color': 'white','color': 'black'}),
                                    html.Button(html.Div([DashIconify(icon="carbon:chart-multi-line",width=100,height=100,),html.Br(),'Lastspitzenkappung']),id='LSK_click',n_clicks=0,style={'background-color': 'white','color': 'black'}),
                                ])]),
                            dcc.Tab(label='Parameter',className='parameter',value='parameter',),
                            dcc.Tab(id='tab_economy',label='Ökonomie', value='show-sequences',),             
                        ]),html.Div(id='humi')
                        ]),md=4),
                        dbc.Col(html.Div(id='forna-container')),
                    ],align="top",
                    ),
                    ],
                fluid=True)]))])

layout = html.Div(id='app-page-inhalt',children=[header,inhalt])
app.layout=layout


@app.callback(
    Output('forna-tabs', 'value'),
    Output('autakie_click', 'n_clicks'),
    Output('LSK_click', 'n_clicks'),
    Input('autakie_click', 'n_clicks'),
    Input('LSK_click', 'n_clicks'),
    )
def next_Tab(autarkie,LSK):
    if (autarkie==0) & (LSK==0):
        return 'what-is',0,0
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if changed_id.startswith('aut'):
        return 'parameter',1,0
    elif changed_id.startswith('LSK'):
        return 'parameter',0,1
    else:
        return 'what-is',0,0
        

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
    Output('technology','children'), 
    Input('n_solar', 'style'),
    Input('n_chp', 'style'),
    Input('n_hp', 'style'),
    Input('n_gas', 'style'),
    Input('n_bat', 'style'),
    Input('n_hyd', 'style'),
    Input('expert','n_clicks'),)
def built_technology(n_solar,n_chp,n_hp,n_gas,n_bat,n_hyd,expertmode):
    technology_list=[]
    if expertmode is None or expertmode%2==0:
        expertmode=False
    else:
        expertmode=True
    if n_solar['color']=='white':
        technology_list.append(pv_inhalt)
    if n_chp['color']=='white':
        technology_list.append(chp_inhalt)
    if n_hp['color']=='white':
        technology_list.append(hp_inhalt)
    if n_gas['color']=='white':
        technology_list.append(gas_inhalt)
    if n_bat['color']=='white':
        technology_list.append(bat_inhalt)
    if n_hyd['color']=='white':
        technology_list.append(hyd_inhalt)
    return html.Div(children=technology_list)

@app.callback(
    Output("E_bat_slider", "children"),
    Input("stromverbrauch", "value"),
    Input('button_expert','n_clicks'),)
def render_E_bat(efh,expertmode):
    if expertmode is None or expertmode%2==0:
        expertmode=False
    else:
        expertmode=True
    if int(efh/4000)==efh/4000:
        if expertmode:
            return html.Div(dcc.RangeSlider(efh/4000,efh/1000,efh/20000,value=[efh/4000,efh/1000],id='E_bat',marks={int(efh/4000):str(int(efh/4000)),int(efh/1000):str(int(efh/1000))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'))
        else:
            return html.Div(dcc.Slider(efh/4000,efh/1000,efh/20000,value=efh/2000,id='E_bat',marks={int(efh/4000):str(int(efh/4000)),int(efh/1000):str(int(efh/1000))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'))
    elif int(efh/1000)==efh/1000:
        if expertmode:
            return html.Div(dcc.RangeSlider(efh/4000,efh/1000,efh/20000,value=[efh/4000,efh/1000],id='E_bat',marks={int(efh/4000):str(int(efh/4000)),int(efh/1000):str(int(efh/1000))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'))
        else:
            return html.Div(dcc.Slider(efh/4000,efh/1000,efh/20000,value=efh/2000,id='E_bat',marks={int(efh/4000):str(int(efh/4000)),int(efh/1000):str(int(efh/1000))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'))
    else:
        if expertmode:
            return html.Div(dcc.RangeSlider(efh/4000,efh/1000,efh/20000,value=[efh/4000,efh/1000],id='E_bat',marks={(efh/4000):str((efh/4000)),(efh/1000):str((efh/1000))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'))
        else:
            return html.Div(dcc.Slider(efh/4000,efh/1000,efh/20000,value=efh/2000,id='E_bat',marks={(efh/4000):str((efh/4000)),(efh/1000):str((efh/1000))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'))
@app.callback(
    Output("P_bat_slider", "children"),
    Input("E_bat", "value"),
)
def render_E_bat(e_bat):
    if e_bat is None:
        raise PreventUpdate
    if isinstance(e_bat,list):
        return html.Div(dcc.RangeSlider(e_bat[0]/4,e_bat[1],e_bat[1]/20,value=[e_bat[0]/4,e_bat[1]],id='P_bat',marks={(e_bat[0]/4):str((e_bat[0]/4)),(e_bat[1]):str((e_bat[1]))},tooltip={"placement": "bottom", "always_visible": False}))
    return html.Div(dcc.Slider(e_bat/4,e_bat,e_bat/20,value=e_bat/2,id='P_bat',marks={(e_bat/4):str((e_bat/4)),(e_bat):str((e_bat))},tooltip={"placement": "bottom", "always_visible": False}))

@app.callback(
    Output("hyd_cap", "children"),
    Input("stromverbrauch", "value"),
    Input('expert','n_clicks'),)
def render_E_hyd(efh,expertmode):
    if expertmode is None or expertmode%2==0:
        expertmode=False
    else:
        expertmode=True
    if int(efh/8)==efh/8:
        if expertmode:
            return html.Div([dcc.RangeSlider(efh/8,efh/2,efh/40,value=[efh/8,efh/2],id='hyd_cap_slider',marks={int(efh/8):str(int(efh/8)),int(efh/2):str(int(efh/2))},tooltip={"placement": "bottom", "always_visible": False})])
        else:
            return html.Div(dcc.Slider(efh/8,efh/2,efh/40,value=efh/4,id='hyd_cap_slider',marks={int(efh/8):str(int(efh/8)),int(efh/2):str(int(efh/2))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'))
    else:
        if expertmode:
            return html.Div([dcc.RangeSlider(efh/8,efh/2,efh/40,value=[efh/8,efh/2],id='hyd_cap_slider',marks={(efh/8):str((efh/8)),int(efh/2):str(int(efh/2))},tooltip={"placement": "bottom", "always_visible": False})])
        else:
            return html.Div(dcc.Slider(efh/8,efh/2,efh/40,value=efh/4,id='hyd_cap_slider',marks={(efh/8):str((efh/8)),int(efh/2):str(int(efh/2))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'))
@app.callback(
    Output("electrolyseur_slider", "children"),
    Input("hyd_cap_slider", "value"),
)
def render_P_hyd(E_h2):
    if E_h2 is None:
        raise PreventUpdate
    try:
        E_h2_0=E_h2[0]
        E_h2_1=E_h2[1]
        if int(E_h2_0/200)==E_h2_0/200:
            if int(E_h2_1/50)==E_h2_1/50:
                return html.Div(children=[dcc.RangeSlider(E_h2_0/200,E_h2_1/50,E_h2_1/1000,id='electrolyseur_power',marks={int(E_h2_0/200):str(int(E_h2_0/200)),int(E_h2_1/50):str(int(E_h2_1/50))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'),html.Br()])
            else:
                return html.Div(children=[dcc.RangeSlider(E_h2_0/200,E_h2_1/50,E_h2_1/1000,id='electrolyseur_power',marks={int(E_h2_0/200):str(int(E_h2_0/200)),(E_h2_1/50):str((E_h2_1/50))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'),html.Br()])
        elif int(E_h2_1/50)==E_h2_1/50:
            return html.Div(children=[dcc.RangeSlider(E_h2_0/200,E_h2_1/50,E_h2_1/1000,id='electrolyseur_power',marks={(E_h2_0/200):str((E_h2_0/200)),int(E_h2_1/50):str(int(E_h2_1/50))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'),html.Br()])
        else:
            return html.Div(children=[dcc.RangeSlider(E_h2_0/200,E_h2_1/50,E_h2_1/1000,id='electrolyseur_power',marks={(E_h2_0/200):str((E_h2_0/200)),(E_h2_1/50):str((E_h2_1/50))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'),html.Br()])
    except:
        if int(E_h2/200)==E_h2/200:
            if int(E_h2/50)==E_h2/50:
                return html.Div(children=[dcc.Slider(E_h2/200,E_h2/50,E_h2/1000,value=E_h2/100,id='electrolyseur_power',marks={int(E_h2/200):str(int(E_h2/200)),int(E_h2/50):str(int(E_h2/50))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'),html.Br()])
            else:
                return html.Div(children=[dcc.Slider(E_h2/200,E_h2/50,E_h2/1000,value=E_h2/100,id='electrolyseur_power',marks={int(E_h2/200):str(int(E_h2/200)),(E_h2/50):str((E_h2/50))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'),html.Br()])
        elif int(E_h2/50)==E_h2/50:
            return html.Div(children=[dcc.Slider(E_h2/200,E_h2/50,E_h2/1000,value=E_h2/100,id='electrolyseur_power',marks={(E_h2/200):str((E_h2/200)),int(E_h2/50):str(int(E_h2/50))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'),html.Br()])
        else:
            return html.Div(children=[dcc.Slider(E_h2/200,E_h2/50,E_h2/1000,value=E_h2/100,id='electrolyseur_power',marks={(E_h2/200):str((E_h2/200)),(E_h2/50):str((E_h2/50))},tooltip={"placement": "bottom", "always_visible": False},persistence='local'),html.Br()])

@app.callback(
    Output('forna-container','children'),
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

@app.callback(
    Output("button_expert", "children"),
    Input("expert", "n_clicks"),
)
def expertmode(n1):
    if n1 is None:
        raise PreventUpdate
    if n1%2==1:
        return [DashIconify(icon="bi:toggle-on",width=100,height=30,),'Expert']
    else: 
        return [DashIconify(icon="bi:toggle-off",width=100,height=30,),'Expert']

@app.callback(
    Output("button_language", "children"),
    Output("app-title",'children'),
    Output("tab_economy",'label'),
    Input("language", "n_clicks"),
)
def language(n1):
    if n1 is None:
        raise PreventUpdate
    if n1%2==0:
        return [DashIconify(icon="emojione:flag-for-united-kingdom",width=30,height=30,),'Language'],[html.H4("PIEG-Strom Webtool"),html.P("Auslegung von Batteriespeichern")],'Ökonomie'
    else: 
        return [DashIconify(icon="emojione:flag-for-germany",width=30,height=30,),'Sprache'],[html.H4("PIEG-Strom Webtool"),html.P("Design of battery storage systems")],'Economy'
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output('bulding_container','children'),
    Output('efh_click', 'style'), 
    Output('mfh_click', 'style'), 
    Output('industry_click', 'style'), 
    Input('efh_click','n_clicks'),
    Input('mfh_click','n_clicks'),
    Input('industry_click','n_clicks'),
    Input('language','n_clicks'),
)
def getcontainer(efh_click,mfh_click,industy_click,n_language):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if changed_id.startswith('efh'):
        if n_language is None or n_language%2==0:
            return EFH_container_ger,{'background-color': '#212529','color': 'white',},{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'}
        else:
            return EFH_container_eng,{'background-color': '#212529','color': 'white',},{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'}
    elif changed_id.startswith('mfh'):
        return MFH_container,{'background-color': 'white','color': 'black'},{'background-color': '#212529','color': 'white',},{'background-color': 'white','color': 'black'}
    elif changed_id.startswith('industry'):
        return Industrie_container,{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'},{'background-color': '#212529','color': 'white',}
    else:
        return 'Ein Gebäudetyp wählen',{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'},{'background-color': 'white','color': 'black'}

@app.callback(
    Output("humi", "children"),
    Input("forna-tabs", "value"),
    State('LSK_click','n_clicks'),
    Input('language','n_clicks'),
)
def render_inhalt(tab,LSK,n_language):
    if tab=='parameter':
        if LSK==0:
            if n_language is None or n_language%2==0:
                return html.Div(className='para',id='para',children=[
                            html.Div(html.H3('Gebäudewahl:'),
                            ),
                            html.Button(html.Div([DashIconify(icon="clarity:home-solid",width=50,height=50,),html.Br(),'Einfamilienhaus'],style={"width":'20vh'}),id='efh_click',n_clicks=0),
                            html.Button(html.Div([DashIconify(icon="bxs:building-house",width=50,height=50,),html.Br(),'Mehrfamilienhaus'],style={"width":'20vh'}),id='mfh_click',n_clicks=0),
                            html.Button(html.Div([DashIconify(icon="la:industry",width=50,height=50,),html.Br(),'Industriegebäude'],style={"width":'20vh'}),id='industry_click',n_clicks=0),
                            html.Div(id='bulding_container'),
                            html.Br(),
                            html.Div(html.H3('Technologiewahl:')),
                            html.Div(technology),
                            ]),
            else:
                return html.Div(className='para',id='para',children=[
                            html.Div(html.H3('Building selection:'),
                            ),
                            html.Button(html.Div([DashIconify(icon="clarity:home-solid",width=50,height=50,),html.Br(),'Single family house'],style={"width":'20vh'}),id='efh_click',n_clicks=0),
                            html.Button(html.Div([DashIconify(icon="bxs:building-house",width=50,height=50,),html.Br(),'Apartment house'],style={"width":'20vh'}),id='mfh_click',n_clicks=0),
                            html.Button(html.Div([DashIconify(icon="la:industry",width=50,height=50,),html.Br(),'Industry building'],style={"width":'20vh'}),id='industry_click',n_clicks=0),
                            html.Div(id='bulding_container'),
                            html.Br(),
                            html.Div(html.H3('Technology selection:')),
                            html.Div(technology),
                            ]),
        else:
            return html.Div(children='LSK')
    elif tab=='show-sequences':
        return html.Div(className='control-tab', children=[
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
    else:
        return html.Div()

if __name__ == '__main__':
    app.run_server(debug=True)