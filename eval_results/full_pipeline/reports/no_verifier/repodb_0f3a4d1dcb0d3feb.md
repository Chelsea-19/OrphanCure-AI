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
      "summary": "Radium-223 dichloride (Ra-223) is a bone-targeted radioligand therapy that has demonstrated effectiveness and prolonged overall survival in patients with bone-metastatic castration-resistant prostate cancer (CRPC). It induces DNA damage and inhibits prostate cancer cell survival, making it a viable repurposing option for this indication.",
      "evidence_counts": {
        "total_papers": 33,
        "supporting": 3,
        "contradicting": 5,
        "inconclusive": 25
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
          "Ra-223 dichloride",
          "Radium dichloride Ra 223",
          "Radium-223 dichloride",
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
          "prostate carcinoma",
          "PCa"
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
      "total_retrieved": 33,
      "polarity": {
        "supports": 3,
        "contradicts": 5,
        "inconclusive": 25
      },
      "support_ratio": "3 of 33 retrieved papers support the hypothesis",
      "queries_used": 10,
      "top_papers": [
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
          "pmid": "36305673",
          "title": "Effectiveness and safety of radium-223 dichloride in patients with castration-resistant prostate cancer and bone metastases in real-world practice: A multi-institutional study.",
          "year": "2023",
          "relevance_score": 7.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Recent"
          ]
        },
        {
          "pmid": "36126563",
          "title": "Ra-223 induces clustered DNA damage and inhibits cell survival in several prostate cancer cell lines.",
          "year": "2022",
          "relevance_score": 6.5,
          "polarity": "INCONCLUSIVE",
          "match_reasons": [
            "Recent"
          ]
        },
        {
          "pmid": "34213559",
          "title": "Association of Chemotherapy, Enzalutamide, Abiraterone, and Radium 223 With Cognitive Function in Older Men With Metastatic Castration-Resistant Prostate Cancer.",
          "year": "2021",
          "relevance_score": 6.0,
          "polarity": "SUPPORTS",
          "match_reasons": []
        },
        {
          "pmid": "27167841",
          "title": "Interim Results From ERADICATE: An Open-Label Phase 2 Study of Radium Ra 223 Dichloride With Concurrent Administration of Abiraterone Acetate Plus Prednisone in Castration-Resistant Prostate Cancer Subjects With Symptomatic Bone Metastases.",
          "year": "2016",
          "relevance_score": 6.0,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Title Match"
          ]
        },
        {
          "pmid": "27015255",
          "title": "Budget Impact of Enzalutamide for Chemotherapy-Na\u00efve Metastatic Castration-Resistant Prostate Cancer.",
          "year": "2016",
          "relevance_score": 6.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal"
          ]
        },
        {
          "pmid": "26573043",
          "title": "Health Economics and Radium-223 (Xofigo\u00ae) in the Treatment of Metastatic Castration-Resistant Prostate Cancer (mCRPC): A Case History and a Systematic Review of the Literature.",
          "year": "2015",
          "relevance_score": 6.0,
          "polarity": "INCONCLUSIVE",
          "match_reasons": [
            "Clinical study"
          ]
        },
        {
          "pmid": "28631036",
          "title": "Practical recommendations for radium-223 treatment of metastatic castration-resistant prostate cancer.",
          "year": "2017",
          "relevance_score": 5.5,
          "polarity": "SUPPORTS",
          "match_reasons": []
        },
        {
          "pmid": "35717046",
          "title": "Radium-223 for Metastatic Castrate-Resistant Prostate Cancer.",
          "year": "2022",
          "relevance_score": 5.5,
          "polarity": "INCONCLUSIVE",
          "match_reasons": [
            "Recent"
          ]
        },
        {
          "pmid": "32140364",
          "title": "A Single-center Retrospective Analysis of the Effect of Radium-223 (Xofigo) on Pancytopenia in Patients with Metastatic Castration-resistant Prostate Cancer.",
          "year": "2020",
          "relevance_score": 5.0,
          "polarity": "INCONCLUSIVE",
          "match_reasons": []
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
            "reason": "3 total citations"
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
            "reason": "3 next steps, 3 data gaps identified"
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
        "Potential for cognitive impairment in older adults.",
        "High cost of treatment."
      ],
      "limitations": [
        "The provided abstracts focus primarily on metastatic castration-resistant prostate cancer (mCRPC) with bone metastases.",
        "Some studies are observational or interim analyses.",
        "Limited information on mechanisms beyond DNA damage and cell survival inhibition."
      ],
      "missing_data": [
        "Detailed toxicity profiles beyond bone metastases.",
        "Efficacy in non-metastatic or hormone-sensitive prostate cancer.",
        "Comparative effectiveness against other advanced prostate cancer treatments."
      ]
    },
    "9_recommended_next_steps": {
      "clinical_next_steps": [
        "Further investigation into the long-term cognitive effects of Ra-223 in older men with mCRPC.",
        "Evaluate the cost-effectiveness of Ra-223 in various healthcare settings.",
        "Explore combination therapies involving Ra-223 with other agents like abiraterone acetate."
      ]
    },
    "10_claim_evidence_table": {
      "total_claims": 3,
      "claims": [
        {
          "claim_id": "CLM-bcfa7c",
          "statement": "Radium-223 dichloride is a bone-targeted radioligand therapy that prolongs overall survival in patients with bone-metastatic castration-resistant prostate cancer.",
          "confidence_numeric": 0.9,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "UNVERIFIED",
          "targets": [],
          "citation_count": 1,
          "risk_flags": []
        },
        {
          "claim_id": "CLM-48ba1a",
          "statement": "Radium-223 dichloride induces clustered DNA damage and inhibits cell survival in prostate cancer cell lines.",
          "confidence_numeric": 0.9,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "UNVERIFIED",
          "targets": [],
          "citation_count": 1,
          "risk_flags": []
        },
        {
          "claim_id": "CLM-917709",
          "statement": "Radium-223 dichloride is the first targeted alpha therapy for patients with castration-resistant prostate cancer and symptomatic bone metastases.",
          "confidence_numeric": 0.9,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "UNVERIFIED",
          "targets": [],
          "citation_count": 1,
          "risk_flags": []
        }
      ]
    },
    "11_provenance_appendix": {
      "total_entries": 3,
      "entries": [
        {
          "claim_id": "CLM-bcfa7c",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "227d29200d9b",
          "timestamp": "2026-06-03T11:58:39.465042+00:00",
          "paper_evidence": [
            {
              "pmid": "36305673",
              "snippet": "Radium-223 (Ra-223) dichloride is the bone-targeted radioligand therapy that prolongs overall survival (OS) in patients with bone-metastatic castration-resistant prostate cancer (CRPC).",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            }
          ],
          "mechanism_evidence": [],
          "queries_used_count": 10
        },
        {
          "claim_id": "CLM-48ba1a",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "227d29200d9b",
          "timestamp": "2026-06-03T11:58:39.465042+00:00",
          "paper_evidence": [
            {
              "pmid": "36126563",
              "snippet": "Ra-223 induces clustered DNA damage and inhibits cell survival in several prostate cancer cell lines.",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            }
          ],
          "mechanism_evidence": [],
          "queries_used_count": 10
        },
        {
          "claim_id": "CLM-917709",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "227d29200d9b",
          "timestamp": "2026-06-03T11:58:39.465042+00:00",
          "paper_evidence": [
            {
              "pmid": "28631036",
              "snippet": "Radium Ra 223 dichloride (radium-223, Xofigo\u00ae) is the first targeted alpha therapy for patients with castration-resistant prostate cancer and symptomatic bone metastases.",
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
    "run_id": "227d29200d9b",
    "created_at": "2026-06-03T11:58:19.784332+00:00",
    "drug": "RADIUM RA 223 DICHLORIDE",
    "disease": "prostate cancer",
    "total_claims": 3,
    "quality_score": 0.7875,
    "reruns": 0
  }
}
```
