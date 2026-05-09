# Polymer Informatics Pipeline: Dielectric Breakdown Strength ($E_b$) Optimization

## System Architecture Overview
This repository contains a robust, end-to-end 9-file micro-service architecture built for the generation, sequence-embedding, machine learning regression, and analytic inverse-design optimization of High-Performance Dielectric Polymer architectures. 

The pipeline specifically orchestrates:
1. **Combinatorial Generation Pipelines** (`code_1`)
2. **Dense Array Graph Descriptor Extractions** (`code_2`, `code_4`)
3. **Advanced Transformer Embeddings & Molecular Fingerprinting** (`code_3`, `code_5`)
4. **Data Aggregation and Merging** (`code_6`)
5. **Zero-Leakage ML Model Construction** (`code_7`)
6. **Analytic Calculus Optimization** (`code_8`)

## Chemistry Combinatorics
The architecture synthesizes exactly **720 unique computational polymer linkages** across three major industrial families:
- **PP (Polypropylene Derivatives):** 240 combinations derived from the structural bounding of varying aliphatic and aromatic olefin permutations.
- **PET (Polyethylene Terephthalate Derivatives):** 240 combinations formulated via precise ester linkages between varying terephthalic acids and modified structural diols.
- **PVDF (Polyvinylidene Fluoride Derivatives):** 240 heavily fluorinated arrays utilizing VDF monomer combinatorics against complex co-polymers sequences.

## The Feature Space
To accurately capture the molecular topologies required to build complex Deep Learning interactions for $E_b$, the system leverages an expansive multi-modal feature vector natively mapping:
1. **40 RDKit Structural Features:** Explicit Fragment bounds isolating aromatics, heterocycles, stereocenters, and functional groups.
2. **40 RDKit Physical Parameters:** Exact mathematical topological markers capturing `BalabanJ`, `VSA` descriptors, `Kappa` geometry, and exact molecular weights constraint bounds.
3. **1024-Bit Morgan Fingerprints:** Circular radii hashing maps capturing the dense atomic neighborhoods across $Radius=2$.
4. **600-Dimensional PolyBERT:** Direct string interpolation sequence embeddings extracted exactly off the localized `[CLS]` prediction token attention mappings without dimensional binning. 
