"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, keiner auf einem Reglerrand und keiner, der durch eine einzelne Regleränderung vom Standard entsteht."""

import abn_constants as C
import abn_evaluation as ev
import abn_presets as P

FIRST = "Zwei Zufallsnetze, p = 0,70"


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, p in C.PRESETS.items():
        assert p["layer"] in C.LAYERS and p["partner"] in C.PARTNERS and C.N_MIN <= p["n"] <= C.N_MAX and C.C_MIN <= p["c"] <= C.C_MAX, name
        assert C.Q_MIN <= p["q"] <= C.Q_MAX and C.P_MIN <= p["p"] <= C.P_MAX and 0 <= p["seed"] <= C.SEED_MAX, name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[FIRST]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_no_preset_sits_on_a_slider_bound():
    bounds = {"n": (C.N_MIN, C.N_MAX), "c": (C.C_MIN, C.C_MAX), "q": (C.Q_MIN, C.Q_MAX), "p": (C.P_MIN, C.P_MAX)}
    for name, preset in C.PRESETS.items():
        for key, (lo, hi) in bounds.items():
            if key == "q" and preset[key] == C.DEFAULT_Q:
                continue                      # q = 1 ist der Standard und zugleich der obere Rand; der Layout-Test setzt dann den unteren Rand
            assert preset[key] not in (lo, hi), (name, key)


def test_no_single_change_of_the_default_produces_another_preset():
    default = C.PRESETS[FIRST]
    for name, p in C.PRESETS.items():
        if name != FIRST:
            assert sum(1 for k in p if p[k] != default[k]) >= 2, name


def test_presets_are_pairwise_different_and_cover_the_findings():
    values = [tuple(sorted(p.items())) for p in C.PRESETS.values()]
    assert len(set(values)) == len(values)
    assert {(p["layer"], p["partner"]) for p in C.PRESETS.values()} == {("er", "independent"), ("ba", "independent"), ("lattice", "independent"), ("lattice", "copy")}


def test_slider_steps_reach_the_presets():
    for name, p in C.PRESETS.items():
        for value, lo, step in ((p["n"], C.N_MIN, 500), (p["c"], C.C_MIN, 0.5), (p["q"], C.Q_MIN, 0.05), (p["p"], C.P_MIN, 0.01)):
            k = (value - lo) / step
            assert abs(k - round(k)) < 1e-9, (name, value)
