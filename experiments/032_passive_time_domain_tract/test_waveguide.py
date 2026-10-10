"""Experiment-local acceptance tests; executed explicitly in GitHub Actions."""
import math
import unittest
import numpy as np
from waveguide import Geometry, PassiveTract, exact_uniform_impedance, pressure_release_eigenfrequencies


class AcousticExperiment(unittest.TestCase):
    def test_wolfram_uniform_oracle(self):
        g=Geometry()
        self.assertAlmostEqual(g.total_length_m, 0.17, places=12)
        self.assertAlmostEqual(g.characteristic_outlet_impedance, 1383433.3333333333, places=7)
        self.assertAlmostEqual(343/(4*g.total_length_m),504.41176470588235,places=9)
        self.assertAlmostEqual(2*g.total_length_m/343,0.0009912536443148688,places=13)

    def test_matched_analytic_impedance(self):
        g=Geometry(); zc=g.characteristic_outlet_impedance
        for f in (250.,500.,1000.):
            self.assertLess(abs(exact_uniform_impedance(f,g,zc)-zc),1e-7)

    def test_numeric_steady_impedance(self):
        g=Geometry(); zc=g.characteristic_outlet_impedance
        for f in (250.,500.,1000.):
            model=PassiveTract(geometry=g,subdivisions=4)
            dt=model.dt_s; n=7200; ps=[];vs=[];times=[]
            for k in range(1,n+1):
                t=k*dt
                drive=1e-6*math.sin(2*math.pi*f*t)*min(1,t/.025)**2
                result=model.step(drive)
                if k>4680:
                    ps.append(result.inlet_pressure_pa);vs.append(result.inlet_flow_m3_s);times.append(t-dt/2)
            ph=np.exp(-2j*math.pi*f*np.asarray(times));z=np.sum(np.array(ps)*ph)/np.sum(np.array(vs)*ph)
            self.assertLess(abs(z-zc)/zc,0.08, (f,z))

    def test_eigenfrequency_refinement(self):
        g=Geometry();oracle=343/(4*.17)*np.array([1,3,5]);errors=[]
        for sub in (2,4,8):
            eigen=pressure_release_eigenfrequencies(g,sub,3)
            err=np.abs(eigen-oracle)/oracle
            errors.append(err)
        self.assertTrue(np.all(errors[2] < errors[1]))
        self.assertTrue(np.all(errors[1] < errors[0]))
        self.assertLess(max(errors[2]),0.01)

    def test_pressure_release_reflection_timing(self):
        g=Geometry();dt=1/48000
        def render(load):
            model=PassiveTract(geometry=g,subdivisions=4,outlet_resistance_pa_s_m3=load)
            obs=[];tt=[]
            for k in range(1,481):
                t=k*dt
                flow=1e-6*math.exp(-0.5*((t-.003)/.00009)**2)
                if abs(t-.003) > .00054:flow=0
                obs.append(model.step(flow).inlet_pressure_pa);tt.append(t-dt/2)
            return np.array(tt), np.array(obs)
        t,open_out=render(0);_,matched=render(g.characteristic_outlet_impedance)
        delta=open_out-matched
        select=(t>.0036)&(t<.0044)
        j=np.where(select)[0][np.argmin(delta[select])]
        self.assertLess(abs((t[j]-.003)-2*g.total_length_m/343),.0002)
        self.assertLess(delta[j],-0.5)
        early=(t<.00345)
        self.assertLess(max(abs(delta[early])),0.01)

    def test_midpoint_discrete_energy_closed_and_matched(self):
        g=Geometry()
        for load in (0.0,g.characteristic_outlet_impedance):
            model=PassiveTract(geometry=g,subdivisions=4,outlet_resistance_pa_s_m3=load)
            abswork=0;errmax=0;before=None
            for j in range(1500):
                t=(j+1)*model.dt_s
                inp=1e-6*math.exp(-.5*((t-.005)/.0002)**2) if t<.007 else 0
                s=model.step(inp)
                abswork+=abs(s.injected_work_j)
                errmax=max(errmax,abs(s.energy_residual_j))
                if j>1000 and before is not None:self.assertLessEqual(s.stored_energy_j,before+2e-16)
                before=s.stored_energy_j
            self.assertLess(errmax/max(abswork,1e-14),1e-9)
            self.assertLess(errmax,1e-14)

    def test_junction_wolfram(self):
        a1=3e-4;a2=a1/2
        r=(a1-a2)/(a1+a2)
        self.assertAlmostEqual(r,1/3,places=14)
        self.assertAlmostEqual(r*r+4*a1*a2/(a1+a2)**2,1,places=14)
        self.assertEqual((a1-a1)/(a1+a1),0)
        altered=Geometry.middle_constriction()
        s=PassiveTract(geometry=altered,subdivisions=4)
        self.assertLess(min(s.areas_m2),min(Geometry().areas_m2))
        for j in range(1000):
            y=s.step(1e-6 if j<15 else 0)
            self.assertTrue(math.isfinite(y.inlet_pressure_pa))
            self.assertLess(abs(y.energy_residual_j),1e-14)

    def test_reject_nonpassive_and_bad_geom(self):
        with self.assertRaises(ValueError):Geometry(areas_m2=(0,)*10)
        with self.assertRaises(ValueError):Geometry(lengths_m=())
        with self.assertRaises(ValueError):PassiveTract(geometry=Geometry(),outlet_resistance_pa_s_m3=-1)
        with self.assertRaises(ValueError):PassiveTract(geometry=Geometry(),dt_s=0)
        with self.assertRaises(ValueError):PassiveTract(geometry=Geometry(),subdivisions=0)
        with self.assertRaises(ValueError):PassiveTract(geometry=Geometry()).step(float('nan'))

    def test_perturbation_inlet_vs_structure(self):
        g=Geometry();h=Geometry.middle_constriction();t=1/48000
        a=PassiveTract(geometry=g,subdivisions=4,dt_s=t)
        b=PassiveTract(geometry=h,subdivisions=4,dt_s=t)
        outs=[];base=[]
        for j in range(1200):
            tm=(j+1)*t
            drive=1e-6*math.exp(-.5*((tm-.003)/.0001)**2)
            base.append(a.step(drive).inlet_pressure_pa)
            outs.append(b.step(drive).inlet_pressure_pa)
        self.assertGreater(max(abs(np.array(base)-np.array(outs))),.001)


if __name__=='__main__':unittest.main()
