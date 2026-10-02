# BreedVision AI - Phase 4 Completion Report

**Status:** PASS

**Classifier Version:** v1

**Final Classes:** 6

**Training-ready Images:** 6183

## Dataset Split

- Train: 2603
- Validation: 1791
- Test: 1789

## Leakage Validation

- Status: PASS
- Group leakage: 0
- Exact hash leakage: 0
- Near-duplicate pair leakage: 0

## Phase 4 Dataset Policy

- Raw datasets remain unchanged.
- Corrupt and invalid images are excluded.
- Exact duplicates are removed.
- Cross-class exact conflicts are excluded.
- Near-duplicate groups remain within one split.
- Train, validation and test leakage has been checked.
- Synthetic data is not used as primary evaluation data.


## Warnings

- Train ratio deviates substantially from the 70% target.
- Validation ratio deviates substantially from the 15% target.
- Test ratio deviates substantially from the 15% target.