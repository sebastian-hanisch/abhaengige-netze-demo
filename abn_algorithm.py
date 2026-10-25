"""Kern: zwei Netzschichten mit Abhängigkeitskanten (Buldyrev-Modell) und die Kaskade, die nach dem Ausfall eines Teils der Knoten entsteht.

Beide Schichten haben dieselben n Knoten; Knoten i der Schicht A und Knoten i der Schicht B bilden ein Paar. Ein Paar ist mit Wahrscheinlichkeit q **gekoppelt**:
fällt ein Partner aus, fällt auch der andere aus. Ein Knoten gilt als lebendig, wenn er in der größten Zusammenhangskomponente seiner Schicht unter den lebenden Knoten liegt
(und, wenn er gekoppelt ist, sein Partner ebenfalls). Anfangs bleiben die Knoten der Schicht A mit Wahrscheinlichkeit p erhalten, die der Schicht B alle; dann wechseln
sich die beiden Schichten ab, bis sich nichts mehr ändert. Bei q = 1 ist das die **gegenseitig verbundene Riesenkomponente**."""

import math

import numpy as np
from scipy import sparse
from scipy.sparse import csgraph


# --- Schichten -------------------------------------------------------------------------------------------------------------------------------


def normalize(edges):
    """Kanten als sortierte Paare (u < v), ohne Schleifen und Doppelte, aufsteigend sortiert."""
    return sorted({(min(int(u), int(v)), max(int(u), int(v))) for u, v in edges if int(u) != int(v)})


def er_edges(n: int, c: float, rng: np.random.Generator):
    """Erdős–Rényi-Schicht G(n, m) mit m = round(c · n / 2) Kanten (mittlerer Grad c)."""
    m = min(int(round(c * n / 2.0)), n * (n - 1) // 2)
    out = set()
    while len(out) < m:
        need = m - len(out)
        a = rng.integers(0, n, size=2 * need + 8)
        b = rng.integers(0, n, size=2 * need + 8)
        for u, v in zip(a, b):
            if u != v:
                out.add((min(int(u), int(v)), max(int(u), int(v))))
                if len(out) == m:
                    break
    return sorted(out)


def ba_edges(n: int, m: int, rng: np.random.Generator):
    """Barabási–Albert-Schicht (m + 1 Startknoten als vollständiger Graph, jeder neue Knoten wählt m verschiedene Enden aus der Liste der Kantenenden); mittlerer Grad etwa 2m."""
    n = max(n, m + 1)
    ends: list[int] = []
    edges = []
    for u in range(m + 1):
        for v in range(u):
            ends += [u, v]
            edges.append((v, u))
    for t in range(m + 1, n):
        chosen: list[int] = []
        while len(chosen) < m:
            v = ends[int(rng.integers(0, len(ends)))]
            if v not in chosen:
                chosen.append(v)
        for v in chosen:
            ends += [v, t]
            edges.append((v, t))
    return normalize(edges)


def lattice_edges(side: int):
    """Quadratisches Gitter side × side mit Rand rund um (Torus), jeder Knoten mit seinen vier Nachbarn; Knoten x · side + y."""
    out = set()
    for x in range(side):
        for y in range(side):
            u = x * side + y
            for v in (((x + 1) % side) * side + y, x * side + (y + 1) % side):
                if u != v:
                    out.add((min(u, v), max(u, v)))
    return sorted(out)


def relabel(edges, perm):
    """Kanten nach Umnummerierung der Knoten: Knoten i heißt danach perm[i]."""
    return normalize((int(perm[u]), int(perm[v])) for u, v in edges)


def adjacency(n: int, edges):
    e = np.asarray(edges, dtype=int).reshape(-1, 2)
    a = sparse.coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n))
    return (a + a.T).tocsr()


def mean_degree(n: int, edges) -> float:
    return 2.0 * len(edges) / n


# --- Kaskade ---------------------------------------------------------------------------------------------------------------------------------


