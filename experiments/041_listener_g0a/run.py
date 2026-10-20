"""EL-G0a: fixed-source, measured-near-field-HRIR versus free-field point-probe A/B.

Research-only. Never equate relative measured HRTF amplitude with calibrated Pa.
Run after installing numpy scipy h5py soundfile; do not vendor third-party SOFA data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import h5py
import numpy as np
import soundfile as sf
from scipy.signal import chirp, fftconvolve, resample_poly

FS = 48000
C = 343.0
RHO = 1.2
MONOPOLE_Q = 1e-6  # m^3/s peak scale, time-varying below
CASES = ('center', 'right', 'left')
ZENODO_MD5 = '4ba9cc348801a6805265c7168b5b3227'  # measured (without LFE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _attr(obj, name: str, default: str = '') -> str:
    x = obj.attrs.get(name, default)
    if isinstance(x, bytes):
        return x.decode('utf8')
    if isinstance(x, np.ndarray) and x.size == 1:
        return str(x.reshape(-1)[0].decode('utf8') if isinstance(x.reshape(-1)[0], bytes) else x.reshape(-1)[0])
    return str(x)


def _coords(x: np.ndarray, kind: str, units: str) -> np.ndarray:
    """SOFA convention world axes: +x front, +y left, +z up."""
    if x.shape[-1] != 3:
        raise ValueError('UNSUPPORTED: position must have 3 coordinates')
    kind = kind.strip().lower()
    units = units.strip().lower().replace('meters', 'metre').replace('meter', 'metre')
    if kind == 'cartesian':
        if units and not all(u.strip() in ('metre', 'm') for u in units.split(',')):
            raise ValueError(f'UNSUPPORTED: cartesian position units {units}')
        return x.copy()
    if kind == 'spherical':
        unit_list = [u.strip() for u in units.split(',')]
        if len(unit_list) != 3 or not all('degree' in u for u in unit_list[:2]) or unit_list[2] not in ('metre', 'm'):
            raise ValueError(f'UNSUPPORTED: spherical units {units}')
        az, el, radius = np.deg2rad(x[..., 0]), np.deg2rad(x[..., 1]), x[..., 2]
        return np.stack((radius*np.cos(el)*np.cos(az), radius*np.cos(el)*np.sin(az), radius*np.sin(el)), axis=-1)
    raise ValueError(f'UNSUPPORTED: position type {kind}')


@dataclass
class SofaData:
    xyz: np.ndarray             # M x 3, SOFA +x front +y left, SI m
    ir: np.ndarray              # M x 2 x N, real FIR
    sample_rate: int
    data_delay_samples: np.ndarray  # M x 2; applied separately (zero if embedded in IR)
    receivers: np.ndarray | None    # 2 x 3, or None when not meaningful
    meta: dict


def load_sofa(path: Path) -> SofaData:
    if not path.is_file() or path.stat().st_size > 50_000_000:
        raise ValueError('INVALID: expected SOFA under 50 MB')
    with h5py.File(path, 'r') as f:
        convention = _attr(f, 'SOFAConventions')
        if convention not in ('SimpleFreeFieldHRIR','SimpleFreeFieldHRTF'):
            raise ValueError(f'UNSUPPORTED: SOFAConventions={convention!r}, expected SimpleFreeFieldHRIR/HRTF')
        pos = f['SourcePosition']
        xyz = _coords(np.asarray(pos, dtype=float), _attr(pos,'Type'), _attr(pos,'Units'))
        if convention == 'SimpleFreeFieldHRIR':
            rate_values = np.asarray(f['Data.SamplingRate'], dtype=float).reshape(-1)
            if len(rate_values) == 0 or not np.allclose(rate_values, rate_values[0]) or rate_values[0] < 16000:
                raise ValueError('UNSUPPORTED: invalid or varying sampling rate')
            rate = int(round(float(rate_values[0])))
            if abs(rate - rate_values[0]) > 1e-6:
                raise ValueError('UNSUPPORTED: fractional sampling rate')
            ir = np.asarray(f['Data.IR'], dtype=float)
        else:
            freq = np.asarray(f['N'], dtype=float).reshape(-1)
            if len(freq) < 9 or freq[0] != 0 or not np.allclose(np.diff(freq), np.diff(freq)[0], atol=.0001, rtol=1e-6):
                raise ValueError('UNSUPPORTED: HRTF frequency axis must be uniform and start at DC')
            rate_float = 2.0 * float(freq[-1])
            rate = int(round(rate_float))
            if rate < 16000 or abs(rate-rate_float) > .02:
                raise ValueError('UNSUPPORTED: invalid HRTF inferred sampling rate')
            real = np.asarray(f['Data.Real'], dtype=float)
            imag = np.asarray(f['Data.Imag'], dtype=float)
            if real.shape != imag.shape:
                raise ValueError('INVALID: HRTF real/imag dimensions mismatch')
            # SOFA TF frequency is complex, no independent additional 1/r factor.
            ir = np.fft.irfft(real+1j*imag, n=(len(freq)-1)*2, axis=-1)
        if ir.ndim != 3 or ir.shape[0] != xyz.shape[0] or ir.shape[1] != 2 or ir.shape[2] < 16 or ir.shape[2] > 65536:
            raise ValueError(f'UNSUPPORTED: Data.IR shape {ir.shape}')
        if not np.isfinite(ir).all() or np.all(ir == 0):
            raise ValueError('INVALID: nonfinite or silent SOFA IR')
        delays = np.zeros((len(xyz), 2))
        if 'Data.Delay' in f:
            ds = f['Data.Delay']
            raw = np.asarray(ds, dtype=float)
            raw = np.broadcast_to(raw, (len(xyz), 2)).copy()
            units = _attr(ds, 'Units', 'sample').strip().lower()
            if units in ('sample', 'samples', ''):
                delays = raw
            elif units in ('second', 'seconds', 's'):
                delays = raw * rate
            else:
                raise ValueError(f'UNSUPPORTED: Data.Delay units {units}')
        if not np.isfinite(delays).all() or np.max(np.abs(delays)) > 20 * rate or np.min(delays) < 0:
            raise ValueError('UNSUPPORTED: unsafe/negative Data.Delay')
        receivers = None
        receiver_reason = 'ReceiverPosition absent'
        if 'ReceiverPosition' in f:
            ds = f['ReceiverPosition']
            rr = np.asarray(ds, dtype=float)
            if rr.shape == (2, 3, 1):
                rr=rr[:,:,0]
            if rr.shape == (2, 3):
                try:
                    rr = _coords(rr, _attr(ds,'Type'), _attr(ds,'Units'))
                except ValueError as exc:
                    receiver_reason = f'UNSUPPORTED receiver geometry: {exc}'
                else:
                    # SOFA R0 left (+y), R1 right (-y); reject wrong-side or placeholder coordinates.
                    if (rr[0,1] > rr[1,1] and abs(rr[0,1]-rr[1,1]) > .05
                            and np.max(np.linalg.norm(rr, axis=1)) < .2):
                        receivers = rr
                        receiver_reason = 'SOFA ReceiverPosition used'
                    else:
                        receiver_reason = 'receiver geometry ambiguous; ideal +/-0.09m probes used'
            else:
                receiver_reason = f'unsupported ReceiverPosition shape {rr.shape}'
        if not np.isfinite(xyz).all() or np.any(np.linalg.norm(xyz, axis=1) <= .09):
            raise ValueError('INVALID: impossible/too-close source position')
        meta = dict(convention=convention, convention_version=_attr(f,'SOFAConventionsVersion'),
                    data_type=_attr(f,'DataType'), title=_attr(f,'GLOBAL_Title'),
                    source_type=_attr(pos,'Type'), source_units=_attr(pos,'Units'),
                    receiver_geometry_used=receivers is not None,
                    receiver_geometry_reason=receiver_reason,
                    ir_length=int(ir.shape[2]), measurements=int(ir.shape[0]),
                    ir_origin='Data.IR original' if convention.endswith('HRIR') else 'irfft of SOFA uniform HRTF frequencies',
                    data_delay_handling='additional nonnegative FIR sample delays',
                    amplitude_calibration='UNVERIFIED: non-Pa relative HRIR response')
    return SofaData(xyz,ir,rate,delays,receivers,meta)


def select_positions(xyz: np.ndarray, distance: float = .30, azimuth: float = 30.0) -> dict[str,int]:
    r = np.linalg.norm(xyz, axis=1)
    az = np.rad2deg(np.arctan2(xyz[:,1],xyz[:,0]))  # SOFA positive y = left
    el = np.rad2deg(np.arcsin(np.clip(xyz[:,2]/r,-1,1)))
    valid = (abs(r-distance) <= .021) & (abs(el) <= 10)
    if not np.any(valid):
        raise ValueError('UNSUPPORTED: no measured source at requested 30cm horizontal plane')
    targets = dict(center=0., right=-azimuth, left=azimuth)
    chosen = {}
    for name,target in targets.items():
        err = abs((az-target+180)%360-180)
        rank = err + .03*abs(el) + 25*abs(r-distance)
        rank[~valid] = np.inf
        idx = int(np.argmin(rank))
        if err[idx] > 11.0:
            raise ValueError(f'UNSUPPORTED: {name} unmeasured near azimuth {target} degrees (closest {az[idx]:.1f})')
        chosen[name] = idx
    if len(set(chosen.values())) != 3:
        raise ValueError('UNSUPPORTED: spatial conditions are not distinct')
    return chosen


def source_q(seconds: float = 2.4) -> np.ndarray:
    t = np.arange(round(seconds*FS),dtype=float)/FS
    # Single known deterministic volume velocity. Band-limited chirp + percussive envelopes.
    # Avoid DC and < 300 Hz where measured dataset is poorly constrained.
    env = np.sin(np.pi*np.clip(t/seconds,0,1))**2
    sweep = chirp(t, f0=460, f1=9000, t1=seconds, method='logarithmic')
    pulses = sum(np.exp(-((t-m)/.019)**2)*np.sin(2*np.pi*freq*t)
                 for m,freq in ((.36,1700),(1.10,4400),(1.86,2800)))
    return MONOPOLE_Q * env * (.67*sweep + .28*pulses)


def delay_fir(x: np.ndarray, delay_samples: float, gain: float=1.0) -> np.ndarray:
    """Causal integer + fractional delay; centered Kaiser-windowed sinc interpolation."""
    if delay_samples < 0 or not np.isfinite(delay_samples):
        raise ValueError('INVALID: negative/nonfinite delay')
    integer = int(math.floor(delay_samples))
    frac = delay_samples - integer
    taps = np.arange(-48,49)
    kernel = np.sinc(taps-frac)*np.kaiser(len(taps),9.0)
    kernel /= kernel.sum()
    # kernel center at index 48: pad with delay-48 to ensure causal signal support
    if integer < 48:
        # The leading filter part is allowed before expected peak, not before t=0.
        pad = integer
        out = fftconvolve(x, kernel, mode='full')[48:]  # reference index 48 -> t=0
        return np.pad(out, (pad,0)) * gain
    return np.pad(fftconvolve(x,kernel, mode='full'), (integer-48,0))*gain


def _resample(ir: np.ndarray, sr: int) -> np.ndarray:
    if sr == FS: return ir
    factor = math.gcd(sr,FS)
    return resample_poly(ir, FS//factor, sr//factor)


def render_a(q: np.ndarray, xyz: np.ndarray, receiver: np.ndarray) -> tuple[np.ndarray,dict]:
    d = np.linalg.norm(xyz - receiver,axis=1)
    dq = np.gradient(q, 1/FS, edge_order=2)
    parts = [delay_fir(dq, float(di)/C*FS, RHO/(4*np.pi*float(di))) for di in d]
    arr = np.zeros((max(map(len,parts)),2))
    for k,x in enumerate(parts): arr[:len(x),k]=x
    return arr,dict(distance_m=d.tolist(),delay_s=(d/C).tolist(),
                    right_minus_left_delay_s=float((d[1]-d[0])/C),
                    right_over_left_level_db=float(20*np.log10(d[0]/d[1])))


def render_b(q: np.ndarray, ir: np.ndarray, sr:int, delay_samples:np.ndarray) -> np.ndarray:
    # HRIR is NOT re-fed through 1/r or ear canal: FIR already represents reception.
    # A measured HRTF normalization/propagation reference is not guaranteed known.
    # Drive derived from the SAME Q(t); arbitrary common scaling of B is disclosed.
    dq = np.gradient(q, 1/FS, edge_order=2)
    parts=[]
    for channel in range(2):
        h = _resample(ir[channel],sr)
        extra_delay = float(delay_samples[channel]) * FS/sr
        if extra_delay:
            h=delay_fir(h,extra_delay)
        parts.append(fftconvolve(dq,h,mode='full'))
    arr=np.zeros((max(map(len,parts)),2))
    for k,x in enumerate(parts):arr[:len(x),k]=x
    return arr


def write_pair(raw_a: np.ndarray, raw_b: np.ndarray, directory: Path, case:str)->dict:
    # One common gain per scene + condition; B has non-calibrated amplitude.
    # Preserve raw, report separately. Do NOT normalize left/right independently.
    # Compare directional/spectral cues; level-distance conclusions are not calibrated.
    peak_a=float(np.max(abs(raw_a)))
    peak_b=float(np.max(abs(raw_b)))
    if not np.isfinite(peak_a+peak_b) or min(peak_a,peak_b)<=1e-13:
        raise ValueError('INVALID: nonfinite/silent audio output')
    # Condition-wide RMS match is an explicit playback compensation, not a physical equality.
    rms_a=float(np.sqrt(np.mean(raw_a**2)))
    rms_b=float(np.sqrt(np.mean(raw_b**2)))
    b_alignment=rms_a/rms_b
    joint_peak=max(peak_a,peak_b*b_alignment)
    playback_gain=min(.70/joint_peak,1e4)
    def dump(audio:np.ndarray,letter:str,trim_gain:float):
        norm=audio*trim_gain*playback_gain
        if np.max(np.abs(norm)) > .701: raise ValueError('INVALID: clipping')
        target=directory/'audio'/f'{case}_{letter}.wav'
        sf.write(target,norm,FS,subtype='PCM_24')
        return {'filename':target.name,'sha256':_sha256(target),'samples':len(norm),
                'channel_peak':np.max(abs(audio),axis=0).tolist()}
    a=dump(raw_a,'A',1.0)
    b=dump(raw_b,'B',b_alignment)
    return {'A':a,'B':b,'rms_a':rms_a,'rms_b':rms_b,
            'b_rms_matching_gain':b_alignment,'playback_gain':playback_gain,
            'level_conclusion':'UNSUPPORTED: B lacks verified absolute pressure calibration'}


def run(sofa:Path,output:Path)->dict:
    if output.exists(): raise FileExistsError('refusing to overwrite evidence directory')
    data=load_sofa(sofa)
    selected=select_positions(data.xyz)
    output.mkdir(parents=True)
    (output/'audio').mkdir()
    q=source_q()
    src_id=_sha256(Path(__file__))
    # SOFA axis +y left, +x front. Fallback distances between anatomical ears 18 cm.
    # Pa for A; unknown relative transfer scale for B.
    receiver=data.receivers if data.receivers is not None else np.array([[0.,+.09,0.],[0.,-.09,0.]])
    result=dict(schema_version='el-g0a-evidence-v1',model_A='freefield_monopole_point_probe',
                model_B='measured_artificial_head_hrir',adoption='NOT_ADOPTED',
                claim_limit='not user-personalized; no perception validation, room, contact or body solver',
                sample_rate_hz=FS,source_type='deterministic Q(t) m^3/s; derivative drives air pressure',
                physics=dict(c_m_s=C,rho_kg_m3=RHO,q_peak_scale_m3_s=MONOPOLE_Q),
                provenance=dict(sofa_sha256=_sha256(sofa),sofa_name=sofa.name,runner_sha256=src_id,
                                meta=data.meta),
                playback_caution='headphones at low volume; NOT calibrated SPL',
                cases={})
    for case, idx in selected.items():
        xyz=data.xyz[idx]
        a,props=render_a(q,xyz,receiver)
        b=render_b(q,data.ir[idx],data.sample_rate,data.data_delay_samples[idx])
        files=write_pair(a,b,output,case)
        az=float(np.rad2deg(np.arctan2(xyz[1],xyz[0])))
        ele=float(np.rad2deg(np.arcsin(xyz[2]/np.linalg.norm(xyz))))
        result['cases'][case]=dict(measurement_index=idx,source_xyz_m=xyz.tolist(),
                                  distance_from_center_m=float(np.linalg.norm(xyz)),
                                  azimuth_deg=az,elevation_deg=ele,
                                  freefield=props,output=files)
    (output/'evidence.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf8')
    (output/'index.html').write_text((Path(__file__).parent/'index.html').read_text(encoding='utf8'),encoding='utf8')
    return result


def main():
    p=argparse.ArgumentParser(description='EL-G0a A/B listening experiment (measured SOFA required)')
    p.add_argument('--sofa',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    result=run(args.sofa,args.output)
    print(json.dumps({'result':'EXPERIMENT_RENDERED_NOT_ADOPTED',
                      'output':str(args.output),'positions':{k:v['azimuth_deg'] for k,v in result['cases'].items()}},ensure_ascii=False))


if __name__=='__main__':main()
