"""
Code 5: Dense Morgan Vectors across Structural Bounds.
"""
from typing import List
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
import numpy as np

def get_morgan_fingerprint(smiles: str, radius: int = 2, nBits: int = 1024) -> List[int]:
    """
    Standard nBits=1024 Morgan hashing vector limit mapping tightly.
    """
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return [0] * nBits
        
    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius, nBits=nBits)
    fp_array = np.zeros((0,), dtype=np.int8)
    Chem.DataStructs.ConvertToNumpyArray(fp, fp_array)
    
    return fp_array.tolist()
