"""
Code 11: Genetic Algorithm for De Novo Polymer Generation.
Generates novel SMILES strings to hit a target Dielectric Breakdown Strength (Eb).
"""

import os
import sys
import random
import numpy as np
import pandas as pd
import joblib
from rdkit import Chem
from rdkit.Chem import AllChem

import config
from code_10_conditional_search import get_candidate_features

# -----------------------------------------------------------------------------
# 1. Mutation & Crossover Definitions
# -----------------------------------------------------------------------------

# Define a set of structural mutations using SMARTS reactions
MUTATION_RXNS = [
    # Halogen Swaps
    AllChem.ReactionFromSmarts('[#6:1]-[F:2] >> [#6:1]-[Cl:2]'),
    AllChem.ReactionFromSmarts('[#6:1]-[Cl:2] >> [#6:1]-[F:2]'),
    
    # Branching / Functional Group Addition (Aliphatic)
    AllChem.ReactionFromSmarts('[CH2:1] >> [CH:1](F)'),
    AllChem.ReactionFromSmarts('[CH2:1] >> [CH:1](C)'),
    AllChem.ReactionFromSmarts('[CH2:1] >> [CH:1](C(F)(F)F)'), # Trifluoromethyl
    AllChem.ReactionFromSmarts('[CH2:1] >> [CH:1](O)'),        # Ether/Hydroxyl start
    
    # Branching / Functional Group Addition (Aromatic)
    AllChem.ReactionFromSmarts('[cH1:1] >> [c:1](F)'),
    AllChem.ReactionFromSmarts('[cH1:1] >> [c:1](C)'),
    
    # Ether linkage insertion
    AllChem.ReactionFromSmarts('[CH2:1]-[CH2:2] >> [CH2:1]-O-[CH2:2]'),
    
    # Saturation / Desaturation
    AllChem.ReactionFromSmarts('[CH2:1]-[CH2:2] >> [CH:1]=[CH:2]'),
    AllChem.ReactionFromSmarts('[CH:1]=[CH:2] >> [CH2:1]-[CH2:2]'),
]

# Simple crossover reaction: cross-breeding two polymer chains by breaking and recombining single bonds
# Matches single bonds between carbons
CROSSOVER_RXN = AllChem.ReactionFromSmarts('[#6:1]-[#6:2].[#6:3]-[#6:4] >> [#6:1]-[#6:4].[#6:3]-[#6:2]')


def mutate(smiles: str) -> str:
    """
    Applies a random structural mutation to the SMILES string.
    Strictly validates the resulting molecule using RDKit.
    """
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return None
        
    # Shuffle reactions to pick a random one that applies
    rxns = MUTATION_RXNS.copy()
    random.shuffle(rxns)
    
    for rxn in rxns:
        products = rxn.RunReactants((mol,))
        if products:
            # Pick a random product configuration if multiple reaction sites exist
            prod_mol = random.choice(products)[0]
            try:
                # Strictly validate chemical viability
                Chem.SanitizeMol(prod_mol)
                return Chem.MolToSmiles(prod_mol)
            except Exception:
                continue
    return None


def crossover(smiles1: str, smiles2: str) -> str:
    """
    Cross-breeds two polymer SMILES to create a novel hybrid.
    Strictly validates the result.
    """
    mol1 = Chem.MolFromSmiles(smiles1)
    mol2 = Chem.MolFromSmiles(smiles2)
    if not mol1 or not mol2:
        return None
        
    products = CROSSOVER_RXN.RunReactants((mol1, mol2))
    if products:
        # Each product tuple contains 2 resulting molecules; we randomly pick one molecule from a random tuple
        prod_tuple = random.choice(products)
        prod_mol = random.choice(prod_tuple)
        try:
            Chem.SanitizeMol(prod_mol)
            return Chem.MolToSmiles(prod_mol)
        except Exception:
            return None
    return None

# -----------------------------------------------------------------------------
# 2. Fitness Function
# -----------------------------------------------------------------------------

def evaluate_fitness(smiles: str, target_eb: float, pipeline, feature_order: list, baseline_temp: float = 200.0, baseline_cryst: float = 0.5) -> tuple[float, float]:
    """
    Calculates fitness of a SMILES string.
    Fitness = negative absolute error from Target Eb (higher is better, max 0).
    Returns (fitness, predicted_eb).
    """
    try:
        # 1. Automatically extract Morgan Fingerprint and Physical RDKit features
        features = get_candidate_features(smiles)
        
        # 2. Assign baseline processing parameters
        features['ProcessingTemp_C'] = baseline_temp
        features['Crystallinity'] = baseline_cryst
        
        # 3. Format as DataFrame to exactly match the pipeline's expected feature order
        df_candidate = pd.DataFrame([features])[feature_order]
        
        # 4. Predict Eb
        predicted_eb = float(pipeline.predict(df_candidate)[0])
        
        # Fitness is the inverse of the error
        error = abs(predicted_eb - target_eb)
        fitness = -error
        return fitness, predicted_eb
    except Exception:
        # If feature extraction fails or RDKit rejects it during descriptor calculation
        return -9999.0, None

