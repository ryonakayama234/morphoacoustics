"""C1-Open scope-limited science gate: expected failure is NOT a gate pass."""
from __future__ import annotations
from copy import deepcopy
import math
import unittest
import numpy as np
from solver import C0,DomainError,Fixture,Model,ELL,LG,P_AMB
from audit import audit,AuditError

class Tests(unittest.TestCase):
    def test_geometry_and_force_analytical(self):
        m=Model(Fixture(n=32))
        x=np.array([3e-6,-1e-6]);v=np.array([.004,-.003]);vol,_=m.geometry(x)
        self.assertAlmostEqual(float(vol.sum()),m.initial_total_volume+ELL*LG*float(x.sum()),15)
        self.assertAlmostEqual(float((m.g@v).sum()),ELL*LG*float(v.sum()),15)
        b,a=100.,120.
        self.assertAlmostEqual(ELL*LG*(b+a/3),.014,12)
        self.assertAlmostEqual(ELL*LG*(b+2*a/3),.018,12)
        err=[]
        for n in (8,16,32):
            mm=Model(Fixture(n=n));p=b+a*mm.centers/LG
            forces=mm.g.T@p
            err.append(max(abs(forces-np.array([.014,.018]))))
        self.assertGreater(err[0],err[1]);self.assertGreater(err[1],err[2])
        self.assertAlmostEqual(err[0]/err[1],4.,5)
        self.assertAlmostEqual(err[1]/err[2],4.,5)

    def test_stationary_nonuniform_area_well_balanced(self):
        m=Model(Fixture(n=32,locked=True,x0=(3e-6,-1e-6),upstream_delta_pa=0.))
        y=m.initial();rhs,_=m.rhs(y)
        self.assertLess(float(np.linalg.norm(rhs[:3*m.n],ord=np.inf)),1e-11)

    def test_throughflow_8_and_16_with_independent_audit(self):
        for n in (8,16):
            with self.subTest(n=n):
                m=Model(Fixture(n=n,upstream_delta_pa=10.));trace=m.run(duration=.0003)
                verdict=audit(trace)
                self.assertEqual(verdict['decision'],'G1_NUMERICAL_CONTROL_PASS')
                self.assertGreater(verdict['tissue_final_x_m'][0],0)

    def test_causal_body_and_passive_locked_control(self):
        n=8
        moving=Model(Fixture(n=n,upstream_delta_pa=10.)).run(duration=.0003,record_every=10000)
        locked=Model(Fixture(n=n,upstream_delta_pa=10.,locked=True)).run(duration=.0003,record_every=10000)
        a=np.array(moving['rows'][-1]['y']);b=np.array(locked['rows'][-1]['y']);
        self.assertGreater(float(np.linalg.norm(a[3*n:3*n+2]-b[3*n:3*n+2])),1e-8)
        self.assertGreater(float(np.linalg.norm(a[n:2*n]-b[n:2*n])),1e-13)
        altered=Model(Fixture(n=n,upstream_delta_pa=10.,x0=(3e-6,-1e-6))).run(duration=.0003,record_every=10000)
        self.assertGreater(float(np.linalg.norm(np.array(altered['rows'][-1]['y'])[:n]-a[:n])),1e-13)

    def test_audit_rejects_mid_trace_change_and_receipt_forgeries(self):
        trace=Model(Fixture(n=8,upstream_delta_pa=10.)).run(duration=.00003)
        audit(trace)
        mutants=[]
        x=deepcopy(trace);x['rows'][7]['y'][8]+=1e-9;mutants.append(x)
        x=deepcopy(trace);x['rows'][10]['stages'][1]['force'][0]*=-1;mutants.append(x)
        x=deepcopy(trace);x['rows'][2]['stages'][0]['pressure'][3]+=5.;mutants.append(x)
        x=deepcopy(trace);x['rows'][4]['interval']['energy_flux']*=0.01;mutants.append(x)
        x=deepcopy(trace);x['rows']=x['rows'][:-1];mutants.append(x)
        x=deepcopy(trace);x['rows'][0]['y'][-1]=.01;mutants.append(x)
        for x in mutants:
            with self.subTest(mutant=mutants.index(x)):
                with self.assertRaises(AuditError):audit(x)

    def test_A3_stop_refined_moving_wall_reverse_boundary(self):
        # This EXPECTED STOP is preserved, not relaxed until new prospective protocol.
        for n in (32,64):
            with self.subTest(n=n):
                m=Model(Fixture(n=n,upstream_delta_pa=10.))
                with self.assertRaisesRegex(DomainError,'UNSUPPORTED_REVERSE_BOUNDARY'):
                    m.run(duration=.0003,record_every=10000)
        # Rigid-wall countercontrol is valid on refined grid.
        trace=Model(Fixture(n=32,locked=True,upstream_delta_pa=10.)).run(duration=.00003)
        verdict=audit(trace)
        self.assertEqual(verdict['decision'],'G1_NUMERICAL_CONTROL_PASS')

    def test_domain_refusals(self):
        with self.assertRaisesRegex(DomainError,'UNSUPPORTED_CONTACT'):
            Model(Fixture(x0=(-.000101,0.))).initial()
        with self.assertRaisesRegex(DomainError,'UNSUPPORTED_DELTA_PRESSURE'):
            Fixture(upstream_delta_pa=800.)
        with self.assertRaisesRegex(DomainError,'INVALID_N'):
            Fixture(n=0)

if __name__=='__main__':unittest.main()
