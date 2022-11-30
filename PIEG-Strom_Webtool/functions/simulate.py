import pandas as pd
from hplib import hplib as hpl
import src.heatstorage as hs
from bslib import bslib as bsl
import numpy as np


def simulate(standort, E_gas, T_vorlauf, n_Personen, eff_tww, Baujahr, wp_model, pv_kwp ,pv_orientation):
    TRJ=pd.read_csv('src/simulation_data/TRJ-Tabelle.csv').head(15)# average year
    weather=pd.read_csv('src/simulation_data/weather/weather_'+str(standort)+'_a_2015_1min.csv') 
    photovoltaic = pd.read_csv('src/simulation_data/pv/pv_' + str(standort)+'_a_2015_1min.csv', header=0, index_col=0)
    photovoltaic=photovoltaic*pv_kwp
    P_el_hh=pd.read_csv('src/simulation_data/electrical_load/existing_house.csv')
    P_tww_load=pd.read_csv('src/simulation_data/dhw_load/dhw_'+str(n_Personen)+'.csv',index_col=0)
    P_tww_load.index=weather.index
    #calc loads 
    eff_heiz=0.9                #average from DIN EN 12831 Tabelle 38

    if Baujahr<=2000:           
        if Baujahr<=1995:
            eff_heiz=0.85       #average from DIN EN 12831 Tabelle 38
        Heizgrenztemperatur=15  #IWU Heizgrenztemperatur 
        gtz=TRJ.iloc[standort-1,11]
    elif Baujahr>2015:
        Heizgrenztemperatur=10
        gtz=TRJ.iloc[standort-1,12]
        P_el_hh=pd.read_csv('src/simulation_data/electrical_load/low_energy_house.csv')
    else:
        Heizgrenztemperatur=12
        gtz=TRJ.iloc[standort-1,10]
    E_TWW=(14.9*30*n_Personen)/eff_tww
    E_Heiz=(E_gas-E_TWW)* eff_heiz * 1000
    P_tww_load['load [W]']=P_tww_load['load [W]']+((E_TWW)-((P_tww_load.mean()*8.76)[1]))/8.76 #calibrate to calculated consumption
    #define simulation parameters
    HeatPump = hpl.HeatPump(hpl.get_parameters(wp_model))
    group_id=HeatPump.group_id
    P_th_ref=HeatPump.p_th_ref
    if T_vorlauf<55:
        t_hs_set=0.85*T_vorlauf-1.75
        f_hs_exp=1.1
    else:
        t_hs_set=2*T_vorlauf/3+8+1/3
        f_hs_exp=1.3
    HS=hpl.HeatingSystem(TRJ.iloc[standort-1,9],20,[T_vorlauf,t_hs_set],1,f_hs_exp)
    HeatStorage_tww=hs.HeatStorage(Volume=300,ambient_temperature=15)
    HeatStorage_h=hs.HeatStorage(Volume=300,ambient_temperature=15)
    batteries = pd.DataFrame([['SG1', 0.0, 0.0],['SG1', 1.0, 0.5],['SG1', 2.0, 1.0],['SG1', 3.0, 1.5],['SG1', 4.0, 2.0],
                            ['SG1', 5.0, 2.5],['SG1', 6.0, 3.0], ['SG1', 7.0, 3.5], ['SG1', 8.0, 4.0],['SG1', 9.0, 4.5],
                          ['SG1', 10.0, 5.0]],
                         columns=['system_id', 'e_bat', 'p_inv']
                         )
    T_sp_tww = 50               # Temperatur beim Start in °C
    P_hp_h = 0                  # Leistung der Wärmepumpe für Heizung beim Start in W
    P_hp_tww = 0                # Leistung der Wärmepumpe für TWW beim Start in W
    hyst_h = 0                  # Hysterese-Schalter Heizung
    hyst_tww = 0                # Hysterese-Schalter Heizung
    T_sp_h,_=HS.calc_heating_dist_temp(weather.at[0, 'temperature 24h [degC]'])            # Soll-Temperatur
    T_sp_tww_set = 47           # Soll-Temperatur
    dt = 60                     # Zeitschrittweite in s
    T_hyst = 3                  # Hysterese-Temperatur in thermischen Speichern
    runtime = 0                 # Laufzeit der Wärmepumpe
    heizlänge = 0               # Länge von Load
    E_heizstab_tww_storage = 0  # Energie vom Heizstab im Tww-Storage
    E_heizstab_h_storage = 0    # Energie vom Heizstab im Heating-Storage
    results_timeseries = pd.DataFrame(index=photovoltaic.index)
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
        temp=weather.at[t, 'temperature 24h [degC]']
        if temp < Heizgrenztemperatur:
            P_load_h_th=((20-temp)*E_Heiz/(gtz*24))
        else:
            P_load_h_th=0
        P_load_tww_th = P_tww_load.at[t,'load [W]']
        T_vl,T_rl = HS.calc_heating_dist_temp(weather.at[t, 'temperature 24h [degC]'])
        T_sp_h_set = T_vl
        T_hp_brine = HS.calc_brine_temp(weather.at[t, 'temperature 24h [degC]'])
        T_amb = weather.at[t, 'temperature [degC]']
        T_amb_24h = weather.at[t, 'temperature 24h [degC]']
        if group_id == 1 or group_id == 4:
            T_hp_in = T_amb
        elif group_id==2 or group_id==5:
            T_hp_in = T_hp_brine
        else:
            print('No Simulation for Water/Water HP')
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
            E_heizstab_tww_storage = E_heizstab_tww_storage + P_th_ref / 60
            T_sp_tww = T_sp_tww + \
                (1/(HeatStorage_tww.V_sp*HeatStorage_tww.c_w)
                    ) * P_th_ref * dt
            P_HEIZSTAB_tww.append(P_th_ref)
        else:
            P_HEIZSTAB_tww.append(0)

        # Heizung: Regelung
        if T_sp_h < T_sp_h_set and hyst_h == 0 and hyst_tww == 0:
            hyst_h = 1

        if T_sp_h < T_sp_h_set+T_hyst and hyst_h == 1 and hyst_tww == 0:

            HP_h = HeatPump.simulate(t_in_primary=T_hp_in,
                                        t_in_secondary=T_sp_h,
                                        t_amb=T_amb_24h,
                                        p_th_min=P_load_h_th*1.5)

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
            E_heizstab_h_storage = E_heizstab_h_storage + P_th_ref / 60
            T_sp_h = T_sp_h + \
                (1/(HeatStorage_h.V_sp*HeatStorage_h.c_w)) * \
                P_th_ref * dt
            P_HEIZSTAB_h.append(P_th_ref)
        else:
            P_HEIZSTAB_h.append(0)

        # Abspeichern relevanter Werte
        T_SP_h.append(T_sp_h)
        T_SP_h_set.append(T_sp_h_set)
        T_HP_in.append(T_hp_in)
        T_AMB_avg_24h.append(
            weather.at[t, 'temperature 24h [degC]'])
        T_SP_tww.append(T_sp_tww)
        P_LOAD_h.append(P_load_h_th)
        P_LOAD_tww.append(P_load_tww_th)
        P_HP_h_th.append(P_hp_h_th)
        P_HP_tww_th.append(P_hp_tww_th)
        P_HP_h_el.append(P_hp_h_el)
        P_HP_tww_el.append(P_hp_tww_el)
        COP_h.append(cop_h)
        COP_tww.append(cop_tww)

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
    # Gesamtstromverbrauch Gebäude
    results_summary=pd.DataFrame()
    P_el_gesamt = results_timeseries['P_hp_h_el'] + \
        results_timeseries['P_hp_tww_el'] + \
        P_el_hh[str(standort)].values + \
        results_timeseries['P_Heizstab_h'] + \
        results_timeseries['P_Heizstab_tww']

    if group_id == 1 or group_id == 4:
        wpkategorie = 'L/W'
    else:
        wpkategorie = 'S/W'
    if group_id > 3:
        wptyp = 'einstufig'
    else:
        wptyp = 'geregelt'

    E_load_th = (
        results_timeseries['P_load_tww']+results_timeseries['P_load_h']).mean()*8.76

    E_hp_h_th = results_timeseries['P_hp_h_th'].mean()*8.76 + \
        results_timeseries['P_Heizstab_h'].mean()*8.76
    E_hp_tww_th = results_timeseries['P_hp_tww_th'].mean()*8.76 + \
        results_timeseries['P_Heizstab_tww'].mean()*8.76
    E_hp_h_el = results_timeseries['P_hp_h_el'].mean()*8.76 + \
        results_timeseries['P_Heizstab_h'].mean()*8.76
    E_hp_tww_el = results_timeseries['P_hp_tww_el'].mean()*8.76 + \
        results_timeseries['P_Heizstab_tww'].mean()*8.76
    # Gesamtstromverbrauch Wärmepumpe
    E_hp_el = E_hp_tww_el + E_hp_h_el

    # Energiebilanz des Heizstabs
    P_heizstab_tww = results_timeseries.loc[results_timeseries['COP_tww']
                                            == 1, 'P_hp_tww_th']
    try:
        E_heizstab_tww = P_heizstab_tww[0] / \
            1000 * (len(P_heizstab_tww) / 60)
    except:
        E_heizstab_tww = 0
    P_heizstab_h = results_timeseries.loc[results_timeseries['COP_h']
                                            == 1, 'P_hp_h_th']
    try:
        E_heizstab_h = P_heizstab_h[0] / \
            1000 * (len(P_heizstab_h) / 60)
    except:
        E_heizstab_h = 0
    E_heizstab = E_heizstab_h + E_heizstab_tww + \
        (E_heizstab_h_storage + E_heizstab_tww_storage)/1000
    reihe=0
    # Netzbezug, Netzeinspeisung
    P_diff = (photovoltaic[pv_orientation]-P_el_gesamt).values
    for idx in batteries.index:
        BAT_soc = []
        BAT_P_bs = []

        BAT = bsl.ACBatMod(system_id=batteries['system_id'][idx],
                            p_inv_custom=batteries['p_inv'][idx],
                            e_bat_custom=batteries['e_bat'][idx])
        if batteries['e_bat'][idx] == 0.0:
            P_gs = np.minimum(0, P_diff)
            P_gf = np.maximum(0, P_diff)
            P_du = np.minimum(P_el_gesamt, photovoltaic[pv_orientation])
        else:
            res = BAT.simulate(p_load=0, soc=0, dt=dt)
            for p_diff in P_diff:
                res = BAT.simulate(p_load=p_diff, soc=res[2], dt=dt)
                BAT_soc.append(res[2])
                BAT_P_bs.append(res[0])
            BAT_soc=np.asarray(BAT_soc)
            BAT_P_bs=np.asarray(BAT_P_bs)
            P_gs = np.minimum(0, (P_diff-BAT_P_bs))
            P_gf = np.maximum(0, (P_diff-BAT_P_bs))

        # Wetterbedingungen
        # 1,2,3,..
        results_summary.loc[reihe, 'Standort'] = standort
        # Old: G15 / New: G12
        results_summary.loc[reihe,
                            'Gradtagszahlen'] = gtz
        # Gebäudeenergien
        # Neubau / Altbau
        results_summary.loc[reihe, 'E_load_h'] = results_timeseries['P_load_h'].mean()*8.76  # kWh im Jahr
        results_summary.loc[reihe, 'E_load_tww'] = results_timeseries['P_load_tww'].mean()*8.76
        # Gesamtstromsverbrauch
        results_summary.loc[reihe, 'E_el_gesamt'] = P_el_gesamt.mean()*8.76
        # grid feed-in
        results_summary.loc[reihe, 'E_gf'] = P_gf.mean()*8.76
        results_summary.loc[reihe, 'E_gs'] = P_gs.mean()*-8.76  # grid supply
        # z.B. 0.562 -> Eigenversorgung / Gesamtstromverbrauch
        results_summary.loc[reihe, 'Autarkiegrad'] = round(
            1-((P_gs.mean()*-8.76)/(P_el_gesamt.mean()*8.76)), 3)
        results_summary.loc[reihe, 'P_gs_avg_max_1h'] = np.mean(np.reshape(
            P_gs*-1, (8760, 60)), 1).max()  # maximaler Netzbezug Mittelwert über eine Stunde
        results_summary.loc[reihe, 'P_gs_avg_max_24h'] = np.mean(np.reshape(
            P_gs*-1, (365, 1440)), 1).max()  # maximaler Netzbezug Mittelwert über einen Tag
        # Wärmepumpe
        # Generic/LW100...
        results_summary.loc[reihe, 'WP-Hersteller'] = hpl.get_parameters(wp_model).Manufacturer.values[0]
        results_summary.loc[reihe, 'WP-Name'] = wp_model
        # L/W / S/W
        results_summary.loc[reihe,
                            'WP-Katergorie'] = wpkategorie
        # Laufzeit in h
        results_summary.loc[reihe, 'WP-Laufzeit'] = runtime/60
        results_summary.loc[reihe, 'Heizlänge'] = heizlänge
        # einstufig / inverter
        results_summary.loc[reihe, 'WP-Typ'] = wptyp
        # installierte Leistung bei -7/52
        results_summary.loc[reihe, 'WP-Leistung'] = P_th_ref
        results_summary.loc[reihe, 'E_hp_h_th'] = E_hp_h_th
        results_summary.loc[reihe, 'E_hp_tww_th'] = E_hp_tww_th
        # Gesamtverbrauch
        results_summary.loc[reihe, 'E_hp_el'] = E_hp_el
        results_summary.loc[reihe, 'E_hp_h_el'] = E_hp_h_el
        results_summary.loc[reihe, 'E_hp_tww_el'] = E_hp_tww_el
        results_summary.loc[reihe, 'JAZ'] = (E_hp_h_th+E_hp_tww_th)/E_hp_el  # nur Wärmepumpe
        # nur Wärmepumpe
        results_summary.loc[reihe, 'JAZ_h'] = E_hp_h_th / E_hp_h_el
        # nur Wärmepumpe
        results_summary.loc[reihe, 'JAZ_tww'] = E_hp_tww_th/E_hp_tww_el
        # mit Wärmevebräuchen
        results_summary.loc[reihe, 'SJAZ'] = E_load_th/E_hp_el
        # Anteil Heizstab in % der Wärmepumpen-Produktion
        results_summary.loc[reihe, 'f_heizstab'] = round(E_heizstab/(E_hp_h_th+E_hp_tww_th), 3)
        # Wärmspeicher
        results_summary.loc[reihe, 'T_sp_h_avg'] = results_timeseries['T_sp_h'].mean()
        results_summary.loc[reihe, 'T_sp_tww_avg'] = results_timeseries['T_sp_tww'].mean()
        # Photovoltaik
        # installierte Leistung
        results_summary.loc[reihe, 'P_pv'] = pv_kwp
        # Süd oder Ost/West
        results_summary.loc[reihe, 'PV_orientation'] = pv_orientation
        # Erzeugung in kWh
        results_summary.loc[reihe, 'E_pv'] = photovoltaic[pv_orientation].mean()*8.76
        # Eigenverbrauch in kWh
        results_summary.loc[reihe, 'E_pv_sc'] = P_du.mean()*8.76
        # Batteriespeicher
        # Speicherkapazität, 0 wenn ohne Batterie
        results_summary.loc[reihe, 'E_bat'] = BAT._E_BAT / 1000 # kWh
        # geladene und entladene Energie
        if BAT._E_BAT == 0:
            results_summary.loc[reihe, 'E_bc'] = 0
            results_summary.loc[reihe, 'E_bd'] = 0
        else:
            results_summary.loc[reihe, 'E_bc'] = np.maximum(0, BAT_P_bs).mean()*8.76
            results_summary.loc[reihe, 'E_bd'] = np.minimum(0, BAT_P_bs).mean()*8.76*-1
        reihe+=1
    wp_model=wp_model.replace('/','')
    results_summary.to_csv('src/simulation_data/simulations/'+str(standort)+'_'+ str(E_gas)+'_'+str(T_vorlauf)+'_'+str(n_Personen)+'_'+str(eff_tww)+'_'+str(Baujahr)+'_'+ wp_model+'_'+str(pv_kwp)+'_'+pv_orientation+'.csv',index=False)
    return results_summary