# -----------------------------------------------------------------------------
# 3. Genetic Algorithm Core (Evolution)
# -----------------------------------------------------------------------------

def run_genetic_algorithm(target_eb: float, generations: int = 10, pop_size: int = 50):
    print("=" * 60)
    print(f"  De Novo Generative Design (GA) - Target Eb: {target_eb} MV/m")
    print("=" * 60)
    
    # Load Model Pipeline
    print("Loading predictive pipeline...")
    try:
        pipeline = joblib.load(config.ENSEMBLE_PATH)
        print(f"Loaded ensemble model from {config.ENSEMBLE_PATH}")
    except FileNotFoundError:
        pipeline = joblib.load(config.MODEL_PATH)
        print(f"Loaded MLP model from {config.MODEL_PATH}")
        
    # Load Initial Population
    print("Loading base population...")
    df = pd.read_csv(config.DATASET_PATH)
    
    # Extract the exact feature order expected by the model
    # Drop SMILES and Target_Eb to get the pure feature columns
    frozen_row = df.iloc[0].drop(['SMILES', 'Target_Eb'])
    feature_order = frozen_row.index.tolist()
    
    # Initialize Population randomly from the dataset
    population = df['SMILES'].sample(n=min(pop_size, len(df)), random_state=42).tolist()
    
    best_overall_smiles = None
    best_overall_fitness = -float('inf')
    best_overall_eb = None
    
    for gen in range(1, generations + 1):
        print(f"\n--- Generation {gen} ---")
        
        # Evaluate Population
        pop_fitness = []
        for smi in population:
            fit, pred_eb = evaluate_fitness(smi, target_eb, pipeline, feature_order)
            if pred_eb is not None:
                pop_fitness.append((smi, fit, pred_eb))
                
        # Sort by fitness (descending, so closest to 0 is first)
        pop_fitness.sort(key=lambda x: x[1], reverse=True)
        
        # Update Best Overall
        if pop_fitness and pop_fitness[0][1] > best_overall_fitness:
            best_overall_smiles = pop_fitness[0][0]
            best_overall_fitness = pop_fitness[0][1]
            best_overall_eb = pop_fitness[0][2]
            
        if not pop_fitness:
            print("Population collapsed (all invalid). Stopping.")
            break
            
        print(f"Best this Gen: Eb = {pop_fitness[0][2]:.2f} MV/m (Error: {abs(pop_fitness[0][1]):.2f} MV/m)")
        print(f"SMILES: {pop_fitness[0][0]}")
        
        # Check early stopping condition (e.g., error < 2 MV/m)
        if abs(best_overall_fitness) < 2.0:
            print("\nTarget Eb achieved within tight 2 MV/m tolerance. Stopping early!")
            break
            
        # Elitism: keep top 20%
        elite_count = max(1, int(pop_size * 0.2))
        elites = [x[0] for x in pop_fitness[:elite_count]]
        
        # Generate new population
        new_population = elites.copy()
        
        attempts = 0
        while len(new_population) < pop_size and attempts < pop_size * 10:
            attempts += 1
            # Randomly choose between Crossover and Mutation
            if random.random() < 0.3 and len(elites) >= 2:
                # Crossover
                parent1, parent2 = random.sample(elites, 2)
                child = crossover(parent1, parent2)
            else:
                # Mutation
                parent = random.choice(elites)
                child = mutate(parent)
                
            # If child is valid and unique, add to the next generation
            if child and child not in new_population:
                new_population.append(child)
                
        population = new_population

    print("\n" + "=" * 60)
    print("  GA Optimization Complete!")
    print("=" * 60)
    print(f"Target Eb:       {target_eb} MV/m")
    print(f"Best SMILES:     {best_overall_smiles}")
    print(f"Predicted Eb:    {best_overall_eb:.2f} MV/m" if best_overall_eb else "Predicted Eb:    None")
    print(f"Absolute Error:  {abs(best_overall_fitness):.2f} MV/m" if best_overall_fitness != -float('inf') else "Absolute Error:  None")
    print("=" * 60)
    
    return {
        "target_eb": target_eb,
        "best_smiles": best_overall_smiles,
        "predicted_eb": best_overall_eb,
        "absolute_error": abs(best_overall_fitness) if best_overall_fitness != -float('inf') else None,
        "generations_run": gen
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="De Novo Polymer Generation via Genetic Algorithm")
    parser.add_argument("--target", type=float, default=650.0, help="Target Dielectric Breakdown Strength (MV/m)")
    parser.add_argument("--gen", type=int, default=10, help="Number of generations")
    parser.add_argument("--pop", type=int, default=30, help="Population size")
    args = parser.parse_args()
    
    run_genetic_algorithm(target_eb=args.target, generations=args.gen, pop_size=args.pop)
