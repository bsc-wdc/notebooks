# MareNostrum Ona in the QCE26 tutorial — instructor runbook

Notebook 01 §4 shows **pre-recorded** Ona results; §5 is an **opt-in** single-fragment
submission. Only §5 needs a live QPU.

Everything goes through `Qdislib.utils.qpu_bridge`: the notebook writes
`circuit_<id>.pkl` into a shared directory and waits; a listener on the quantum
cluster runs it on the QPU and writes `result_<id>.pkl` back. Ids are
`<time_ns>_<pid>`, so attendees never collide.

---

## 0. One-time: the shared directory  (DONE, verified 2026-09-09)

The spool lives in the listener account's own home, because that is the only
place both sides can reach without asking ops:

    /home/bsc/bsc019635/qce26_spool

Why not `/gpfs/scratch/nct_390`: it is mounted on both clusters, but it is owned
by `root:nct_390` with no world-execute, so `bsc019635` (the only account that can
submit QPU jobs) cannot traverse into it -- and `nct00013` cannot grant that,
because it does not own the directory (`setfacl: Operation not permitted`).

The grants already applied, from `bsc019635`:

    setfacl -m g:nct_390:x  $HOME              # traverse only; they cannot list it
    mkdir -p $HOME/qce26_spool && chmod g+s $HOME/qce26_spool
    setfacl -m  g:nct_390:rwx $HOME/qce26_spool
    setfacl -d -m g:nct_390:rwx $HOME/qce26_spool
    chmod o-rwx $HOME/qce26_spool

Verified end to end on **both** clusters: students `nct01054` and `nct01120` can
write `circuit_*.pkl`; `bsc019635` reads them, writes `result_*.pkl` back and
deletes the circuit -- the listener's exact cycle. Students cannot list the home
directory itself.

---

## 1. Before the tutorial: capture the real results

Start the listener on the quantum cluster (Red):

```bash
export QDISLIB_SUBCIRCUITS_DIR=/home/bsc/bsc019635/qce26_spool
export RUNCARD_RED=/path/to/red_runcard.yml
python examples/qpu_listener.py --qpu red --nshots 1000
```

Then, on the classical side with the same `QDISLIB_SUBCIRCUITS_DIR`:

```bash
cd notebooks/QCE26
python ona_capture.py --shots 8192          # 12 fragments -> ona_results.json
```

`--max-qpu-qubits 2` restricts hardware to the six 2-qubit fragments (the
3-qubit ones then come from the simulator, and the file records that per
fragment in its `device` field).

**Until you run this, `ona_results.json` is the shipped placeholder** —
simulator values plus synthetic noise. The notebook prints the file's `source`
field verbatim, so it announces itself as `PLACEHOLDER ... NOT hardware`. After a
real capture it prints `MareNostrum Ona (Red QPU)`. Regenerate the placeholder
with `python ona_capture.py --placeholder`.

Commit the resulting `ona_results.json` alongside the notebooks so
`pycompss app deploy notebooks` ships it.

---

## 2. On the day: the live opt-in

Start the listener exactly as above and leave it running.

Attendees flip `SUBMIT_TO_ONA = True` in notebook 01 §5. Each run is **one**
hardware execution of a 2-qubit fragment. Their timeout is 300 s, so a dead
listener fails their cell in five minutes instead of hanging it.

The listener is **serial** — one circuit at a time. Thirty submissions is a few
minutes of queue; that is fine. What is *not* fine:

- the commented instructor one-liner (`qpu=True, qpu_dict={"MN_Ona": 2}`) is
  **six** executions per call — demo it once from the front, don't let the room run it;
- notebook 02 (~500 subcircuits) and notebook 03 (sampling) must never point at the QPU.

Stop the listener:

```bash
touch "$QDISLIB_SUBCIRCUITS_DIR/STOP"     # or Ctrl-C, or --idle-timeout 900
```

---

## 3. When it goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| `QPUTimeoutError` after 300 s | listener down, or a different `QDISLIB_SUBCIRCUITS_DIR` | `echo $QDISLIB_SUBCIRCUITS_DIR` on both sides; check for `circuit_*.pkl` piling up |
| `QPUExecutionError` | the listener caught a failure and reported it back | read its message; the listener itself keeps running |
| `Permission denied` writing the pickle | attendee can't write the shared dir | §0 ACL |
| `ValueError: ... $RUNCARD_RED is not set` | listener started without the runcard | export it before launching |
| `InvalidCutError` mentioning identity | an `I` observable on a cut qubit | QPUs can't decouple it — use `ZZZZZ`, no `I`, on hardware |
| Notebook says `PLACEHOLDER` | `ona_capture.py` never ran | §1 |

**Cut selection is seeded.** Notebook 01 pins `find_cut(..., seed=0)`; without it
the cut flips between `CZ_4` and `CZ_6` and the recorded per-fragment values stop
matching. `ona_capture.py` uses the same seed and the notebook asserts the cut
matches the file.

**Shots on hardware are the listener's** `--nshots`, not the notebook's
`shots=`. Expectations are normalised by the shot count the QPU actually
returned.
