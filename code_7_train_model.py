"""
Code 7: Phase A — Improved Academic QSPR Regression Trainer.
Changes from original:
  - MLP: (128,64) → (256,128,64), max_iter 200→2000, adaptive LR, patience=20
  - Added GradientBoostingRegressor as ensemble partner
  - VotingRegressor blends MLP pipeline + GBR pipeline (weights from config)
  - Exports both mlp_pipeline.pkl (backward compat) and ensemble_pipeline.pkl
  - Auto-appends benchmark results to Final_Report.md
"""
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import GradientBoostingRegressor, VotingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

import config


def build_preprocessor(morgan_cols, polybert_cols):
    """
    Constructs the zero-leakage ColumnTransformer (fit-on-train-only).
    Shared between MLP pipeline and GBR pipeline so both receive identical features.
    """
    return ColumnTransformer(
        transformers=[
            ('pca_morgan',   PCA(n_components=config.NUM_MORGAN_PCA,   random_state=config.RANDOM_SEED), morgan_cols),
            ('pca_polybert', PCA(n_components=config.NUM_POLYBERT_PCA, random_state=config.RANDOM_SEED), polybert_cols),
        ],
        remainder='passthrough'
    )


def build_mlp_pipeline(preprocessor):
    """
    Phase A improved MLP: deeper layers, adaptive LR, longer patience.
    """
    return Pipeline([
        ('preprocessor', preprocessor),
        ('imputer',      SimpleImputer(strategy='median')),
        ('scaler',       StandardScaler()),
        ('collinearity', config.CollinearityDropper(threshold=0.95)),
        ('mlp', MLPRegressor(
            hidden_layer_sizes   = config.MLP_HIDDEN_LAYER_SIZES,
            activation           = config.MLP_ACTIVATION,
            solver               = config.MLP_SOLVER,
            learning_rate        = config.MLP_LEARNING_RATE,
            learning_rate_init   = config.MLP_LEARNING_RATE_INIT,
            max_iter             = config.MLP_MAX_ITER,
            early_stopping       = config.MLP_EARLY_STOPPING,
            validation_fraction  = config.MLP_VALIDATION_FRACTION,
            n_iter_no_change     = config.MLP_N_ITER_NO_CHANGE,
            alpha                = config.MLP_ALPHA,
            random_state         = config.RANDOM_SEED,
        ))
    ])


def build_gbr_pipeline(preprocessor):
    """
    GradientBoostingRegressor pipeline — shares the same preprocessor steps.
    GBR handles non-linearity and outliers that MLP may miss.
    """
    return Pipeline([
        ('preprocessor', preprocessor),
        ('imputer',      SimpleImputer(strategy='median')),
        ('scaler',       StandardScaler()),
        ('collinearity', config.CollinearityDropper(threshold=0.95)),
        ('gbr', GradientBoostingRegressor(
            n_estimators     = config.GBR_N_ESTIMATORS,
            learning_rate    = config.GBR_LEARNING_RATE,
            max_depth        = config.GBR_MAX_DEPTH,
            subsample        = config.GBR_SUBSAMPLE,
            min_samples_leaf = config.GBR_MIN_SAMPLES_LEAF,
            random_state     = config.GBR_RANDOM_STATE,
        ))
    ])


def print_metrics(label, y_true, y_pred):
    r2   = r2_score(y_true, y_pred)
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    print(f"\n--- {label} BENCHMARKS ---")
    print(f"  R²:   {r2:.4f}")
    print(f"  MAE:  {mae:.2f} MV/m")
    print(f"  RMSE: {rmse:.2f} MV/m\n")
    return r2, mae, rmse


def save_metrics_to_report(mlp_metrics, ensemble_metrics):
    """Appends actual benchmark values to Final_Report.md."""
    try:
        with open('Final_Report.md', 'r') as f:
            content = f.read()

        # Replace placeholder tokens
        content = content.replace('[ INSERT MAE SCORE HERE ]',  f"{ensemble_metrics[1]:.2f}")
        content = content.replace('[ INSERT RMSE SCORE HERE ]', f"{ensemble_metrics[2]:.2f}")
        content = content.replace('[ INSERT R2 SCORE HERE ]',   f"{ensemble_metrics[0]:.4f}")

        # Append Phase A comparison section
        addition = f"""
## Section 4: Phase A — Model Improvement Results

| Model | R² | MAE (MV/m) | RMSE (MV/m) |
|---|---|---|---|
| MLP (original: 128,64 / iter=200) | 0.7453 | 30.75 | 39.18 |
| MLP (tuned: 256,128,64 / iter=2000) | {mlp_metrics[0]:.4f} | {mlp_metrics[1]:.2f} | {mlp_metrics[2]:.2f} |
| **Ensemble (MLP+GBR blend)** | **{ensemble_metrics[0]:.4f}** | **{ensemble_metrics[1]:.2f}** | **{ensemble_metrics[2]:.2f}** |
"""
        if "Section 4" not in content:
            content += addition

        with open('Final_Report.md', 'w') as f:
            f.write(content)

        print("Final_Report.md updated with Phase A benchmark results.")
    except Exception as e:
        print(f"Warning: Could not update Final_Report.md: {e}")


