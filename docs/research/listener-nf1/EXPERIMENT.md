# EL-NF1 — reproduction (WSL2/Linux)

Prerequisite: Python 3.11+, no dependency on unmerged research code.

~~~bash
python -m pip install -e '.[dev]'
python -m pip install 'scipy>=1.11' 'h5py>=3.8'
python -m pytest -q tests/test_experiment_045_el_nf1.py
mkdir -p /tmp/el-nf1
curl --fail --location --retry 4 --retry-delay 5 --connect-timeout 25 --max-time 180 \
  'https://zenodo.org/records/7316545/files/NF_LIB_HRTF_measured.sofa?download=1' \
  --output /tmp/el-nf1/NF_LIB_HRTF_measured.sofa
printf '%s  %s\n' '4ba9cc348801a6805265c7168b5b3227' /tmp/el-nf1/NF_LIB_HRTF_measured.sofa | md5sum -c -
python experiments/045_el_nf1_receiver/run.py \
  --sofa /tmp/el-nf1/NF_LIB_HRTF_measured.sofa \
  --output /tmp/el-nf1/evidence.json
~~~

Workflow: \`.github/workflows/el-nf1-receiver.yml\`. The runner writes numerical evidence even when the preregistered engineering candidate criterion **fails**; a numerical REVISE_OR_REJECT is a valid research result, not a CI infrastructure error. SOFA parse/invalid metadata **fails** the job. Synthetic SOFA tests only verify algorithm implementation. A GO_LIMITED_NUMERICAL_CANDIDATE never means human/clinical or ASMR perception or product adoption.
