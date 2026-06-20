# OrphanCure Full Pipeline Report: repodb_2df019ef279bf716

- Drug: Finasteride
- Disease: Benign Prostatic Hyperplasia
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
      "summary": "Finasteride is a well-established treatment for benign prostatic hyperplasia (BPH) due to its mechanism of inhibiting SRD5A2, which reduces dihydrotestosterone (DHT) levels crucial for prostate growth. Extensive literature supports its use, although side effects like sexual dysfunction are noted.",
      "evidence_counts": {
        "total_papers": 56,
        "supporting": 27,
        "contradicting": 7,
        "inconclusive": 22
      },
      "common_targets_count": 1
    },
    "2_normalized_hypothesis": {
      "statement": "Repurpose FINASTERIDE for benign prostatic hyperplasia",
      "drug": {
        "id": "CHEMBL710",
        "name": "FINASTERIDE",
        "aliases": [
          "Proscar",
          "Propecia",
          "Fincar",
          "Finasterid",
          "Finasteridum"
        ],
        "resolution_method": "auto"
      },
      "disease": {
        "id": "EFO_0000284",
        "name": "benign prostatic hyperplasia",
        "aliases": [
          "BPH",
          "benign prostatic hypertrophy",
          "enlarged prostate",
          "prostatic hyperplasia benign",
          "adenofibromyomatous hyperplasia of prostate"
        ],
        "resolution_method": "auto"
      }
    },
    "3_mechanistic_rationale": {
      "total_mechanisms": 1,
      "mechanisms": [
        {
          "target": "SRD5A2",
          "drug_action": "INHIBITOR",
          "disease_score": 0.624,
          "pathway": "Finasteride inhibits SRD5A2, the enzyme responsible for converting testosterone to dihydrotestosterone (DHT), thereby reducing DHT levels which are a key driver of prostate growth in benign prostatic hyperplasia."
        }
      ]
    },
    "4_target_overlap_summary": {
      "total_overlapping": 1,
      "top_targets": [
        {
          "symbol": "SRD5A2",
          "name": "steroid 5 alpha-reductase 2",
          "drug_action": "INHIBITOR",
          "disease_association_score": 0.624
        }
      ]
    },
    "5_literature_evidence_summary": {
      "total_retrieved": 56,
      "polarity": {
        "supports": 27,
        "contradicts": 7,
        "inconclusive": 22
      },
      "support_ratio": "27 of 56 retrieved papers support the hypothesis",
      "queries_used": 11,
      "top_papers": [
        {
          "pmid": "30209896",
          "title": "Finasteride and Erectile Dysfunction in Patients with Benign Prostatic Hyperplasia or Male Androgenetic Alopecia.",
          "year": "2019",
          "relevance_score": 11.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study",
            "Title Match"
          ]
        },
        {
          "pmid": "40946793",
          "title": "Stromal Steroid 5 Alpha-Reductase 2 Promotes Prostate Growth through WNT5A-Lymphoid Enhancer-Binding Factor 1-Insulin-Like Growth Factor 1 Signaling in Benign Prostatic Hyperplasia.",
          "year": "2025",
          "relevance_score": 10.5,
          "polarity": "INCONCLUSIVE",
          "match_reasons": [
            "Targets: 1",
            "Recent"
          ]
        },
        {
          "pmid": "38636573",
          "title": "Future aspects of plant derived bioactive metabolites as therapeutics to combat benign prostatic hyperplasia.",
          "year": "2024",
          "relevance_score": 10.0,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Clinical study",
            "Recent"
          ]
        },
        {
          "pmid": "38308714",
          "title": "Tadalafil versus tamsulosin as combination therapy with 5-alpha reductase inhibitors in benign prostatic hyperplasia, urinary and sexual outcomes.",
          "year": "2024",
          "relevance_score": 9.5,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Clinical study",
            "Recent"
          ]
        },
        {
          "pmid": "39138902",
          "title": "The risk of psychiatric disorders in finasteride users with benign prostatic hyperplasia and androgenetic alopecia: A population-based case-control study.",
          "year": "2024",
          "relevance_score": 9.0,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Recent",
            "Title Match"
          ]
        },
        {
          "pmid": "39703506",
          "title": "Immune-related diagnostic markers for benign prostatic hyperplasia and their potential as drug targets.",
          "year": "2024",
          "relevance_score": 9.0,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Recent"
          ]
        },
        {
          "pmid": "36982979",
          "title": "Alteration of Gut Microbes in Benign Prostatic Hyperplasia Model and Finasteride Treatment Model.",
          "year": "2023",
          "relevance_score": 9.0,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Recent",
            "Title Match"
          ]
        },
        {
          "pmid": "38105612",
          "title": "Effects of L-Carnitine and Coenzyme Q10 Supplementation on Lower Urinary Tract Symptoms in Men with Benign Prostatic Hyperplasia: A Randomized, Controlled, Clinical Trial.",
          "year": "2024",
          "relevance_score": 9.0,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Clinical study",
            "Recent"
          ]
        },
        {
          "pmid": "38003881",
          "title": "Food Administration and Not Genetic Variants Causes Pharmacokinetic Variability of Tadalafil and Finasteride.",
          "year": "2023",
          "relevance_score": 9.0,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Clinical study",
            "Recent"
          ]
        },
        {
          "pmid": "36777802",
          "title": "Mixture of Corni Fructus and Schisandrae Fructus improves testosterone-induced benign prostatic hyperplasia through regulating 5\u03b1-reductase 2 and androgen receptor.",
          "year": "2023",
          "relevance_score": 9.0,
          "polarity": "SUPPORTS",
          "match_reasons": [
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
        "overall_score": 0.85,
        "decision": "finalize",
        "dimensions": {
          "completeness": {
            "score": 1.0,
            "reason": "5/5 sections present"
          },
          "evidence_support": {
            "score": 1.0,
            "reason": "2/2 claims have paper evidence"
          },
          "citation_validity": {
            "score": 1.0,
            "reason": "7 total citations"
          },
          "mechanistic_specificity": {
            "score": 0.5,
            "reason": "1/2 claims reference targets"
          },
          "contradiction_handling": {
            "score": 0.3,
            "reason": "No contradiction analysis"
          },
          "traceability": {
            "score": 1.0,
            "reason": "2/2 claims have provenance"
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
        "Risk of high-grade prostate cancer (though debated and potentially related to detection bias).",
        "Sexual dysfunction (erectile dysfunction, decreased libido, ejaculatory disorders).",
        "Potential for psychiatric side effects (depression, anxiety)."
      ],
      "limitations": [
        "The provided abstracts focus on the use of finasteride for BPH and its associated side effects, rather than novel repurposing.",
        "The mechanistic data is limited to the SRD5A2 inhibition, which is already a known mechanism for BPH treatment.",
        "The literature summary indicates a large number of papers, but the provided snippets are selective."
      ],
      "missing_data": [
        "Detailed comparative efficacy data against newer BPH treatments.",
        "Long-term safety data specifically for BPH patients with extensive follow-up.",
        "Further research into the precise mechanisms of finasteride's side effects."
      ]
    },
    "9_recommended_next_steps": {
      "clinical_next_steps": [
        "Continue to use finasteride as a standard treatment for BPH.",
        "Monitor patients for known side effects, particularly sexual dysfunction and potential psychiatric effects.",
        "Investigate novel combination therapies or adjunct treatments to mitigate side effects or enhance efficacy."
      ]
    },
    "10_claim_evidence_table": {
      "total_claims": 2,
      "claims": [
        {
          "claim_id": "CLM-4582a7",
          "statement": "Finasteride inhibits SRD5A2, an enzyme involved in androgen metabolism, which is a key target in benign prostatic hyperplasia.",
          "confidence_numeric": 0.9,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "UNVERIFIED",
          "targets": [
            "SRD5A2"
          ],
          "citation_count": 2,
          "risk_flags": []
        },
        {
          "claim_id": "CLM-56e9be",
          "statement": "Finasteride is a conventional medication used for the treatment of benign prostatic hyperplasia (BPH).",
          "confidence_numeric": 0.9,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "UNVERIFIED",
          "targets": [],
          "citation_count": 5,
          "risk_flags": []
        }
      ]
    },
    "11_provenance_appendix": {
      "total_entries": 2,
      "entries": [
        {
          "claim_id": "CLM-4582a7",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "be1627e840b5",
          "timestamp": "2026-06-03T14:29:14.874337+00:00",
          "paper_evidence": [
            {
              "pmid": "40946793",
              "snippet": "Steroid 5 \u03b1-reductase 2 (SRD5A2) is a key enzyme in androgen metabolism and a pharmacologic target in benign prostatic hyperplasia.",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            },
            {
              "pmid": "38636573",
              "snippet": "Conventional drugs such as finasteride and dutasteride are used as 5\u03b1-reductase inhibitors for the treatment of BPH.",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            }
          ],
          "mechanism_evidence": [
            {
              "target": "SRD5A2",
              "action": "INHIBITOR"
            }
          ],
          "queries_used_count": 11
        },
        {
          "claim_id": "CLM-56e9be",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "be1627e840b5",
          "timestamp": "2026-06-03T14:29:14.874337+00:00",
          "paper_evidence": [
            {
              "pmid": "30209896",
              "snippet": "Finasteride is primarily used to treat benign prostatic hyperplasia (BPH) and male androgenetic alopecia (MAA).",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            },
            {
              "pmid": "38308714",
              "snippet": "To compare the urological and sexual outcomes of using either tamsulosin/finateride or tadalafil/finasteride as combination therapies in patients with large prostate.",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            },
            {
              "pmid": "39138902",
              "snippet": "There is a long-standing debate if finasteride, a medication used to treat benign prostatic hyperplasia (BPH) and androgenetic alopecia (AGA), can cause psychiatric side effects.",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            },
            {
              "pmid": "36982979",
              "snippet": "We investigated the alteration of gut microbiota with implications for the diagnosis, prevention, and treatment of BPH and identified correlations among various indicators, including hormone indicator",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            },
            {
              "pmid": "38105612",
              "snippet": "Considering that BPH drug treatment is associated with complications, this study aimed to investigate the effects of L-carnitine (LC) and Coenzyme Q10 (CoQ10) supplementation as an adjunct therapy to ",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            }
          ],
          "mechanism_evidence": [],
          "queries_used_count": 11
        }
      ]
    }
  },
  "metadata": {
    "run_id": "be1627e840b5",
    "created_at": "2026-06-03T14:28:53.396401+00:00",
    "drug": "FINASTERIDE",
    "disease": "benign prostatic hyperplasia",
    "total_claims": 2,
    "quality_score": 0.85,
    "reruns": 0
  }
}
```
