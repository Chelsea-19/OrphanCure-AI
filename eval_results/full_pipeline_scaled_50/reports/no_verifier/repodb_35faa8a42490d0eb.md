# OrphanCure Full Pipeline Report: repodb_35faa8a42490d0eb

- Drug: Neomycin
- Disease: Hepatic Coma
- Mode: no_verifier
- Status: completed
- Final assessment: Unlikely

This generated report is for research support only and is not medical advice.

## Structured Output

```json
{
  "sections": {
    "1_executive_summary": {
      "conclusion": "Unlikely",
      "confidence": "Low",
      "summary": "There is no available literature to support or refute the repurposing of neomycin for viral human hepatitis. The provided data does not contain any information regarding neomycin's mechanism of action against hepatitis viruses or any clinical evidence of its efficacy.",
      "evidence_counts": {
        "total_papers": 0,
        "supporting": 0,
        "contradicting": 0,
        "inconclusive": 0
      },
      "common_targets_count": 0
    },
    "2_normalized_hypothesis": {
      "statement": "Repurpose NEOMYCIN for viral human hepatitis infection",
      "drug": {
        "id": "CHEMBL3989751",
        "name": "NEOMYCIN",
        "aliases": [
          "Neomycin sulfate",
          "Neomycin B",
          "Framycetin",
          "Mycifradine",
          "Neomycin palmitate"
        ],
        "resolution_method": "auto"
      },
      "disease": {
        "id": "EFO_0004196",
        "name": "viral human hepatitis infection",
        "aliases": [
          "viral hepatitis",
          "hepatitis, viral",
          "viral liver disease",
          "viral liver infection",
          "viral hepatitis disease"
        ],
        "resolution_method": "auto"
      }
    },
    "3_mechanistic_rationale": {
      "total_mechanisms": 0,
      "mechanisms": []
    },
    "4_target_overlap_summary": {
      "total_overlapping": 0,
      "top_targets": []
    },
    "5_literature_evidence_summary": {
      "total_retrieved": 0,
      "polarity": {
        "supports": 0,
        "contradicts": 0,
        "inconclusive": 0
      },
      "support_ratio": "No papers retrieved",
      "queries_used": 10,
      "top_papers": []
    },
    "6_contradictory_evidence": {
      "count": 0,
      "claims": []
    },
    "7_confidence_assessment": {
      "overall": "Low",
      "dimensions": {
        "mechanistic_strength": "Low",
        "literature_strength": "Low",
        "clinical_evidence": "Low"
      },
      "quality_scorecard": {
        "overall_score": 0.388,
        "decision": "rerun",
        "dimensions": {
          "completeness": {
            "score": 0.8,
            "reason": "4/5 sections present"
          },
          "evidence_support": {
            "score": 0.0,
            "reason": "No claims generated"
          },
          "citation_validity": {
            "score": 0.0,
            "reason": "0 total citations"
          },
          "mechanistic_specificity": {
            "score": 0.0,
            "reason": "0/0 claims reference targets"
          },
          "contradiction_handling": {
            "score": 0.3,
            "reason": "No contradiction analysis"
          },
          "traceability": {
            "score": 0.0,
            "reason": "0/0 claims have provenance"
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
          "evidence_support",
          "citation_validity",
          "mechanistic_specificity",
          "contradiction_handling",
          "traceability"
        ],
        "rerun_targets": [
          "LiteratureAgent",
          "MechanismAgent",
          "SynthesisCriticAgent"
        ]
      }
    },
    "8_risk_flags_limitations": {
      "risk_flags": [
        "Neomycin is an aminoglycoside antibiotic with known nephrotoxicity and ototoxicity, which could pose significant risks in a chronic condition like hepatitis."
      ],
      "limitations": [
        "The absence of any retrieved literature severely limits the ability to assess the hypothesis.",
        "No mechanistic data was provided to infer potential antiviral activity."
      ],
      "missing_data": [
        "Information on neomycin's antiviral activity against hepatitis viruses.",
        "Studies on the mechanism of action of neomycin in the context of viral hepatitis.",
        "Clinical trial data on the efficacy and safety of neomycin for treating viral hepatitis."
      ]
    },
    "9_recommended_next_steps": {
      "clinical_next_steps": [
        "Conduct a thorough literature search for any studies investigating neomycin's antiviral properties, particularly against hepatitis viruses.",
        "Investigate the known mechanisms of action of neomycin to determine if any targets are relevant to hepatitis virus replication or pathogenesis.",
        "If preliminary mechanistic data is found, consider in vitro studies to assess neomycin's efficacy against hepatitis viruses."
      ]
    },
    "10_claim_evidence_table": {
      "total_claims": 0,
      "claims": []
    },
    "11_provenance_appendix": {
      "total_entries": 0,
      "entries": []
    }
  },
  "metadata": {
    "run_id": "007b33afc2ed",
    "created_at": "2026-06-03T14:33:38.453447+00:00",
    "drug": "NEOMYCIN",
    "disease": "viral human hepatitis infection",
    "total_claims": 0,
    "quality_score": 0.3875,
    "reruns": 0
  }
}
```
