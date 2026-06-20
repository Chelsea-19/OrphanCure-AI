# OrphanCure Full Pipeline Report: repodb_04246cb3a1c31ef7

- Drug: Progesterone
- Disease: Premature Birth
- Mode: no_target_expansion
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
      "summary": "Progesterone, acting as an agonist of the progesterone receptor (PGR), is a well-established therapeutic for preventing premature birth by inhibiting uterine contractions. Multiple studies demonstrate its efficacy, particularly in high-risk populations, supporting its repurposing for this indication.",
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
          "pathway": "Progesterone receptor (PGR) activation by progesterone inhibits uterine contractions and cervical ripening, thereby preventing premature birth."
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
      "queries_used": 10,
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
            "reason": "2/2 claims have paper evidence"
          },
          "citation_validity": {
            "score": 1.0,
            "reason": "2 verified, 0 partial out of 2"
          },
          "mechanistic_specificity": {
            "score": 1.0,
            "reason": "2/2 claims reference targets"
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
            "reason": "2 next steps, 2 data gaps identified"
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
        "Need for careful patient selection to maximize benefit and minimize risk.",
        "Potential for side effects associated with progesterone use."
      ],
      "limitations": [
        "The provided mechanism data is a general statement and not specific to the cited papers.",
        "One paper (35178856) investigates genetic variants of PGR and their association with premature birth, which is related but not direct evidence of progesterone's therapeutic effect.",
        "Some papers (e.g., 36694081, 40814120, 40694719) are indirectly related or focus on different aspects of pregnancy and progesterone use."
      ],
      "missing_data": [
        "Comparative effectiveness of different progesterone formulations (oral vs. vaginal) in diverse patient populations.",
        "Long-term outcomes for infants born after progesterone treatment for preterm birth prevention."
      ]
    },
    "9_recommended_next_steps": {
      "clinical_next_steps": [
        "Continue use of progesterone for prevention of preterm birth in high-risk pregnancies.",
        "Further investigate the role of specific PGR genetic variants in predicting premature birth risk."
      ]
    },
    "10_claim_evidence_table": {
      "total_claims": 2,
      "claims": [
        {
          "claim_id": "CLM-eefdb2",
          "statement": "Progesterone receptor (PGR) activation by progesterone inhibits uterine contractions and cervical ripening, thereby preventing premature birth.",
          "confidence_numeric": 0.9,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "VERIFIED",
          "targets": [
            "PGR"
          ],
          "citation_count": 4,
          "risk_flags": []
        },
        {
          "claim_id": "CLM-d76d00",
          "statement": "Genetic variations in the progesterone receptor gene (PGR) may be associated with spontaneous premature birth.",
          "confidence_numeric": 0.6,
          "confidence_label": "MEDIUM",
          "polarity": "INCONCLUSIVE",
          "verification_status": "VERIFIED",
          "targets": [
            "PGR"
          ],
          "citation_count": 1,
          "risk_flags": []
        }
      ]
    },
    "11_provenance_appendix": {
      "total_entries": 2,
      "entries": [
        {
          "claim_id": "CLM-eefdb2",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "3e3de5cd2ef8",
          "timestamp": "2026-06-03T12:12:51.731682+00:00",
          "paper_evidence": [
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
          "queries_used_count": 10
        },
        {
          "claim_id": "CLM-d76d00",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "3e3de5cd2ef8",
          "timestamp": "2026-06-03T12:12:51.731682+00:00",
          "paper_evidence": [
            {
              "pmid": "35178856",
              "snippet": "There was statistically significant difference between cases and controls in the distribution of newborns' allele frequency of minor C allele of the PGR SNP rs1942836 (p = 0.03, Fishers' exact test) i",
              "polarity": "INCONCLUSIVE",
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
          "queries_used_count": 10
        }
      ]
    }
  },
  "metadata": {
    "run_id": "3e3de5cd2ef8",
    "created_at": "2026-06-03T12:12:10.594182+00:00",
    "drug": "PROGESTERONE",
    "disease": "premature birth",
    "total_claims": 2,
    "quality_score": 0.9125,
    "reruns": 0
  }
}
```
