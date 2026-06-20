# OrphanCure Full Pipeline Report: repodb_3ac2b491643eebc5

- Drug: Ulobetasol
- Disease: Scalp psoriasis
- Mode: full
- Status: completed
- Final assessment: Valid

This generated report is for research support only and is not medical advice.

## Structured Output

```json
{
  "sections": {
    "1_executive_summary": {
      "conclusion": "Valid",
      "confidence": "High",
      "summary": "Halobetasol propionate, a potent corticosteroid, is a validated topical treatment for plaque psoriasis. Its mechanism involves binding to the glucocorticoid receptor (NR3C1) to suppress inflammatory gene expression, directly addressing the hyperproliferation and inflammation characteristic of the disease. Clinical trials demonstrate its efficacy, often in combination with tazarotene, supporting its repurposing for psoriasis.",
      "evidence_counts": {
        "total_papers": 38,
        "supporting": 17,
        "contradicting": 14,
        "inconclusive": 7
      },
      "common_targets_count": 1
    },
    "2_normalized_hypothesis": {
      "statement": "Repurpose HALOBETASOL PROPIONATE for psoriasis",
      "drug": {
        "id": "CHEMBL1200908",
        "name": "HALOBETASOL PROPIONATE",
        "aliases": [
          "Halobetasol 17-propionate",
          "Ultravate",
          "Halobetasol",
          "Diprolene AF",
          "Psorcon"
        ],
        "resolution_method": "auto"
      },
      "disease": {
        "id": "EFO_0000676",
        "name": "psoriasis",
        "aliases": [
          "psoriatic disease",
          "Psoriasis vulgaris",
          "psoriasis vulgaris",
          "psoriatic disorder",
          "psoriatic condition"
        ],
        "resolution_method": "auto"
      }
    },
    "3_mechanistic_rationale": {
      "total_mechanisms": 1,
      "mechanisms": [
        {
          "target": "NR3C1",
          "drug_action": "AGONIST",
          "disease_score": 0.609,
          "pathway": "Halobetasol propionate, a potent corticosteroid, binds to the glucocorticoid receptor (NR3C1) to suppress inflammatory gene expression, thereby reducing the hyperproliferation and inflammation characteristic of psoriasis."
        }
      ]
    },
    "4_target_overlap_summary": {
      "total_overlapping": 1,
      "top_targets": [
        {
          "symbol": "NR3C1",
          "name": "nuclear receptor subfamily 3 group C member 1",
          "drug_action": "AGONIST",
          "disease_association_score": 0.609
        }
      ]
    },
    "5_literature_evidence_summary": {
      "total_retrieved": 38,
      "polarity": {
        "supports": 17,
        "contradicts": 14,
        "inconclusive": 7
      },
      "support_ratio": "17 of 38 retrieved papers support the hypothesis",
      "queries_used": 11,
      "top_papers": [
        {
          "pmid": "38306148",
          "title": "Halobetasol Propionate 0.01% and Tazarotene 0.045% Lotion With a Ceramide-Containing Moisturizer in Adults With Psoriasis.",
          "year": "2024",
          "relevance_score": 12.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study",
            "Recent",
            "Title Match"
          ]
        },
        {
          "pmid": "36877884",
          "title": "Breaking the Frustrating Cycle of Topical Steroids in Psoriasis: A Review of a Novel Vehicle for Fixed-Dose Combination Halobetasol Propionate/Tazarotene.",
          "year": "2023",
          "relevance_score": 12.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study",
            "Recent",
            "Title Match"
          ]
        },
        {
          "pmid": "35533304",
          "title": "Halobetasol Propionate 0.01% Lotion for Plaque Psoriasis and Corticosteroid-Responsive Dermatoses.",
          "year": "2022",
          "relevance_score": 11.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study",
            "Recent",
            "Title Match"
          ]
        },
        {
          "pmid": "34871475",
          "title": "Fixed Combination Halobetasol Propionate and Tazarotene Lotion for Plaque Psoriasis.",
          "year": "2021",
          "relevance_score": 11.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study",
            "Title Match"
          ]
        },
        {
          "pmid": "34232005",
          "title": "Fixed-Combination Halobetasol Propionate and Tazarotene Lotion for Psoriasis in Patients With Skin of Color.",
          "year": "2021",
          "relevance_score": 11.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study",
            "Title Match"
          ]
        },
        {
          "pmid": "32845589",
          "title": "Halobetasol Propionate Lotion 0.01% for Moderate-to-Severe Plaque Psoriasis: Pooled Analysis in Male and Female Participants.",
          "year": "2020",
          "relevance_score": 11.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study",
            "Title Match"
          ]
        },
        {
          "pmid": "34397206",
          "title": "Fixed-Combination Halobetasol Propionate/Tazarotene Lotion for Psoriasis in Patients With 3%-5% Affected Body Surface Area.",
          "year": "2021",
          "relevance_score": 11.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study",
            "Title Match"
          ]
        },
        {
          "pmid": "32272516",
          "title": "Halobetasol Propionate 0.01%/Tazarotene 0.045% Lotion for Moderate-to-Severe Psoriasis: Pooled Phase 3 Analysis of Lower Extremities.",
          "year": "2020",
          "relevance_score": 11.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study",
            "Title Match"
          ]
        },
        {
          "pmid": "33683083",
          "title": "Once-Daily Halobetasol Propionate 0.01% Lotion for Moderate-to-Severe Plaque Psoriasis: Phase 3 Analysis of Hispanic Participants.",
          "year": "2021",
          "relevance_score": 11.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study",
            "Title Match"
          ]
        },
        {
          "pmid": "34106439",
          "title": "Fixed-Combination Halobetasol Propionate and Tazarotene in the Treatment of Psoriasis: Narrative Review of Mechanisms of Action and Therapeutic Benefits.",
          "year": "2021",
          "relevance_score": 10.5,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Clinical study",
            "Title Match"
          ]
        }
      ]
    },
    "6_contradictory_evidence": {
      "count": 0,
      "claims": []
    },
    "7_confidence_assessment": {
      "overall": "High",
      "dimensions": {
        "mechanistic_strength": "High",
        "literature_strength": "High",
        "clinical_evidence": "High"
      },
      "quality_scorecard": {
        "overall_score": 0.912,
        "decision": "finalize",
        "dimensions": {
          "completeness": {
            "score": 1.0,
            "reason": "5/5 sections present"
          },
          "evidence_support": {
            "score": 1.0,
            "reason": "1/1 claims have paper evidence"
          },
          "citation_validity": {
            "score": 1.0,
            "reason": "1 verified, 0 partial out of 1"
          },
          "mechanistic_specificity": {
            "score": 1.0,
            "reason": "1/1 claims reference targets"
          },
          "contradiction_handling": {
            "score": 0.3,
            "reason": "No contradiction analysis"
          },
          "traceability": {
            "score": 1.0,
            "reason": "1/1 claims have provenance"
          },
          "output_structure": {
            "score": 1.0,
            "reason": "Executive summary + confidence assessment"
          },
          "actionability": {
            "score": 1.0,
            "reason": "3 next steps, 3 data gaps identified"
          }
        },
        "weak_dimensions": [
          "contradiction_handling"
        ],
        "rerun_targets": []
      }
    },
    "8_risk_flags_limitations": {
      "risk_flags": [
        "Adherence challenges due to potential for local irritation or cosmetic concerns.",
        "Potential for corticosteroid-induced side effects (e.g., skin atrophy, telangiectasias) with prolonged use.",
        "Risk of tachyphylaxis or reduced efficacy over time."
      ],
      "limitations": [
        "The provided abstracts primarily focus on the use of halobetasol propionate in combination with tazarotene, limiting direct assessment of halobetasol propionate monotherapy efficacy.",
        "The mechanistic data is inferred from the general properties of potent corticosteroids rather than specific experimental results for halobetasol propionate in psoriasis.",
        "The evidence summary indicates a significant number of contradicting and inconclusive papers, which are not detailed in the provided abstracts."
      ],
      "missing_data": [
        "Detailed information on the specific inflammatory gene expression suppressed by halobetasol propionate in psoriasis.",
        "Comparative studies of halobetasol propionate monotherapy versus combination therapy for psoriasis.",
        "Data on the efficacy of halobetasol propionate in different stages or severities of psoriasis beyond plaque psoriasis."
      ]
    },
    "9_recommended_next_steps": {
      "clinical_next_steps": [
        "Evaluate long-term efficacy and safety of halobetasol propionate for psoriasis.",
        "Investigate optimal dosing and application strategies for halobetasol propionate in various psoriasis phenotypes.",
        "Explore combination therapies with halobetasol propionate for enhanced treatment outcomes."
      ]
    },
    "10_claim_evidence_table": {
      "total_claims": 1,
      "claims": [
        {
          "claim_id": "CLM-0a0c23",
          "statement": "Halobetasol propionate acts as an agonist for the glucocorticoid receptor (NR3C1), suppressing inflammatory gene expression.",
          "confidence_numeric": 0.9,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "VERIFIED",
          "targets": [
            "NR3C1"
          ],
          "citation_count": 8,
          "risk_flags": []
        }
      ]
    },
    "11_provenance_appendix": {
      "total_entries": 1,
      "entries": [
        {
          "claim_id": "CLM-0a0c23",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "84a57800aa5e",
          "timestamp": "2026-06-03T14:20:45.438182+00:00",
          "paper_evidence": [
            {
              "pmid": "38306148",
              "snippet": "Fixed-combination halobetasol propionate 0.01% and tazarotene 0.045% lotion (HP/TAZ) is indicated for the topical treatment of plaque psoriasis in adults, with a demonstrated clinical profile in two p",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            },
            {
              "pmid": "36877884",
              "snippet": "Topical steroids and tazarotene are both options for topical psoriasis treatment, but as monotherapies, they are associated with adverse events (AEs) that make adherence to prescribed treatment challe",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            },
            {
              "pmid": "35533304",
              "snippet": "A novel topical corticosteroid, halobetasol propionate (HP) 0.01% lotion (Bryhali\u2122), has recently been introduced for the treatment of plaque psoriasis and corticosteroid-responsive dermatoses in adul",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            },
            {
              "pmid": "34871475",
              "snippet": "A novel fixed combination lotion containing the super-potent corticosteroid halobetasol propionate 0.01% and retinoid tazarotene 0.045% (Duobrii\u2122) has recently been introduced and indicated for the tr",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            },
            {
              "pmid": "34232005",
              "snippet": "Fixed-combination halobetasol propionate (0.01%) and tazarotene (0.045%) lotion (HP/TAZ) was investigated in two phase 3, multicenter, double-blind, vehicle-controlled trials (NCT02462070; NCT02462122",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            },
            {
              "pmid": "32845589",
              "snippet": "Two double-blind, vehicle-controlled, phase 3 studies evaluated halobetasol propionate (HP) 0.01% lotion for the treatment of moderate-to-severe localized plaque psoriasis; pooled post hoc analyses in",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            },
            {
              "pmid": "34397206",
              "snippet": "Fixed-combination halobetasol propionate (0.01%) and tazarotene (0.045%) lotion (HP/TAZ) vs vehicle lotion was evaluated in participants with 3% to 5% BSA involvement.",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            },
            {
              "pmid": "32272516",
              "snippet": "A fixed combination halobetasol propionate 0.01%/tazarotene 0.045% (HP/TAZ) lotion demonstrated efficacy and safety in patients with moderate-to-severe localized plaque psoriasis.",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            }
          ],
          "mechanism_evidence": [
            {
              "target": "NR3C1",
              "action": "AGONIST"
            }
          ],
          "queries_used_count": 11
        }
      ]
    }
  },
  "metadata": {
    "run_id": "84a57800aa5e",
    "created_at": "2026-06-03T14:20:22.426150+00:00",
    "drug": "HALOBETASOL PROPIONATE",
    "disease": "psoriasis",
    "total_claims": 1,
    "quality_score": 0.9125,
    "reruns": 0
  }
}
```
