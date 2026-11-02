// EL-R2-S1 B2 independent ECMAScript traveling-wave numerical reference.
// Reproduces the *prospectively registered* 24 synthetic cases.
// NO import of Python/Core UniformTube, measured data or human ear assumptions.
const C = (re, im=0) => ({re,im});
const add = (x,y) => C(x.re+y.re,x.im+y.im);
const mul = (x,y) => C(x.re*y.re-x.im*y.im,x.re*y.im+x.im*y.re);
const div = (x,y) => {
  const d=y.re*y.re+y.im*y.im;
  return C((x.re*y.re+x.im*y.im)/d,(x.im*y.re-x.re*y.im)/d);
};
const scale = (x,k) => C(x.re*k,x.im*k);
const sq = x => x.re*x.re+x.im*x.im;
const expneg = t => C(Math.cos(t),-Math.sin(t));
const rho=1.21,c=343,zs=13834333.333333334,zt=27668666.666666668;
const rows=[];
for(const A of [4e-5,8e-5]) for(const L of [.015,.035,.045])
  for(const f of [750,2200,5100,7900]){
    const zc=rho*c/A,k=2*Math.PI*f/c,theta=k*L,q=expneg(theta);
    const gamma=(zt-zc)/(zt+zc),rs=zs/zc;
    const pl=div(scale(q,1+gamma),
      add(C(1+rs),scale(mul(q,q),(1-rs)*gamma)));
    const ul=scale(pl,1/zt);
    const p0=mul(pl,C(Math.cos(theta),zc*Math.sin(theta)/zt));
    const u0=mul(pl,C(Math.cos(theta)/zt,Math.sin(theta)/zc));
    const ps=.5*u0.re, pe=.5*(p0.re*u0.re+p0.im*u0.im);
    const pt=.5*sq(pl)/zt, pr=.5*zs*sq(u0);
    if(Math.abs(ps-pt-pr)>1e-13) throw new Error("Power conservation failure");
    rows.push([A,L,f,pl.re,pl.im,p0.re,p0.im,
      ul.re,ul.im,u0.re,u0.im,ps,pe,pt,pr]);
  }
const oracle={
  schema:"el-r2-s1.b2.scattering24.v1",
  provenance:"Prospectively registered D1 commit 79012a91b820f073251bdea042217145cde5b8e0; independently calculated by ECMAScript traveling-wave complex arithmetic 2026-11-02; synthetic, nonblinded, not experimental ear data",
  phasor:"peak_exp_plus_iwt",
  direction:"+U entrance_to_terminal",
  reference_planes:["SOURCE_EQUIVALENT","CANAL_ENTRANCE","TERMINAL_SIDE"],
  rho_kg_m3:rho,c_m_s:c,source_pressure:[1,0],
  source_impedance_pa_s_m3:zs,terminal_impedance_pa_s_m3:zt,
  columns:["area_m2","length_m","frequency_hz","pL_real_pa",
    "pL_imag_pa","p0_real_pa","p0_imag_pa","uL_real_m3_s",
    "uL_imag_m3_s","u0_real_m3_s","u0_imag_m3_s","Psource_w",
    "Pentrance_w","Pterminal_w","Ploss_w"],
  rows
};
process.stdout.write(JSON.stringify(oracle,null,2)+"\n");
