# Progesterone - Premature Birth

## 1. Case Metadata

- pair_id: `repodb_04246cb3a1c31ef7`
- drug: Progesterone
- disease: Premature Birth
- repoDB label: `negative_or_failed`
- full pipeline prediction: `positive`
- full confidence score: 0.8
- full status: `completed`
- case type: `verifier_effect`
- manual review status: `TODO_MANUAL_REVIEW`

## 2. Why This Case Was Selected

Shows lower unsupported-claim rate in full mode than no_verifier. The case is included for manual review, not as a definitive biomedical conclusion.

## 3. Evidence Summary

### 3.1 PubMed Evidence

- PMIDs available in PubMed baseline: 70
- PMIDs used by full pipeline: 59
- Abstract availability rate from baseline: 1

Top available PMID/title rows:

- PMID `29157866` (2018): Vaginal progesterone for preventing preterm birth and adverse perinatal outcomes in singleton gestations with a short cervix: a meta-analysis of individual p...
- PMID `37211087` (2023): Combined vaginal progesterone and cervical cerclage in the prevention of preterm birth: a systematic review and meta-analysis.
- PMID `35460628` (2022): Does vaginal progesterone prevent recurrent preterm birth in women with a singleton gestation and a history of spontaneous preterm birth? Evidence from a sys...
- PMID `35168930` (2022): Interventions to prevent spontaneous preterm birth in women with singleton pregnancy who are at high risk: systematic review and network meta-analysis.
- PMID `33039310` (2020): Preterm birth prevention.

The literature signal should be interpreted as co-mention and retrieved-document support. It does not establish efficacy.

### 3.2 Open Targets Evidence

- drug resolved: yes
- disease resolved: yes
- disease targets: 100
- drug targets: 1
- overlapping targets: 1
- support score: 0.4323

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

Conclusion field: `Valid`. Short summary: Progesterone, acting as an agonist of the progesterone receptor (PGR), is a well-established therapeutic for preventing premature birth by inhibiting uterine contractions. Multiple studies demonstrate its efficacy, particularly in high-risk populations, supporting its repurposing for this indication.

### 3.5 Claim Verification

- claims: 2
- verified claims: 2
- unsupported claims: 0
- citation verified rate: 1
- unsupported claim rate: 0

Claim examples:

- `VERIFIED` claim: Progesterone receptor (PGR) activation by progesterone inhibits uterine contractions and cervical ripening, thereby preventing premature birth. PMIDs: 39012912, 37196896, 37211087, 41576138
- `VERIFIED` claim: Genetic variations in the progesterone receptor gene (PGR) may be associated with spontaneous premature birth. PMIDs: 35178856

## 4. Manual Interpretation

The available evidence suggests a research-support assessment only. The retrieved literature and structured evidence may be consistent with the full-agent assessment, but this case does not establish efficacy, safety, or clinical utility. Any apparent alignment or mismatch with the repoDB proxy label requires expert review of the original repoDB row, PubMed abstracts, Open Targets mappings, and graph paths.

## 5. Error Analysis Or Reliability Analysis

This case is useful for `verifier_effect`. It shows how OrphanCure preserves provenance, exposes missing evidence, and separates report faithfulness from repoDB label prediction. If the prediction is incorrect or partial, the case should be used to study failure modes rather than to claim biomedical validity.

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
