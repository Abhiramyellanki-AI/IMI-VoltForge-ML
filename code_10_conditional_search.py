"""
Code 10 (Phase B): Conditional Polymer Search Engine
Given (target_eb, polymer_class), finds the best matching polymers from the dataset.

Strategy:
  1. Infer polymer class from SMILES pattern matching (PP / PET / PVDF)
  2. Filter dataset by requested class
  3. Rank filtered candidates by |Target_Eb - target_eb|
  4. Re-rank top-20 by Morgan cosine diversity to surface structurally varied results
  5. Return top-K final candidates with all relevant metadata
"""
import os
import sys
import numpy as np
import pandas as pd
from typing import List, Dict, Optional

# Ensure the project root is importable when called from production/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from code_2_structural import get_structural_features
from code_4_physical    import get_physical_features
from code_5_morgan      import get_morgan_fingerprint


# ─────────────────────────────────────────────────────────────────────────────
#  Class Inference
# ─────────────────────────────────────────────────────────────────────────────

def infer_polymer_class(smiles: str) -> str:
    """
    Infers polymer family from SMILES patterns.
    Priority order: PVDF → PET → PP (defined in config.CLASS_PRIORITY).

    PVDF: any fluorine on a carbon backbone  → C(F), CF, C(F)(F)
    PET:  aromatic ester linkage             → C(=O)c1 or c1ccc + OCC
    PP:   aliphatic olefin backbone          → CC( pattern
    """
    for cls in config.CLASS_PRIORITY:
        patterns = config.CLASS_PATTERNS[cls]
        if any(p in smiles for p in patterns):
            return cls
    return "Unknown"


