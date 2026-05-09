"""
Code 9: Generate Presentation-Ready Dataset Report
"""
import pandas as pd
import numpy as np

def generate_report():
    print("Loading raw feature mappings...")
    try:
        df = pd.read_csv('ready_polymer_dataset.csv')
    except Exception as e:
        print(f"Error loading ready_polymer_dataset.csv: {e}")
        return
        
    print("Computing 'Good Fit' analytical flags...")
    # The "Good Fit" Logic: >= 450.0 MV/m
    df['Good_Fit'] = np.where(df['Target_Eb'] >= 450.0, 'Yes', 'No')
    
    print("Reorganizing dataframe sequence for academic legibility...")
    
    # 1. Base Generation Mechanics
    base_cols = ['SMILES', 'ProcessingTemp_C', 'Crystallinity']
    
    # 2. Extract Explicit Physical & Structural Arrays strictly keeping nomenclature
    struct_cols = [c for c in df.columns if c.startswith('Struct_')]
    phys_cols = [c for c in df.columns if c.startswith('Phys_')]
    
    # 3. Extract High-Dimensional Arrays (Morgan/PolyBERT sets mapped prior to downstream PCA compression)
    morgan_cols = [c for c in df.columns if c.startswith('Morgan_Bit_')]
    polybert_cols = [c for c in df.columns if c.startswith('PolyBERT_Dim_')]
    
    # 4. Critical Ends
    target_cols = ['Good_Fit', 'Target_Eb']
    
    # Reassemble exact Sequence
    ordered_columns = base_cols + struct_cols + phys_cols + morgan_cols + polybert_cols + target_cols
    
    # Check if any columns dropped from expectations
    df_ordered = df[ordered_columns]
    
    output_filename = 'presentation_ready_report.csv'
    df_ordered.to_csv(output_filename, index=False)
    
    print(f"===========================================================")
    print(f"SUCCESS: Report saved as -> {output_filename}")
    print(f"===========================================================")
    print(f"Rows: {df_ordered.shape[0]}")
    print(f"Total Ordered Columns: {df_ordered.shape[1]}")
    print(f"- End Anchors Successfully Verified: {df_ordered.columns[-2]} | {df_ordered.columns[-1]}")

if __name__ == "__main__":
    generate_report()
