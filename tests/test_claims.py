"""Befunde der README als Bänder: jede Zahl, die dort steht, ist hier an einem festen Plan geprüft (Seeds und Pläne wie in messen.py)."""

import pytest

import abn_algorithm as A
import abn_constants as C
import abn_evaluation as ev


@pytest.fixture(scope="module")
def layers():
    return {r["name"]: r for r in ev.series_layers()}


@pytest.fixture(scope="module")
def coupling():
    return {r["q"]: r for r in ev.series_coupling()}


def analyse(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


def test_theory_threshold_is_a_constant_over_the_mean_degree():
    for k in (3.0, 4.0, 6.0, 8.0):
        assert A.er_critical_p(k) * k == pytest.approx(2.4554, abs=2e-4)
    assert A.er_critical_p(4.0) == pytest.approx(0.6139, abs=5e-4)


def test_default_preset_loses_a_sixth_to_a_fifth_of_the_single_layer():
    a = analyse("Zwei Zufallsnetze, p = 0,70")
    assert a.n == 3000 and 4 <= a.rounds <= 5
    assert a.final_a == pytest.approx(0.54, abs=0.02) and a.final_a == a.final_b and a.single == pytest.approx(0.639, abs=0.01)
    assert a.theory == pytest.approx(0.558, abs=0.001) and ev.verdict_state(a)[0] == "info"


def test_the_collapse_presets_collapse_and_the_copy_does_not():
    assert analyse("Zwei Zufallsnetze, p = 0,55").final_a < C.COLLAPSE_BELOW and analyse("Zwei Zufallsnetze, p = 0,55").single == pytest.approx(0.449, abs=0.01)
    lat = analyse("Gitter, zufällig gekoppelt, p = 0,65")
    assert lat.n == 3481 and lat.final_a < C.COLLAPSE_BELOW and lat.single == pytest.approx(0.611, abs=0.01)
    cp = analyse("Gitter als Kopie, p = 0,65")
    assert cp.rounds == 2 and cp.final_a == pytest.approx(cp.single, abs=0.01) and ev.verdict_state(cp)[0] == "success"
    ba = analyse("Skalenfreie Schichten, p = 0,55")
    assert ba.final_a == pytest.approx(0.315, abs=0.02) and ba.single == pytest.approx(0.454, abs=0.01) and ba.theory is None


def test_the_preset_below_threshold_collapses_for_every_seed_but_just_above_it_is_bimodal():
    below = [ev.analyse(ev.Settings(n=3500, p=0.55, seed=s)).final_a for s in range(1, 13)]
    assert max(below) < C.COLLAPSE_BELOW
    near = [ev.analyse(ev.Settings(n=3500, p=0.60, seed=s)).final_a for s in range(1, 13)]
    assert sum(x < C.COLLAPSE_BELOW for x in near) == 9 and all(0.33 < x < 0.38 for x in near if x >= C.COLLAPSE_BELOW)     # entweder kein Kern oder einer von rund einem Drittel
    above = [ev.analyse(ev.Settings(n=3500, p=0.65, seed=s)).final_a for s in range(1, 13)]
    assert all(0.40 < x < 0.50 for x in above)


def test_series_er_is_abrupt_near_the_theory_threshold(layers):
    r = layers["Zufallsnetze"]
    assert r["n"] == 4900 and r["abrupt"] and r["step"] == pytest.approx(0.30, abs=0.03) and (r["step_from"], r["step_to"]) == (0.6, 0.625)
    assert r["onset"] == 0.625 and r["mutual"][-1] == pytest.approx(0.96, abs=0.01) and A.er_critical_p(4.0) == pytest.approx(0.614, abs=0.001)


def test_series_scale_free_layers_are_continuous(layers):
    r = layers["skalenfreie Netze"]
    assert not r["abrupt"] and r["step"] == pytest.approx(0.07, abs=0.02) and r["onset"] == 0.425 and r["mutual"][-1] > 0.99


def test_series_lattice_depends_on_the_coupling(layers):
    rnd, cp = layers["Gitter, zufällig gekoppelt"], layers["Gitter als Kopie"]
    assert rnd["abrupt"] and rnd["step"] == pytest.approx(0.38, abs=0.04) and (rnd["step_from"], rnd["step_to"]) == (0.65, 0.675) and rnd["onset"] == 0.675
    assert not cp["abrupt"] and cp["step"] == pytest.approx(0.17, abs=0.03) and cp["onset"] == 0.525
    assert cp["step"] < C.ABRUPT_STEP < rnd["step"]                                                    # die Kopie liegt dicht an der Schwelle der Einstufung (Konvention)


def test_series_coupling_is_abrupt_only_with_full_coupling(coupling):
    assert [q for q, r in coupling.items() if r["abrupt"]] == [1.0]
    for q in (0.0, 0.25, 0.5, 0.75):
        assert coupling[q]["step"] < 0.12, q
    assert coupling[1.0]["step"] == pytest.approx(0.30, abs=0.03)
    assert coupling[0.0]["onset"] == 0.3 and coupling[1.0]["onset"] == 0.625
    onsets = [coupling[q]["onset"] for q in C.SERIES_QS]
    assert onsets == sorted(onsets)                                                                    # je stärker die Kopplung, desto später der Einsatz


def test_the_single_layer_threshold_is_far_below_the_coupled_one(layers):
    r = layers["Zufallsnetze"]
    assert r["single"][0] > 0.05 and r["mutual"][0] < 0.01                                               # schon bei p = 0,30 (> 1/k = 0,25) trägt eine einzelne Schicht, gekoppelt bricht alles zusammen
    assert A.er_single_fixed_point(0.3, 4.0) == pytest.approx(r["single"][0], abs=0.05)


def test_the_series_take_a_few_seconds_each():
    import time

    t = time.time()
    ev.series_layers(runs=1, ps=(0.5, 0.7), side=30)
    assert time.time() - t < 30
