"""Preregistered independent analytic control; standard-library unittest."""
import math
import unittest
from dataclasses import replace
from rigid_reference import RigidChannel, Fluid, solve_fixed_wall, UnsupportedRegime, check_receipt

G, F = RigidChannel(), Fluid()


def exact_flow(g, f, dp):
    # Analytic integration of h(z)^-3 over a LINEAR taper, not candidate midpoint sum.
    return 2 * g.width_m * g.half_gap_m**3 * (1-g.taper_slope**2)**2 * dp / (3*f.viscosity_pa_s*g.length_m)


class FrozenB0Tests(unittest.TestCase):
    def test_H0_constant_closed_form(self):
        for p in (.1, .2, .4):
            for n in (4,8,16,32):
                o = solve_fixed_wall(G,F,p,n)
                self.assertLess(abs(o.volume_flow_m3_s/exact_flow(G,F,p)-1),1e-12)
                self.assertTrue(check_receipt(o,p))

    def test_H1_taper_convergence(self):
        for slope in (-.2,.2):
            geom=replace(G,taper_slope=slope)
            for p in (.1,.2,.4):
                errors=[]
                for n in (4,8,16,32):
                    obs=solve_fixed_wall(geom,F,p,n)
                    errors.append(abs(obs.volume_flow_m3_s/exact_flow(geom,F,p)-1))
                self.assertLess(errors[-1],1e-4)
                self.assertTrue(all(errors[i]/errors[i+1]>=3.8 for i in range(3)))

    def test_H2_orientation_pressure(self):
        for p in (.1,.2,.4):
            a=solve_fixed_wall(replace(G,taper_slope=-.2),F,p,16)
            b=solve_fixed_wall(replace(G,taper_slope=.2),F,p,16)
            self.assertLess(abs(a.volume_flow_m3_s/b.volume_flow_m3_s-1),1e-12)
            self.assertGreater(abs(a.face_pressure_pa[4]-b.face_pressure_pa[4]),.001*p)
            self.assertAlmostEqual(a.face_pressure_pa[-1],0,places=12)
            self.assertAlmostEqual(b.face_pressure_pa[-1],0,places=12)

    def test_H3_power_positive_exact_discrete(self):
        for slope in (-.2,0.,.2):
            for p in (0., .1,.2,.4):
                o=solve_fixed_wall(replace(G,taper_slope=slope),F,p,32)
                self.assertGreaterEqual(o.input_power_w,0)
                self.assertTrue(check_receipt(o,p))
                if p:
                    self.assertLessEqual(abs(o.power_residual_w),1e-12*max(o.input_power_w,1e-18))
                else:
                    self.assertEqual(o.input_power_w,0)

    def test_H4_virtual_force_converges(self):
        for p in (.1,.2,.4):
            expected_l = 2*G.width_m*G.length_m*p/3
            expected_u = G.width_m*G.length_m*p/3
            e=[]
            e_upper=[]
            for n in (4,8,16,32):
                o=solve_fixed_wall(G,F,p,n)
                e.append(abs(o.virtual_force_lower_n-expected_l))
                e_upper.append(abs(o.virtual_force_upper_n-expected_u))
            self.assertTrue(all(e[i]>e[i+1] for i in range(3)))
            self.assertLess(e[-1]/expected_l,.001)
            self.assertTrue(all(e_upper[i]>e_upper[i+1] for i in range(3)))
            self.assertLess(e_upper[-1]/expected_u,.001)

    def test_H5_reject_outside_model(self):
        invalid=[(replace(G,half_gap_m=-1),F,.1,16),
                 (replace(G,taper_slope=1.0),F,.1,16),
                 (G,replace(F,viscosity_pa_s=0),.1,16),
                 (G,F,float('nan'),16), (G,F,.1,1)]
        for args in invalid:
            with self.subTest(args=args), self.assertRaises(ValueError):solve_fixed_wall(*args)
        for p in (-.1,800.):
            with self.subTest(p=p), self.assertRaises(UnsupportedRegime):solve_fixed_wall(G,F,p,16)

    def test_tamper_fails_closed(self):
        obs=solve_fixed_wall(G,F,.2,16)
        self.assertTrue(check_receipt(obs,.2))
        self.assertFalse(check_receipt(replace(obs, dissipation_w=obs.dissipation_w*.5),.2))
        self.assertFalse(check_receipt(replace(obs, power_residual_w=.001),.2))
        self.assertFalse(check_receipt(replace(obs, face_pressure_pa=obs.face_pressure_pa[:-1]+(1.,)),.2))
        self.assertFalse(check_receipt(replace(obs, loss_per_cell_w=obs.loss_per_cell_w[:-1]+(-1.0,)),.2))
        self.assertFalse(check_receipt(obs,.4))

if __name__ == '__main__':
    unittest.main()
