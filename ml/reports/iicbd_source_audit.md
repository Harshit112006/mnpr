# BreedVision AI - IICBD Source Audit

## Dataset

Annotated Multiview Image Dataset of Prominent Indigenous Indian Cattle Breeds

DOI: 10.17632/xc3j9v382w.1

## Published Metadata

The published dataset description reports:

- 9,598 RGB images
- 9 indigenous Indian cattle breeds

Reported breeds:

1. Bargur
2. Gir
3. Hallikar
4. Kankrej
5. Ongole
6. Pulikulam
7. Rathi
8. Sahiwal
9. Tharparkar

## Local Download Audit

The downloaded archive was inspected recursively.

Total image files found:

7,226

Recognized images:

7,226

Unrecognized images:

0

### Locally Available Breeds

| Breed | Image Count |
|---|---:|
| Bargur | 470 |
| Gir | 3648 |
| Hallikar | 1951 |
| Ongole | 343 |
| Tharparkar | 814 |
| **Total** | **7,226** |

## Missing Reported Breeds

The following breeds were listed in the published description but were not present in the downloaded archive:

- Kankrej
- Pulikulam
- Rathi
- Sahiwal

A direct archive-content search was also performed for these breed names.

No matching entries were found.

Therefore, the discrepancy is not caused by incomplete extraction.

## BreedVision Decision

BreedVision will preserve the downloaded IICBD archive unchanged.

The five available breed classes may be used as verified source data.

The four missing classes will not be manually fabricated, renamed, or reconstructed.

Additional cattle and buffalo classes will only be added from separately documented and audited sources.

## Data Integrity Rule

The raw IICBD directory must remain unchanged.

All cleaning, deduplication, normalization and dataset merging will be performed outside the raw dataset directory.