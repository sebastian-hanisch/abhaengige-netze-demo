"""Szenario: das Schichtpaar zu den Einstellungen (deterministisch je Zufalls-Seed)."""

import math

import numpy as np

import abn_algorithm as A
import abn_constants as C


def layer_edges(kind: str, n: int, c: float, rng: np.random.Generator):
    """Kanten einer Schicht: Erdős–Rényi mit mittlerem Grad c, Barabási–Albert mit m = round(c / 2) (mindestens 1) oder das Gitter mit der Seite round(√n) (n wird dann zum Quadrat)."""
    if kind == "er":
        return n, A.er_edges(n, c, rng)
    if kind == "ba":
        return n, A.ba_edges(n, max(1, int(round(c / 2.0))), rng)
    if kind == "lattice":
        side = max(3, int(round(math.sqrt(n))))
        return side * side, A.lattice_edges(side)
    raise ValueError(f"unbekannte Schicht: {kind}")


def make_pair(kind: str, partner: str, n: int, c: float, seed: int):
    """Schicht A und Schicht B als (Knotenzahl, Kanten A, Kanten B). Unabhängig: Schicht B ist eine zweite Ziehung (beim Gitter dasselbe Gitter mit zufällig umnummerierten Knoten);
    Kopie: Schicht B hat genau die Kanten von A."""
    rng = np.random.default_rng(seed)
    n_eff, ea = layer_edges(kind, n, c, rng)
    if partner == "copy":
        return n_eff, ea, list(ea)
    if partner != "independent":
        raise ValueError(f"unbekannter Partner: {partner}")
    if kind == "lattice":
        return n_eff, ea, A.relabel(ea, rng.permutation(n_eff))
    return n_eff, ea, layer_edges(kind, n, c, rng)[1]
