#!/usr/bin/env python3
"""Capture real MareNostrum Ona results for QCE26 notebook 01.

Run this ONCE before the tutorial, with the QPU listener running on the quantum
cluster against the same shared directory. It evaluates the twelve gate-cut
fragments of notebook 01's example circuit on the QPU and writes
``ona_results.json``, which the notebook loads and reconstructs live.

    # on the quantum cluster (Red QPU):
    export QDISLIB_SUBCIRCUITS_DIR=/gpfs/projects/<proj>/qce26/subcircuits
    export RUNCARD_RED=/path/to/red_runcard.yml
    python examples/qpu_listener.py --qpu red --nshots 1000

    # on the classical side, same directory:
    export QDISLIB_SUBCIRCUITS_DIR=/gpfs/projects/<proj>/qce26/subcircuits
    python ona_capture.py --shots 8192

``--placeholder`` regenerates the shipped stand-in (simulator + synthetic noise)
without touching any hardware, so the notebook stays runnable before the real
capture happens. The notebook prints the ``source`` field verbatim, so a
placeholder always announces itself as one.
"""

import argparse
import datetime
import json
import os
import sys

from qibo import models, gates

import Qdislib as qd

OBSERVABLES = "ZZZZZ"
CUT_SEED = 0  # find_cut is non-deterministic without it; the notebook uses the same


def example_circuit():
    """Notebook 01's circuit -- keep this identical to the notebook's copy."""
    circuit = models.Circuit(5)
    circuit.add(gates.RY(0, 0.8))
    circuit.add(gates.CZ(0, 1))
    circuit.add(gates.RY(1, 0.5))
    circuit.add(gates.CZ(1, 2))
    circuit.add(gates.RY(2, 0.6))
    circuit.add(gates.CZ(2, 3))
    circuit.add(gates.RY(3, 0.4))
    circuit.add(gates.CZ(3, 4))
    circuit.add(gates.RX(4, 0.3))
    return circuit


def _fragments(shots):
    cut = qd.find_cut(example_circuit(), gate_cut=True, wire_cut=False, seed=CUT_SEED)
    subs = qd.gate_cutting_subcircuits(
        example_circuit(), cut, observables=OBSERVABLES, software="qibo"
    )
    return cut, subs


def capture(shots, max_qpu_qubits, timeout):
    """Evaluate every fragment, routing the small ones to the QPU."""
    from Qdislib.core.cutting_algorithms.gate_cutting import _expec_value_qibo_qpu
    from Qdislib.utils.qpu_bridge import subcircuits_dir

    if timeout:
        os.environ["QDISLIB_QPU_TIMEOUT"] = str(timeout)
    print(f"hand-off directory: {subcircuits_dir()}", flush=True)

    cut, subs = _fragments(shots)
    records = []
    for i, frag in enumerate(subs):
        circuit, observable = frag[0], frag[1]
        n = circuit.nqubits
        simulated = qd.expectation_value(frag, shots=shots)
        if n <= max_qpu_qubits:
            print(f"  [{i:2d}] {n}q {observable}: submitting to Ona ...", flush=True)
            try:
                value, device = _expec_value_qibo_qpu(frag, shots=shots), "ona"
            except Exception as exc:  # a dead listener must not lose the rest
                print(f"       FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
                value, device = simulated, f"simulator (Ona failed: {type(exc).__name__})"
        else:
            value, device = simulated, "simulator (too wide for the QPU)"
        print(f"  [{i:2d}] {n}q {observable}: {value:+.5f}  [{device}]", flush=True)
        records.append(
            {
                "index": i,
                "nqubits": n,
                "observable": observable,
                "device": device,
                "value": float(value),
                "simulator": float(simulated),
            }
        )
    return cut, subs, records


def placeholder(shots, noise):
    """Simulator values plus a fixed synthetic bias, so the notebook runs today."""
    import numpy as np

    rng = np.random.default_rng(20260908)
    cut, subs = _fragments(shots)
    records = []
    for i, frag in enumerate(subs):
        circuit, observable = frag[0], frag[1]
        simulated = float(qd.expectation_value(frag, shots=shots))
        # Shrink towards zero (decoherence) plus a little scatter -- the shape real
        # hardware has, without pretending to be a measurement.
        value = float(np.clip(simulated * (1.0 - noise) + rng.normal(0, noise / 2), -1, 1))
        records.append(
            {
                "index": i,
                "nqubits": circuit.nqubits,
                "observable": observable,
                "device": "placeholder",
                "value": value,
                "simulator": simulated,
            }
        )
    return cut, subs, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shots", type=int, default=8192)
    parser.add_argument(
        "--max-qpu-qubits",
        type=int,
        default=3,
        help="Send fragments up to this width to the QPU (2 = only the small half).",
    )
    parser.add_argument("--timeout", type=float, default=None, help="$QDISLIB_QPU_TIMEOUT")
    parser.add_argument("--qpu", default="Red", help="Recorded in the file's provenance.")
    parser.add_argument("--noise", type=float, default=0.12, help="--placeholder only")
    parser.add_argument("--placeholder", action="store_true", help="No hardware; stand-in data.")
    parser.add_argument(
        "--out", default=os.path.join(os.path.dirname(__file__), "ona_results.json")
    )
    args = parser.parse_args()

    if args.placeholder:
        cut, subs, records = placeholder(args.shots, args.noise)
        source = "PLACEHOLDER - simulator with synthetic noise, NOT hardware"
    else:
        cut, subs, records = capture(args.shots, args.max_qpu_qubits, args.timeout)
        source = f"MareNostrum Ona ({args.qpu} QPU)"

    values = [r["value"] for r in records]
    payload = {
        "source": source,
        "captured_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "qdislib_version": qd.__version__,
        "circuit": "notebook 01 example_circuit (5 qubits, CZ chain)",
        "cut": list(cut),
        "cut_seed": CUT_SEED,
        "observables": OBSERVABLES,
        "shots": args.shots,
        "analytical": float(qd.analytical_solution(example_circuit(), OBSERVABLES)),
        "reconstructed": float(subs.reconstruct(values)),
        "fragments": records,
    }
    with open(args.out, "w") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")

    print(f"\nsource       : {payload['source']}")
    print(f"cut          : {payload['cut']}")
    print(f"reconstructed: {payload['reconstructed']:+.5f}")
    print(f"analytical   : {payload['analytical']:+.5f}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
