#!/usr/bin/env python3
"""Send one subcircuit fragment to MareNostrum Ona, from a tutorial notebook.

Three things have to be right, and none of them is obvious from the notebook:

1. **Where.** Writer and listener meet in ``$QDISLIB_SUBCIRCUITS_DIR``. The
   library default lives under one person's home, which nobody else can write
   to, so :func:`spool_dir` insists on the shared path being set.
2. **What crosses.** MN5 ships qibo 0.2.10 and the quantum cluster 0.2.15, so a
   pickled ``Circuit`` is not safe to send. We ship its OpenQASM text and the
   listener rebuilds it -- data crosses the boundary, library objects do not.
3. **Which qubits.** The listener maps logical qubit *i* to physical qubit *i*.
   On Red that lands on Q0/Q1/Q2, three of which were faulty on 2026-09-08
   (Q0 and Q2 read 1 regardless of state, Q1's pi-pulse reached 24%). We pad the
   fragment into a full-width circuit and place its gates on known-good qubits,
   then marginalise the counts back down.

Usage from a notebook::

    import ona_submit
    value, counts = ona_submit.run(subcircuits_ona[0])
"""

import os
import re

# Physical qubits to run on. 4 is the only one of the three joined to both
# others (CZ(4,5)=0.950, CZ(4,6)=0.958 on 2026-09-08), so it takes the fragment
# qubit that has two CZ partners. Re-pick these from the day's 2q_gates.csv.
CENTRE = 4
LEAVES = (5, 6)
WIDTH = 9  # physical qubits 0..8 are all calibrated for M and Drag

_CZ_RE = re.compile(r"cz\s+q\[(\d+)\]\s*,\s*q\[(\d+)\]")
_HEADER = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[%d];\n' % WIDTH


def spool_dir():
    """The shared hand-off directory, or a clear error saying to set it."""
    directory = os.environ.get("QDISLIB_SUBCIRCUITS_DIR")
    if not directory:
        raise RuntimeError(
            "QDISLIB_SUBCIRCUITS_DIR is not set. Point it at the tutorial's "
            "shared directory (the same one the listener watches), e.g.\n"
            "    os.environ['QDISLIB_SUBCIRCUITS_DIR'] = "
            "'/gpfs/projects/nct_386/qce26/subcircuits'"
        )
    return directory


def _placement(qasm, nqubits):
    """Map this fragment's qubits onto CENTRE/LEAVES so every CZ is calibrated."""
    adjacency = {}
    for a, b in ((int(m[0]), int(m[1])) for m in _CZ_RE.findall(qasm)):
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)
    centre = next((q for q, ns in adjacency.items() if len(ns) >= 2), None)
    if centre is None:  # 0 or 1 two-qubit gate: any calibrated pair will do
        order = [CENTRE, LEAVES[1], LEAVES[0]]
        return {q: order[i] for i, q in enumerate(range(nqubits))}
    leaves = [q for q in range(nqubits) if q != centre]
    placement = {centre: CENTRE}
    placement.update(dict(zip(leaves, LEAVES)))
    return placement


def _rewrite(qasm, placement):
    body = [
        re.sub(r"q\[(\d+)\]", lambda m: "q[%d]" % placement[int(m.group(1))], line.strip())
        for line in qasm.splitlines()
        if line.strip()
        and not line.strip().startswith(("//", "OPENQASM", "include", "qreg"))
    ]
    return _HEADER + "\n".join(body) + "\n"


def submit_qasm(qasm, observable, nqubits, timeout=300, poll_interval=1.0):
    """Run one fragment, given as QASM, on Ona; return ``(expectation, counts)``.

    Takes plain data rather than a fragment object on purpose. Under PyCOMPSs a
    fragment is a *future*, and reading one requires a ``@task`` -- but a task
    defined in this module cannot run: the COMPSs workers import task modules from
    the application directory, and this file lives in the hidden ``.qce26`` folder,
    so the worker raises ``ModuleNotFoundError: No module named 'ona_submit'``.
    The notebook therefore defines that little task itself and passes the result
    here.

    :param qasm: The fragment's OpenQASM 2 text.
    :param observable: Its Pauli string, e.g. ``"ZZI"``.
    :param nqubits: The fragment's qubit count.
    :param timeout: Seconds to wait for the listener before giving up.
    :return: The expectation value, and the marginal counts it came from.
    """
    from Qdislib.core.cutting_algorithms.wire_cutting import (
        _expectation_from_counts_qibo,
    )
    from Qdislib.utils.qpu_bridge import submit_and_wait

    if "measure" in qasm:
        # A wire-cut fragment carries no measurement; anything else means the cut
        # needs a mid-circuit outcome the QPU cannot return.
        raise ValueError(
            "This fragment measures a qubit mid-circuit. A QPU returns only "
            "aggregated final counts, so use a wire cut, whose fragments measure "
            "only at the end."
        )

    placement = _placement(qasm, nqubits)
    payload = {
        "qasm": _rewrite(qasm, placement),
        "readout_bits": [placement[i] for i in range(nqubits)],
        "observable": observable,
    }

    os.environ.setdefault("QDISLIB_QPU_TIMEOUT", str(timeout))
    result = submit_and_wait(
        payload, directory=spool_dir(), timeout=timeout, poll_interval=poll_interval
    )
    raw = result["counts"] if isinstance(result, dict) else result.counts()

    counts = {}
    for key, n in raw.items():
        bits = "".join(key[b] for b in payload["readout_bits"])
        counts[bits] = counts.get(bits, 0) + n
    shots = sum(counts.values()) or 1
    return _expectation_from_counts_qibo(counts, observable, shots), counts
