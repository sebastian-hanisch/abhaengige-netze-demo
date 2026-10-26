# Abhängige Netze: wann bricht ein gekoppeltes System zusammen? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-abhaengige-netze-demo.streamlit.app/)** -->

Achtes Stück der **Netzmodelle-Linie** (Graphentheorie) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Die Linie erzeugt Netze aus Zufallsmodellen und prüft sie gegen Theorie und Daten;
dieses Stück fragt, **was geschieht, wenn zwei Netze voneinander abhängen**, zum Beispiel Strom und Kommunikation. Vorgänger sind [netzmotive-demo](https://github.com/sebastian-hanisch/netzmotive-demo) (Muster gegen Nullmodelle) und [raeumliche-netze-demo](https://github.com/sebastian-hanisch/raeumliche-netze-demo) (Netze im Raum); lastbasierte Kaskaden behandelt [kaskaden-demo](https://github.com/sebastian-hanisch/kaskaden-demo), hier zählt nur der Zusammenhang.

Die Demo koppelt zwei Netzschichten auf denselben Knoten: Knoten *i* der Schicht A hängt von Knoten *i* der Schicht B ab (mit Wahrscheinlichkeit q). Ein Teil der Knoten von A fällt aus, dann löscht eine **Kaskade** abwechselnd in beiden Schichten alles, was nicht mehr zur größten Komponente gehört, bis nichts mehr wegfällt.
Schichten: zwei Zufallsnetze (Erdős–Rényi), zwei skalenfreie Netze (Barabási–Albert) oder zwei Gitter (Torus, entweder zufällig gekoppelt oder als Kopie). Der Kern ist eigener Code; `networkx` kommt nur als Gegenprobe in die Tests.

## Warum dieses Problem

Ein Zufallsnetz für sich behält eine Riesenkomponente, solange mehr als etwa ein Viertel seiner Knoten (bei mittlerem Grad 4) übrig ist. Hängt es aber von einem zweiten ab, fällt mit jedem Knoten der einen Schicht auch dessen Partner in der anderen aus, und der Zusammenhalt der einen Schicht zerlegt die andere weiter.
Die Frage der Demo: **Wie viele Knoten dürfen ausfallen, bevor beide Schichten zusammenbrechen, und bricht das System allmählich oder auf einmal?**

## Modell

**Kaskade.** Anfangs bleiben die Knoten von A mit Wahrscheinlichkeit p erhalten, in B bleiben alle. Dann wird abwechselnd die größte Komponente der lebenden Knoten von A bestimmt (alle übrigen gekoppelten Knoten fallen aus, ihre Partner in B auch), danach die von B, bis sich nichts mehr ändert.
Bei q = 1 ist das Ergebnis die **gegenseitig verbundene Riesenkomponente**; bei q = 0 sind die Schichten unabhängig.
**Theorie (zwei Zufallsnetze, q = 1, unendlich großes Netz):** der überlebende Anteil x löst x = p (1 − e^(−k x))², es gibt eine Lösung x > 0 genau ab p_c ≈ 2,4554 / k; bei k = 4 sind das **0,614**. Eine einzelne Schicht hat x = p S mit S = 1 − e^(−p k S) und einen stetigen Übergang bei p = 1 / k.
Die Konstante 2,4554 stammt aus dem Gedächtnis (Buldyrev u. a.), der Eigenlöser der Demo reproduziert sie (siehe Befunde). Formeln und Lesehilfe stehen im 📐-Expander der App.

## Methodik

- **Kern** (`abn_algorithm.py`): G(n, m)-Zufallsnetz, Barabási–Albert-Netz (Start mit einer Clique), Torusgitter, größte Komponente der lebenden Knoten, die Kaskade mit Verlauf je Runde, Theorie als Fixpunkt (Iteration und Bisektion für p_c).
- **Szenario und Auswertung** (`abn_scenario.py`, `abn_evaluation.py`): Schichtpaare (bei unabhängiger Kopplung zweite Ziehung, beim Gitter zufällig umnummeriert, bei der Kopie dieselben Kanten), Analyse je Einstellung, zwei Messreihen mit festem Programm, alle Verdikte als reine Funktionen.
- **Oberfläche** (`app.py`): fünf Schnellstart-Szenarien, Regler für Schicht, Partner, Knotenzahl, mittleren Grad, Kopplung q, Anteil p und Zufalls-Seed, Verlauf der Kaskade, Vergleich mit einer einzelnen Schicht und der Theorie, Kernfrage, zwei Messreihen auf Klick, Annahmen und Formeln.
- **Messreihen:** je Netzart acht Paare mit 4 900 Knoten (Gitter 70 × 70) und mittlerem Grad 4, p von 0,30 bis 1,00 in Schritten von 0,025; ein **abrupter** Übergang heißt hier: der größte Anstieg der gegenseitigen Riesenkomponente zwischen zwei benachbarten p-Werten beträgt **mindestens 0,2**. Das ist eine Konvention und hängt vom Raster ab.

## Befunde (gemessen, keine Behauptungen)

Messreihen mit festen Zufalls-Seeds (`SERIES_SEED` 100000), je acht Paare. Die Schnellstart-Szenarien sind Einzelläufe mit dem Zufalls-Seed 35. **Die Zufallszahlen eines `numpy`-Generators sind nicht über Versionen stabil**: die Tests prüfen deshalb Bänder um diese Zahlen.

| Frage | Befund | Test |
|---|---|---|
| Stimmt der Kern? | Größte Komponente gleich `networkx` auf Zufallsmasken; die Kaskade gleich einer einfachen `networkx`-Umsetzung auf 40 Zufallsinstanzen; Endzustand ist ein Fixpunkt; bei q = 0 gleich der gewöhnlichen Riesenkomponente; eine Kopie verliert nichts; Theorie gleich Simulation; Hubgröße des Barabási–Albert-Netzes gleich `networkx`. | `tests/test_oracle_abhaengige_netze.py` |
| Wo liegt die Schwelle der Theorie? | p_c · k = **2,4554** für k = 3, 4, 6 und 8 (p_c = **0,819**, **0,614**, **0,409**, **0,307**); bei k = 4 liegt der Zusammenbruch also bei etwas über 0,61. | `test_claims.py::test_theory_threshold_is_a_constant_over_the_mean_degree` |
| Wie groß ist der Verlust gegenüber einer einzelnen Schicht? | Zwei Zufallsnetze, n = 3 000, p = 0,70: gekoppelt bleiben **54,0 %** der Knoten in beiden Schichten (Theorie 55,8 %), eine einzelne Schicht hätte 63,9 %; die Kaskade braucht 4 Runden (bei Seeds 1 bis 12: 4 bis 5). | `test_claims.py::test_default_preset_loses_a_sixth_to_a_fifth_of_the_single_layer` |
| Bricht es allmählich oder auf einmal? | Zwei Zufallsnetze, 4 900 Knoten: bis p = 0,60 praktisch nichts, bei 0,625 sofort etwa **0,30** mehr (Einsatz ab 0,625, bei p = 1 sind es 0,96); die einzelne Schicht trägt schon bei p = 0,30 (etwa 0,10). Die Theorie sagt p_c = 0,614 voraus. | `test_claims.py::test_series_er_is_abrupt_near_the_theory_threshold`, `::test_the_single_layer_threshold_is_far_below_the_coupled_one` |
| Und nahe der Schwelle? | n = 3 500, p = 0,55: **12 von 12** Seeds brechen zusammen. Bei p = 0,60 (knapp unter der Theorie): **9 von 12** brechen zusammen, die übrigen drei behalten einen Kern von **0,34 bis 0,37**; bei p = 0,65 bleiben alle zwischen 0,42 und 0,49. Nahe der Schwelle ist der Ausgang je Netzpaar also zufällig, der Kern ist entweder weg oder von etwa einem Drittel. | `test_claims.py::test_the_preset_below_threshold_collapses_for_every_seed_but_just_above_it_is_bimodal` |
| Machen skalenfreie Schichten es besser? | Zwei Barabási–Albert-Netze (mittlerer Grad 4; bei mittlerem Grad 2, einem Baum, fällt der Anteil dagegen bei p ≈ 0,98 um 0,46, nachgemessen, nicht Teil der Reihe): Einsatz schon bei p = **0,425**, größter Schritt nur **0,07** (zwischen 0,475 und 0,500), also stetig; Schnellstart bei p = 0,55: **31,5 %** gekoppelt gegen 45,4 % für eine einzelne Schicht. | `test_claims.py::test_series_scale_free_layers_are_continuous`, `::test_the_collapse_presets_collapse_and_the_copy_does_not` |
| Und Gitter? | Zufällig gekoppelt: abrupt (Einsatz ab p = **0,675**, größter Schritt **0,38** zwischen 0,650 und 0,675); als Kopie auf denselben Knoten: kein Verlust, Einsatz ab 0,525 und größter Schritt **0,17** (stetig im Sinne der Konvention, sie liegt aber dicht an der Grenze 0,2). Schnellstart bei p = 0,65: zufällig gekoppelt **0** (einzelne Schicht 61,1 %), als Kopie **60,8 %** nach 2 Runden. | `test_claims.py::test_series_lattice_depends_on_the_coupling`, `::test_the_collapse_presets_collapse_and_the_copy_does_not` |
| Was ändert die Stärke der Kopplung? | Von den fünf getesteten q (0, 0,25, 0,50, 0,75 und 1) ist nur q = 1 abrupt (Schritt **0,30**); bei q = 0, 0,25, 0,50 und 0,75 liegt der größte Schritt zwischen 0,06 und 0,10. Bei q = 0,9 springt der Anteil in größeren Netzen (ab 20 000 Knoten, Raster 0,0125) ebenfalls um etwa 0,25 (nachgemessen, nicht Teil der Reihe). Der Einsatz wandert mit q von p = 0,300 (q = 0 und 0,25) über 0,325 und 0,450 bis 0,625. | `test_claims.py::test_series_coupling_is_abrupt_only_with_full_coupling` |

## Ehrliche Grenzen

- **Endliche Netze, keine Aussage über den Grenzwert.** Mit 3 000 bis 6 000 Knoten verwischt der Übergang; „abrupt“ heißt hier nur ein Anstieg um mindestens 0,2 zwischen zwei Rasterpunkten und hängt von der Schrittweite 0,025 ab. Die Gitterkopie (0,17) liegt knapp unter der Grenze; ein feineres Raster könnte sie anders einstufen. Auch der mittlere Grad geht ein: bei Zufallsnetzen mit Grad 6 und 8 (Raster 0,0125, 4 900 Knoten) misst der größte Schritt 0,18 und 0,17, nach der Konvention also „stetig“; die Reihen laufen nur mit Grad 4.
- **Nur Zusammenhang, keine Last.** Kapazitäten, Lastumverteilung und Zeitverläufe fehlen (siehe `kaskaden-demo`). Ein Knoten lebt, wenn er in der größten Komponente liegt; kleinere Komponenten zählen nicht, obwohl sie im Betrieb weiterarbeiten könnten.
- **Eine Abhängigkeit je Knoten, in beide Richtungen.** Reale Abhängigkeiten sind seltener eins zu eins; Mehrfachabhängigkeit und einseitige Abhängigkeit sind nicht abgedeckt.
- **Zwei Extreme der Kopplung im Raum.** Zufällig gekoppelt oder als Kopie; Zwischenstufen (Partner in der Nähe, wie in der räumlichen Literatur) fehlen.
- **Die Theorie gilt nur für zwei Zufallsnetze mit q = 1.** Für Barabási–Albert und Gitter liefert die Demo keine Formel, nur Messung.
- **Streit in der Literatur.** Ob der Übergang „hybrid“ ist und wie er für kleine Netze auszulegen ist, wird in der Literatur diskutiert (Buldyrev u. a. gegen Son u. a.); die Demo misst nur den Sprung und ordnet nicht ein.
- **Die Konstante 2,4554 und die Literatur** (Buldyrev u. a. 2010; Parshani u. a. 2010; Son u. a. 2012) stammen aus dem Gedächtnis und sind nicht im Original geprüft; der Eigenlöser der Demo reproduziert die Konstante.

## Befunde und Korrekturen gegenüber dem Plan

- **Port:** 9169 statt 9162 (9158 bis 9168 sind vergeben).
- **H1 bestätigt:** zwei Zufallsnetze, k = 4: bis p = 0,60 praktisch nichts, bei 0,65 etwa 0,45 (Plan: 0,46); die einzelne Schicht wächst stetig (bei p = 0,30 schon etwa 0,10).
- **H2 bestätigt, Zahl geändert:** Barabási–Albert glatter, größter Schritt 0,07 (Plan: 0,14 aus einem anderen Raster und Lauf).
- **H3 jetzt gemessen** (im Plan „nicht gemessen“): Gitter abrupt, wenn die Schichten zufällig gekoppelt sind (0,38), stetig als Kopie auf denselben Knoten (0,17). Entscheidend ist also die Kopplung, nicht das Gitter selbst.
- **Preset geändert:** „Zwei Zufallsnetze, p = 0,55“ statt 0,60: bei p = 0,60 ist der Ausgang je Zufalls-Seed zufällig (Zufalls-Seed 35 behält einen Kern, 9 von 12 anderen nicht), bei 0,55 brechen alle Seeds zusammen.

## Verifikation

- **Kern:** jede Einheit an einer Mini-Instanz von Hand (Weg 0–1–2–3, zwei Paare in B; Kaskadenverlauf (4, 4), (2, 2), (2, 2); q = 0), Randfälle (kleinste und größte Reglerwerte für jede Schicht und jeden Partner, p = 0 und p = 1, Netze ohne Kanten, kleinstes Gitter, Rundengrenze).
- **Orakel:** `networkx` für Komponenten, Kaskade, Hubgröße; Fixpunkteigenschaft des Endzustands; Theorie gegen Simulation.
- **Verdikte:** reine Funktionen, jede Schwelle (1 % und 90 %) und jede Zahl im Text an handgesetzten Werten (`tests/test_verdicts.py`).
- **Presets, Layout, Oberfläche:** wie in allen Demos (Presets vollständig und im Regelbereich und auf dem Raster der Regler, keines auf einem Reglerrand, kein Preset entsteht durch Änderung eines einzigen Reglers, Schnellstart oben, aktives Preset hervorgehoben, AppTest jeder Button und jeder Regler an den Rändern).
- **Mutationsprüfung** (`tools/mutate_demo.py`): 85 Stellen im Kern `abn_algorithm.py`, **68 gefangen** (39 davon über wortgleiche Zeilen in Nachbar-Demos), 9 als äquivalent festgehalten, 8 Zeitüberschreitungen (das Werkzeug zählt sie nicht). Der erste Lauf ließ 10 Mutanten überleben; einer deckte eine echte Lücke auf (die Reihenfolge der Gitterkanten, jetzt in `test_algorithm.py` geprüft). Die neun äquivalenten Stellen: `<` statt `<=` beim Ziehen mit `rng.random` (gleich nur mit Wahrscheinlichkeit null), das Vorzeichen im Abbruchkriterium der beiden Fixpunktiterationen (sie laufen dann bis zur Rundengrenze und enden am selben Wert), `>` statt `>=` an der Schwelle 10⁻⁴, eine Runde weniger in der Obergrenze von 20 000 Iterationen und das Vorzeichen des Nachbarn im Torusgitter (dieselbe Kantenmenge von der anderen Seite gezählt). Die 8 Zeitüberschreitungen sind Mutanten der Ziehschleife von G(n, m) (Zeilen 25 und 33, wie in den Nachbar-Demos) und zwei der Abbruchbedingung der Kaskade (Zeile 123); vier Abwandlungen dieser Bedingung (`!=`, `or`, `any`) wurden von Hand in einer Kopie geprüft und von den Tests gefangen, welche zwei genau in die Zeitüberschreitung liefen, ist nicht einzeln festgehalten.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `abn_algorithm.py` | Kern: Netzerzeuger, größte Komponente, Kaskade, Theorie |
| `abn_constants.py` | Regler-Grenzen, Schwellen, feste Pläne, Farben, Presets |
| `abn_evaluation.py` | Analyse, Messreihen, Verdikte, Tabellen |
| `abn_layout.py` | Fester Kopf (Stylesheet) |
| `abn_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `abn_scenario.py` | Schichtpaare (unabhängig, umnummeriert oder als Kopie) |
| `abn_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `app.py` | Streamlit-App |
| `messen.py` | Einmalige Messung der Zahlen in dieser README (nicht Teil der App) |
| `requirements-dev.txt` | Laufzeit plus pytest und networkx (nur Gegenprobe) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanzen, Kern, Orakel, Verdikte, Randfälle, Presets, Abbildungen, Layout, AppTest, Footer, Laufzeit-Importe, Claims |

## Bewusst nicht umgesetzt

- **Lastbasierte Kaskaden:** dafür gibt es [kaskaden-demo](https://github.com/sebastian-hanisch/kaskaden-demo); hier zählt nur der Zusammenhang.
- **Mehr als zwei Schichten und Mehrfachabhängigkeit:** würden die Modelle deutlich ändern; die Theorie dazu ist nicht Gegenstand dieser Demo.
- **Gezielte Angriffe** (auf die Knoten mit höchstem Grad): würden die Schichtart gegenüber zufälligem Ausfall neu bewerten; die Demo entfernt Knoten zufällig.
- **Einordnung des Übergangs als „hybrid“:** die Demo misst den Sprung, die Einordnung bleibt der Literatur überlassen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und SciPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
