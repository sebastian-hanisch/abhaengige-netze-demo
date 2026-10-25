"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import abn_algorithm as A
import abn_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_cascade(history, n: int):
    """Anteil lebender Knoten in A und B nach jeder Runde der Kaskade (Runde 0: nach dem anfänglichen Ausfall in A)."""
    xs = list(range(len(history)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[h[0] / n for h in history], mode="lines+markers", line=dict(color=C.COLOR_MEASURED, width=3), name="Schicht A", hovertemplate="Runde %{x}: %{y:.3f}<extra>A</extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[h[1] / n for h in history], mode="lines+markers", line=dict(color=C.COLOR_THIRD, width=3, dash="dash"), name="Schicht B", hovertemplate="Runde %{x}: %{y:.3f}<extra>B</extra>"))
    fig.update_xaxes(title_text="Runde der Kaskade", dtick=1)
    fig.update_yaxes(title_text="Anteil lebender Knoten", range=[-0.02, 1.02])
    return _base(fig)


def build_compare(a):
    """Anfangs erhaltener Anteil p, einzelne Schicht (größte Komponente) und gekoppelt nach der Kaskade, nebeneinander (bei zwei Zufallsnetzen und q = 1 auch die Theorie)."""
    names = ["anfangs erhalten (p)", "einzelne Schicht", "gekoppelt nach der Kaskade"]
    vals = [a.settings.p, a.single, a.final_a]
    colors = [C.COLOR_LAYER, C.COLOR_THEORY, C.COLOR_ALERT if a.final_a < C.COLLAPSE_BELOW else C.COLOR_MEASURED]
    if a.theory is not None:
        names.append("Theorie (n → ∞)")
        vals.append(a.theory)
        colors.append(C.COLOR_THIRD)
    fig = go.Figure(go.Bar(x=names, y=vals, marker_color=colors, text=[f"{v * 100:.1f} %" for v in vals], textposition="outside", hovertemplate="%{x}: %{y:.3f}<extra></extra>"))
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Anteil der Knoten", range=[0, 1.12])
    return _base(fig)


def build_curves(rows, with_theory: bool = False, k: float = C.SERIES_C):
    """Anteil lebender Knoten in A über p, eine Linie je Zeile (gekoppelt); gestrichelt grau: einzelne Zufallsschicht (erste Zeile), optional die Theorie für zwei Zufallsnetze."""
    palette = [C.COLOR_MEASURED, C.COLOR_THEORY, C.COLOR_THIRD, C.COLOR_ALERT, "#7f7f7f"]
    fig = go.Figure()
    for i, r in enumerate(rows):
        fig.add_trace(go.Scatter(x=r["ps"], y=r["mutual"], mode="lines+markers", line=dict(color=palette[i % len(palette)], width=3), marker=dict(size=5), name=r["name"],
                                 hovertemplate="p = %{x}: %{y:.3f}<extra></extra>"))
    first = rows[0]
    fig.add_trace(go.Scatter(x=first["ps"], y=first["single"], mode="lines", line=dict(color=C.COLOR_LAYER, width=2, dash="dash"), name=f"einzelne Schicht ({first['name']})", hovertemplate="p = %{x}: %{y:.3f}<extra></extra>"))
    if with_theory:
        fig.add_trace(go.Scatter(x=first["ps"], y=[A.er_mutual_fixed_point(p, k) for p in first["ps"]], mode="lines", line=dict(color="#000000", width=1.5, dash="dot"), name="Theorie, zwei Zufallsnetze (n → ∞)"))
    fig.update_xaxes(title_text="Anteil p der anfangs erhaltenen Knoten von A")
    fig.update_yaxes(title_text="Anteil lebender Knoten nach der Kaskade", range=[-0.02, 1.02])
    return _base(fig, height=420)
