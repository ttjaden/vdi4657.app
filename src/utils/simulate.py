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

