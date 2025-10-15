import numpy as np
import math

# to do
# classes: Forecast (photovoltaic, load), Battery (schedule, control)
# definitions without classes: evaluation

class BatProg:
    def __init__(self, dt: int = 60, P_stc: int = 5, C_bu: int = 5,
                 P_inv: float = 2.5, p_gfl: float = 0.5, eta_batt: float = 0.95,
                 eta_inv: float = 0.94, tf_past: int = 3, tf_prog: int = 15): 
        """
        Some hard coded values.

        Parameters
        ----------
        dt : numeric
            Time increment in seconds
        P_stc : numeric
            nominal power of the PV generator under STC test conditions in kWp
        C_bu : numeric
            usable battery capacity in kWh
        P_inv : numeric
            Nominal power of the battery inverter in kW
        p_gfl : numeric (0...1)
            specific grid feed-in limit in kW/kWp
        eta_batt : numeric (0...1)
            Efficiency of battery storage (without AC/DC conversion)
        eta_inv : numeric (0...1)
            Efficiency of the battery inverter
        tf_past : numeric
            Look-back time window in h
        tf_prog : numeric
            Forecast horizon in h
        """
        self.dt=dt
        self.P_stc=P_stc
        self.C_bu=C_bu
        self.P_inv=P_inv
        self.p_gfl=p_gfl
        self.eta_batt=eta_batt
        self.eta_inv=eta_inv
        self.tf_past=tf_past
        self.tf_prog=tf_prog
    
    def batt_sim(self, P_b: float, soc_0: float):
        """ 
        Simple battery storage model in which conversion losses 
        are accounted for by constant loss factors.
        Source: J. Weniger: Dimensionierung und Netzintegration von
        PV-Speichersystemen. Masterarbeit, Hochschule für Technik und Wirtschaft
        HTW Berlin, 2013

        Parameters
        ----------
        P_b : numeric
            requestet Power of battery in this timestep (positiv: charge, negativ: discharge)
        soc_0 : numeric (0...1)
            Battery state of charge before this timestep

        Returns
        -------
        P_b : numeric
            actual power of battery in this timestep (positiv: charge, negativ: discharge)
        soc : numeric  (0...1)
            Battery state of charge after this timestep
    
         Mögliche AC-seitige Batterieleistung auf die
         Batteriewechselrichter-Nennleistung begrenzen
        """
        P_b=np.maximum(-self.P_inv*1000,np.minimum(self.P_inv*1000,P_b))
        #Batteriespeicherinhalt im Zeitschritt zuvor
        E_b0=soc_0*self.C_bu*1000
        if P_b>=0:# %Batterieladung
            # Mögliche DC-seitige Batterieleistung unter Berücksichtigung des
            # Batteriewechselrichter-Wirkungsgrads bestimmen
            P_b=P_b*self.eta_inv
            #Ladung
            E_b=np.minimum(self.C_bu*1000, E_b0+self.eta_batt*P_b*self.dt/3600)
            # Anpassung der wirklich genutzten Leistung
            P_b=np.minimum(P_b,(self.C_bu*1000-E_b0)/(self.eta_batt*self.dt/3600))
        
        else:# % Batterieentladung
            #Mögliche DC-seitige Batterieleistung unter Berücksichtigung des
            # Batteriewechselrichter-Wirkungsgrads bestimmen
            P_b=P_b/self.eta_inv
            #Entladung
            E_b=np.maximum(0, E_b0+P_b*self.dt/3600)
            #Anpassung der wirklich genutzten Leistung
            P_b=np.maximum(P_b,(-E_b0)/(self.dt/3600))

        #Realisierte AC-seitige Batterieleistung
        if P_b >0:#Ladung
            P_b=P_b/self.eta_inv
        else:#Entladung
            P_b=P_b*self.eta_inv
        #Ladezustand
        soc=E_b/(self.C_bu*1000)
        return(P_b,soc)

    def simu_erg(self,P_pv,P_ld,P_b):
        """
        Calculation of the relative power flows and annual energy balances. 
        The autarky level and the regulation losses are also determined.

        Parameters
        ----------
        P_pv : array
            PV power output in W
        P_ld : array
            household electrical load (load demand) in W
        P_b : array
            Battery power in W (positive: charge, negative: discharge)

        Returns
        -------
        a : numeric (0...1)
            degree of self-sufficiency
        v : numeric  (0...1)
            regulation losses 
        pf : dictionary
            with the following colums
            P_pv: PV power output in W
            P_ld: household electrical load (load demand) in W
            P_d: Differential power (PV power minus household load) in W
            P_du: Directly consumed PV power (direct usage) in W
            P_bc: Battery charge power in W
            P_bd: Battery discharge power in W
            P_gf: grid feed-in power in W
            P_gs: grid supply power in W
            P_ct: Power of regulation losses in W
        eb : dictionary
            with the following colums
            E_pv: generated PV energy in MWh/a
            E_ld: household electricity demand (load demand) in MWh/a
            E_du: PV energy directly consumed (direct usage) in MWh/a
            E_bc: battery charge in MWh/a
            E_bd: battery discharge in MWh/a
            E_gf: grid feed-in in MWh/a
            E_gs: grid supply in MWh/a
            E_ct: PV energy curtailment in MWh/a
        """
        pf=dict()
        pf['P_pv']=P_pv
        pf['P_ld']=P_ld
        pf['P_d']=P_pv-P_ld
        pf['P_du']=np.minimum(P_pv,P_ld)
        pf['P_bc']=np.maximum(0,P_b)
        pf['P_bd']=abs(np.minimum(0,P_b))
        pf['P_gf']=np.maximum(0,np.minimum(self.P_stc*1000*self.p_gfl,pf['P_d']-pf['P_bc']))
        pf['P_gs']=abs(np.minimum(0,pf['P_d']+pf['P_bd']))
        pf['P_ct']=P_pv-pf['P_du']-pf['P_bc']-pf['P_gf']

        eb=dict()
        eb['E_pv']=P_pv.mean()*8.76
        eb['E_ld']=P_ld.mean()*8.76
        eb['E_du']=pf['P_du'].mean()*8.76
        eb['E_bc']=pf['P_bc'].mean()*8.76
        eb['E_bd']=pf['P_bd'].mean()*8.76
        eb['E_gf']=pf['P_gf'].mean()*8.76
        eb['E_gs']=pf['P_gs'].mean()*8.76
        eb['E_ct']=pf['P_ct'].mean()*8.76

        a = (eb['E_du']+eb['E_bd'])/eb['E_ld']
        v = eb['E_ct']/eb['E_pv']
        return (a,v,pf,eb)

    def prog4pv(self, time, p_pv):
        """Optimized: Generation of PV forecasts based on historical measured values."""
        p_pv = np.asarray(p_pv)
        n_steps = len(time)
        day_steps = int(86400 / self.dt)
        tf_past_steps = self.tf_past * int(3600 / self.dt)
        tf_prog_steps = int(self.tf_prog * 3600 / self.dt)
        maxpv = np.max(p_pv)
        # Preallocate arrays
        p_pvmax = np.zeros(n_steps)
        KTF = np.zeros(n_steps)
        # Efficient rolling window for max PV per day
        for t in range(day_steps - 1, n_steps - day_steps, day_steps):
            d_pv = min(math.ceil(t * self.dt / 86400), 10)
            start = t - d_pv * day_steps + 1
            p_pvsel = p_pv[start:t + 1]
            shape = (day_steps, d_pv)
            if p_pvsel.size == day_steps * d_pv:
                p_pvmax[t:t + day_steps] = np.max(p_pvsel.reshape(shape, order='F'), axis=1)
        n = p_pv <= 0
        p_pv_day = p_pv[~n]
        pv_max_day = p_pvmax[~n]
        valid_len = len(p_pv_day)
        E_pv_past = np.zeros(valid_len)
        E_max = np.zeros(valid_len)
        # Use cumulative sum for fast windowed sum
        cumsum_pv = np.concatenate(([0], np.cumsum(p_pv_day)))
        cumsum_max = np.concatenate(([0], np.cumsum(pv_max_day)))
        idx = np.arange(tf_past_steps, valid_len)
        E_pv_past[idx] = cumsum_pv[idx + 1] - cumsum_pv[idx + 1 - tf_past_steps]
        E_max[idx] = cumsum_max[idx + 1] - cumsum_max[idx + 1 - tf_past_steps]
        k_TF = np.divide(E_pv_past, E_max, out=np.zeros_like(E_pv_past), where=E_max != 0)
        KTF[~n] = k_TF
        if self.dt < 900:
            block = int(3600 / self.dt / 4)
            n_blocks = int(len(time) / block)
            KTF = np.mean(KTF[:block * n_blocks].reshape((block, n_blocks), order='F'), axis=0)
            p_pvmax = np.mean(p_pvmax[:block * n_blocks].reshape((block, n_blocks), order='F'), axis=0)
            p_pvmax = np.tile(p_pvmax, 2)
            p_pvf = np.zeros((len(KTF), self.tf_prog * 4))
            for t in range(len(p_pvf)):
                end = t + self.tf_prog * 4
                p_pvf[t, :] = np.maximum(0, np.minimum(maxpv, KTF[t] * p_pvmax[t:end]))
        else:
            p_pvmax = np.tile(p_pvmax, 2)
            n_forecast = math.ceil(self.tf_prog * 3600 / self.dt)
            p_pvf = np.zeros((n_steps, n_forecast))
            for t in range(n_steps):
                end = t + n_forecast
                p_pvf[t, :] = np.maximum(0, np.minimum(maxpv, KTF[t] * p_pvmax[t:end]))
        p_pvf[np.isnan(p_pvf)] = 0
        return p_pvf

    def prog4ld(self, time, P_ld):
        """Optimized: Generation of load forecasts based on historical measured values."""
        P_ld = np.asarray(P_ld)
        n_steps = len(time)
        if self.dt < 900:
            block = int(900 / self.dt)
            n_blocks = int(n_steps / block)
            P_ld15 = np.mean(P_ld[:block * n_blocks].reshape((block, n_blocks), order='F'), axis=0)
            time_f = time[::block]
            g1 = np.exp(-0.1 * (np.arange(self.tf_prog * 4) + 1)) / np.exp(-0.1)
            g2 = 1 - g1
            P_ldf = np.zeros((len(time_f), self.tf_prog * 4))
            for t in range(96, len(time_f)):
                P_ldf[t, :] = g1 * P_ld15[t - 1] + g2 * P_ld15[t - 96:t - 96 + self.tf_prog * 4]
        else:
            n_forecast = math.ceil(self.tf_prog * 3600 / self.dt)
            P_ldf = np.zeros((n_steps, n_forecast))
            time_f = time
            g1 = np.exp(-0.1 * (np.arange(n_forecast) + 1)) / np.exp(-0.1)
            g2 = 1 - g1
            for t in range(int(86400 / self.dt), n_steps):
                P_ldf[t, :] = g1 * P_ld[t - 1] + g2 * P_ld[t - int(86400 / self.dt):t - int(86400 / self.dt) + n_forecast]
        return P_ldf, time_f

    def batt_prog(self, t, P_df, soc):
        """Optimized: Creation of a schedule for the battery power over the forecast horizon."""
        t_fsel = math.floor(t * self.dt / 900)
        P_dfsel = P_df[t_fsel, :]
        soc_0 = soc[t - 1]
        E_b0 = soc_0 * self.C_bu * 1000
        n = int(self.tf_prog * 4)
        p_gfl_steps = int(self.p_gfl * 100 + 1)
        p_gflvir = np.arange(0, self.p_gfl + 0.01, 0.01)
        P_sf = np.maximum(0, P_dfsel)
        # Vectorized computation for all p_gflvir
        P_sf_mat = np.tile(P_sf, (p_gfl_steps, 1)).T
        p_gflvir_mat = np.tile(p_gflvir * self.P_stc * 1000, (n, 1))
        excess = np.maximum(0, P_sf_mat - p_gflvir_mat)
        energy = np.sum(excess * self.eta_batt * self.eta_inv * self.dt * 900 / self.dt / 3600, axis=0)
        value = np.abs(energy - (self.C_bu * 1000 - E_b0))
        idx = np.argmin(value)
        p_gflvir_sel = p_gflvir[idx]
        P_bcf = np.maximum(0, P_dfsel - p_gflvir_sel * self.P_stc * 1000)
        P_bf = np.round(np.minimum(P_bcf, P_dfsel))
        return P_bf, P_dfsel
        
    def err_ctrl(self,t,P_d,P_dfsel,P_bf):
        """
        Adjustment of the planned battery power to compensate for forecast errors. 
        For this purpose, the forecast charging power is corrected by a control system
        by the difference between the forecast and measured values.

         Source: J. Weniger, J. Bergner, V. Quaschning: Integration of PV power
         and load forecasts into the operation of residential PV battery systems.
         In: 4th Solar Integration Workshop. Berlin, 2014
         
        Parameters
        ----------
        t : numeric
            Time step
        P_d : array
            differential power in W (P_pv-P_ld)
        P_dfsel : array
            forcast of differential Power at this timestep 
        P_bf : array
            forcast power of battery for the next timesteps(positiv: charge, negativ: discharge)

        Returns
        -------
        P_b : numeric
            Battery power in this timestep (positiv: charge, negativ: discharge)
         """

        if P_d[t]>0:#(Leistungsüberschuss)
            """ % Anpassung der Ladeleistung, wenn die aktuelle Differenzleistung größer
                % null und überschüssige PV-Leistung vorhanden ist
                %
                % Batterieladeleistung wird angepasst, wenn eine der folgenden
                % Bedingungen erfüllt wird:
                %
                % (1) Die für den aktuellen Zeitschritt prognostizierte
                % Batterieleistung ist ungleich null
                % (2) Die aktuelle Differenzleistung ist größer als die max.
                % prognostizierte Einspeiseleistung (virtuelle Einspeisegrenze)
                % während des Prognosehorizonts
                % (3) Die aktuelle Differenzleistung übersteigt die max. zulässige
                % Einspeisegrenze"""
            
            if (P_bf[0]!=0) or (P_d[t]>np.max(P_dfsel-P_bf)) or (P_d[t]>self.p_gfl*self.P_stc*1000):
                """ % Aktuelle Ladeleistung um die Differenz zwischen der aktuellen
                    % Differenzleistung P_d(t) und der prognostizierten Differenzleistung
                    % P_dfsel(1) korrigieren. Dadurch wird gewährleistet, dass die
                    % zuvor ermittelte virtuelle Einspeisegrenze eingehalten wird"""
                    
                # Ladeleistung auf die Nennleistung des Batteriewechselrichters begrenzen
                P_b=np.maximum(0,P_bf[0]+P_d[t]-P_dfsel[0])
                # Ladeleistung auf die Nennleistung des Batteriewechselrichters begrenzen
                P_b=np.minimum(self.P_inv*1000,P_b)
            else:
                """ % Wenn keine der zuvor aufgeführten Bedingungen erfüllt wird, soll
                    % die aktuelle Batterieladeleistung auf null gesetzt werden.
                    % Dadurch wird eine stufige Anpassung der Einspeiseleistung
                    % verhindert."""
                P_b=0
        else:#% P_d(t)<0 (Leistungsdefizit)
            """ % Entladeleistung gemäß Leistungsdefizit anpassen und auf die Nennleistung des
                % Batteriewechselrichters begrenzen."""
            P_b=np.maximum(-self.P_inv*1000,P_d[t])  
        return(P_b)
      