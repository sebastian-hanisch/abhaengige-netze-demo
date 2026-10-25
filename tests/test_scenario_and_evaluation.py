"""Szenario und Auswertung: Schichtpaare, Determinismus, Konsistenz der Kennzahlen, Hilfsfunktionen der Reihen, Messreihen (Struktur und Richtung), feste Pläne."""

import numpy as np
import pytest

import abn_algorithm as A
import abn_constants as C
import abn_evaluation as ev
from abn_scenario import layer_edges, make_pair


def test_layer_edges_by_hand():
    rng = np.random.default_rng(1)
    n, e = layer_edges("er", 500, 4.0, rng)
    assert n == 500 and len(e) == 1000
    n, e = layer_edges("ba", 500, 4.0, rng)
    assert n == 500 and len(e) == 3 + 497 * 2                                         # m = 2
    n, e = layer_edges("ba", 500, 2.0, rng)
    assert len(e) == 1 + 498 * 1                                                      # m = 1 (c = 2): ein Baum auf 500 Knoten
    n, e = layer_edges("lattice", 3000, 4.0, rng)
    assert n == 55 * 55 and len(e) == 2 * n                                           # round(√3000) = 55, jeder Knoten Grad 4
    with pytest.raises(ValueError):
        layer_edges("x", 10, 4.0, rng)


def test_make_pair_by_hand():
    n, ea, eb = make_pair("er", "independent", 400, 4.0, 1)
    assert n == 400 and ea != eb and len(ea) == len(eb) == 800 and (n, ea, eb) == make_pair("er", "independent", 400, 4.0, 1)
    n, ea, eb = make_pair("er", "copy", 400, 4.0, 1)
    assert ea == eb
    n, ea, eb = make_pair("lattice", "independent", 400, 4.0, 1)
    assert n == 400 and ea != eb and sorted(A.degrees_of(n, ea)) == sorted(A.degrees_of(n, eb)) == [4] * 400                    # dasselbe Gitter, zufällig umnummeriert
    assert make_pair("lattice", "copy", 400, 4.0, 1)[1] == make_pair("lattice", "copy", 400, 4.0, 1)[2]
    assert make_pair("er", "independent", 400, 4.0, 1)[1] != make_pair("er", "independent", 400, 4.0, 2)[1]
    with pytest.raises(ValueError):
        make_pair("er", "x", 100, 4.0, 1)


def test_analyse_is_deterministic_and_consistent():
    s = ev.Settings(layer="er", n=1500, p=0.8, seed=3)
    a, b = ev.analyse(s), ev.analyse(s)
    assert a.history == b.history and a.final_a == b.final_a and a.rounds == len(a.history) - 1
    assert a.history[0][1] == a.n and a.history[0][0] == pytest.approx(0.8 * 1500, rel=0.08)                           # anfangs bleiben etwa p der Knoten von A, ganz B
    assert a.final_a == a.history[-1][0] / a.n and a.final_b == a.history[-1][1] / a.n and a.mean_degree == pytest.approx(4.0)
    assert a.theory == pytest.approx(A.er_mutual_fixed_point(0.8, 4.0))
    assert a.final_a == pytest.approx(a.theory, abs=0.08) and a.final_a < a.single


def test_theory_only_for_two_independent_random_networks_with_full_coupling():
    assert ev.analyse(ev.Settings(layer="ba", n=1000)).theory is None
    assert ev.analyse(ev.Settings(layer="er", n=1000, q=0.9)).theory is None
    assert ev.analyse(ev.Settings(layer="er", n=1000, partner="copy")).theory is None
    assert ev.analyse(ev.Settings(layer="er", n=1000)).theory is not None


def test_a_copy_loses_nothing_and_without_coupling_nothing_is_lost():
    cp = ev.analyse(ev.Settings(layer="er", partner="copy", n=1500, p=0.8, seed=2))
    assert cp.final_a == pytest.approx(cp.single, abs=0.0) or abs(cp.final_a - cp.single) < 0.06             # Kopie: wie eine einzelne Schicht (andere Ziehung für das einzelne p)
    free = ev.analyse(ev.Settings(layer="er", n=1500, p=0.8, q=0.0, seed=2))
    assert free.final_a == pytest.approx(free.single, abs=0.06)


def test_largest_step_and_onset_by_hand():
    ps, vals = [0.5, 0.6, 0.7, 0.8], [0.0, 0.02, 0.5, 0.6]
    assert ev.largest_step(ps, vals) == pytest.approx((0.48, 0.6, 0.7))
    assert ev.onset(ps, vals) == 0.7 and ev.onset(ps, vals, 0.01) == 0.6 and ev.onset(ps, [0.0, 0.0], 0.05) is None and ev.onset([0.3, 0.4], [0.05, 0.1]) == 0.3


def test_curve_structure_and_direction():
    r = ev.curve("er", "independent", 1.0, runs=2, ps=(0.4, 0.5, 0.6, 0.7, 0.8, 0.9), side=30)
    assert r["n"] == 900 and r["ps"] == [0.4, 0.5, 0.6, 0.7, 0.8, 0.9] and len(r["mutual"]) == len(r["single"]) == 6 and r["runs"] == 2
    assert r["mutual"][0] < 0.01 and r["mutual"][-1] > 0.7 and all(m <= s + 0.06 for m, s in zip(r["mutual"], r["single"]))
    assert r["step"] == pytest.approx(max(np.diff(r["mutual"]))) and r["abrupt"] == (r["step"] >= C.ABRUPT_STEP) and r["onset"] in r["ps"]
    assert r["step_to"] > r["step_from"]


def test_series_structure():
    rows = ev.series_layers(runs=2, ps=(0.5, 0.7, 0.9), side=20)
    assert [(r["layer"], r["partner"]) for r in rows] == [("er", "independent"), ("ba", "independent"), ("lattice", "independent"), ("lattice", "copy")]
    assert [r["name"] for r in rows] == ["Zufallsnetze", "skalenfreie Netze", "Gitter, zufällig gekoppelt", "Gitter als Kopie"]
    rows = ev.series_coupling(qs=(0.0, 1.0), runs=2, ps=(0.5, 0.9), side=20)
    assert [r["q"] for r in rows] == [0.0, 1.0] and [r["name"] for r in rows] == ["q = 0,00", "q = 1,00"] and all(r["layer"] == "er" for r in rows)


def test_the_fixed_plans_and_defaults_are_the_documented_ones():
    assert C.SERIES_SEED == 100000 and C.SERIES_SIDE == 70 and C.SERIES_C == 4.0 and C.SERIES_RUNS == 8 and C.SERIES_QS == (0.0, 0.25, 0.5, 0.75, 1.0)
    assert C.SERIES_PS[0] == 0.3 and C.SERIES_PS[-1] == 1.0 and len(C.SERIES_PS) == 29 and C.SERIES_PS[1] == 0.325
    s = ev.Settings()
    assert (s.layer, s.partner, s.n, s.c, s.q, s.p, s.seed) == ("er", "independent", 3000, 4.0, 1.0, 0.7, 35) and (C.COLLAPSE_BELOW, C.ABRUPT_STEP) == (0.01, 0.2)
