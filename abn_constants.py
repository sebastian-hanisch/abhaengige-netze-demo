"""Konstanten: Regler-Grenzen, Schwellen, feste Pläne der Messreihen, Farben und Presets."""

LAYERS = {"er": "Zufallsnetz (Erdős–Rényi)", "ba": "Skalenfreies Netz (Barabási–Albert)", "lattice": "Gitter (Torus, Grad 4)"}
DEFAULT_LAYER = "er"
PARTNERS = {"independent": "unabhängig (anderes Netz bzw. zufällig umnummeriertes Gitter)", "copy": "Kopie von A (gleiche Kanten)"}
DEFAULT_PARTNER = "independent"

N_MIN, N_MAX, DEFAULT_N = 1000, 6000, 3000            # Knoten je Schicht (beim Gitter das nächste Quadrat)
C_MIN, C_MAX, DEFAULT_C = 2.0, 8.0, 4.0               # mittlerer Grad (Zufallsnetz) bzw. 2 · m (Barabási–Albert); das Gitter hat Grad 4
Q_MIN, Q_MAX, DEFAULT_Q = 0.0, 1.0, 1.0               # Anteil der gekoppelten Knotenpaare
P_MIN, P_MAX, DEFAULT_P = 0.2, 1.0, 0.70              # Anteil der Knoten der Schicht A, die anfangs erhalten bleiben
SEED_MAX, DEFAULT_SEED = 999999, 35

COLLAPSE_BELOW = 0.01         # unter diesem Anteil lebender Knoten gilt das System als zusammengebrochen
ABRUPT_STEP = 0.2             # ein Übergang gilt als abrupt, wenn der Anteil zwischen zwei benachbarten p-Werten der Reihe um mindestens so viel springt (Konvention der Demo)

# feste Pläne der Messreihen (nie ein einzelnes Netzpaar)
SERIES_SEED = 100000          # Netzpaar j hat den Seed SERIES_SEED + j
SERIES_SIDE = 70              # Gitterseite: 4 900 Knoten je Schicht
SERIES_C = 4.0
SERIES_RUNS = 8
SERIES_PS = tuple(round(0.30 + 0.025 * i, 3) for i in range(29))        # 0,30 bis 1,00 in Schritten von 0,025
SERIES_QS = (0.0, 0.25, 0.5, 0.75, 1.0)

COLOR_MEASURED = "#2F6B65"
COLOR_THEORY = "#4c78a8"
COLOR_THIRD = "#e8a33d"
COLOR_ALERT = "#d62728"
COLOR_LAYER = "rgba(120,120,120,0.55)"


def _p(layer="er", partner="independent", n=3500, c=DEFAULT_C, q=DEFAULT_Q, p=DEFAULT_P):
    return {"layer": layer, "partner": partner, "n": n, "c": c, "q": q, "p": p, "seed": DEFAULT_SEED}


PRESETS = {
    "Zwei Zufallsnetze, p = 0,70": {"layer": "er", "partner": "independent", "n": DEFAULT_N, "c": DEFAULT_C, "q": DEFAULT_Q, "p": DEFAULT_P, "seed": DEFAULT_SEED},
    "Zwei Zufallsnetze, p = 0,55": _p(p=0.55),
    "Skalenfreie Schichten, p = 0,55": _p(layer="ba", p=0.55),
    "Gitter, zufällig gekoppelt, p = 0,65": _p(layer="lattice", p=0.65),
    "Gitter als Kopie, p = 0,65": _p(layer="lattice", partner="copy", p=0.65),
}
PRESET_HELP = {
    "Zwei Zufallsnetze, p = 0,70": "Zwei Zufallsnetze mit mittlerem Grad 4, jeder Knoten hängt an seinem Gegenstück: Wenn 30 % der Knoten von A ausfallen, bleibt ein Teil beider Netze zusammenhängend, aber weniger als bei einer einzelnen Schicht.",
    "Zwei Zufallsnetze, p = 0,55": "Etwas weniger Knoten bleiben erhalten, und die Kaskade löscht beide Netze ganz: der Zusammenbruch ist ein Sprung, kein langsames Schrumpfen.",
    "Skalenfreie Schichten, p = 0,55": "Dieselbe Kopplung bei skalenfreien Schichten: hier bleibt bei p = 0,55 noch ein Teil bestehen, wo zwei Zufallsnetze schon verloren sind; der Übergang ist weicher.",
    "Gitter, zufällig gekoppelt, p = 0,65": "Zwei Gitter, deren Knoten zufällig einander zugeordnet sind: dieselbe Schicht allein hätte bei p = 0,65 noch eine Riesenkomponente, gekoppelt bricht sie ganz zusammen.",
    "Gitter als Kopie, p = 0,65": "Zwei gleiche Gitter, Knoten an derselben Stelle gekoppelt: kein Zusatzverlust, das System verhält sich wie eine einzelne Schicht.",
}
