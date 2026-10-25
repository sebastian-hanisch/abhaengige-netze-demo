"""Kennzahlen, Messreihen und Verdikte (reine Funktionen: die App ruft st.<Art>(Text), die Tests prüfen jede Zahl im Text)."""

from dataclasses import dataclass

import numpy as np

import abn_algorithm as A
import abn_constants as C
from abn_scenario import make_pair


def num(x: float, digits: int = 1) -> str:
    """Zahl mit Dezimalkomma (für Texte)."""
    return f"{x:.{digits}f}".replace(".", ",")


def pct(x: float, digits: int = 0) -> str:
    """Anteil als Prozentzahl mit Dezimalkomma, zum Beispiel 0,456 → „46 %“."""
    return f"{num(x * 100, digits)} %"


@dataclass(frozen=True)
class Settings:
    layer: str = C.DEFAULT_LAYER
    partner: str = C.DEFAULT_PARTNER
    n: int = C.DEFAULT_N
    c: float = C.DEFAULT_C
    q: float = C.DEFAULT_Q
    p: float = C.DEFAULT_P
    seed: int = C.DEFAULT_SEED


@dataclass(eq=False)
class Analysis:
    settings: Settings
    n: int
    mean_degree: float
    history: list             # [(lebende in A, lebende in B)] vor und nach jeder Runde
    final_a: float            # Anteil lebender Knoten in A am Ende
    final_b: float
    single: float             # Anteil in der größten Komponente einer einzelnen Schicht bei demselben p
    theory: float | None      # Theorie für n → ∞ (zwei unabhängige Zufallsnetze, q = 1), sonst None

    @property
    def rounds(self) -> int:
        return len(self.history) - 1


def analyse(s: Settings) -> Analysis:
    n, ea, eb = make_pair(s.layer, s.partner, s.n, s.c, s.seed)
    adj_a, adj_b = A.adjacency(n, ea), A.adjacency(n, eb)
    rng = np.random.default_rng(s.seed + 1)
    a, b, hist = A.cascade(adj_a, adj_b, s.p, s.q, rng)
    single = A.single_layer_giant(adj_a, s.p, np.random.default_rng(s.seed + 2))
    k = A.mean_degree(n, ea)
    theory = A.er_mutual_fixed_point(s.p, k) if (s.layer == "er" and s.partner == "independent" and s.q == 1.0) else None
    return Analysis(s, n, k, hist, float(a.sum() / n), float(b.sum() / n), single, theory)


# --- Messreihen ------------------------------------------------------------------------------------------------------------------------------


def largest_step(ps, values) -> tuple[float, float, float]:
    """Größter Anstieg zwischen zwei benachbarten Werten: (Höhe, p davor, p danach)."""
    d = np.diff(np.asarray(values, dtype=float))
    i = int(np.argmax(d))
    return float(d[i]), float(ps[i]), float(ps[i + 1])


def onset(ps, values, threshold: float = 0.05):
    """Kleinstes p, bei dem der Mittelwert mindestens `threshold` erreicht (None, wenn nie)."""
    for p, v in zip(ps, values):
        if v >= threshold:
            return float(p)
    return None


def curve(layer: str, partner: str, q: float, runs: int = C.SERIES_RUNS, ps=C.SERIES_PS, side: int = C.SERIES_SIDE, c: float = C.SERIES_C) -> dict:
    """Mittlerer Anteil lebender Knoten der Schicht A über p (Kaskade) und einer einzelnen Schicht, gemittelt über `runs` feste Netzpaare; dazu größter Sprung und Einsatzpunkt."""
    n = side * side
    pairs = []
    for j in range(runs):
        n_eff, ea, eb = make_pair(layer, partner, n, c, C.SERIES_SEED + j)
        pairs.append((A.adjacency(n_eff, ea), A.adjacency(n_eff, eb)))
    mutual, single = [], []
    for ip, p in enumerate(ps):
        mv, sv = [], []
        for j, (a, b) in enumerate(pairs):
            rng = np.random.default_rng(C.SERIES_SEED + 1000 * (j + 1) + ip)
            mv.append(A.mutual_giant(a, b, p, q, rng))
            sv.append(A.single_layer_giant(a, p, np.random.default_rng(C.SERIES_SEED + 7000 * (j + 1) + ip)))
        mutual.append(float(np.mean(mv)))
        single.append(float(np.mean(sv)))
    step, lo, hi = largest_step(ps, mutual)
    return dict(layer=layer, partner=partner, q=q, ps=list(ps), mutual=mutual, single=single, step=step, step_from=lo, step_to=hi, onset=onset(ps, mutual), abrupt=step >= C.ABRUPT_STEP, runs=runs, n=n)


