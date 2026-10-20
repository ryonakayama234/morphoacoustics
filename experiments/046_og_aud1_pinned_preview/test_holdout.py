"""Prospectively filed candidate holdout; 12-state independently built Python matrix.

Gate A has NOT been signed by an independent reviewer; this is a computational
cross-check of an ideal lossless 1D network, NOT biological acoustic validation.
"""
from __future__ import annotations
import json
from pathlib import Path
import unittest

import numpy as np

PATH=Path(__file__).with_name("GATE_A_FROZEN_CANDIDATE.json")


def port_matrix(area,freq,wrong_velocities=False):
    rho,c=1.2,343.
    lengths=[.08,.09,.06]
    areas=[.0003,.0003,area]
    z=[rho*c/x for x in areas]
    zref=z[0]
    mat=np.zeros((12,12),dtype=np.complex128)
    rhs=np.zeros(12,dtype=np.complex128)
    for tube in range(3):
        theta=2*np.pi*freq*lengths[tube]/c
        first=4*tube
        mat[2*tube,first]=1
        mat[2*tube,first+2]=-np.cos(theta)
        mat[2*tube,first+3]=-1j*(z[tube]/zref)*np.sin(theta)
        mat[2*tube+1,first+1]=1
        mat[2*tube+1,first+2]=-1j*(zref/z[tube])*np.sin(theta)
        mat[2*tube+1,first+3]=-np.cos(theta)
    mat[6,2],mat[6,4]=1,-1
    mat[7,2],mat[7,8]=1,-1
    mat[8,3]=1
    if wrong_velocities:
        # Incorrect velocity continuity rather than volume-flow continuity.
        mat[8,5],mat[8,9]=-areas[0]/areas[1],-areas[0]/areas[2]
    else:
        mat[8,5]=mat[8,9]=-1
    mat[9,6],mat[9,7]=1,-z[1]/zref
    mat[10,10],mat[10,11]=1,-z[2]/zref
    mat[11,1]=1
    rhs[11]=zref*(1e-6+.4e-6j)
    return np.linalg.solve(mat,rhs),z,zref


class NewHoldout(unittest.TestCase):
    def test_frozen_unseen_grid_full_port_and_mutants(self):
        spec=json.loads(PATH.read_text())
        self.assertEqual(spec["status"],"GATE_A_PROPOSED_NOT_INDEPENDENTLY_RATIFIED")
        self.assertEqual(spec["holdout_freq_hz"],[137,431,619,1129,1607,2459,3571,3989])
        worst=0.
        minimum=float("inf")
        for area in spec["areas_C_m2"]:
            for f in spec["holdout_freq_hz"]:
                y,z,zref=port_matrix(area,f)
                U=y[1]/zref
                self.assertGreater(abs(U),1e-15)
                zj=1/(1/z[1]+1/z[2])
                r=(zj-z[0])/(zj+z[0])
                theta=2*np.pi*f*.08/343
                zin=z[0]*(1+r*np.exp(-2j*theta))/(1-r*np.exp(-2j*theta))
                F=z[0]*U/(1-r*np.exp(-2j*theta))
                pJ=(1+r)*F*np.exp(-1j*theta)
                analytic_p=[
                    zin*U,pJ,pJ,pJ*np.exp(-2j*np.pi*f*.09/343),
                    pJ,pJ*np.exp(-2j*np.pi*f*.06/343)]
                analytic_U=[
                    U,pJ/zj,pJ/z[1],pJ/z[1]*np.exp(-2j*np.pi*f*.09/343),
                    pJ/z[2],pJ/z[2]*np.exp(-2j*np.pi*f*.06/343)]
                for k in range(6):
                    worst=max(worst,abs(y[2*k]-analytic_p[k])/max(1,abs(analytic_p[k])))
                    worst=max(worst,abs(y[2*k+1]/zref-analytic_U[k])/max(1e-12,abs(analytic_U[k])))
                power_in=(y[0]*np.conj(U)).real/2
                power_out=((y[6]*np.conj(y[7])+y[10]*np.conj(y[11]))/zref).real/2
                self.assertLess(abs(power_in-power_out)/abs(power_in),1e-8)
                minimum=min(minimum,(y[0]/U).real)
                bad,_,_=port_matrix(area,f,wrong_velocities=True)
                self.assertGreater(abs(bad[0]-y[0])/max(1,abs(y[0])),.01)
        self.assertLess(worst,1e-10)
        self.assertGreater(minimum,0)
        print("HELDOUT_12_PORT_MAX_RELATIVE",worst,"MIN_RE_Z",minimum)


if __name__=="__main__":
    unittest.main()
