import pandas as pd
from hplib import hplib as hpl
from bslib import bslib as bsl
import numpy as np
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

# Thermal storage
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

# Calculation of photovoltaic ac power time series
# normalized to 1 kWp with 1 kW inverter
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
    # run calculation
    mc_sys_s.run_model(mc_sys_s.results.weather)
    return mc_sys_s.results.ac.values.tolist()

# Calculation of battery storage
# inverter = 0.5 kW per kWh useable capacity
def calc_bs(df, e_bat):
    # define 5 steps for battery sizes
    batteries = pd.DataFrame([['SG1', 0.0, 0.0],
                            ['SG1', e_bat*1/5,e_bat*1/10],
                            ['SG1', e_bat*2/5, e_bat*2/10],
                            ['SG1', e_bat*3/5, e_bat*3/10],
                            ['SG1', e_bat*4/5, e_bat*4/10],
                            ['SG1', e_bat, e_bat*5/10]],
                            columns=['system_id', 'e_bat', 'p_inv']
                            )
    P_diff=df['p_PV']+df['p_chp']-df['p_el_hh']
    dt=900
    A=[]
    E=[]
    E_GS=[]
    E_GF=[]
    E_GF_CHP=[]
    E_GF_PV=[]
    for idx in batteries.index:
        BAT_soc = []
        BAT_P_bs = []
        BAT = bsl.ACBatMod(system_id=batteries['system_id'][idx],
                                    p_inv_custom=batteries['p_inv'][idx]*1000,
                                    e_bat_custom=batteries['e_bat'][idx])
        if batteries['e_bat'][idx] == 0.0:
            P_gs = np.minimum(0.0, P_diff)
            P_gf = np.maximum(0.0, P_diff)
            P_gf_chp = np.minimum(P_gf, df['p_chp'].values)
            P_gf_pv = np.maximum(0.0, (P_gf-P_gf_chp))
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
            P_gf_chp = np.minimum(P_gf, df['p_chp'].values)
            P_gf_pv = np.maximum(0.0, (P_gf-P_gf_chp))
        a=1-((P_gs.mean()*-8.76)/(df['p_el_hh'].mean()*8.76))
        e=((df['p_PV'].mean()*8.76)-(P_gf.mean()*8.76))/(df['p_PV'].mean()*8.76)
        A.append(a)
        E.append(e)
        E_GS.append(P_gs.mean()*8.76)
        E_GF.append(P_gf.mean()*8.76)
        E_GF_CHP.append(P_gf_chp.mean()*8.76)
        E_GF_PV.append(P_gf_pv.mean()*8.76)
    batteries['Netzeinspeisung']=E_GF
    batteries['Netzeinspeisung_PV']=E_GF_PV
    batteries['Netzeinspeisung_CHP']=E_GF_CHP
    batteries['Netzbezug']=E_GS
    batteries['Autarkiegrad']=A
    batteries['Eigenverbrauch']=E
    batteries['Autarkiegrad ohne Stromspeicher']=round((batteries['Autarkiegrad']*100).values[0],2)
    batteries['Eigenverbrauch ohne Stromspeicher']=round((batteries['Eigenverbrauch']*100).values[0],2)
    batteries['Erhöhung der Autarkie durch Stromspeicher']=((batteries['Autarkiegrad']*100)-batteries['Autarkiegrad ohne Stromspeicher']).round(2)
    batteries['Erhöhung des Eigenverbrauchs durch Stromspeicher']=((batteries['Eigenverbrauch']*100)-batteries['Eigenverbrauch ohne Stromspeicher']).round(2)
    return batteries

