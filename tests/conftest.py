"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import abn_algorithm as A  # noqa: E402


@pytest.fixture
def path_a():
    """Schicht A: Weg 0–1–2–3 (zusammenhängend)."""
    return A.adjacency(4, [(0, 1), (1, 2), (2, 3)])


@pytest.fixture
def two_pairs_b():
    """Schicht B: zwei getrennte Kanten (0,1) und (2,3), die größte Komponente ist bei Gleichstand {0, 1}."""
    return A.adjacency(4, [(0, 1), (2, 3)])
