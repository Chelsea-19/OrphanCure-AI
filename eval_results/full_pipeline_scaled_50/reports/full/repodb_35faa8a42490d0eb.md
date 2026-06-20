# OrphanCure Full Pipeline Report: repodb_35faa8a42490d0eb

- Drug: Neomycin
- Disease: Hepatic Coma
- Mode: full
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
      "summary": "No mechanistic data or scientific literature was provided to evaluate the hypothesis of repurposing NEOMYCIN for viral human hepatitis infection. Therefore, a rigorous assessment of its potential is not possible based on the given information, leading to an 'Unlikely' conclusion due to the complete absence of supporting evidence.",
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
          "Neomycin Sulfate",
          "Neomycin B",
          "Framycetin",
          "Soframycin",
          "Myciguent"
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
          "viral hepatitis disease",
          "viral hepatitis syndrome"
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
        "Insufficient data to assess efficacy or safety risks for this repurposing hypothesis."
      ],
      "limitations": [
        "The evaluation is severely limited by the complete absence of provided mechanistic data and scientific literature, making any definitive conclusion impossible."
      ],
      "missing_data": [
        "Mechanistic data detailing NEOMYCIN's interaction with viral human hepatitis targets or pathways.",
        "Scientific literature (pre-clinical, clinical, or observational studies) on NEOMYCIN's efficacy or safety in the context of viral human hepatitis.",
        "Common targets and specific mechanism details for NEOMYCIN relevant to viral human hepatitis."
      ]
    },
    "9_recommended_next_steps": {
      "clinical_next_steps": [
        "Conduct a comprehensive literature search for NEOMYCIN's activity against viral human hepatitis.",
        "Investigate potential mechanisms of action for NEOMYCIN that could be relevant to viral human hepatitis.",
        "Explore in vitro studies of NEOMYCIN's antiviral effects against hepatitis viruses."
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
    "run_id": "4b2477583764",
    "created_at": "2026-06-03T14:10:41.503031+00:00",
    "drug": "NEOMYCIN",
    "disease": "viral human hepatitis infection",
    "total_claims": 0,
    "quality_score": 0.3875,
    "reruns": 2
  }
}
```
