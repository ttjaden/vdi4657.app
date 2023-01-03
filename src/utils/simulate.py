import pandas as pd
from hplib import hplib as hpl
from bslib import bslib as bsl
import numpy as np
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS


def calc_pv(trj, year, type, tilt, orientation):
    locations=pd.read_csv('src/assets/data/weather/TRJ-Tabelle.csv')
    location = Location(locations['lat'][trj], locations['lon'][trj],'Europe/Berlin', locations['height'][trj], locations['station'][trj])
    module_parameters = dict(pdc0=1000, gamma_pdc=-0.003)
    inverter_parameters = dict(pdc0=1000*0.96)
    temperature_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_polymer']
    sys_s = PVSystem(surface_tilt=tilt, surface_azimuth=orientation,
            module_parameters=module_parameters,
            inverter_parameters=inverter_parameters,
            temperature_model_parameters=temperature_parameters)
    mc_sys_s = ModelChain.with_pvwatts(sys_s, location, name=locations['station'][trj]+'_Süd')
    weather_csv = pd.read_csv('src/assets/data/weather/TRY_'+str(locations['TRY'][trj])+'_'+type+'_'+str(year)+'_15min.csv', header=0, index_col=0)
    weather = pd.concat([weather_csv['synthetic global irradiance [W/m^2]'],
                        weather_csv['synthetic diffuse irradiance [W/m^2]'],
                        weather_csv['wind speed [m/s]'],
                        weather_csv['temperature [degC]']],
                        axis=1, keys=['ghi', 'dhi', 'wind_speed', 'temp_air'])
    if year==2015:
        weather.index = pd.date_range(
            '2015-01-01 00:00', '2015-12-31 23:59', freq='15min', tz="Europe/Berlin")
    else:
        weather.index = pd.date_range(
            '2045-01-01 00:00', '2045-12-31 23:59', freq='15min', tz="Europe/Berlin")
    mc_sys_s.complete_irradiance(weather)
    # PV Simulation durchführen und Zeitreihen abspeichern
    mc_sys_s.run_model(mc_sys_s.results.weather)
    return mc_sys_s.results.ac.values.tolist()

def calc_bat(df, bat_size):
    batteries = pd.DataFrame([['SG1', 0.0, 0.0],['SG1', bat_size/5,bat_size/10],['SG1', bat_size*2/5, bat_size*2/10],['SG1', bat_size*3/5, bat_size*3/10],['SG1', bat_size*4/5, bat_size*4/10],['SG1', bat_size, bat_size/2]],
                            columns=['system_id', 'e_bat', 'p_inv']
                            )
    P_diff=df['p_PV']-df['p_el_hh']
    dt=900
    A=[]
    E=[]
    E_GS=[]
    E_GF=[]
    for idx in batteries.index:
        BAT_soc = []
        BAT_P_bs = []
        BAT = bsl.ACBatMod(system_id=batteries['system_id'][idx],
                                    p_inv_custom=batteries['p_inv'][idx]*1000,
                                    e_bat_custom=batteries['e_bat'][idx])
        if batteries['e_bat'][idx] == 0.0:
            P_gs = np.minimum(0.0, P_diff)
            P_gf = np.maximum(0.0, P_diff)
        else:
            res = BAT.simulate(p_load=0, soc=0, dt=dt)
            for p_diff in P_diff:
                res = BAT.simulate(p_load=p_diff, soc=res[2], dt=dt)
                BAT_soc.append(res[2])
                BAT_P_bs.append(res[0])
            BAT_soc=np.asarray(BAT_soc)
            BAT_P_bs=np.asarray(BAT_P_bs)
            P_gs = np.minimum(0.0, (P_diff-BAT_P_bs))
            P_gf = np.maximum(0.0, (P_diff-BAT_P_bs))
        a=1-((P_gs.mean()*-8.76)/(df['p_el_hh'].mean()*8.76))
        e=((df['p_PV'].mean()*8.76)-(P_gf.mean()*8.76))/(df['p_PV'].mean()*8.76)
        A.append(a)
        E.append(e)
        E_GS.append(P_gs.mean()*8.76)
        E_GF.append(P_gf.mean()*8.76)
    batteries['A']=A
    batteries['E']=E
    batteries['E_gf']=E_GF
    batteries['E_gs']=E_GS
    return batteries

class HeatStorage():
    def __init__(self,
                 Volume= 1000, #in l
                 ambient_temperature = 15,
                 c_w=4180):
        self.V_sp=Volume
        self.c_w=c_w
        self.T_amb=ambient_temperature
    def calculate_new_storage_temperature(self, T_sp, dt, P_hp, P_ld):
        P_loss=0.0038 *self.V_sp + 0.85
        T_sp=T_sp + (1/(self.V_sp*self.c_w))*(P_hp - P_ld - P_loss*(T_sp-self.T_amb))*dt
        return T_sp

