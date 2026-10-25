"""Einmalige Messung der README-Zahlen (nicht Teil der App): feste Pläne, Ausgabe auf stdout."""

import sys
import time

import numpy as np

sys.path.insert(0, ".")
import abn_algorithm as A
import abn_constants as C
import abn_evaluation as ev

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

t0 = time.time()
print("PRESETS")
for name, p in C.PRESETS.items():
    a = ev.analyse(ev.Settings(**p))
    print(name, "n", a.n, "Runden", a.rounds, "A", round(a.final_a, 3), "B", round(a.final_b, 3), "einzeln", round(a.single, 3),
          "Theorie", None if a.theory is None else round(a.theory, 3), "Start", a.history[0], ev.verdict_state(a)[0])

print("THEORIE")
for k in (3.0, 4.0, 6.0, 8.0):
    print("k", k, "p_c gekoppelt", round(A.er_critical_p(k), 4), "p_c * k", round(A.er_critical_p(k) * k, 4))

print("SEEDS nahe der Schwelle (ER, n=3500, c=4, q=1)")
for p in (0.55, 0.60, 0.65, 0.70):
    outs = [round(ev.analyse(ev.Settings(n=3500, p=p, seed=s)).final_a, 3) for s in range(1, 13)]
    print("p", p, outs, "Zusammenbrüche", sum(o < C.COLLAPSE_BELOW for o in outs))

print("RUNDEN (ER, p=0.7, Seeds 1-12)")
rounds = [ev.analyse(ev.Settings(p=0.7, seed=s)).rounds for s in range(1, 13)]
print(rounds, "min", min(rounds), "max", max(rounds))

print("SERIE SCHICHTEN")
for r in ev.series_layers():
    print(ev.curve_row(r), "step", round(r["step"], 3), "von", r["step_from"], "bis", r["step_to"], "n", r["n"])
print("SERIE KOPPLUNG")
for r in ev.series_coupling():
    print(ev.curve_row(r), "q", r["q"], "step", round(r["step"], 3), "von", r["step_from"], "bis", r["step_to"])
print("sec", round(time.time() - t0, 1))