def giant_mask(adj, alive):
    """Wahrheitswerte der Knoten in der größten Zusammenhangskomponente des von den lebenden Knoten aufgespannten Teilgraphen (bei Gleichstand die mit dem kleinsten Knoten)."""
    alive = np.asarray(alive, dtype=bool)
    idx = np.flatnonzero(alive)
    out = np.zeros(len(alive), dtype=bool)
    if len(idx) == 0:
        return out
    _, labels = csgraph.connected_components(adj[idx][:, idx], directed=False)
    out[idx[labels == int(np.argmax(np.bincount(labels)))]] = True
    return out


def single_layer_giant(adj, p: float, rng: np.random.Generator) -> float:
    """Anteil der Knoten in der größten Komponente einer einzelnen Schicht, wenn jeder Knoten mit Wahrscheinlichkeit p erhalten bleibt (Platzperkolation)."""
    n = adj.shape[0]
    return float(giant_mask(adj, rng.random(n) < p).sum() / n)


def cascade(adj_a, adj_b, p: float, q: float, rng: np.random.Generator, coupled=None, max_rounds: int = 10_000):
    """Kaskade nach dem Ausfall von Knoten der Schicht A. Rückgabe: (a, b, history) mit den lebenden Knoten beider Schichten am Ende und der Liste der Zahlen (lebende in A, lebende in B)
    nach jeder Runde (die erste Zahl vor der ersten Runde). `coupled` (Wahrheitswerte je Paar) ersetzt die Ziehung mit Wahrscheinlichkeit q."""
    n = adj_a.shape[0]
    if coupled is None:
        coupled = rng.random(n) < q
    a = rng.random(n) < p
    b = np.ones(n, dtype=bool)
    history = [(int(a.sum()), int(b.sum()))]
    for _ in range(max_rounds):
        a1 = giant_mask(adj_a, a)
        b1 = b & (a1 | ~coupled)
        b2 = giant_mask(adj_b, b1)
        a2 = a1 & (b2 | ~coupled)
        history.append((int(a2.sum()), int(b2.sum())))
        if (a2 == a).all() and (b2 == b).all():
            break
        a, b = a2, b2
    return a2, b2, history


def mutual_giant(adj_a, adj_b, p: float, q: float, rng: np.random.Generator) -> float:
    """Anteil der Knoten der Schicht A, die am Ende der Kaskade leben."""
    a, _, _ = cascade(adj_a, adj_b, p, q, rng)
    return float(a.sum() / adj_a.shape[0])


# --- Theorie (zwei Erdős–Rényi-Schichten mit gleichem mittleren Grad, q = 1) ------------------------------------------------------------------


def er_mutual_fixed_point(p: float, k: float, iterations: int = 5000) -> float:
    """Größte Lösung von x = p (1 − e^(−k x))²: Anteil der gegenseitig verbundenen Riesenkomponente für n → ∞ (Iteration von x = 1 abwärts; null, wenn nur die triviale Lösung bleibt)."""
    x = 1.0
    for _ in range(iterations):
        nxt = p * (1.0 - math.exp(-k * x)) ** 2
        if abs(nxt - x) < 1e-13:
            x = nxt
            break
        x = nxt
    return x if x > 1e-4 else 0.0


def er_critical_p(k: float) -> float:
    """Kleinster Anteil p, bei dem `er_mutual_fixed_point` eine nichttriviale Lösung hat (Bisektion): der Übergang ist ein Sprung."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if er_mutual_fixed_point(mid, k) > 0.0:
            hi = mid
        else:
            lo = mid
    return hi


def er_single_fixed_point(p: float, k: float) -> float:
    """Anteil der Knoten in der Riesenkomponente einer einzelnen Erdős–Rényi-Schicht bei Platzperkolation mit Erhaltungswahrscheinlichkeit p: p · S mit S = 1 − e^(−p k S)."""
    s = 1.0
    for _ in range(20000):
        nxt = 1.0 - math.exp(-p * k * s)
        if abs(nxt - s) < 1e-13:
            s = nxt
            break
        s = nxt
    return p * s if s > 1e-6 else 0.0


def degrees_of(n: int, edges):
    """Grade aller Knoten als Liste."""
    return np.bincount(np.asarray(edges, dtype=int).ravel(), minlength=n).tolist()
