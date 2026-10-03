# BreedVision AI - Machine Learning Workspace

This directory contains the machine-learning dataset preparation,
training, evaluation and inference pipeline for BreedVision AI.

## Current Phase

Phase 5 - Breed Classifier Training & Benchmarking - Complete

Breed Classifier v1 has been trained, benchmarked, selected using validation Macro F1, and evaluated on the held-out test set.

## Directory Structure

- `data/raw/` - Original downloaded datasets. Never modify.
- `data/interim/` - Intermediate cleaned data.
- `data/processed/` - Final validated dataset.
- `data/splits/` - Train, validation and test splits.
- `scripts/` - Dataset preparation and validation scripts.
- `reports/` - Dataset statistics and audit reports.
- `notebooks/` - Exploratory analysis.
- `configs/` - Dataset and class configuration.
- `weights/` - Future trained model files.

## Dataset Rules

1. Real labelled photographs are the primary data source.
2. Raw datasets must remain unchanged.
3. Synthetic images must not be mixed into validation or test sets.
4. Duplicate and near-duplicate images must be checked before splitting.
5. Training, validation and test leakage must be prevented.
6. Breed labels must be normalized before training.
7. Dataset provenance and licences must be documented.
8. Validation and test images must not receive training augmentation.

## Current Model Status

- Bovine detector: Not trained yet.
- Breed classifier: v1 trained and validated. See configs/breed_classifier_v1.json.
- Production inference model: Not available yet.