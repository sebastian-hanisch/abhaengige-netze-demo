"""Kern: jede Einheit an einer Mini-Instanz von Hand (DEMO-PLAYBOOK §1b)."""

import numpy as np
import pytest

import abn_algorithm as A


def test_normalize_and_relabel_by_hand():
    assert A.normalize([(3, 1), (1, 3), (2, 2), (0, 1)]) == [(0, 1), (1, 3)]
    assert A.relabel([(0, 1), (1, 2)], [2, 0, 1]) == [(0, 1), (0, 2)]               # 0 → 2, 1 → 0, 2 → 1: (0,1) wird (2,0), (1,2) wird (0,1)


def test_adjacency_and_mean_degree_by_hand():
    a = A.adjacency(4, [(0, 1), (1, 2)])
    assert a.toarray().tolist() == [[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]]
    assert A.mean_degree(4, [(0, 1), (1, 2)]) == 1.0 and A.mean_degree(10, [(0, 1)] * 5) == 1.0


def test_layer_sizes_by_hand():
    rng = np.random.default_rng(1)
    assert len(A.er_edges(100, 4.0, rng)) == 200 and len(set(A.er_edges(100, 4.0, rng))) == 200
    assert len(A.er_edges(5, 100.0, rng)) == 10                                       # höchstens alle Paare
    ba = A.ba_edges(50, 3, rng)
    assert len(ba) == 6 + 46 * 3 and len(set(ba)) == len(ba)
    lat = A.lattice_edges(4)
    assert len(lat) == 32 and set(A.adjacency(16, lat).sum(axis=1).A1) == {4.0}      # Torus: jeder Knoten hat Grad 4
    assert len(A.lattice_edges(3)) == 18
    assert lat[:4] == [(0, 1), (0, 3), (0, 4), (0, 12)]                               # aufsteigend sortiert; Knoten 0 hat die Nachbarn 1, 3 (über den Rand), 4 und 12 (über den Rand)


def test_giant_mask_by_hand():
    adj = A.adjacency(5, [(0, 1), (1, 2), (3, 4)])
    assert A.giant_mask(adj, np.ones(5, dtype=bool)).tolist() == [True, True, True, False, False]
    assert A.giant_mask(adj, [True, False, True, True, True]).tolist() == [False, False, False, True, True]       # ohne Knoten 1 sind {0}, {2}, {3, 4} übrig
    assert A.giant_mask(adj, np.zeros(5, dtype=bool)).tolist() == [False] * 5
    tie = A.adjacency(4, [(0, 1), (2, 3)])
    assert A.giant_mask(tie, np.ones(4, dtype=bool)).tolist() == [True, True, False, False]                       # Gleichstand: kleinster Knoten


def test_single_layer_giant_by_hand(path_a):
    assert A.single_layer_giant(path_a, 1.0, np.random.default_rng(1)) == 1.0
    assert A.single_layer_giant(path_a, 0.0, np.random.default_rng(1)) == 0.0


def test_cascade_with_fully_coupled_pairs_by_hand(path_a, two_pairs_b):
    a, b, hist = A.cascade(path_a, two_pairs_b, 1.0, 1.0, np.random.default_rng(1), coupled=np.ones(4, dtype=bool))
    # Runde 1: A ganz lebendig, B zerfällt in {0,1} und {2,3}, die Gleichstandsregel behält {0,1}, A verliert 2 und 3; Runde 2: nichts ändert sich mehr
    assert a.tolist() == [True, True, False, False] and b.tolist() == [True, True, False, False]
    assert hist == [(4, 4), (2, 2), (2, 2)]


def test_cascade_without_coupling_leaves_layer_a_alone(path_a, two_pairs_b):
    a, b, hist = A.cascade(path_a, two_pairs_b, 1.0, 0.0, np.random.default_rng(1), coupled=np.zeros(4, dtype=bool))
    assert a.tolist() == [True] * 4 and b.tolist() == [True, True, False, False] and hist[-1] == (4, 2) and hist[0] == (4, 4)


def test_cascade_draws_the_coupling_with_probability_q(path_a, two_pairs_b):
    a1, _, _ = A.cascade(path_a, two_pairs_b, 1.0, 1.0, np.random.default_rng(3))
    a0, _, _ = A.cascade(path_a, two_pairs_b, 1.0, 0.0, np.random.default_rng(3))
    assert a1.sum() == 2 and a0.sum() == 4                                           # q = 1 koppelt alle Paare, q = 0 keines


def test_cascade_is_deterministic_per_seed(path_a, two_pairs_b):
    r1 = A.cascade(path_a, two_pairs_b, 0.7, 0.5, np.random.default_rng(5))
    r2 = A.cascade(path_a, two_pairs_b, 0.7, 0.5, np.random.default_rng(5))
    assert (r1[0] == r2[0]).all() and (r1[1] == r2[1]).all() and r1[2] == r2[2]


def test_mutual_giant_is_the_fraction_alive_in_a(path_a, two_pairs_b):
    assert A.mutual_giant(path_a, two_pairs_b, 1.0, 1.0, np.random.default_rng(1)) == 0.5
    assert A.mutual_giant(path_a, two_pairs_b, 1.0, 0.0, np.random.default_rng(1)) == 1.0


def test_theory_by_hand():
    assert A.er_mutual_fixed_point(1.0, 50.0) == pytest.approx(1.0, abs=1e-9)         # (1 − e^(−50))² = 1
    assert A.er_mutual_fixed_point(0.5, 50.0) == pytest.approx(0.5, abs=1e-9)
    assert A.er_mutual_fixed_point(0.5, 4.0) == 0.0                                    # unter der Schwelle nur die triviale Lösung
    x = A.er_mutual_fixed_point(0.8, 4.0)
    assert x == pytest.approx(0.8 * (1 - np.exp(-4 * x)) ** 2, abs=1e-9) and 0.7 < x < 0.72
    assert A.er_single_fixed_point(1.0, 4.0) == pytest.approx(0.9802, abs=1e-3)       # S = 1 − e^(−4 S)
    assert A.er_single_fixed_point(0.2, 4.0) == 0.0                                    # p k = 0,8 < 1: keine Riesenkomponente
    s = A.er_single_fixed_point(0.5, 4.0)
    assert s == pytest.approx(0.5 * (1 - np.exp(-0.5 * 4 * s / 0.5)), abs=1e-6)


def test_critical_p_is_the_start_of_the_nontrivial_solution():
    pc = A.er_critical_p(4.0)
    assert A.er_mutual_fixed_point(pc + 1e-6, 4.0) > 0 and A.er_mutual_fixed_point(pc - 1e-3, 4.0) == 0.0
    assert pc == pytest.approx(0.6139, abs=1e-3)                                       # 2,4554 / 4 (Zahl aus dem Gedächtnis, hier gerechnet)
    assert A.er_critical_p(6.0) == pytest.approx(2.4554 / 6, abs=1e-3)
    assert A.er_critical_p(2.0) > A.er_critical_p(4.0) > A.er_critical_p(8.0)
