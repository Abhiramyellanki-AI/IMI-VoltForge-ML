"""
Code 2: Exactly 40 structural limits rigorously enforced.
"""
from typing import Dict
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem import Fragments

_FRAG_SMARTS = {
    "fr_benzene": "c1ccccc1",
    "fr_ether": "[OD2]([#6])[#6]",
    "fr_amide": "C(=O)-N",
    "fr_NH0": "[NH0,nH0]",
    "fr_NH1": "[NH1,nH1]",
    "fr_NH2": "[NH2,nH2]",
    "fr_COO": "[#6]C(=O)[O;H,-1]",
    "fr_C_O": "[CX3]=[OX1]",
    "fr_COO2": "[CX3](=O)[OX1H0-,OX2H1]",
    "fr_phenol": "[OX2H]-c1ccccc1",
    "fr_pyridine": "n1ccccc1",
    "fr_piperdine": "N1CCCCC1",
    "fr_piperzine": "N1CCNCC1",
    "fr_Ar_N": "n",
    "fr_Ar_OH": "c[OH1]",
    "fr_halogen": "[#9,#17,#35,#53]",
    "fr_alkyl_halide": "[CX4]-[Cl,Br,I,F]",
    "fr_aniline": "c-[NX3;!$(N=*)]",
    "fr_ester": "[#6][CX3](=O)[OX2H0][#6]",
    "fr_ketone": "[#6][CX3](=O)[#6]",
    "fr_lactone": "[C&R1](=O)[O&R1][C&R1]",
    "fr_urea": "C(=O)(-N)-N",
    "fr_aldehyde": "[CX3H1](=O)[#6]",
    "fr_bicyclic": "[R2][R2]"
}
_PATTERNS = {}

def get_structural_features(smiles: str) -> Dict[str, float]:
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return {f"struct_{i}": 0.0 for i in range(40)}

    feats = {}
    
    # 1-24: Exact SMARTS Pattern Fragments
    for name, sma in _FRAG_SMARTS.items():
        if name not in _PATTERNS:
            _PATTERNS[name] = Chem.MolFromSmarts(sma)
        feats[name] = float(len(mol.GetSubstructMatches(_PATTERNS[name])))
    
    # Rings & Bounds (Using native RDKit Descriptors)
    feats["NumRotatableBonds"] = float(rdMolDescriptors.CalcNumRotatableBonds(mol))
    feats["NumRings"] = float(rdMolDescriptors.CalcNumRings(mol))
    feats["NumAromaticRings"] = float(rdMolDescriptors.CalcNumAromaticRings(mol))
    feats["NumAliphaticRings"] = float(rdMolDescriptors.CalcNumAliphaticRings(mol))
    feats["NumSaturatedRings"] = float(rdMolDescriptors.CalcNumSaturatedRings(mol))
    feats["NumHeterocycles"] = float(rdMolDescriptors.CalcNumHeterocycles(mol))
    feats["NumAromaticHeterocycles"] = float(rdMolDescriptors.CalcNumAromaticHeterocycles(mol))
    feats["NumAliphaticHeterocycles"] = float(rdMolDescriptors.CalcNumAliphaticHeterocycles(mol))
    feats["NumSaturatedHeterocycles"] = float(rdMolDescriptors.CalcNumSaturatedHeterocycles(mol))
    feats["NumHeavyAtoms"] = float(mol.GetNumHeavyAtoms())
    
    # Special Stereocenters & Acceptors
    feats["NumAmideBonds"] = float(rdMolDescriptors.CalcNumAmideBonds(mol))
    feats["NumSpiroAtoms"] = float(rdMolDescriptors.CalcNumSpiroAtoms(mol))
    feats["NumBridgeheadAtoms"] = float(rdMolDescriptors.CalcNumBridgeheadAtoms(mol))
    feats["NumAtomStereoCenters"] = float(rdMolDescriptors.CalcNumAtomStereoCenters(mol))
    feats["NumHBA"] = float(rdMolDescriptors.CalcNumHBA(mol))
    feats["NumHBD"] = float(rdMolDescriptors.CalcNumHBD(mol))

    assert len(feats) == 40, f"Error: Exact structure elements {len(feats)} not 40"
    return feats
