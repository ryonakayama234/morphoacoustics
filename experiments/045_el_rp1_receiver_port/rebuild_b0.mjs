/** Independent EL-RP1 B0 complex traveling-wave oracle, frozen before Core-matrix RP1 Gate B. */
const buildOracle = function buildOracle() {
  const C=(r,i=0)=>({r,i}),add=(a,b)=>C(a.r+b.r,a.i+b.i),sub=(a,b)=>C(a.r-b.r,a.i-b.i),mul=(a,b)=>C(a.r*b.r-a.i*b.i,a.r*b.i+a.i*b.r),scale=(a,s)=>C(a.r*s,a.i*s),div=(a,b)=>{const d=b.r*b.r+b.i*b.i;return C((a.r*b.r+a.i*b.i)/d,(a.i*b.r-a.r*b.i)/d)},abs2=a=>a.r*a.r+a.i*a.i;
  const rho=1.21,c=343,ps=1,zs=13834333.333333334,zt=27668666.666666668, rows=[];
  for(const A of [4e-5,8e-5]) for(const L of [.025,.035]) for(const f of [750,2200,5100,7900]) {
    const zc=rho*c/A,rs=zs/zc,gamma=(zt-zc)/(zt+zc),theta=2*Math.PI*f*L/c;
    const q=C(Math.cos(theta),-Math.sin(theta)),gammaIn=scale(mul(q,q),gamma);
    const den=add(C(1+rs),scale(gammaIn,1-rs)),forward=div(C(ps),den),backward=mul(forward,gammaIn);
    const p0=add(forward,backward),u0=scale(sub(forward,backward),1/zc);
    const atTerminal=mul(forward,q),pL=scale(atTerminal,1+gamma),uL=scale(atTerminal,(1-gamma)/zc);
    const powerDrive=ps*u0.r/2,powerEntrance=(p0.r*u0.r+p0.i*u0.i)/2,powerTerminal=(pL.r*uL.r+pL.i*uL.i)/2,powerSourceLoss=zs*abs2(u0)/2;
    rows.push([A,L,f,p0.r,p0.i,u0.r,u0.i,pL.r,pL.i,uL.r,uL.i,powerDrive,powerEntrance,powerTerminal,powerSourceLoss]);
  }
  return {schema:"el-rp1.b0.traveling-wave-oracle.v1",scientific_scope:"IDEAL_SYNTHETIC_1D_ONLY",preregistration_sha:"a33c8c68879f732cd830b2caab6b8024b5322297",method:"independent_complex_travelling_waves_ecmascript_not_core_matrix",fixed:{source_pressure_pa:ps,source_impedance_pa_s_m3:zs,terminal_impedance_pa_s_m3:zt,air_density_kg_m3:rho,sound_speed_m_s:c,phasor:"peak_exp_plus_iwt",positive_u:"entrance_to_terminal"},fields:["area_m2","length_m","frequency_hz","p0_real_pa","p0_imag_pa","u0_real_m3_s","u0_imag_m3_s","pL_real_pa","pL_imag_pa","uL_real_m3_s","uL_imag_m3_s","power_source_w","power_entrance_w","power_terminal_w","power_source_resistor_loss_w"],rows};
};
process.stdout.write(JSON.stringify(buildOracle(),null,2)+'\n');