def main():
    print("=" * 55)
    print("  Phase A — IMI Model Improvement Training Run")
    print("=" * 55)

    print("\n[1/7] Loading dataset...")
    df = pd.read_csv('ready_polymer_dataset.csv')
    X  = df.drop(columns=['SMILES', 'Target_Eb'])
    y  = df['Target_Eb']
    print(f"      Dataset: {X.shape[0]} polymers × {X.shape[1]} features")

    print("[2/7] Partitioning Train/Test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=config.RANDOM_SEED
    )

    morgan_cols   = [f"Morgan_Bit_{i}"  for i in range(1024)]
    polybert_cols = [f"PolyBERT_Dim_{i}" for i in range(600)]

    # ─── Build Individual Pipelines ──────────────────────────────────────
    print(f"[3/7] Building MLP pipeline {config.MLP_HIDDEN_LAYER_SIZES} with adaptive LR...")
    mlp_preprocessor = build_preprocessor(morgan_cols, polybert_cols)
    mlp_pipeline      = build_mlp_pipeline(mlp_preprocessor)

    print("[4/7] Building GBR pipeline (300 estimators, depth=5)...")
    gbr_preprocessor = build_preprocessor(morgan_cols, polybert_cols)
    gbr_pipeline      = build_gbr_pipeline(gbr_preprocessor)

    # ─── Train MLP First (stand-alone) ───────────────────────────────────
    print("[5/7] Fitting MLP pipeline on training set...")
    mlp_pipeline.fit(X_train, y_train)
    y_pred_mlp = mlp_pipeline.predict(X_test)
    mlp_metrics = print_metrics("MLP (tuned)", y_test, y_pred_mlp)

    # Serialize backward-compatible model
    joblib.dump(mlp_pipeline, config.MODEL_PATH)
    print(f"      Saved -> {config.MODEL_PATH}")

    # ─── Build + Train Ensemble ───────────────────────────────────────────
    print("[6/7] Fitting Ensemble (VotingRegressor: MLP + GBR)...")
    # Note: VotingRegressor fits each estimator independently on X_train
    # We pass freshly-built pipelines so each gets its own preprocessor fit
    mlp_pipeline2     = build_mlp_pipeline(build_preprocessor(morgan_cols, polybert_cols))
    gbr_pipeline2     = build_gbr_pipeline(build_preprocessor(morgan_cols, polybert_cols))

    ensemble = VotingRegressor(
        estimators=[('mlp', mlp_pipeline2), ('gbr', gbr_pipeline2)],
        weights=list(config.ENSEMBLE_WEIGHTS),
        n_jobs=1,    # sequential to avoid joblib multiprocessing issues
    )
    ensemble.fit(X_train, y_train)
    y_pred_ens = ensemble.predict(X_test)
    ens_metrics = print_metrics("Ensemble (MLP+GBR)", y_test, y_pred_ens)

    joblib.dump(ensemble, config.ENSEMBLE_PATH)
    print(f"      Saved -> {config.ENSEMBLE_PATH}")

    # ─── Plots ────────────────────────────────────────────────────────────
    print("[7/7] Generating evaluation plots...")

    # Scatter: ensemble predictions vs actual
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_pred_ens, alpha=0.75, color='royalblue',
                edgecolors='black', s=50, label='Ensemble Predictions')
    plt.scatter(y_test, y_pred_mlp, alpha=0.4, color='darkorange',
                edgecolors='none', s=35, label='MLP-only Predictions')
    lims = [min(y_test.min(), y_pred_ens.min()) - 10,
            max(y_test.max(), y_pred_ens.max()) + 10]
    plt.plot(lims, lims, 'r--', lw=2.5, label='Perfect Fit')
    plt.xlim(lims); plt.ylim(lims)
    plt.title('Phase A: Ensemble vs Actual Target Eb', fontsize=14, pad=15)
    plt.xlabel('Simulated Target Eb (MV/m)', fontsize=12)
    plt.ylabel('Predicted Eb (MV/m)', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig('eb_predictions.png', dpi=300)

    # Loss curve for tuned MLP
    mlp_model = mlp_pipeline.named_steps['mlp']
    plt.figure(figsize=(8, 6))
    plt.plot(mlp_model.loss_curve_, color='crimson', lw=2, label='Training Loss')
    if hasattr(mlp_model, 'validation_scores_') and mlp_model.validation_scores_:
        # Plot negative validation score as a proxy loss
        val_loss = [-s for s in mlp_model.validation_scores_]
        plt.plot(val_loss, color='steelblue', lw=1.5, linestyle='--', label='Validation Score (neg)')
    plt.title('Phase A: MLPRegressor Training Loss Curve', fontsize=14, pad=15)
    plt.xlabel('Iterations', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig('mlp_loss_curve.png', dpi=300)

    # Error distribution for ensemble
    abs_errors = np.abs(y_test - y_pred_ens)
    plt.figure(figsize=(8, 6))
    plt.hist(abs_errors, bins=25, color='darkorange', edgecolor='black', alpha=0.75)
    plt.title('Phase A: Ensemble Absolute Error Distribution (Test Set)', fontsize=14, pad=15)
    plt.xlabel('Absolute Error Margin (MV/m)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig('error_distribution_hist.png', dpi=300)
    print("      Plots saved: eb_predictions.png, mlp_loss_curve.png, error_distribution_hist.png")

    # ─── Update Report ────────────────────────────────────────────────────
    save_metrics_to_report(mlp_metrics, ens_metrics)

    print("\n" + "=" * 55)
    print("  Phase A COMPLETE")
    print(f"  Ensemble R²:   {ens_metrics[0]:.4f}")
    print(f"  Ensemble MAE:  {ens_metrics[1]:.2f} MV/m")
    print(f"  Ensemble RMSE: {ens_metrics[2]:.2f} MV/m")
    print(f"  Models:        {config.MODEL_PATH} | {config.ENSEMBLE_PATH}")
    print("=" * 55)


if __name__ == "__main__":
    main()
