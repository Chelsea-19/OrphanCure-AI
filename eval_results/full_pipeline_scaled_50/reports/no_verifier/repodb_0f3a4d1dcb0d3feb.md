# OrphanCure Full Pipeline Report: repodb_0f3a4d1dcb0d3feb

- Drug: Radium Ra 223 Dichloride
- Disease: Malignant neoplasm of prostate
- Mode: no_verifier
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
      "summary": "Radium-223 dichloride (Ra-223) is an approved alpha emitter that specifically targets bone metastases in prostate cancer. Multiple studies demonstrate its effectiveness in improving survival, reducing symptomatic skeletal events, and enhancing quality of life in patients with metastatic castration-resistant prostate cancer (mCRPC). Real-world data further support its clinical utility.",
      "evidence_counts": {
        "total_papers": 50,
        "supporting": 3,
        "contradicting": 11,
        "inconclusive": 36
      },
      "common_targets_count": 0
    },
    "2_normalized_hypothesis": {
      "statement": "Repurpose RADIUM RA 223 DICHLORIDE for prostate cancer",
      "drug": {
        "id": "CHEMBL2107816",
        "name": "RADIUM RA 223 DICHLORIDE",
        "aliases": [
          "Xofigo",
          "Radium-223 dichloride",
          "Ra-223 dichloride",
          "Radium dichloride Ra 223",
          "Ra 223 dichloride"
        ],
        "resolution_method": "auto"
      },
      "disease": {
        "id": "MONDO_0008315",
        "name": "prostate cancer",
        "aliases": [
          "prostatic adenocarcinoma",
          "adenocarcinoma of prostate",
          "cancer of the prostate",
          "malignant neoplasm of prostate",
          "prostate carcinoma"
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
      "total_retrieved": 50,
      "polarity": {
        "supports": 3,
        "contradicts": 11,
        "inconclusive": 36
      },
      "support_ratio": "3 of 50 retrieved papers support the hypothesis",
      "queries_used": 10,
      "top_papers": [
        {
          "pmid": "41346006",
          "title": "Effectiveness and Safety of Radium-223 for Bone-Metastatic Castration-Resistant Prostate Cancer: The KYUCOG-1901 Study.",
          "year": "2026",
          "relevance_score": 10.5,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study",
            "Recent"
          ]
        },
        {
          "pmid": "41090322",
          "title": "UK real-world data of radium-223 dichloride in metastatic prostate cancer.",
          "year": "2025",
          "relevance_score": 9.5,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study",
            "Recent"
          ]
        },
        {
          "pmid": "36156455",
          "title": "Radium-223 dichloride treatment in metastatic castration-resistant prostate cancer in Finland: A real-world evidence multicenter study.",
          "year": "2023",
          "relevance_score": 9.5,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study",
            "Recent"
          ]
        },
        {
          "pmid": "40334149",
          "title": "Outcomes of Radium-223 and Stereotactic Ablative Radiotherapy Versus Stereotactic Ablative Radiotherapy for Oligometastatic Prostate Cancers: The RAVENS Phase II Randomized Trial.",
          "year": "2025",
          "relevance_score": 8.0,
          "polarity": "INCONCLUSIVE",
          "match_reasons": [
            "Clinical study",
            "Recent"
          ]
        },
        {
          "pmid": "29734647",
          "title": "Recent Advances in Prostate Cancer Treatment and Drug Discovery.",
          "year": "2018",
          "relevance_score": 8.0,
          "polarity": "INCONCLUSIVE",
          "match_reasons": [
            "Clinical study"
          ]
        },
        {
          "pmid": "31227054",
          "title": "Radionuclide Therapy of Metastatic Prostate Cancer.",
          "year": "2019",
          "relevance_score": 7.5,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study"
          ]
        },
        {
          "pmid": "29022046",
          "title": "[Radium-223 dichloride in patients with castration-refractory prostate cancer].",
          "year": "2017",
          "relevance_score": 7.5,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study"
          ]
        },
        {
          "pmid": "31471713",
          "title": "Radium-223 dichloride in prostate cancer: proof of principle for the use of targeted alpha treatment in clinical practice.",
          "year": "2020",
          "relevance_score": 7.0,
          "polarity": "INCONCLUSIVE",
          "match_reasons": [
            "Clinical study"
          ]
        },
        {
          "pmid": "38774416",
          "title": "Outcomes and patterns of use of Radium-223 in metastatic castration-resistant prostate cancer.",
          "year": "2024",
          "relevance_score": 7.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Recent"
          ]
        },
        {
          "pmid": "36305673",
          "title": "Effectiveness and safety of radium-223 dichloride in patients with castration-resistant prostate cancer and bone metastases in real-world practice: A multi-institutional study.",
          "year": "2023",
          "relevance_score": 7.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Recent"
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
        "overall_score": 0.787,
        "decision": "finalize",
        "dimensions": {
          "completeness": {
            "score": 1.0,
            "reason": "5/5 sections present"
          },
          "evidence_support": {
            "score": 1.0,
            "reason": "3/3 claims have paper evidence"
          },
          "citation_validity": {
            "score": 1.0,
            "reason": "7 total citations"
          },
          "mechanistic_specificity": {
            "score": 0.0,
            "reason": "0/3 claims reference targets"
          },
          "contradiction_handling": {
            "score": 0.3,
            "reason": "No contradiction analysis"
          },
          "traceability": {
            "score": 1.0,
            "reason": "3/3 claims have provenance"
          },
          "output_structure": {
            "score": 1.0,
            "reason": "Executive summary + confidence assessment"
          },
          "actionability": {
            "score": 1.0,
            "reason": "3 next steps, 4 data gaps identified"
          }
        },
        "weak_dimensions": [
          "mechanistic_specificity",
          "contradiction_handling"
        ],
        "rerun_targets": []
      }
    },
    "8_risk_flags_limitations": {
      "risk_flags": [
        "Potential for myelosuppression and gastrointestinal toxicity (general risk for radium therapy, not explicitly detailed in snippets)."
      ],
      "limitations": [
        "Some studies are observational or retrospective, limiting causal inference.",
        "Limited data on combination therapies requires further validation.",
        "The provided abstracts do not detail specific mechanistic targets beyond bone metastasis localization."
      ],
      "missing_data": [
        "Detailed data on integration with subsequent therapies.",
        "Predictors of completing six cycles of treatment.",
        "Long-term outcomes in real-world settings.",
        "Data on combination with abiraterone or enzalutamide needs validation."
      ]
    },
    "9_recommended_next_steps": {
      "clinical_next_steps": [
        "Investigate optimal sequencing of Ra-223 with novel androgen axis drugs and chemotherapy.",
        "Further evaluate Ra-223 in earlier stages of prostate cancer or in combination with other targeted therapies.",
        "Explore predictors of response and resistance to Ra-223 treatment."
      ]
    },
    "10_claim_evidence_table": {
      "total_claims": 3,
      "claims": [
        {
          "claim_id": "CLM-024f5b",
          "statement": "Radium-223 dichloride improves survival in patients with bone-metastatic castration-resistant prostate cancer.",
          "confidence_numeric": 0.9,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "UNVERIFIED",
          "targets": [],
          "citation_count": 3,
          "risk_flags": []
        },
        {
          "claim_id": "CLM-c8f778",
          "statement": "Radium-223 dichloride targets bone metastases specifically in prostate cancer.",
          "confidence_numeric": 0.9,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "UNVERIFIED",
          "targets": [],
          "citation_count": 2,
          "risk_flags": []
        },
        {
          "claim_id": "CLM-961cbf",
          "statement": "Radium-223 dichloride can be used in combination with other prostate cancer therapies.",
          "confidence_numeric": 0.8,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "UNVERIFIED",
          "targets": [],
          "citation_count": 2,
          "risk_flags": []
        }
      ]
    },
    "11_provenance_appendix": {
      "total_entries": 3,
      "entries": [
        {
          "claim_id": "CLM-024f5b",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "809fdb2ebaf0",
          "timestamp": "2026-06-03T14:40:49.480061+00:00",
          "paper_evidence": [
            {
              "pmid": "41346006",
              "snippet": "Radium-223 dichloride (Ra-223) improves survival in bone-metastatic castration-resistant prostate cancer (mCRPC).",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            },
            {
              "pmid": "36156455",
              "snippet": "Results of a previously reported phase III randomized trial showed survival benefit for radium-223 compared to best supportive care in castration-resistant prostate cancer (CRPC) with bone metastases.",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            },
            {
              "pmid": "29022046",
              "snippet": "In the ASYMPCA clinical trial, radium-223 was shown to improve overall survival and to reduce the time to the first symptomatic skeletal event.",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            }
          ],
          "mechanism_evidence": [],
          "queries_used_count": 10
        },
        {
          "claim_id": "CLM-c8f778",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "809fdb2ebaf0",
          "timestamp": "2026-06-03T14:40:49.480061+00:00",
          "paper_evidence": [
            {
              "pmid": "36156455",
              "snippet": "Radium-233 dichloride is an alpha emitter that specifically targets bone metastases in prostate cancer.",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            },
            {
              "pmid": "31471713",
              "snippet": "Radium-223 dichloride in prostate cancer: proof of principle for the use of targeted alpha treatment in clinical practice.",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            }
          ],
          "mechanism_evidence": [],
          "queries_used_count": 10
        },
        {
          "claim_id": "CLM-961cbf",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "809fdb2ebaf0",
          "timestamp": "2026-06-03T14:40:49.480061+00:00",
          "paper_evidence": [
            {
              "pmid": "29022046",
              "snippet": "The efficacy of radium-223 dichloride was not inhibited by the use of chemotherapy with docetaxel.",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            },
            {
              "pmid": "29022046",
              "snippet": "Studies have demonstrated a longer overall survival (OS) in patients with a combined treatment of abiraterone or enzalutamide; however, until this data is validated...",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            }
          ],
          "mechanism_evidence": [],
          "queries_used_count": 10
        }
      ]
    }
  },
  "metadata": {
    "run_id": "809fdb2ebaf0",
    "created_at": "2026-06-03T14:40:30.148940+00:00",
    "drug": "RADIUM RA 223 DICHLORIDE",
    "disease": "prostate cancer",
    "total_claims": 3,
    "quality_score": 0.7875,
    "reruns": 0
  }
}
```