def add_class_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Annotates a dataframe that has a 'SMILES' column with a 'PolymerClass' column.
    Does NOT re-run any feature extraction — purely pattern-based.
    """
    df = df.copy()
    df['PolymerClass'] = df['SMILES'].apply(infer_polymer_class)
    return df


# ─────────────────────────────────────────────────────────────────────────────
#  Morgan Cosine Re-Ranker
# ─────────────────────────────────────────────────────────────────────────────

def _morgan_vector(smiles: str) -> np.ndarray:
    """Returns a 1024-bit Morgan fingerprint as a float numpy array."""
    fp = get_morgan_fingerprint(smiles, radius=2, nBits=1024)
    return np.array(fp, dtype=np.float32)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def _diverse_rerank(candidates: pd.DataFrame, top_k: int) -> pd.DataFrame:
    """
    From a pre-filtered + |Eb|-ranked candidate pool, selects top_k results
    that are maximally diverse in Morgan space.

    Uses a greedy max-min selection:
      - Always pick the closest-Eb match first
      - Each subsequent pick maximizes min-distance to already-selected set
    """
    if len(candidates) <= top_k:
        return candidates

    smiles_list = candidates['SMILES'].tolist()
    fps = [_morgan_vector(s) for s in smiles_list]

    selected_idx = [0]   # always start with closest-Eb match

    for _ in range(top_k - 1):
        best_candidate = -1
        best_score     = -1.0

        for i in range(len(candidates)):
            if i in selected_idx:
                continue
            # Minimum cosine DISTANCE (1 - similarity) to already selected
            min_dist = min(
                1.0 - _cosine_similarity(fps[i], fps[j])
                for j in selected_idx
            )
            if min_dist > best_score:
                best_score     = min_dist
                best_candidate = i

        if best_candidate == -1:
            break
        selected_idx.append(best_candidate)

    return candidates.iloc[selected_idx].reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Main Search Function
# ─────────────────────────────────────────────────────────────────────────────

def search_by_eb_and_class(
    target_eb: float,
    polymer_class: str,
    top_k: int = 5,
    pre_filter_k: int = 20,
    dataset_path: Optional[str] = None,
) -> List[Dict]:
    """
    Core search function for Phase B conditional polymer generation.

    Args:
        target_eb:      Desired dielectric breakdown strength in MV/m
        polymer_class:  'PP', 'PET', or 'PVDF' (case-insensitive)
        top_k:          Number of final diverse candidates to return
        pre_filter_k:   Pool size before diversity re-ranking (default 20)
        dataset_path:   Override dataset CSV path (defaults to config.DATASET_PATH)

    Returns:
        List of dicts, each containing:
          SMILES, PolymerClass, Target_Eb, ProcessingTemp_C, Crystallinity,
          Eb_Delta (distance from target), Rank
    """
    path = dataset_path or config.DATASET_PATH

    # ── Load and annotate dataset ──────────────────────────────────────────
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Dataset not found at '{path}'. "
            "Run code_6_main.py first to generate ready_polymer_dataset.csv"
        )

    # Only keep columns we need for speed
    meta_cols = ['SMILES', 'ProcessingTemp_C', 'Crystallinity', 'Target_Eb']
    df_meta = df[meta_cols].copy()
    df_meta = add_class_column(df_meta)

    # ── Filter by polymer class ────────────────────────────────────────────
    cls_upper = polymer_class.strip().upper()
    cls_map   = {"PP": "PP", "PET": "PET", "PVDF": "PVDF"}

    if cls_upper not in cls_map:
        raise ValueError(
            f"Unknown polymer_class '{polymer_class}'. "
            f"Valid options: {list(cls_map.keys())}"
        )

    filtered = df_meta[df_meta['PolymerClass'] == cls_map[cls_upper]].copy()

    if filtered.empty:
        raise ValueError(
            f"No polymers of class '{cls_upper}' found in dataset. "
            "Check class inference patterns in config.CLASS_PATTERNS."
        )

    # ── Rank by |Eb - target_eb| ───────────────────────────────────────────
    filtered['Eb_Delta'] = (filtered['Target_Eb'] - target_eb).abs()
    filtered = filtered.sort_values('Eb_Delta').head(pre_filter_k).reset_index(drop=True)

    # ── Diversity re-rank in Morgan space ──────────────────────────────────
    diverse = _diverse_rerank(filtered, top_k)

    # ── Format output ──────────────────────────────────────────────────────
    results = []
    for rank, row in diverse.iterrows():
        results.append({
            "rank":              int(rank) + 1,
            "smiles":            row['SMILES'],
            "polymer_class":     row['PolymerClass'],
            "target_eb_dataset": round(float(row['Target_Eb']), 2),
            "eb_delta":          round(float(row['Eb_Delta']), 2),
            "processing_temp_c": round(float(row['ProcessingTemp_C']), 2),
            "crystallinity":     round(float(row['Crystallinity']), 4),
        })

    return results


# ─────────────────────────────────────────────────────────────────────────────
#  On-the-fly Feature Extraction (for new SMILES not in dataset)
# ─────────────────────────────────────────────────────────────────────────────

def get_candidate_features(smiles: str) -> Dict:
    """
    Computes the lightweight (no PolyBERT) feature set for a novel SMILES.
    Used by the API's /predict endpoint in lightweight mode.

    Returns a flat dict matching the dataset column schema for
    Struct_*, Phys_*, Morgan_Bit_* (1024 dims).
    Note: PolyBERT_Dim_* features will be zero-padded.
    """
    features = {}

    struct_feats = get_structural_features(smiles)
    for k, v in struct_feats.items():
        features[f"Struct_{k}"] = v

    phys_feats = get_physical_features(smiles)
    for k, v in phys_feats.items():
        features[f"Phys_{k}"] = v

    morgan_fp = get_morgan_fingerprint(smiles, radius=2, nBits=1024)
    for i, bit in enumerate(morgan_fp):
        features[f"Morgan_Bit_{i}"] = bit

    # Zero-pad PolyBERT dims (lightweight mode — no transformer)
    for i in range(600):
        features[f"PolyBERT_Dim_{i}"] = 0.0

    return features


# ─────────────────────────────────────────────────────────────────────────────
#  CLI Test Harness
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  Phase B — Conditional Polymer Search Test")
    print("=" * 60)

    test_cases = [
        (600.0, "PVDF"),
        (450.0, "PET"),
        (350.0, "PP"),
    ]

    for eb_target, cls in test_cases:
        print(f"\n>>> Searching: target_eb={eb_target} MV/m | class={cls}")
        try:
            results = search_by_eb_and_class(eb_target, cls, top_k=3)
            for r in results:
                print(
                    f"  Rank {r['rank']}: Eb={r['target_eb_dataset']} MV/m "
                    f"(Δ={r['eb_delta']}) | Temp={r['processing_temp_c']}°C "
                    f"| Cryst={r['crystallinity']} | {r['smiles'][:50]}..."
                )
        except Exception as e:
            print(f"  ERROR: {e}")

    print("\nPhase B search engine verified.")
