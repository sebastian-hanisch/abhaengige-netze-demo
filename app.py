"""Abhängige Netze: wann bricht ein gekoppeltes System zusammen? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 8 der Linie „Netzmodelle“: zwei Netzschichten, deren Knoten paarweise voneinander abhängen (Strom und Kommunikation, Buldyrev-Modell). Fällt ein Teil der Knoten aus, löscht eine Kaskade
abwechselnd in beiden Schichten alles, was nicht mehr zur größten Komponente gehört. Der Kern liegt in abn_algorithm.py.

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import abn_constants as C
import abn_evaluation as ev
from abn_evaluation import Settings, analyse, curve_row, num, pct, verdict_coupling, verdict_layers, verdict_state
from abn_layout import dunkles_design, kopf_css
from abn_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from abn_visualization import build_cascade, build_compare, build_curves

st.set_page_config(page_title="Abhängige Netze – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _series_layers():
    return ev.series_layers()


@st.cache_data(show_spinner=False)
def _series_coupling():
    return ev.series_coupling()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in abn_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🔗 Abhängige Netze: wann bricht ein gekoppeltes System zusammen?")
st.markdown(
    """
Ein Stromnetz braucht die Leitstellen, die Leitstellen brauchen Strom: **zwei Netze, deren Knoten paarweise voneinander abhängen**. Fällt ein Teil der Knoten aus, bleibt in jedem Netz nur die größte zusammenhängende Gruppe funktionsfähig;
ihr Gegenstück im anderen Netz fällt mit den Ausgefallenen weg, dort zerfällt wieder ein Teil, und so weiter: eine **Kaskade**. Die Demo zeigt, **wann das System dabei plötzlich ganz zusammenbricht** statt langsam zu schrumpfen,
wie sich Zufallsnetze, skalenfreie Netze und Gitter unterscheiden und was passiert, wenn nur ein Teil der Knoten gekoppelt ist. Achtes Stück (optional) der Linie „Netzmodelle“; die lastbasierten Kaskaden und die Epidemien stehen in `kaskaden-demo`,
die einmaligen unabhängigen Ausfälle in `robustheit-demo`.

