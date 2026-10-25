"""Orakel-Tests mit unabhängigem Rechenweg (ORACLE-PLAYBOOK): `networkx` für die größte Komponente, eine naive Schleifen-Kaskade mit `networkx`-Teilgraphen,
die Theorie der Fixpunktgleichung gegen große Simulationen, exakte Sonderfälle (q = 0, Kopie von A)."""

import numpy as np
import pytest

import abn_algorithm as A


def nx_giant(nx, n, edges, alive):
    """Größte Komponente der lebenden Knoten mit networkx; bei Gleichstand die mit dem kleinsten Knoten (wie im Kern)."""
    g = nx.Graph()
    g.add_nodes_from(int(i) for i in np.flatnonzero(alive))
    g.add_edges_from((u, v) for u, v in edges if alive[u] and alive[v])
    comps = sorted((sorted(c) for c in nx.connected_components(g)), key=lambda c: (-len(c), c[0]))
    out = np.zeros(n, dtype=bool)
    if comps:
        out[comps[0]] = True
    return out


def naive_cascade(nx, n, ea, eb, a0, coupled):
    """Naive Kaskade: wiederholt, bis sich nichts mehr ändert, mit networkx statt der sparse-Komponenten."""
    a, b = a0.copy(), np.ones(n, dtype=bool)
    while True:
        a1 = nx_giant(nx, n, ea, a)
        b1 = b & (a1 | ~coupled)
        b2 = nx_giant(nx, n, eb, b1)
        a2 = a1 & (b2 | ~coupled)
        if (a2 == a).all() and (b2 == b).all():
            return a2, b2
        a, b = a2, b2


def test_giant_mask_equals_networkx_on_random_subgraphs():
    nx = pytest.importorskip("networkx")
    rng = np.random.default_rng(1)
    for n, c in ((30, 1.5), (60, 2.0), (80, 3.0)):
        edges = A.er_edges(n, c, rng)
        adj = A.adjacency(n, edges)
        for _ in range(10):
            alive = rng.random(n) < 0.7
            assert (A.giant_mask(adj, alive) == nx_giant(nx, n, edges, alive)).all()


def test_cascade_equals_a_naive_networkx_cascade_on_many_small_instances():
    nx = pytest.importorskip("networkx")
    rng = np.random.default_rng(2)
    for trial in range(40):
        n = int(rng.integers(20, 50))
        ea, eb = A.er_edges(n, 3.0, rng), A.er_edges(n, 3.0, rng)
        q, p = float(rng.choice([0.0, 0.3, 0.7, 1.0])), float(rng.uniform(0.4, 1.0))
        coupled = rng.random(n) < q
        seed = 1000 + trial
        a0 = np.random.default_rng(seed).random(n) < p                    # dieselbe Ziehung, die der Kern mit gegebenem `coupled` macht
        a, b, _ = A.cascade(A.adjacency(n, ea), A.adjacency(n, eb), p, q, np.random.default_rng(seed), coupled=coupled)
        na, nb = naive_cascade(nx, n, ea, eb, a0, coupled)
        assert (a == na).all() and (b == nb).all(), trial


def test_the_final_state_is_a_fixed_point_and_the_history_only_shrinks():
    rng = np.random.default_rng(3)
    for _ in range(15):
        n = 60
        ea, eb = A.er_edges(n, 3.0, rng), A.er_edges(n, 3.0, rng)
        adj_a, adj_b = A.adjacency(n, ea), A.adjacency(n, eb)
        coupled = rng.random(n) < 0.8
        a, b, hist = A.cascade(adj_a, adj_b, 0.8, 0.8, np.random.default_rng(int(rng.integers(1 << 20))), coupled=coupled)
        a1 = A.giant_mask(adj_a, a)
        b2 = A.giant_mask(adj_b, b & (a1 | ~coupled))
        assert (a1 & (b2 | ~coupled) == a).all() and (b2 == b).all()                     # ein weiterer Schritt ändert nichts
        assert all(h1[0] <= h0[0] and h1[1] <= h0[1] for h0, h1 in zip(hist[:-1], hist[1:]))


