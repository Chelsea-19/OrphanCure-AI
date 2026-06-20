# OrphanCure Full Pipeline Report: repodb_04246cb3a1c31ef7

- Drug: Progesterone
- Disease: Premature Birth
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
      "summary": "Progesterone, acting via its receptor (PGR), is a well-established mechanism for inhibiting uterine contractions and maintaining pregnancy, thus preventing premature birth. Multiple studies demonstrate its efficacy in various formulations and high-risk populations, supporting its repurposing for premature birth prevention.",
      "evidence_counts": {
        "total_papers": 59,
        "supporting": 8,
        "contradicting": 2,
        "inconclusive": 49
      },
      "common_targets_count": 1
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
          "Prometrium"
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
      "total_mechanisms": 1,
      "mechanisms": [
        {
          "target": "PGR",
          "drug_action": "AGONIST",
          "disease_score": 0.554,
          "pathway": "Progesterone, acting through its receptor (PGR), inhibits uterine contractions and maintains pregnancy by suppressing myometrial activity and cervical ripening, thus preventing premature birth."
        }
      ]
    },
    "4_target_overlap_summary": {
      "total_overlapping": 1,
      "top_targets": [
        {
          "symbol": "PGR",
          "name": "progesterone receptor",
          "drug_action": "AGONIST",
          "disease_association_score": 0.554
        }
      ]
    },
    "5_literature_evidence_summary": {
      "total_retrieved": 59,
      "polarity": {
        "supports": 8,
        "contradicts": 2,
        "inconclusive": 49
      },
      "support_ratio": "8 of 59 retrieved papers support the hypothesis",
      "queries_used": 11,
      "top_papers": [
        {
          "pmid": "35178856",
          "title": "Progesterone receptor genetic variants in pregnant women and fetuses as possible predictors of spontaneous premature birth: A preliminary case-control study.",
          "year": "2022",
          "relevance_score": 10.5,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Targets: 1",
            "Recent",
            "Title Match"
          ]
        },
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
      "overall": "Low",
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
            "reason": "1/1 claims have paper evidence"
          },
          "citation_validity": {
            "score": 0.5,
            "reason": "0 verified, 1 partial out of 1"
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
        "ALL evidence verification failed",
        "Need to ensure appropriate patient selection for progesterone therapy.",
        "Potential for side effects associated with progesterone use."
      ],
      "limitations": [
        "The provided abstracts do not detail the specific disease score for progesterone's mechanism of action beyond the initial mention.",
        "While many papers support progesterone's role, the exact percentage of supporting, contradicting, and inconclusive papers is not fully detailed in the provided snippets.",
        "Some studies focus on genetic variants of the progesterone receptor rather than direct progesterone intervention."
      ],
      "missing_data": [
        "Specific details on the comparative effectiveness of different progesterone formulations (e.g., oral vs. vaginal) in preventing preterm birth.",
        "Data on the efficacy of progesterone in preventing preterm birth in non-high-risk populations.",
        "Long-term outcomes for infants born after progesterone treatment for preterm birth prevention."
      ]
    },
    "9_recommended_next_steps": {
      "clinical_next_steps": [
        "Further investigation into optimal progesterone formulations (e.g., vaginal, oral) and dosing for different risk groups.",
        "Comparative studies of progesterone against other interventions like cervical cerclage and pessary.",
        "Exploration of progesterone's role in specific subtypes of premature birth, potentially linked to PGR genetic variants."
      ]
    },
    "10_claim_evidence_table": {
      "total_claims": 1,
      "claims": [
        {
          "claim_id": "CLM-af16d5",
          "statement": "Progesterone, through its receptor (PGR), inhibits uterine contractions and maintains pregnancy, thereby preventing premature birth.",
          "confidence_numeric": 0.9,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "PARTIALLY_VERIFIED",
          "targets": [
            "PGR"
          ],
          "citation_count": 6,
          "risk_flags": []
        }
      ]
    },
    "11_provenance_appendix": {
      "total_entries": 1,
      "entries": [
        {
          "claim_id": "CLM-af16d5",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "18c721cbc575",
          "timestamp": "2026-06-03T14:03:59.906208+00:00",
          "paper_evidence": [
            {
              "pmid": "35178856",
              "snippet": "Four single nucleotide polymorphisms (SNPs) of the progesterone receptor gene (PGR) and to identify women who may have higher or lower odds for spontaneous premature birth",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": "Quote mismatch (fuzzy check failed)"
            },
            {
              "pmid": "36694081",
              "snippet": "Defects in embryo implantation and decidualization can cause a series of adverse chain reactions which can contribute to harmful pregnancy outcomes, such as embryo growth retardation, preeclampsia, mi",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            },
            {
              "pmid": "39012912",
              "snippet": "Cervical cerclage, cervical pessary, and vaginal progesterone have each been shown to reduce preterm birth (PTB) in high-risk women",
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
          "mechanism_evidence": [
            {
              "target": "PGR",
              "action": "AGONIST"
            }
          ],
          "queries_used_count": 11
        }
      ]
    }
  },
  "metadata": {
    "run_id": "18c721cbc575",
    "created_at": "2026-06-03T14:03:37.083600+00:00",
    "drug": "PROGESTERONE",
    "disease": "premature birth",
    "total_claims": 1,
    "quality_score": 0.85,
    "reruns": 0
  }
}
```