# Calculation of heat pump
def calc_hp(building, p_th_load, group_id, t_room=20, T_sp_tww_set=50):
    # read load and weather
    weather = pd.read_csv('src/assets/data/weather/TRY_'+building['location']+'_a_2015_15min.csv', header=0, index_col=0)
    p_th_load=pd.DataFrame(p_th_load)
    P_th_tww = p_th_load['load [W]']
    P_th_h = p_th_load['p_th_heating [W]']
    # set parameter
    P_tww = 1000+200*building['Inhabitants']    # additional heating load for DHW in W 1000 W + 200 W/person
    dt = 900                                    # time step size in s 
    T_hyst = 3                                  # hysteresis temperatur for thermal storage

    # Maximm heat load including additional power for DHW
    P_th_max=(t_room - building['T_min_ref']) * building['Q_sp'] * building['Area'] + P_tww
 
    # Thermal storages
    HeatStorage_h = HeatStorage(Volume=100+20*P_th_max/1000, ambient_temperature=15)                # Heizungspuffer 100l + 20 l/kW
    HeatStorage_tww = HeatStorage(Volume=200+50*building['Inhabitants'], ambient_temperature=15)    # TWW-Speicher 200l + 50 l/person

    # Define heating system set temperatures 
    HS = hpl.HeatingSystem(t_outside_min=building['T_min_ref'],
                            t_inside_set=t_room,
                            t_hs_set=[building['T_vl_max'],
                            building['T_rl_max']],
                            f_hs_exp=building['f_hs_exp'])
    
    # Define generic heat pump
    if group_id == 1 or group_id == 4:
        t_in = -7 #building['T_min_ref']
    else:
        t_in = 0
    t_out=building['T_vl_max']
    para = hpl.get_parameters(model='Generic',
                            group_id=group_id,
                            t_in=t_in,
                            t_out=t_out,
                            p_th=P_th_max)
    HeatPump = hpl.HeatPump(para)
    
    # Prepare simulation loop with start conditions
    T_sp_h = building['T_vl_max']   # temperature of thermal heat storage
    T_sp_tww = 50                   # temperature of DHW het storage
    P_hp_h_th = 0                   # thermal power of heat pump for heating
    P_hp_tww_th = 0                 # thermal power of heat pump for DHW
    hyst_h = 0                      # hysteresis-switch for heating
    hyst_tww = 0                    # hysteresis-switch for DHW
    runtime = 0                     # runtime of heat pump per on/off cycle
    runtime_tot = 0                 # runtime of heat pump in total
    i=0
    # Dateframe for time series
    results_timeseries = pd.DataFrame()
    # Timeseries results
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
        # Set temperatures
        T_sp_tww_set = T_sp_tww_set
        T_vl = HS.calc_heating_dist_temp(
            weather.at[t, 'temperature 24h [degC]'])[0]
        T_rl = HS.calc_heating_dist_temp(
            weather.at[t, 'temperature 24h [degC]'])[1]
        T_sp_h_set = T_vl

        # Loads
        P_load_tww_th = P_th_tww[i]
        P_load_h_th = P_th_h[i]
        if P_load_h_th > 0 or P_load_tww_th > 0:
            runtime_tot = runtime_tot+dt

        # Calculate primary input temperatures for heat pump
        T_hp_brine = HS.calc_brine_temp(
            weather.at[t, 'temperature 24h [degC]'])
        T_amb = weather.at[t, 'temperature [degC]']
        T_amb_24h = weather.at[t, 'temperature 24h [degC]']
        if group_id == 1 or group_id == 4:
            T_hp_in = T_amb
        else:
            T_hp_in = T_hp_brine

        # DHW control
        if T_sp_tww < T_sp_tww_set and hyst_tww == 0:
            hyst_tww = 1
        if T_sp_tww < T_sp_tww_set+T_hyst and hyst_tww == 1:
            HP_tww = HeatPump.simulate(t_in_primary=T_hp_in,
                                        t_in_secondary=T_sp_tww,
                                        t_amb=T_amb_24h)
            P_hp_tww_th = HP_tww['P_th']
            P_hp_tww_el = HP_tww['P_el']
            cop_tww = HP_tww['COP']
            runtime = runtime+dt
        else:
            hyst_tww = 0
            P_hp_tww_th = 0
            P_hp_tww_el = 0
            cop_tww = 0

        # Calculate DHW heat storage temperature
        T_sp_tww = HeatStorage_tww.calculate_new_storage_temperature(T_sp=T_sp_tww,
                                                                        dt=dt,
                                                                        P_hp=P_hp_tww_th,
                                                                        P_ld=P_load_tww_th)
        if T_sp_tww < T_sp_tww_set-5:
            T_sp_tww = T_sp_tww + \
                (1/(HeatStorage_tww.V_sp*HeatStorage_tww.c_w)
                    ) * P_th_max * dt
            P_HEIZSTAB_tww.append(P_th_max)
        else:
            P_HEIZSTAB_tww.append(0)

        # Heating control
        if T_sp_h < T_sp_h_set and hyst_h == 0 and hyst_tww == 0:
            hyst_h = 1
        if T_sp_h < T_sp_h_set+T_hyst and hyst_h == 1 and hyst_tww == 0:
            HP_h = HeatPump.simulate(t_in_primary=T_hp_in,
                                        t_in_secondary=T_sp_h,
                                        t_amb=T_amb_24h)
            P_hp_h_th = HP_h['P_th']
            P_hp_h_el = HP_h['P_el']
            cop_h = HP_h['COP']
            # Check for regulated heat pumps if output power is enough
            if P_load_h_th > 0:
                f_power = (P_hp_h_th / (P_load_h_th + 500))
            else:
                f_power = 1
            if f_power < 1:
                P_hp_h_th = (P_hp_h_th / f_power) * 1.1
                P_hp_h_el = (P_hp_h_el / f_power) * 1.1
            runtime = runtime+dt
        else:
            hyst_h = 0
            P_hp_h_th = 0
            P_hp_h_el = 0
            cop_h = 0

        # Calculate thermal heat storage temperature
        T_sp_h = HeatStorage_h.calculate_new_storage_temperature(T_sp=T_sp_h,
                                                                    dt=dt,
                                                                    P_hp=P_hp_h_th,
                                                                    P_ld=P_load_h_th)
        if T_sp_h < T_sp_h_set-7:
            T_sp_h = T_sp_h + \
                (1/(HeatStorage_h.V_sp*HeatStorage_h.c_w)) * \
                P_th_max * dt
            P_HEIZSTAB_h.append(P_th_max)
        else:
            P_HEIZSTAB_h.append(0)

        # Save data to time series
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
    
    # After simulation loop: save to data frame 
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
    # check fraction of electric emergency heater 
    frac_heater_h = results_timeseries['P_Heizstab_h'].mean()*8.76/(results_timeseries['P_Heizstab_h'].mean()*8.76+results_timeseries['P_hp_h_th'].mean()*8.76)*100
    frac_heater_tww = results_timeseries['P_Heizstab_tww'].mean()*8.76/(results_timeseries['P_Heizstab_tww'].mean()*8.76+results_timeseries['P_hp_tww_th'].mean()*8.76)*100
    # TODO JAZ und Anteil Heizstab TWW / Heizung
    return results_timeseries , P_th_max, t_in, t_out

