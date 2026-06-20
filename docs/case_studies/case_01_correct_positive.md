# Theophylline - Asthma

## 1. Case Metadata

- pair_id: `repodb_0557bc43eff59f45`
- drug: Theophylline
- disease: Asthma
- repoDB label: `positive`
- full pipeline prediction: `positive`
- full confidence score: 0.55
- full status: `completed`
- case type: `correct_positive`
- manual review status: `TODO_MANUAL_REVIEW`

## 2. Why This Case Was Selected

Meets selection criteria for correct_positive. The case is included for manual review, not as a definitive biomedical conclusion.

## 3. Evidence Summary

### 3.1 PubMed Evidence

- PMIDs available in PubMed baseline: 67
- PMIDs used by full pipeline: 54
- Abstract availability rate from baseline: 0.875

Top available PMID/title rows:

- PMID `14988770` (2004): Theophylline: mechanism of action and use in asthma and chronic obstructive pulmonary disease.
- PMID `8471184` (1993): Theophylline. Current thoughts on the risks and benefits of its use in asthma.
- PMID `7589387` (1995): Theophylline and selective phosphodiesterase inhibitors as anti-inflammatory drugs in the treatment of bronchial asthma.
- PMID `8614425` (1996): Theophylline in asthma.
- PMID `9756185` (1998): Asthma, adenosine, mast cells and theophylline.

The literature signal should be interpreted as co-mention and retrieved-document support. It does not establish efficacy.

### 3.2 Open Targets Evidence

- drug resolved: yes
- disease resolved: yes
- disease targets: 100
- drug targets: 10
- overlapping targets: 10
- support score: 0.5343

Open Targets support is target-evidence context, not clinical truth.

### 3.3 PrimeKG Graph Evidence

- drug mapped: yes
- disease mapped: no
- graph path exists: no
- shortest path length: 0
- graph connectivity score: 0

Graph paths:

- No graph path rows available for this pair.

PrimeKG connectivity is mechanism support only and does not prove efficacy.

### 3.4 Full-Agent Generated Report

Conclusion field: `Potential`. Short summary: Theophylline is a potential candidate for asthma repurposing due to its established mechanisms involving PDE4 inhibition and adenosine receptor antagonism, which are relevant to asthma pathology. While literature supports its use, concerns regarding selectivity and side effects, particularly with non-selective PDE4 inhibition, warrant further investigation.

### 3.5 Claim Verification

- claims: 5
- verified claims: 5
- unsupported claims: 0
- citation verified rate: 1
- unsupported claim rate: 0

Claim examples:

- `VERIFIED` claim: Theophylline's inhibition of phosphodiesterase 4 (PDE4) isoforms, such as PDE4D, PDE4A, and PDE4B, can lead to increased intracellular cAMP levels, promoting bronchodilation and reducing airway inflammation, which are beneficial in asthma. PMIDs: 33234690, 40654275, 42166818
- `VERIFIED` claim: Theophylline's antagonism of adenosine receptors (e.g., ADORA1, ADORA2A, ADORA2B, ADORA3) may modulate inflammatory responses and immune cell activation, potentially impacting asthma exacerbations. PMIDs: 41089433
- `VERIFIED` claim: Genetic variants in PDE4D are associated with asthma susceptibility. PMIDs: 37549468
- `VERIFIED` claim: Theophylline has been directly compared to doxofylline for efficacy and safety in stable asthmatic patients. PMIDs: 26023566
- `VERIFIED` claim: Non-selective PDE4D inhibition by theophylline can lead to unfavorable side effects, contrasting with the desired therapeutic results from selective PDE4B inhibition. PMIDs: 40654275, 42166818

## 4. Manual Interpretation

The available evidence suggests a research-support assessment only. The retrieved literature and structured evidence may be consistent with the full-agent assessment, but this case does not establish efficacy, safety, or clinical utility. Any apparent alignment or mismatch with the repoDB proxy label requires expert review of the original repoDB row, PubMed abstracts, Open Targets mappings, and graph paths.

## 5. Error Analysis Or Reliability Analysis

This case is useful for `correct_positive`. It shows how OrphanCure preserves provenance, exposes missing evidence, and separates report faithfulness from repoDB label prediction. If the prediction is incorrect or partial, the case should be used to study failure modes rather than to claim biomedical validity.

## 6. Interview Talking Points

- 30-second explanation: This case shows how OrphanCure turns a drug-disease pair into a traceable evidence report with PubMed, Open Targets, graph, and verifier outputs.
- 2-minute explanation: Discuss the repoDB proxy label, what evidence layers were available, whether the generated claims were verified, and why this does or does not align with the label.
- Technical takeaway: The case keeps `pair_id`, evidence availability, claims, and verification status tied together.
- Limitation: Evidence grounding is not the same as clinical validation.

## 7. Safety Note

This case study is for research and educational purposes only. It is not medical advice and must not be used for clinical decision-making.

## 8. Manual Review Checklist

- [ ] repoDB row checked
- [ ] PubMed PMIDs checked
- [ ] Abstracts checked
- [ ] Open Targets mappings checked
- [ ] PrimeKG paths checked
- [ ] Generated claims checked
- [ ] Citations checked
- [ ] Biomedical expert review completed
