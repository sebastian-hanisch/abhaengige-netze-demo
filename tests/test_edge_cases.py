"""Randfälle: kleinste und größte Reglerwerte für jede Schichtart, p = 1, nichts überlebt, kleines Gitter, Netze ohne Kanten."""

import numpy as np

import abn_algorithm as A
import abn_constants as C
import abn_evaluation as ev


def test_every_layer_and_partner_at_the_extreme_settings():
    for layer in C.LAYERS:
        for partner in C.PARTNERS:
            for n, c, q, p in ((C.N_MIN, C.C_MIN, C.Q_MIN, C.P_MIN), (C.N_MIN, C.C_MAX, C.Q_MAX, C.P_MAX), (C.N_MAX, C.C_MIN, C.Q_MAX, C.P_MIN)):
                a = ev.analyse(ev.Settings(layer=layer, partner=partner, n=n, c=c, q=q, p=p, seed=1))
                assert 0.0 <= a.final_a <= 1.0 and 0.0 <= a.final_b <= 1.0 and a.rounds >= 1 and a.history[-1] == a.history[-2] and ev.verdict_state(a)[0] in ("success", "info", "warning"), (layer, partner, n, c, q, p)


def test_with_everything_surviving_the_cascade_stops_after_one_round_for_connected_layers():
    n = 400
    edges = A.er_edges(n, 8.0, np.random.default_rng(1))
    adj = A.adjacency(n, edges)
    a, b, hist = A.cascade(adj, adj, 1.0, 1.0, np.random.default_rng(1))
    assert len(hist) == 2 and hist[0] == hist[1] and a.sum() == b.sum() == A.giant_mask(adj, np.ones(n, dtype=bool)).sum()


def test_nothing_survives_when_the_survival_share_is_zero():
    n = 100
    adj = A.adjacency(n, A.er_edges(n, 4.0, np.random.default_rng(1)))
    a, b, hist = A.cascade(adj, adj, 0.0, 1.0, np.random.default_rng(1))
    assert a.sum() == 0 and b.sum() == 0 and hist[0] == (0, 100) and hist[-1] == (0, 0)
    a, b, _ = A.cascade(adj, adj, 0.0, 0.0, np.random.default_rng(1))
    assert a.sum() == 0 and b.sum() == A.giant_mask(adj, np.ones(n, dtype=bool)).sum()           # ohne Kopplung bleibt B unberührt


def test_layers_without_edges_leave_nothing_but_single_nodes():
    adj = A.adjacency(5, [])
    assert A.giant_mask(adj, np.ones(5, dtype=bool)).sum() == 1                                    # eine einzelne Komponente aus einem Knoten
    a, b, hist = A.cascade(adj, adj, 1.0, 1.0, np.random.default_rng(1), coupled=np.ones(5, dtype=bool))
    assert a.sum() == 1 and b.sum() == 1 and hist[-1] == (1, 1)


def test_the_smallest_lattice_runs():
    adj = A.adjacency(9, A.lattice_edges(3))
    a, b, _ = A.cascade(adj, adj, 1.0, 1.0, np.random.default_rng(1))
    assert a.sum() == 9 and b.sum() == 9


def test_max_rounds_guard_returns_a_state():
    n = 60
    adj = A.adjacency(n, A.er_edges(n, 3.0, np.random.default_rng(2)))
    a, b, hist = A.cascade(adj, adj, 0.8, 1.0, np.random.default_rng(3), max_rounds=1)
    assert len(hist) == 2 and len(a) == n and len(b) == n
