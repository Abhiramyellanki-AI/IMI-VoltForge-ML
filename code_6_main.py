"""
Code 6: Main script that integrates Codes 1-5 and creates the raw dataset (no PCA applied yet to avoid test leakage).
"""
import pandas as pd

from code_1_generate import generate_polymers
from code_2_structural import get_structural_features
from code_3_polybert import get_polybert_features_batch
from code_4_physical import get_physical_features
from code_5_morgan import get_morgan_fingerprint

def build_final_dataset():
    print("--- Step 1: Generating Bounded Polymers ---")
    dataset_records = generate_polymers()
    smiles_list = [record["SMILES"] for record in dataset_records]
    print(f"Generated {len(smiles_list)} unique polymer SMILES records.")
    
    print("\n--- Step 2: Extracting PolyBERT Features (Full Dimension Pipeline) ---")
    polybert_dict = get_polybert_features_batch(smiles_list)
    
    all_data = []
    
    print("\n--- Step 3: Computing Structural, Physical, and Morgan Features ---")
    for idx, record in enumerate(dataset_records):
        if idx > 0 and idx % 200 == 0:
            print(f"Processing ({idx}/{len(dataset_records)})...")
            
        smiles = record["SMILES"]
        
        # Initiate base record properties
        row_data = {
            "SMILES": smiles,
            "ProcessingTemp_C": record["ProcessingTemp_C"],
            "Crystallinity": record["Crystallinity"],
            "Target_Eb": record["Target_Eb"]
        }
        
        struct_feats = get_structural_features(smiles)
        for k, v in struct_feats.items():
            row_data[f"Struct_{k}"] = v
            
        phys_feats = get_physical_features(smiles)
        for k, v in phys_feats.items():
            row_data[f"Phys_{k}"] = v
            
        # Exact full 1024 Academic Structure Bounds
        morgan_fp = get_morgan_fingerprint(smiles, radius=2, nBits=1024)
        for i, bit in enumerate(morgan_fp):
            row_data[f"Morgan_Bit_{i}"] = bit
            
        # Pull Exact 600 PolyBert Dimensions
        pb_feats = polybert_dict.get(smiles, [0]*600)
        for i, val in enumerate(pb_feats):
            row_data[f"PolyBERT_Dim_{i}"] = val
            
        all_data.append(row_data)

    print("\n--- Step 4: Assembling Raw Final Dataset (Leak Free) ---")
    df = pd.DataFrame(all_data)
    
    # Save massive raw dataset directly
    output_filename = "ready_polymer_dataset.csv"
    df.to_csv(output_filename, index=False)
    
    print(f"\nDimensions: {df.shape[0]} Polymers x {df.shape[1] - 4} Extracted Features")
    print(f"Dataset securely saved as {output_filename}")

    # ---------------- Latent Space Scatter Plot ---------------- #
    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA
    
    print("\n--- Generating Defensive Latent Space Projection ---")
    morgan_cols = [f"Morgan_Bit_{i}" for i in range(1024)]
    raw_morgan = df[morgan_cols].values
    
    pca_visual = PCA(n_components=2, random_state=42)
    morgan_pca_2d = pca_visual.fit_transform(raw_morgan)
    
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(morgan_pca_2d[:, 0], morgan_pca_2d[:, 1], c=df['Target_Eb'], cmap='viridis', alpha=0.7)
    plt.colorbar(scatter, label='Target Eb (MV/m)')
    plt.title('Morgan Fingerprint Latent Space (PCA)')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig('pca_latent_space.png', dpi=300)
    print("Saved Latent Space Visualization to 'pca_latent_space.png'")

if __name__ == "__main__":
    build_final_dataset()
