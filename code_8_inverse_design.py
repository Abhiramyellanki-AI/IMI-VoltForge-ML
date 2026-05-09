"""
Code 8: Iterative Inverse Design Search Protocol using Calculus L-BFGS-B Optimization.
"""
import pandas as pd
import numpy as np
import joblib
from scipy.optimize import minimize
import config

def objective_wrapper(x, pipeline, base_row, target_eb, feature_order):
    """
    Evaluates absolute bounds difference from target metric via bounded MLP pipeline.
    x[0] -> ProcessingTemp_C
    x[1] -> Crystallinity
    """
    candidate = base_row.copy()
    
    # Inject dynamically generated optimizing calculus constraints
    candidate['ProcessingTemp_C'] = x[0]
    candidate['Crystallinity'] = x[1]
    
    # Push series structure securely mapped to dataframe
    df_candidate = pd.DataFrame([candidate])[feature_order]
    
    # Inference wrapper bounds prediction cleanly
    prediction = pipeline.predict(df_candidate)[0]
    
    return (prediction - target_eb) ** 2

def main():
    print("Loading Core MLP Mathematical Pipeline Models...")
    try:
        pipeline = joblib.load('mlp_pipeline.pkl')
        dataset = pd.read_csv('ready_polymer_dataset.csv')
    except Exception as e:
        print(f"Error Mapping Core Dependency Files: {e}")
        print("Please ensure you have generated dataset and run code_7.")
        return
        
    print("Isolating Test Case Polymer for Baseline Bounds Injection...")
    sample_index = 0
    sample_polymer_smi = dataset.iloc[sample_index]['SMILES']
    
    # Extract baseline raw attributes completely freezing specific topology sets
    frozen_row = dataset.iloc[sample_index].drop(['SMILES', 'Target_Eb'])
    feature_order = frozen_row.index.tolist()
    
    DESIRED_EB = 700.0  # MV/m target threshold
    print(f"Optimizing Base Polymer: {sample_polymer_smi}")
    print(f"Goal: Morph bounds to hit Dielectric Strength of {DESIRED_EB} MV/m")
    
    # ------------------ Calculus Inverse Design ------------------ #
    bounds = [config.TEMP_BOUNDS, config.CRYST_BOUNDS]
    initial_guesses = [
        [config.TEMP_BOUNDS[0] + 10, config.CRYST_BOUNDS[0] + 0.1],
        [(config.TEMP_BOUNDS[0] + config.TEMP_BOUNDS[1]) / 2, (config.CRYST_BOUNDS[0] + config.CRYST_BOUNDS[1]) / 2],
        [config.TEMP_BOUNDS[1] - 10, config.CRYST_BOUNDS[1] - 0.1]
    ]
    
    best_res = None
    for guess in initial_guesses:
        res = minimize(
            objective_wrapper,
            x0=guess,
            args=(pipeline, frozen_row, DESIRED_EB, feature_order),
            method='L-BFGS-B',
            bounds=bounds,
            options={'disp': False, 'maxiter': 500}
        )
        if best_res is None or res.fun < best_res.fun:
            best_res = res
            
    res = best_res
    
    print("\n" + "="*40)
    print("=== DIELECTRIC DESIGN OPTIMIZATION VALIDATED ===")
    print("="*40)
    print(f"SMILES Base Molecule: -> {sample_polymer_smi}")
    
    if res.success:
        print("\nCalculus Gradients Successfully Reached Local Minimum!")
        print(f"Optimal Processing Temperature: {res.x[0]:.2f} °C")
        print(f"Optimal Crystallinity Fraction: {res.x[1]:.4f}")
        
        # Verify final output mapping
        frozen_row['ProcessingTemp_C'] = res.x[0]
        frozen_row['Crystallinity'] = res.x[1]
        final_candidate_df = pd.DataFrame([frozen_row])[feature_order]
        final_prediction = pipeline.predict(final_candidate_df)[0]
        
        print(f"Estimated Machine Learning Output: -> {final_prediction:.2f} MV/m (Target: {DESIRED_EB})")
        print(f"Absolute Margin Error: {abs(final_prediction - DESIRED_EB):.2f} MV/m")
    else:
        print("\nGradient Optimization Failed Converging...")
        print(f"Message: {res.message}")

if __name__ == "__main__":
    main()