Weiter unten: 🔬 **Messreihen** (Schichtart und Kopplung), 🚧 **Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So läuft die Kaskade", expanded=True):
    st.markdown(
        """
1. **Zwei Schichten, dieselben Knoten.** Knoten i der Schicht A und Knoten i der Schicht B sind ein Paar; mit Wahrscheinlichkeit q ist das Paar **gekoppelt** (fällt der eine aus, fällt der andere aus).
2. **Anfangsausfall.** Von den Knoten der Schicht A bleiben nur der Anteil p erhalten; ihre gekoppelten Gegenstücke in B fallen mit aus.
3. **Kaskade.** Abwechselnd: in der Schicht A zählt nur die größte Zusammenhangskomponente der lebenden Knoten; alles andere fällt aus und reißt seine gekoppelten Partner in B mit. Dann dasselbe in B, dann wieder in A, bis sich nichts mehr ändert.
4. **Ergebnis.** Der Anteil lebender Knoten am Ende, verglichen mit dem, was eine **einzelne** Schicht bei demselben p in ihrer Riesenkomponente behielte.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    layer = st.selectbox("Schichtart", list(C.LAYERS), format_func=C.LAYERS.get, key="layer_select", help="Beide Schichten sind von dieser Art. Das Gitter ist ein Torus mit Grad 4.")
    partner = st.selectbox("Schicht B", list(C.PARTNERS), format_func=C.PARTNERS.get, key="partner_select",
                           help="Unabhängig: eine zweite Ziehung (beim Gitter dasselbe Gitter mit zufällig umnummerierten Knoten). Kopie: Schicht B hat genau die Kanten von A; dann fehlt der Zusatzverlust durch die Kopplung.")
    n = st.slider("Knoten je Schicht", *bounds("n_slider"), key="n_slider", step=500, help="Beim Gitter wird das nächste Quadrat genommen.")
    c = st.slider("Mittlerer Grad", *bounds("c_slider"), key="c_slider", step=0.5, help="Beim Zufallsnetz der mittlere Grad, beim skalenfreien Netz etwa 2m mit m = Grad / 2; das Gitter hat immer Grad 4.")
    q = st.slider("Anteil gekoppelter Paare q", *bounds("q_slider"), key="q_slider", step=0.05, help="1 = jedes Paar gekoppelt, 0 = die Schichten sind unabhängig und die Kaskade ist eine gewöhnliche Perkolation.")
    p = st.slider("Anfangs erhaltene Knoten p", *bounds("p_slider"), key="p_slider", step=0.01, help="Anteil der Knoten der Schicht A, die dem ersten Ausfall entgehen.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neue Schichten ziehen", width="stretch", on_click=randomize_seed)

sync_query_params({"layer_select": layer, "partner_select": partner, "n_slider": int(n), "c_slider": round(float(c), 1), "q_slider": round(float(q), 2), "p_slider": round(float(p), 2), "seed_input": int(seed)})

settings = Settings(layer=layer, partner=partner, n=int(n), c=round(float(c), 1), q=round(float(q), 2), p=round(float(p), 2), seed=int(seed))
with st.spinner("Baue die Schichten und lasse die Kaskade laufen …"):
    a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Knoten je Schicht", f"{a.n}", delta=f"mittlerer Grad {num(a.mean_degree, 1)}", delta_color="off")
m2.metric("Lebend in A am Ende", pct(a.final_a, 1), delta=f"in B {pct(a.final_b, 1)}", delta_color="off")
m3.metric("Einzelne Schicht", pct(a.single, 1), delta=f"bei p = {num(settings.p, 2)}", delta_color="off")
m4.metric("Runden der Kaskade", f"{a.rounds}", delta=f"Theorie (n → ∞): {pct(a.theory, 1)}" if a.theory is not None else "keine Theorie für diese Einstellung", delta_color="off")
c1, c2 = st.columns(2)
c1.plotly_chart(build_cascade(a.history, a.n), width="stretch", key="main_cascade")
c2.plotly_chart(build_compare(a), width="stretch", key="main_compare")
st.caption("Links der Anteil lebender Knoten nach jeder Runde (Runde 0: nach dem Anfangsausfall in A); rechts, was anfangs erhalten bleibt, was eine einzelne Schicht in der Riesenkomponente behielte und was gekoppelt übrig bleibt.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was bleibt nach der Kaskade?")
kind, text = verdict_state(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Messreihen ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Messreihen: wo der Übergang liegt und wie abrupt er ist")
st.caption(
    f"Feste Programme, unabhängig von den Reglern: {C.SERIES_SIDE ** 2} Knoten je Schicht, mittlerer Grad {num(C.SERIES_C, 0)}, p von {num(C.SERIES_PS[0], 2)} bis {num(C.SERIES_PS[-1], 2)} in Schritten von 0,025; je Punkt der Mittelwert über {C.SERIES_RUNS} feste Schichtpaare. "
    "Jede Reihe rechnet auf Klick in einigen Sekunden. „Abrupt“ heißt hier: der Anteil springt zwischen zwei benachbarten p-Werten um mindestens 0,2 (eine Festlegung der Demo)."
)
tab1, tab2 = st.tabs(["Schichtart", "Anteil gekoppelter Paare"])
with tab1:
    st.markdown("**Gleiche Kopplung, verschiedene Schichten.** Zufallsnetze brechen abrupt zusammen, skalenfreie Netze (Barabási–Albert, mittlerer Grad 4) nicht; ein Gitter bricht abrupt zusammen, wenn die Kopplung zufällig ist, und gar nicht zusätzlich, wenn beide Schichten dieselbe Lage haben.")
    if st.button("Reihe rechnen", key="layers_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe (einige Sekunden) …"):
            _series_layers()
        st.session_state["layers_done"] = time.perf_counter() - t0
    if "layers_done" in st.session_state:
        rows = _series_layers()
        st.plotly_chart(build_curves(rows, with_theory=True), width="stretch", key="layers_chart")
        st.table([curve_row(r) for r in rows])
        kind, text = verdict_layers(rows)
        getattr(st, kind)(text)
        st.caption(f"Rechenzeit dieser Sitzung: {num(st.session_state['layers_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")
with tab2:
    st.markdown("**Tendenz: Je weniger Paare gekoppelt sind, desto weicher der Übergang (nicht streng monoton).** Zwei Zufallsnetze, Anteil q gekoppelter Paare von 0 (gewöhnliche Perkolation) bis 1.")
    if st.button("Reihe rechnen", key="coupling_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe (einige Sekunden) …"):
            _series_coupling()
        st.session_state["coupling_done"] = time.perf_counter() - t0
    if "coupling_done" in st.session_state:
        rows = _series_coupling()
        st.plotly_chart(build_curves(rows), width="stretch", key="coupling_chart")
        st.table([curve_row(r) for r in rows])
        kind, text = verdict_coupling(rows)
        getattr(st, kind)(text)
        st.caption(f"Rechenzeit dieser Sitzung: {num(st.session_state['coupling_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Jeder Knoten hat genau einen Partner** | Reale Abhängigkeiten sind nicht eins zu eins; ein Knoten kann von mehreren abhängen oder von keinem, und die Abhängigkeit kann in nur einer Richtung gelten. | diese Demo (Anteil q) |
| **Ein Knoten lebt, wenn er in der größten Komponente liegt** | Kleinere Komponenten könnten für sich weiterarbeiten; die Regel zählt nur die größte (so im Modell von Buldyrev). | diese Demo |
| **Die Kopplung ist räumlich unabhängig** | Wenn gekoppelte Knoten nah beieinander liegen (Gitter als Kopie, oder kurze Abhängigkeitslängen), verschwindet der Zusatzverlust ganz oder zum Teil; die Demo kennt nur die beiden Extreme. | Netze im Raum (Vorgänger) |
| **Die Theorie gilt für unendlich große Netze** | Bei etwa 3 000 bis 5 000 Knoten verwischt der Übergang; nahe der Schwelle ist der Ausgang je Netzpaar zufällig (Zusammenbruch oder Rest), die Messreihe nimmt deshalb den Mittelwert über acht Paare. | diese Demo |
| **Kaskade statt Last** | Es wird nur der Zusammenhang gerechnet; Lasten, Kapazitäten und Zeitverläufe fehlen. | `kaskaden-demo` |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** Gegeben sind zwei Graphen $A$ und $B$ auf denselben $n$ Knoten; ein Knoten $i$ ist mit Wahrscheinlichkeit $q$ gekoppelt.

| Symbol | Bedeutung |
|---|---|
| $p$ | Anteil der Knoten von $A$, die anfangs erhalten bleiben |
| $q$ | Anteil gekoppelter Paare |
| $k$ | mittlerer Grad der Zufallsnetze |
| $x$ | Anteil lebender Knoten nach der Kaskade |

**Kaskade.** Mit den lebenden Mengen $a_0$ (zufällig mit Dichte $p$) und $b_0$ (alle) wird abwechselnd bestimmt:
$a_{t}' = \operatorname{Riese}_A(a_{t})$, $b_{t}' = b_{t} \cap (a_{t}' \cup \bar{C})$, $b_{t+1} = \operatorname{Riese}_B(b_{t}')$, $a_{t+1} = a_{t}' \cap (b_{t+1} \cup \bar{C})$,
wobei $\bar{C}$ die ungekoppelten Knoten sind und $\operatorname{Riese}$ die größte Komponente der lebenden Knoten. Bei $q = 1$ ist das Ergebnis die **gegenseitig verbundene Riesenkomponente**.

**Zwei Zufallsnetze, $q = 1$** (aus dem Gedächtnis nach Buldyrev u. a.): der Anteil $x$ löst

$$x = p \, \big(1 - e^{-k x}\big)^2.$$

Es gibt eine Lösung $x > 0$ genau ab $p_c \approx 2{,}4554 / k$; dort springt $x$ von null auf einen positiven Wert (Übergang erster Art). Eine einzelne Schicht dagegen hat $x = p S$ mit $S = 1 - e^{-p k S}$ und einen stetigen Übergang bei $p = 1/k$.

**Literatur** (aus dem Gedächtnis, nicht im Original geprüft): Buldyrev, Parshani, Paul, Stanley und Havlin, *Catastrophic cascade of failures in interdependent networks*, Nature 464 (2010); Parshani, Buldyrev und Havlin, *Interdependent networks: reducing the coupling strength leads to a change from a first to second order percolation transition*, Physical Review Letters 105 (2010);
Son, Bizhani, Christensen, Grassberger und Paczuski, *Percolation theory on interdependent networks based on epidemic spreading*, Europhysics Letters 97 (2012).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
