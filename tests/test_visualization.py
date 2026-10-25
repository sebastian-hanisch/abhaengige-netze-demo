"""Abbildungen: Spuren je Figur, Werte, Farben, Achsen gesperrt."""

import abn_algorithm as A
import abn_constants as C
import abn_evaluation as ev
import abn_visualization as V


def _locked(fig):
    return fig.layout.xaxis.fixedrange is True and fig.layout.yaxis.fixedrange is True


def test_cascade_figure_shows_both_layers_per_round():
    fig = V.build_cascade([(700, 1000), (540, 540), (540, 540)], 1000)
    assert [t.name for t in fig.data] == ["Schicht A", "Schicht B"] and _locked(fig)
    assert list(fig.data[0].x) == [0, 1, 2] and list(fig.data[0].y) == [0.7, 0.54, 0.54] and list(fig.data[1].y) == [1.0, 0.54, 0.54]


def test_compare_figure_with_and_without_theory():
    a = ev.analyse(ev.Settings(n=1000, p=0.8, seed=3))
    fig = V.build_compare(a)
    assert list(fig.data[0].x) == ["anfangs erhalten (p)", "einzelne Schicht", "gekoppelt nach der Kaskade", "Theorie (n → ∞)"] and _locked(fig)
    assert list(fig.data[0].y) == [0.8, a.single, a.final_a, a.theory]
    b = ev.analyse(ev.Settings(layer="ba", n=1000, p=0.8, seed=3))
    assert len(V.build_compare(b).data[0].x) == 3


def test_compare_figure_marks_a_collapse_in_red():
    a = ev.analyse(ev.Settings(layer="lattice", n=900, p=0.62, seed=1))
    assert a.final_a < C.COLLAPSE_BELOW
    assert V.build_compare(a).data[0].marker.color[2] == C.COLOR_ALERT


def rows():
    def row(name, mutual, single):
        return dict(name=name, ps=[0.5, 0.7, 0.9], mutual=mutual, single=single)

    return [row("Zufallsnetze", [0.0, 0.5, 0.84], [0.4, 0.65, 0.87]), row("skalenfreie Netze", [0.2, 0.6, 0.89], [0.4, 0.65, 0.9])]


def test_curve_figure_has_a_line_per_row_the_single_layer_and_optional_theory():
    fig = V.build_curves(rows())
    assert [t.name for t in fig.data] == ["Zufallsnetze", "skalenfreie Netze", "einzelne Schicht (Zufallsnetze)"] and _locked(fig)
    assert list(fig.data[0].y) == [0.0, 0.5, 0.84] and list(fig.data[2].y) == [0.4, 0.65, 0.87]
    th = V.build_curves(rows(), with_theory=True)
    assert th.data[-1].name == "Theorie, zwei Zufallsnetze (n → ∞)" and list(th.data[-1].y) == [A.er_mutual_fixed_point(p, C.SERIES_C) for p in (0.5, 0.7, 0.9)]
