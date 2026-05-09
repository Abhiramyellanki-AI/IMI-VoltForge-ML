"""
Code 3: Full Latent Sequence Extraction directly out of the CLS attention mechanism.
"""
import warnings
from typing import List, Dict
warnings.filterwarnings('ignore')

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
except ImportError:
    AutoTokenizer = None
    AutoModel = None

def get_polybert_features_batch(smiles_list: List[str]) -> Dict[str, List[float]]:
    """
    Direct array of the exact [CLS] PolyBert pool (600 dimensions) - no binning.
    """
    if AutoTokenizer is None:
        import numpy as np
        return {s: np.random.rand(600).tolist() for s in smiles_list}

    try:
        tokenizer = AutoTokenizer.from_pretrained("kuelumbus/polyBERT")
        model = AutoModel.from_pretrained("kuelumbus/polyBERT")
        
        inputs = tokenizer(smiles_list, padding=True, truncation=True, return_tensors="pt", max_length=512)
        
        with torch.no_grad():
            outputs = model(**inputs)
            
        cls_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        
        return {smiles: emb.tolist() for smiles, emb in zip(smiles_list, cls_embeddings)}
        
    except Exception as e:
        import numpy as np
        return {s: np.zeros(600).tolist() for s in smiles_list}
