"""Independent reviewer oracle for BODYMAP-B2-PREREG/1 (FZ-V1).

Authored and attested by the supervisor/reviewer (Muse). This package is
firewalled from the candidate: it imports nothing from ``candidate``,
``verification`` or any existing solver helper, and it never reads a
candidate-produced verdict or expected-value file. Bessel functions are
summed from the FZ-V1 power series in arbitrary precision (mpmath);
mpmath's own ``besselj`` is never used as the acceptance oracle.
"""
