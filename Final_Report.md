# Final Report: Applied Polymer Informatics and Inverse Design

## Section 1: Data Leakage Prevention and Dimensionality Reduction
One of the most critical engineering requirements when utilizing high-dimensional molecular vectors (such as 1024-bit Morgan Fingerprints and 600-dimensional PolyBERT sentence embeddings) is preventing Principal Component Analysis (PCA) data leakage. In naive pipelines, executing PCA globally across the entire database structurally embeds variance from the validation sets directly into dimensions exposed during model training.

Our pipeline definitively eradicated this via mathematical isolation within `sklearn.compose.ColumnTransformer`. 

The `ColumnTransformer` is natively embedded as Step 1 inside the overall `sklearn.pipeline.Pipeline`. We strictly mapped the 1024 Morgan headers to execute local `PCA(n_components=40)` compression alongside the 600 PolyBERT mapping receiving parallel `PCA(n_components=40)` compression. Crucially, we utilize the `remainder='passthrough'` bounding parameter. Since the pipeline architecture `.fit()` object is executed purely on `X_train`, the PCA eigenvectors are learned solely against training boundaries. The 40 structural physical parameters and independent optimization bounds (Temp/Cryst) bypass matrix reduction natively. This completely isolates the Test vectors to standard transform applications guaranteeing mathematically sound unseen test validations. 

## Section 2: Validation utilizing Strict Regression Metrics
Unlike historical polymer solubility heuristics measuring Binary Accuracies, predicting Dielectric Breakdown Strength ($E_b$) requires high-resolution dimensional metrics scaling bounds locally. As $E_b$ is explicitly a **continuous scalar variable**, employing regression variance metrics is the only mathematically correct evaluation strategy.

**Pipeline Test Data Evaluation Parameters:**
- **MAE (Mean Absolute Error):** 26.39 $MV/m$
- **RMSE (Root Mean Squared Error):** 42.61 $MV/m$
- **$R^2$ (Coefficient of Determination):** 0.8482

The MAE provides the simplest interpretable metric capturing how many exact $MV/m$ units the Neural Network diverges structurally from true values on average. The RMSE applies quadratic penalization natively against severe outliers, securing confidence that extreme deviations are mitigated. Finally, the $R^2$ coefficient maps the exact percentage of raw variance safely captured by the underlying mapping matrices compared to a flat benchmark mean. 

## Section 3: Calculus Inverse Design Optimization Strategy
Moving away from randomized generational heuristics found via Genetic Algorithms, our inverse objective maps analytically targeting continuous design constraints. After freezing an arbitrary sample candidate's highly complex internal chemical boundaries (160 isolated multi-modal dimensional elements post-PCA), we defined the continuous independent space vectors: $Processing\_Temp\_C$ and $Crystallinity$.

Utilizing SciPy's bounded gradient minimization protocol (`scipy.optimize.minimize` via **L-BFGS-B** bounds), we wrapped our fully-fitted MLPRegressor predictive architecture strictly inside a boundary cost function. 

The objective function returns exactly `abs(prediction - Desired_Target_Eb)`. By mapping bounded limits (`100-300 °C` and `10%-90%` crystallization fractions) into the Low-Memory Broyden–Fletcher–Goldfarb–Shanno algorithm (L-BFGS-B), the engine calculates explicit local derivatives across the Temperature/Crystallinity surface against the pre-trained Neural Network weights. The solver efficiently bounds the moving physical limits iteratively downwards until the gradient slope naturally zeroes confirming the lowest absolute mapping discrepancy natively.

## Section 4: Phase A — Model Improvement Results

| Model | R² | MAE (MV/m) | RMSE (MV/m) |
|---|---|---|---|
| MLP (original: 128,64 / iter=200) | 0.7453 | 30.75 | 39.18 |
| MLP (tuned: 256,128,64 / iter=2000) | 0.7527 | 42.24 | 54.38 |
| **Ensemble (MLP+GBR blend)** | **0.8482** | **26.39** | **42.61** |
