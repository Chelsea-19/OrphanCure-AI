# OrphanCure Full Pipeline Report: repodb_04246cb3a1c31ef7

- Drug: Progesterone
- Disease: Premature Birth
- Mode: no_graph_features
- Status: completed
- Final assessment: Potential

This generated report is for research support only and is not medical advice.

## Structured Output

```json
{
  "sections": {
    "1_executive_summary": {
      "conclusion": "Potential",
      "confidence": "Medium",
      "summary": "Progesterone, particularly in vaginal formulations, is investigated as a potential treatment to prevent premature birth, especially in high-risk pregnancies. While some studies suggest a role for progesterone receptor gene variants in predicting premature birth, and clinical trials compare progesterone with other interventions, direct evidence for progesterone as a primary repurposed drug for premature birth is still developing.",
      "evidence_counts": {
        "total_papers": 59,
        "supporting": 8,
        "contradicting": 2,
        "inconclusive": 49
      },
      "common_targets_count": 0
    },
    "2_normalized_hypothesis": {
      "statement": "Repurpose PROGESTERONE for premature birth",
      "drug": {
        "id": "CHEMBL103",
        "name": "PROGESTERONE",
        "aliases": [
          "Progestogen",
          "Luteohormone",
          "Pregn-4-ene-3,20-dione",
          "P4",
          "Progestasert"
        ],
        "resolution_method": "auto"
      },
      "disease": {
        "id": "EFO_0003917",
        "name": "premature birth",
        "aliases": [
          "preterm birth",
          "prematurity",
          "PTB",
          "premature delivery",
          "preterm delivery"
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
      "total_retrieved": 59,
      "polarity": {
        "supports": 8,
        "contradicts": 2,
        "inconclusive": 49
      },
      "support_ratio": "8 of 59 retrieved papers support the hypothesis",
      "queries_used": 10,
      "top_papers": [
        {
          "pmid": "36694081",
          "title": "Progress on the Role of Estrogen and Progesterone Signaling in Mouse Embryo Implantation and Decidualization.",
          "year": "2023",
          "relevance_score": 9.5,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Recent"
          ]
        },
        {
          "pmid": "35178856",
          "title": "Progesterone receptor genetic variants in pregnant women and fetuses as possible predictors of spontaneous premature birth: A preliminary case-control study.",
          "year": "2022",
          "relevance_score": 8.5,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Recent",
            "Title Match"
          ]
        },
        {
          "pmid": "39012912",
          "title": "Comparing cervical cerclage, pessary and vaginal progesterone for prevention of preterm birth in women with a short cervix (SuPPoRT): A multicentre randomised controlled trial.",
          "year": "2024",
          "relevance_score": 8.0,
          "polarity": "INCONCLUSIVE",
          "match_reasons": [
            "Clinical study",
            "Recent"
          ]
        },
        {
          "pmid": "37196896",
          "title": "Vaginal progesterone for preventing preterm birth\u00a0and adverse perinatal outcomes in twin\u00a0gestations: a systematic review and meta-analysis.",
          "year": "2023",
          "relevance_score": 8.0,
          "polarity": "INCONCLUSIVE",
          "match_reasons": [
            "Clinical study",
            "Recent"
          ]
        },
        {
          "pmid": "37211087",
          "title": "Combined vaginal progesterone and cervical cerclage in the prevention of preterm birth: a systematic review and meta-analysis.",
          "year": "2023",
          "relevance_score": 8.0,
          "polarity": "INCONCLUSIVE",
          "match_reasons": [
            "Clinical study",
            "Recent"
          ]
        },
        {
          "pmid": "40814120",
          "title": "Comparison of oral dydrogesterone and vaginal progesterone for luteal phase support in natural and modified natural cycle frozen embryo transfers.",
          "year": "2025",
          "relevance_score": 7.0,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Recent"
          ]
        },
        {
          "pmid": "41576138",
          "title": "Pregnancy outcomes in women at high risk of preterm birth receiving a vaginal cervical cerclage with, or without, progesterone: A retrospective, secondary analysis of the C-STICH randomised controlled trial data.",
          "year": "2026",
          "relevance_score": 7.0,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Recent"
          ]
        },
        {
          "pmid": "40694719",
          "title": "THE ROLE OF THE VAGINAL MICROBIOTA IN THE PATHOGENESIS OF PRETERM PREMATURE BIRTH IN WOMEN WITH IC: A SYSTEMATIC REVIEW.",
          "year": "2025",
          "relevance_score": 7.0,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Recent"
          ]
        },
        {
          "pmid": "29157866",
          "title": "Vaginal progesterone for preventing preterm birth and adverse perinatal outcomes in singleton gestations with a\u00a0short cervix: a meta-analysis of individual patient data.",
          "year": "2018",
          "relevance_score": 7.0,
          "polarity": "CONTRADICTS",
          "match_reasons": [
            "Contradiction signal",
            "Clinical study"
          ]
        },
        {
          "pmid": "35460628",
          "title": "Does vaginal progesterone prevent recurrent preterm birth in women with a singleton gestation and a history of spontaneous preterm birth? Evidence from a systematic review and meta-analysis.",
          "year": "2022",
          "relevance_score": 7.0,
          "polarity": "INCONCLUSIVE",
          "match_reasons": [
            "Clinical study",
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
      "overall": "Medium",
      "dimensions": {
        "mechanistic_strength": "Medium",
        "literature_strength": "High",
        "clinical_evidence": "Medium"
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
            "reason": "3 verified, 0 partial out of 3"
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
        "The effectiveness of progesterone may be context-dependent (e.g., specific risk factors, gestational age).",
        "Progesterone receptor gene variants may indicate a predisposition to premature birth, suggesting a complex interplay of factors."
      ],
      "limitations": [
        "The provided literature focuses on progesterone's role in preventing preterm birth in specific high-risk groups, not necessarily as a broad repurposing strategy for all premature births.",
        "Some studies are preliminary or focus on genetic associations rather than direct therapeutic efficacy.",
        "The exact mechanisms by which progesterone prevents preterm birth are not fully elucidated in these abstracts."
      ],
      "missing_data": [
        "Direct evidence of progesterone's efficacy as a repurposed drug for premature birth outside of specific high-risk populations.",
        "Detailed comparative data on oral vs. vaginal progesterone for preterm birth prevention.",
        "Long-term outcomes of infants born after progesterone treatment for preterm birth prevention."
      ]
    },
    "9_recommended_next_steps": {
      "clinical_next_steps": [
        "Conduct further randomized controlled trials comparing different progesterone formulations and dosages for preterm birth prevention.",
        "Investigate the role of progesterone receptor gene polymorphisms in stratifying patients for progesterone therapy.",
        "Explore combination therapies of progesterone with other interventions like cervical cerclage or pessary."
      ]
    },
    "10_claim_evidence_table": {
      "total_claims": 3,
      "claims": [
        {
          "claim_id": "CLM-a82746",
          "statement": "Progesterone signaling is involved in maintaining pregnancy and preventing adverse outcomes like premature birth.",
          "confidence_numeric": 0.7,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "VERIFIED",
          "targets": [],
          "citation_count": 1,
          "risk_flags": []
        },
        {
          "claim_id": "CLM-987969",
          "statement": "Vaginal progesterone is being evaluated for the prevention of preterm birth in high-risk pregnancies, including those with a short cervix or twin gestations.",
          "confidence_numeric": 0.8,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "VERIFIED",
          "targets": [],
          "citation_count": 4,
          "risk_flags": []
        },
        {
          "claim_id": "CLM-cb28ed",
          "statement": "Genetic variations in the progesterone receptor gene may be associated with the risk of spontaneous premature birth.",
          "confidence_numeric": 0.6,
          "confidence_label": "MEDIUM",
          "polarity": "INCONCLUSIVE",
          "verification_status": "VERIFIED",
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
          "claim_id": "CLM-a82746",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "1d91972be7d3",
          "timestamp": "2026-06-03T12:22:38.463114+00:00",
          "paper_evidence": [
            {
              "pmid": "36694081",
              "snippet": "Defects in embryo implantation and decidualization can cause a series of adverse chain reactions which can contribute to harmful pregnancy outcomes, such as embryo growth retardation, preeclampsia, mi",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            }
          ],
          "mechanism_evidence": [],
          "queries_used_count": 10
        },
        {
          "claim_id": "CLM-987969",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "1d91972be7d3",
          "timestamp": "2026-06-03T12:22:38.463114+00:00",
          "paper_evidence": [
            {
              "pmid": "39012912",
              "snippet": "Cervical cerclage, cervical pessary, and vaginal progesterone have each been shown to reduce preterm birth (PTB) in high-risk women, but to our knowledge, there has been no randomised comparison of th",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            },
            {
              "pmid": "37196896",
              "snippet": "To evaluate the efficacy of vaginal progesterone for the prevention of preterm birth and adverse perinatal outcomes in twin gestations.",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            },
            {
              "pmid": "37211087",
              "snippet": "Vaginal progesterone and cervical cerclage are both effective interventions for reducing preterm birth.",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            },
            {
              "pmid": "41576138",
              "snippet": "Vaginal cervical cerclage and progesterone are established treatments for prevention of pregnancy loss and prematurity.",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            }
          ],
          "mechanism_evidence": [],
          "queries_used_count": 10
        },
        {
          "claim_id": "CLM-cb28ed",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "1d91972be7d3",
          "timestamp": "2026-06-03T12:22:38.463114+00:00",
          "paper_evidence": [
            {
              "pmid": "35178856",
              "snippet": "There was statistically significant difference between cases and controls in the distribution of newborns' allele frequency of minor C allele of the PGR SNP rs1942836 (p = 0.03, Fishers' exact test) i",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
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
    "run_id": "1d91972be7d3",
    "created_at": "2026-06-03T12:22:15.018358+00:00",
    "drug": "PROGESTERONE",
    "disease": "premature birth",
    "total_claims": 3,
    "quality_score": 0.7875,
    "reruns": 0
  }
}
```