def test_without_coupling_layer_a_is_the_ordinary_giant_of_the_surviving_nodes():
    rng = np.random.default_rng(4)
    n = 400
    ea, eb = A.er_edges(n, 2.5, rng), A.er_edges(n, 2.5, rng)
    adj_a, adj_b = A.adjacency(n, ea), A.adjacency(n, eb)
    for p in (0.5, 0.8):
        seed = int(rng.integers(1 << 20))
        a0 = np.random.default_rng(seed).random(n) < p
        a, _, _ = A.cascade(adj_a, adj_b, p, 0.0, np.random.default_rng(seed), coupled=np.zeros(n, dtype=bool))
        assert (a == A.giant_mask(adj_a, a0)).all()                                       # q = 0: gewöhnliche Perkolation


def test_a_copy_of_layer_a_adds_no_loss():
    rng = np.random.default_rng(5)
    n = 500
    ea = A.er_edges(n, 3.0, rng)
    adj = A.adjacency(n, ea)
    for p in (0.5, 0.8, 1.0):
        seed = int(rng.integers(1 << 20))
        a0 = np.random.default_rng(seed).random(n) < p
        a, b, _ = A.cascade(adj, adj, p, 1.0, np.random.default_rng(seed), coupled=np.ones(n, dtype=bool))
        assert (a == A.giant_mask(adj, a0)).all() and (b == a).all()


def test_the_fixed_point_equation_matches_large_simulations():
    n, k = 6000, 4.0
    rng = np.random.default_rng(6)
    for p, tol in ((0.8, 0.04), (0.7, 0.05), (0.95, 0.03)):
        vals = []
        for _ in range(4):
            a, b = A.adjacency(n, A.er_edges(n, k, rng)), A.adjacency(n, A.er_edges(n, k, rng))
            vals.append(A.mutual_giant(a, b, p, 1.0, rng))
        assert np.mean(vals) == pytest.approx(A.er_mutual_fixed_point(p, k), abs=tol), p


def test_below_the_critical_p_the_system_collapses_and_above_it_does_not():
    n, k = 5000, 4.0
    rng = np.random.default_rng(7)
    low, high = [], []
    for _ in range(6):
        a, b = A.adjacency(n, A.er_edges(n, k, rng)), A.adjacency(n, A.er_edges(n, k, rng))
        low.append(A.mutual_giant(a, b, 0.55, 1.0, rng))
        high.append(A.mutual_giant(a, b, 0.68, 1.0, rng))
    assert max(low) < 0.02 and min(high) > 0.3 and A.er_critical_p(k) == pytest.approx(0.614, abs=0.002)


def test_a_single_layer_matches_the_single_layer_theory():
    n, k = 6000, 4.0
    rng = np.random.default_rng(8)
    adj = A.adjacency(n, A.er_edges(n, k, rng))
    for p in (0.4, 0.6, 0.9):
        v = np.mean([A.single_layer_giant(adj, p, rng) for _ in range(6)])
        assert v == pytest.approx(A.er_single_fixed_point(p, k), abs=0.03)


def test_the_lattice_layers_match_the_known_site_percolation_threshold():
    """Eine einzelne Gitterschicht hat ihre Schwelle bei p ≈ 0,593 (Platzperkolation auf dem Quadratgitter, Zahl aus dem Gedächtnis): darunter keine, deutlich darüber eine Riesenkomponente."""
    adj = A.adjacency(70 * 70, A.lattice_edges(70))
    rng = np.random.default_rng(9)
    assert np.mean([A.single_layer_giant(adj, 0.5, rng) for _ in range(5)]) < 0.1
    assert np.mean([A.single_layer_giant(adj, 0.7, rng) for _ in range(5)]) > 0.6


def test_ba_edges_match_networkx_in_hub_size():
    nx = pytest.importorskip("networkx")
    own = [max(A.adjacency(300, A.ba_edges(300, 2, np.random.default_rng(s))).sum(axis=1).A1) for s in range(8)]
    ref = [max(d for _, d in nx.barabasi_albert_graph(300, 2, seed=s).degree()) for s in range(8)]
    assert abs(np.mean(own) - np.mean(ref)) < 0.4 * np.mean(ref)
    assert len(A.ba_edges(300, 2, np.random.default_rng(1))) == 3 + 297 * 2          # Startgraph vollständig auf m + 1 Knoten (networkx startet mit einem Stern: eine Kante weniger)