def sim_hp(location, Area, building, group_id, t_room=20):
    # Feste Parameter
    P_tww = 1000        # Heizlast-Aufschlag für Trinkwarmwasser in W
    E_th_tww = 1875     # Wärmebedarf Trinkwarmwasser in kWh/a
    dt = 900            # Zeitschrittweite in s
    T_hyst = 3          # Hysterese-Temperatur in thermischen Speichern
    # Wärmespeicher
    HeatStorage_h = HeatStorage(Volume=300, ambient_temperature=15)  # Heizungspuffer
    HeatStorage_tww = HeatStorage(Volume=300, ambient_temperature=15)  # TWW-Speicher

    # Gebäude-Klassen
    Heizlast=pd.read_csv('src/assets/data/weather/TRJ-Tabelle.csv')
    P_th_max=(t_room - Heizlast['T_min_ref'][location-1]) * building['Q_sp'] * Area + P_tww
    HS = hpl.HeatingSystem(t_outside_min=Heizlast['T_min_ref'][location-1],
                                            t_inside_set=t_room,
                                            t_hs_set=[building['T_vl_max'],
                                                    building['T_rl_max']],
                                            f_hs_exp=building['f_hs_exp'])
    if group_id == 1 or group_id == 4:
        t_in = -7  # locations['T_min_ref'][index]
    else:
    # HS.calc_brine_temp(locations['T_min_ref'][index])
        t_in = 0
    t_out=building['T_vl_max']
    para = hpl.get_parameters(model='Generic',
                            group_id=group_id,
                            t_in=t_in,
                            t_out=t_out,
                            p_th=P_th_max)
    HeatPump = hpl.HeatPump(para)
    load_building=[]
    weather = pd.read_csv('src/assets/data/weather/TRY_'+str(location)+'_a_2015_15min.csv', header=0, index_col=0)
    for t in weather.index:
    # gleitender Tagesmittelwert und neue Berechnung der Heizlast
        temp = weather.at[t, 'temperature 24h [degC]']
        if temp < building['T_limit']:
            load_building.append((t_room - temp) * building['Q_sp'] * Area)
        else:
            load_building.append(0)
    # Simulations-Schleife
    # Temperatur beim Start in °C
    T_sp_h = building['T_vl_max']
    T_sp_tww = 50  # Temperatur beim Start in °C
    P_hp_h = 0  # Leistung der Wärmepumpe für Heizung beim Start in W
    P_hp_tww = 0  # Leistung der Wärmepumpe für TWW beim Start in W
    hyst_h = 0  # Hysterese-Schalter Heizung
    hyst_tww = 0  # Hysterese-Schalter Trinkwarmwasser
    runtime = 0  # Laufzeit der Wärmepumpe
    heizlänge = 0  # Länge von Load
    E_heizstab_tww_storage = 0  # Energie vom Heizstab im Tww-Storage
    E_heizstab_h_storage = 0  # Energie vom Heizstab im Heating-Storage
    i=0
    # Ergebnis DataFrame Zeitreihen
    results_timeseries = pd.DataFrame()

    # Timeseries Results
    T_SP_h = []
    T_SP_h_set = []
    T_SP_tww = []
    P_LOAD_h = []
    P_LOAD_tww = []
    P_HP_h_th = []
    P_HP_tww_th = []
    P_HP_h_el = []
    P_HP_tww_el = []
    P_HEIZSTAB_h = []
    P_HEIZSTAB_tww = []
    COP_h = []
    COP_tww = []
    T_HP_in = []
    T_AMB_avg_24h = []

    for t in weather.index:
        # Soll-Temperaturen
        T_sp_tww_set = 47
        T_vl = HS.calc_heating_dist_temp(
            weather.at[t, 'temperature 24h [degC]'])[0]
        T_rl = HS.calc_heating_dist_temp(
            weather.at[t, 'temperature 24h [degC]'])[1]
        T_sp_h_set = T_vl

        # Lasten
        P_load_tww_th = 0
        P_load_h_th = load_building[i]
        if P_load_h_th > 0 or P_load_tww_th > 0:
            heizlänge = heizlänge+1/60
        # HP inflow Temperatur berechnen
        T_hp_brine = HS.calc_brine_temp(
            weather.at[t, 'temperature 24h [degC]'])
        T_amb = weather.at[t, 'temperature [degC]']
        T_amb_24h = weather.at[t, 'temperature 24h [degC]']
        if group_id == 1 or group_id == 4:
            T_hp_in = T_amb
        else:
            T_hp_in = T_hp_brine
        # Trinkwarmwasser: Regelung
        if T_sp_tww < T_sp_tww_set and hyst_tww == 0:
            hyst_tww = 1
        if T_sp_tww < T_sp_tww_set+T_hyst and hyst_tww == 1:
            HP_tww = HeatPump.simulate(t_in_primary=T_hp_in,
                                        t_in_secondary=T_sp_tww,
                                        t_amb=T_amb_24h)
            P_hp_tww_th = HP_tww['P_th']
            P_hp_tww_el = HP_tww['P_el']
            cop_tww = HP_tww['COP']
            runtime = runtime+1
        else:
            hyst_tww = 0
            P_hp_tww_th = 0
            P_hp_tww_el = 0
            cop_tww = 0

        # Trinkwarmwasser: Speichertemperatur
        T_sp_tww = HeatStorage_tww.calculate_new_storage_temperature(T_sp=T_sp_tww,
                                                                        dt=dt,
                                                                        P_hp=P_hp_tww_th,
                                                                        P_ld=P_load_tww_th)
        if T_sp_tww < T_sp_tww_set-5:
            E_heizstab_tww_storage = E_heizstab_tww_storage + P_th_max / 60
            T_sp_tww = T_sp_tww + \
                (1/(HeatStorage_tww.V_sp*HeatStorage_tww.c_w)
                    ) * P_th_max * dt
            P_HEIZSTAB_tww.append(P_th_max)
        else:
            P_HEIZSTAB_tww.append(0)

        # Heizung: Regelung
        if T_sp_h < T_sp_h_set and hyst_h == 0 and hyst_tww == 0:
            hyst_h = 1

        if T_sp_h < T_sp_h_set+T_hyst and hyst_h == 1 and hyst_tww == 0:

            HP_h = HeatPump.simulate(t_in_primary=T_hp_in,
                                        t_in_secondary=T_sp_h,
                                        t_amb=T_amb_24h)

            P_hp_h_th = HP_h['P_th']
            P_hp_h_el = HP_h['P_el']
            cop_h = HP_h['COP']

            if P_load_h_th > 0:
                f_power = (P_hp_h_th / (P_load_h_th + 500))
            else:
                f_power = 1

            if f_power < 1:
                P_hp_h_th = (P_hp_h_th / f_power) * 1.1
                P_hp_h_el = (P_hp_h_el / f_power) * 1.1

            runtime = runtime+1

        else:
            hyst_h = 0
            P_hp_h_th = 0
            P_hp_h_el = 0
            cop_h = 0
            T_delta = 0

        # Heizung: Speichertemperaturen
        T_sp_h = HeatStorage_h.calculate_new_storage_temperature(T_sp=T_sp_h,
                                                                    dt=dt,
                                                                    P_hp=P_hp_h_th,
                                                                    P_ld=P_load_h_th)
        if T_sp_h < T_sp_h_set-5:
            E_heizstab_h_storage = E_heizstab_h_storage + P_th_max / 60
            T_sp_h = T_sp_h + \
                (1/(HeatStorage_h.V_sp*HeatStorage_h.c_w)) * \
                P_th_max * dt
            P_HEIZSTAB_h.append(P_th_max)
        else:
            P_HEIZSTAB_h.append(0)

        # Abspeichern relevanter Werte
        T_SP_h.append(T_sp_h)
        T_SP_h_set.append(T_sp_h_set)
        T_HP_in.append(T_hp_in)
        T_AMB_avg_24h.append(weather.at[t, 'temperature 24h [degC]'])
        T_SP_tww.append(T_sp_tww)
        P_LOAD_h.append(P_load_h_th)
        P_LOAD_tww.append(P_load_tww_th)
        P_HP_h_th.append(P_hp_h_th)
        P_HP_tww_th.append(P_hp_tww_th)
        P_HP_h_el.append(P_hp_h_el)
        P_HP_tww_el.append(P_hp_tww_el)
        COP_h.append(cop_h)
        COP_tww.append(cop_tww)
        i+=1

    results_timeseries['T_sp_h'] = T_SP_h
    results_timeseries['T_sp_h_set'] = T_SP_h_set
    results_timeseries['T_hp_in'] = T_HP_in
    results_timeseries['T_amb_avg_24h'] = T_AMB_avg_24h
    results_timeseries['T_sp_tww'] = T_SP_tww
    results_timeseries['P_load_h'] = P_LOAD_h
    results_timeseries['P_load_tww'] = P_LOAD_tww
    results_timeseries['P_hp_h_th'] = P_HP_h_th
    results_timeseries['P_hp_tww_th'] = P_HP_tww_th
    results_timeseries['P_hp_h_el'] = P_HP_h_el
    results_timeseries['P_Heizstab_h'] = P_HEIZSTAB_h
    results_timeseries['P_hp_tww_el'] = P_HP_tww_el
    results_timeseries['P_Heizstab_tww'] = P_HEIZSTAB_tww
    results_timeseries['COP_h'] = COP_h
    results_timeseries['COP_tww'] = COP_tww
    return results_timeseries , P_th_max, t_in, t_out