# Calculation of combined heat and power
def calc_chp(building, p_th_load, power_to_heat_ratio, chp_to_peak_ratio=0.3, t_room=20, T_sp_tww_set=50):
    # read load and weather
    weather = pd.read_csv('src/assets/data/weather/TRY_'+building['location']+'_a_2015_15min.csv', header=0, index_col=0)
    p_th_load=pd.DataFrame(p_th_load)
    P_th_tww = p_th_load['load [W]']
    P_th_h = p_th_load['p_th_heating [W]']
    # set parameter
    P_tww = 1000+200*building['Inhabitants']    # additional heating load for DHW in W 1000 W + 200 W/person
    dt = 900                                    # time step size in s 
    T_hyst = 3                                  # hysteresis temperatur for thermal storage

    # Maximm heat load including additional power for DHW
    P_th_max=(t_room - building['T_min_ref']) * building['Q_sp'] * building['Area'] + P_tww
 
    # Thermal storages
    HeatStorage_h = HeatStorage(Volume=100+20*P_th_max/1000, ambient_temperature=15)                # Heizungspuffer 100l + 20 l/kW
    HeatStorage_tww = HeatStorage(Volume=200+50*building['Inhabitants'], ambient_temperature=15)    # TWW-Speicher 200l + 50 l/person

    # Define heating system set temperatures 
    HS = hpl.HeatingSystem(t_outside_min=building['T_min_ref'],
                            t_inside_set=t_room,
                            t_hs_set=[building['T_vl_max'],
                            building['T_rl_max']],
                            f_hs_exp=building['f_hs_exp'])

    # Define CHP and gas heater values
    P_th_peak = P_th_max
    P_th_chp = P_th_peak * chp_to_peak_ratio
    P_el_chp = P_th_chp * power_to_heat_ratio
    
    # Prepare simulation loop with start conditions
    T_sp_h = building['T_vl_max']   # temperature of thermal heat storage
    T_sp_tww = 50                   # temperature of DHW het storage
    P_chp_h_th = 0                   # thermal power of heat pump for heating
    P_chp_tww_th = 0                 # thermal power of heat pump for DHW
    hyst_h = 0                      # hysteresis-switch for heating
    hyst_tww = 0                    # hysteresis-switch for DHW
    runtime = 0                     # runtime of heat pump per on/off cycle
    runtime_tot = 0                 # runtime of heat pump in total
    i=0
    # Dateframe for time series
    results_timeseries = pd.DataFrame()
    # Timeseries results
    T_SP_h = []
    T_SP_h_set = []
    T_SP_tww = []
    P_LOAD_h = []
    P_LOAD_tww = []
    P_CHP_h_th = []
    P_CHP_tww_th = []
    P_CHP_h_el = []
    P_CHP_tww_el = []
    P_PEAK_h = []
    P_PEAK_tww = []
    T_AMB_avg_24h = []
    for t in weather.index:
        # Set temperatures
        T_sp_tww_set = T_sp_tww_set
        T_vl = HS.calc_heating_dist_temp(
            weather.at[t, 'temperature 24h [degC]'])[0]
        T_rl = HS.calc_heating_dist_temp(
            weather.at[t, 'temperature 24h [degC]'])[1]
        T_sp_h_set = T_vl

        # Loads
        P_load_tww_th = P_th_tww[i]
        P_load_h_th = P_th_h[i]
        if P_load_h_th > 0 or P_load_tww_th > 0:
            runtime_tot = runtime_tot+dt

        # DHW control
        if T_sp_tww < T_sp_tww_set and hyst_tww == 0:
            hyst_tww = 1
        if T_sp_tww < T_sp_tww_set+T_hyst and hyst_tww == 1:
            P_chp_tww_th = P_th_chp
            P_chp_tww_el = P_el_chp
            runtime = runtime+dt
        else:
            hyst_tww = 0
            P_chp_tww_th = 0
            P_chp_tww_el = 0

        # Calculate DHW heat storage temperature
        T_sp_tww = HeatStorage_tww.calculate_new_storage_temperature(T_sp=T_sp_tww,
                                                                        dt=dt,
                                                                        P_hp=P_chp_tww_th,
                                                                        P_ld=P_load_tww_th)
        if T_sp_tww < T_sp_tww_set-5:
            T_sp_tww = T_sp_tww + \
                (1/(HeatStorage_tww.V_sp*HeatStorage_tww.c_w)
                    ) * P_th_peak * dt
            P_PEAK_tww.append(P_th_peak)
        else:
            P_PEAK_tww.append(0)

        # Heating control
        if T_sp_h < T_sp_h_set and hyst_h == 0 and hyst_tww == 0:
            hyst_h = 1
        if T_sp_h < T_sp_h_set+T_hyst and hyst_h == 1 and hyst_tww == 0:
            P_chp_h_th = P_th_chp
            P_chp_h_el = P_el_chp
            runtime = runtime+dt
        else:
            hyst_h = 0
            P_chp_h_th = 0
            P_chp_h_el = 0

        # Calculate thermal heat storage temperature
        T_sp_h = HeatStorage_h.calculate_new_storage_temperature(T_sp=T_sp_h,
                                                                    dt=dt,
                                                                    P_hp=P_chp_h_th,
                                                                    P_ld=P_load_h_th)
        if T_sp_h < T_sp_h_set-7:
            T_sp_h = T_sp_h + \
                (1/(HeatStorage_h.V_sp*HeatStorage_h.c_w)) * \
                P_th_peak * dt
            P_PEAK_h.append(P_th_peak)
        else:
            P_PEAK_h.append(0)

        # Save data to time series
        T_SP_h.append(T_sp_h)
        T_SP_h_set.append(T_sp_h_set)
        T_AMB_avg_24h.append(weather.at[t, 'temperature 24h [degC]'])
        T_SP_tww.append(T_sp_tww)
        P_LOAD_h.append(P_load_h_th)
        P_LOAD_tww.append(P_load_tww_th)
        P_CHP_h_th.append(P_chp_h_th)
        P_CHP_tww_th.append(P_chp_tww_th)
        P_CHP_h_el.append(P_chp_h_el)
        P_CHP_tww_el.append(P_chp_tww_el)
        i+=1
    
    # After simulation loop: save to data frame 
    results_timeseries['T_sp_h'] = T_SP_h
    results_timeseries['T_sp_h_set'] = T_SP_h_set
    results_timeseries['T_amb_avg_24h'] = T_AMB_avg_24h
    results_timeseries['T_sp_tww'] = T_SP_tww
    results_timeseries['P_load_h'] = P_LOAD_h
    results_timeseries['P_load_tww'] = P_LOAD_tww
    results_timeseries['P_chp_h_th'] = P_CHP_h_th
    results_timeseries['P_chp_tww_th'] = P_CHP_tww_th
    results_timeseries['P_chp_h_el'] = P_CHP_h_el
    results_timeseries['P_peak_h'] = P_PEAK_h
    results_timeseries['P_chp_tww_el'] = P_CHP_tww_el
    results_timeseries['P_peak_tww'] = P_PEAK_tww

    # Laufzeit in h
    runtime = runtime / 3600

    # TODO Laufzeit bzw. Vollbenutzungsstunden mit ausgeben
    return results_timeseries, P_th_max, P_th_chp, P_el_chp, runtime