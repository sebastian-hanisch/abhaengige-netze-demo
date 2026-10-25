"""Verdikte (reine Funktionen): Art und jede Zahl im Text an handgesetzten Werten, einschließlich der Schwellen und Zweige."""

import abn_constants as C
import abn_evaluation as ev
from abn_evaluation import Analysis, Settings


def make(final_a, single, p=0.7, theory=None, n=3000, rounds=4, final_b=None):
    hist = [(int(0.7 * n), n)] + [(int(final_a * n), int((final_a if final_b is None else final_b) * n))] * rounds
    return Analysis(Settings(p=p), n, 4.0, hist, final_a, final_a if final_b is None else final_b, single, theory)


def test_num_and_pct():
    assert ev.num(3.14159, 2) == "3,14" and ev.pct(0.456) == "46 %" and ev.pct(0.0456, 1) == "4,6 %" and ev.pct(1.0) == "100 %"


def test_verdict_text_numbers():
    kind, text = ev.verdict_state(make(0.54, 0.639, theory=0.5576))
    assert "Nach 4 Runden der Kaskade leben in A 54,0 % und in B 54,0 % der 3000 Knoten (anfangs blieben 70 % der Knoten von A)" in text
    assert "eine einzelne Schicht hätte bei demselben p 63,9 % in ihrer Riesenkomponente" in text and "Die Theorie für unendlich große Netze sagt 55,8 % voraus." in text
    kind, text = ev.verdict_state(make(0.54, 0.639, final_b=0.5))
    assert "in B 50,0 %" in text and "Theorie" not in text


def test_verdict_kinds_and_thresholds():
    assert ev.verdict_state(make(0.0, 0.6))[0] == "warning" and "zusammengebrochen" in ev.verdict_state(make(0.0, 0.6))[1]
    assert ev.verdict_state(make(0.0099, 0.6))[0] == "warning" and ev.verdict_state(make(0.0101, 0.6))[0] == "info"           # Schwelle 1 %
    assert ev.verdict_state(make(0.54, 0.6))[0] == "success"                                                                  # 0,54 ≥ 0,9 · 0,6
    assert ev.verdict_state(make(0.539, 0.6))[0] == "info" and "merklichen Teil" in ev.verdict_state(make(0.539, 0.6))[1]
    assert ev.verdict_state(make(0.6, 0.6))[0] == "success" and "kaum etwas" in ev.verdict_state(make(0.6, 0.6))[1]


def test_curve_row_by_hand():
    r = dict(name="Zufallsnetze", onset=0.625, step=0.3, step_from=0.6, step_to=0.625, mutual=[0.0, 0.5, 0.956], abrupt=True)
    assert ev.curve_row(r) == {"Netz": "Zufallsnetze", "Einsatz ab p": "0,625", "größter Sprung": "0,30", "zwischen p": "0,600 und 0,625", "Anteil bei p = 1": "0,96", "Übergang": "abrupt"}
    r = dict(r, onset=None, abrupt=False)
    assert ev.curve_row(r)["Einsatz ab p"] == "–" and ev.curve_row(r)["Übergang"] == "stetig"


def rows_layers():
    def row(layer, partner, step, lo, hi, abrupt):
        return dict(layer=layer, partner=partner, step=step, step_from=lo, step_to=hi, abrupt=abrupt)

    return [row("er", "independent", 0.30, 0.6, 0.625, True), row("ba", "independent", 0.07, 0.475, 0.5, False), row("lattice", "independent", 0.38, 0.65, 0.675, True), row("lattice", "copy", 0.17, 0.55, 0.575, False)]


def test_layers_verdict_by_hand():
    kind, text = ev.verdict_layers(rows_layers())
    assert kind == "info" and "Zufallsnetze: Sprung um 0,30 zwischen p = 0,600 und 0,625" in text and "skalenfreie Netze: größter Schritt 0,07" in text
    assert "Gitter zufällig gekoppelt: Sprung um 0,38 zwischen 0,650 und 0,675" in text and "Gitter als Kopie: größter Schritt 0,17 (stetig)" in text
    rows = rows_layers()
    rows[3]["abrupt"] = True
    assert "(abrupt)" in ev.verdict_layers(rows)[1]


def test_coupling_verdict_by_hand():
    rows = [dict(q=q, step=s, abrupt=s >= C.ABRUPT_STEP) for q, s in ((0.0, 0.07), (0.5, 0.06), (0.75, 0.1), (1.0, 0.3))]
    kind, text = ev.verdict_coupling(rows)
    assert kind == "info" and "q = 0,00: 0,07, q = 0,50: 0,06, q = 0,75: 0,10, q = 1,00: 0,30" in text and "abrupt (Schritt ab 0,2) ab q = 1,00" in text
    rows[2]["abrupt"] = True
    assert "ab q = 0,75" in ev.verdict_coupling(rows)[1]
    assert "bei keinem q abrupt" in ev.verdict_coupling([dict(q=0.0, step=0.07, abrupt=False)])[1]