def series_layers(**kw) -> list[dict]:
    """Je Schichtart die Kurve bei vollständiger Kopplung: Zufallsnetz, skalenfrei, Gitter zufällig gekoppelt, Gitter als Kopie."""
    spec = (("er", "independent", "Zufallsnetze"), ("ba", "independent", "skalenfreie Netze"), ("lattice", "independent", "Gitter, zufällig gekoppelt"), ("lattice", "copy", "Gitter als Kopie"))
    rows = []
    for layer, partner, name in spec:
        r = curve(layer, partner, 1.0, **kw)
        r["name"] = name
        rows.append(r)
    return rows


def series_coupling(qs=C.SERIES_QS, **kw) -> list[dict]:
    """Zwei Zufallsnetze bei verschiedenem Anteil q gekoppelter Knotenpaare."""
    rows = []
    for q in qs:
        r = curve("er", "independent", q, **kw)
        r["name"] = f"q = {num(q, 2)}"
        rows.append(r)
    return rows


# --- Verdikte --------------------------------------------------------------------------------------------------------------------------------


def verdict_state(a: Analysis) -> tuple[str, str]:
    """Kernfrage der Hauptansicht: was bleibt nach der Kaskade, und was hätte eine einzelne Schicht behalten?"""
    s = a.settings
    head = (f"Nach {a.rounds} Runden der Kaskade leben in A {pct(a.final_a, 1)} und in B {pct(a.final_b, 1)} der {a.n} Knoten (anfangs blieben {pct(s.p, 0)} der Knoten von A); "
            f"eine einzelne Schicht hätte bei demselben p {pct(a.single, 1)} in ihrer Riesenkomponente.")
    if a.theory is not None:
        head += f" Die Theorie für unendlich große Netze sagt {pct(a.theory, 1)} voraus."
    if a.final_a < C.COLLAPSE_BELOW:
        return "warning", head + " Das System ist zusammengebrochen: die Kaskade hat beide Schichten bis auf Reste gelöscht."
    if a.final_a < 0.9 * a.single:
        return "info", head + " Die Kopplung kostet einen merklichen Teil dessen, was eine einzelne Schicht behielte."
    return "success", head + " Die Kopplung kostet kaum etwas gegenüber einer einzelnen Schicht."


def curve_row(r: dict) -> dict:
    """Eine Zeile der Tabelle zu einer Kurve: Einsatzpunkt, größter Sprung mit Lage, Wert bei p = 1, Art des Übergangs."""
    return {
        "Netz": r["name"], "Einsatz ab p": "–" if r["onset"] is None else num(r["onset"], 3), "größter Sprung": num(r["step"], 2), "zwischen p": f"{num(r['step_from'], 3)} und {num(r['step_to'], 3)}",
        "Anteil bei p = 1": num(r["mutual"][-1], 2), "Übergang": "abrupt" if r["abrupt"] else "stetig",
    }


def verdict_layers(rows: list[dict]) -> tuple[str, str]:
    """Messreihe über die Schichtarten: welche Übergänge abrupt sind und wie groß der Sprung ist."""
    by = {(r["layer"], r["partner"]): r for r in rows}
    er, ba, la, lc = by[("er", "independent")], by[("ba", "independent")], by[("lattice", "independent")], by[("lattice", "copy")]
    return "info", (
        f"Zufallsnetze: Sprung um {num(er['step'], 2)} zwischen p = {num(er['step_from'], 3)} und {num(er['step_to'], 3)}; "
        f"skalenfreie Netze: größter Schritt {num(ba['step'], 2)}; Gitter zufällig gekoppelt: Sprung um {num(la['step'], 2)} zwischen {num(la['step_from'], 3)} und {num(la['step_to'], 3)}; "
        f"Gitter als Kopie: größter Schritt {num(lc['step'], 2)} ({'abrupt' if lc['abrupt'] else 'stetig'})."
    )


def verdict_coupling(rows: list[dict]) -> tuple[str, str]:
    """Messreihe über die Kopplung: Größe des größten Sprungs je q und ab welchem q er abrupt ist."""
    parts = ", ".join(f"q = {num(r['q'], 2)}: {num(r['step'], 2)}" for r in rows)
    abrupt = [r["q"] for r in rows if r["abrupt"]]
    tail = (f"abrupt (Schritt ab {num(C.ABRUPT_STEP, 1)}) ab q = {num(min(abrupt), 2)}" if abrupt else "bei keinem q abrupt")
    return "info", f"Größter Schritt des Anteils zwischen benachbarten p-Werten: {parts}; der Übergang ist {tail}."
