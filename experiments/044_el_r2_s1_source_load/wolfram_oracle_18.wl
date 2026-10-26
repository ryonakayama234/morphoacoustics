(* EL-R2-S1 independently regenerable 18-case traveling-wave oracle
   Gate A 2026-10-22. No Core matrix usage. Source: 1Pa peak,
   resistive Zs, Zt held ABSOLUTE as A and L vary. exp(+i omega t).
   Run from repo root:
     wolframscript -file experiments/044_el_r2_s1_source_load/wolfram_oracle_18.wl > /tmp/el-r2-s1-18.json
   Compare numeric values with checked in oracle (not byte-identical JSON).
*)
Print[Module[{rho=1.21,c=343.,aref=3.*^-5, ps=1., s,t,records,rows,ci},s=rho c/aref;t=2 s;records=Flatten[Table[Module[{zc=rho c/area,k=2 Pi f/c,q,gam,sc,ul,uin,pin,pt,powerSource,powerTerminal,powerR},q=Exp[-I k len];gam=(t-zc)/(t+zc);sc=s/zc;pt=ps q(1+gam)/((1+sc)+(1-sc)gam q^2);ul=pt/t;pin=pt (Cos[k len]+I zc Sin[k len]/t);uin=pt (I Sin[k len]/zc+Cos[k len]/t);powerSource=Re[ps Conjugate[uin]]/2;powerTerminal=Re[pt Conjugate[ul]]/2;powerR=s Abs[uin]^2/2;{area,len,f,Re[pt],Im[pt],Re[pin],Im[pin],powerSource,powerTerminal,powerR}],{area,{3.*^-5,6.*^-5}},{len,{.02,.025,.03}},{f,{1000.,3000.,7000.}}],2];rows=Map[(N[#,13])&,records,{2}];ci=<|"schema"->"el-r2-s1.wolfram.scattering.v0","source_pressure_pa"->1.,"source_impedance_pa_s_m3"->s,"terminal_impedance_pa_s_m3"->t,"columns"->{"area_m2","length_m","frequency_hz","terminal_pressure_real_pa","terminal_pressure_imag_pa","entrance_pressure_real_pa","entrance_pressure_imag_pa","source_mean_power_w","terminal_mean_power_w","source_resistor_dissipation_w"},"rows"->rows|>;ExportString[ci,"RawJSON","Compact"->True]]];
