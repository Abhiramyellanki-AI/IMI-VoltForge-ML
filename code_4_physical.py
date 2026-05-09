"""
Code 4: Exactly 40 Physical Parameters mathematically constrained.
"""
from typing import Dict
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import rdMolDescriptors
import rdkit.Chem.GraphDescriptors as GraphDescriptors

def get_physical_features(smiles: str) -> Dict[str, float]:
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return {f"phys_{i}": 0.0 for i in range(40)}

    feats = {}
    
    # 1-7 Basic Phys & Shape Bounds
    feats["ExactMolWt"] = float(Descriptors.ExactMolWt(mol))
    feats["MolLogP"] = float(Descriptors.MolLogP(mol))
    feats["MolMR"] = float(Descriptors.MolMR(mol))
    feats["TPSA"] = float(rdMolDescriptors.CalcTPSA(mol))
    feats["LabuteASA"] = float(rdMolDescriptors.CalcLabuteASA(mol))
    feats["BalabanJ"] = float(GraphDescriptors.BalabanJ(mol))
    feats["BertzCT"] = float(GraphDescriptors.BertzCT(mol))
    
    # 8-19 Chi Indeces
    feats["Chi0"] = float(GraphDescriptors.Chi0(mol))
    feats["Chi0n"] = float(GraphDescriptors.Chi0n(mol))
    feats["Chi0v"] = float(GraphDescriptors.Chi0v(mol))
    feats["Chi1"] = float(GraphDescriptors.Chi1(mol))
    feats["Chi1n"] = float(GraphDescriptors.Chi1n(mol))
    feats["Chi1v"] = float(GraphDescriptors.Chi1v(mol))
    feats["Chi2n"] = float(GraphDescriptors.Chi2n(mol))
    feats["Chi2v"] = float(GraphDescriptors.Chi2v(mol))
    feats["Chi3n"] = float(GraphDescriptors.Chi3n(mol))
    feats["Chi3v"] = float(GraphDescriptors.Chi3v(mol))
    feats["Chi4n"] = float(GraphDescriptors.Chi4n(mol))
    feats["Chi4v"] = float(GraphDescriptors.Chi4v(mol))
    
    # 20-25 Kappa & Ipc
    feats["Kappa1"] = float(GraphDescriptors.Kappa1(mol))
    feats["Kappa2"] = float(GraphDescriptors.Kappa2(mol))
    feats["Kappa3"] = float(GraphDescriptors.Kappa3(mol))
    feats["HallKierAlpha"] = float(GraphDescriptors.HallKierAlpha(mol))
    feats["Ipc"] = float(GraphDescriptors.Ipc(mol))
    feats["FractionCSP3"] = float(rdMolDescriptors.CalcFractionCSP3(mol))
    
    # 26-40 Detailed Electronic Fields
    slog = rdMolDescriptors.SlogP_VSA_(mol)
    smr  = rdMolDescriptors.SMR_VSA_(mol)
    peoe = rdMolDescriptors.PEOE_VSA_(mol)
    
    feats["SMR_VSA1"] = float(smr[0]) if len(smr) > 0 else 0.0
    feats["SMR_VSA2"] = float(smr[1]) if len(smr) > 1 else 0.0
    feats["SMR_VSA3"] = float(smr[2]) if len(smr) > 2 else 0.0
    feats["SMR_VSA4"] = float(smr[3]) if len(smr) > 3 else 0.0
    feats["SMR_VSA5"] = float(smr[4]) if len(smr) > 4 else 0.0
    
    feats["SlogP_VSA1"] = float(slog[0]) if len(slog) > 0 else 0.0
    feats["SlogP_VSA2"] = float(slog[1]) if len(slog) > 1 else 0.0
    feats["SlogP_VSA3"] = float(slog[2]) if len(slog) > 2 else 0.0
    feats["SlogP_VSA4"] = float(slog[3]) if len(slog) > 3 else 0.0
    feats["SlogP_VSA5"] = float(slog[4]) if len(slog) > 4 else 0.0
    
    feats["PEOE_VSA1"] = float(peoe[0]) if len(peoe) > 0 else 0.0
    feats["PEOE_VSA2"] = float(peoe[1]) if len(peoe) > 1 else 0.0
    feats["PEOE_VSA3"] = float(peoe[2]) if len(peoe) > 2 else 0.0
    feats["PEOE_VSA4"] = float(peoe[3]) if len(peoe) > 3 else 0.0
    feats["PEOE_VSA5"] = float(peoe[4]) if len(peoe) > 4 else 0.0

    assert len(feats) == 40, f"Error: Exact physical elements {len(feats)} not 40"
    return feats
