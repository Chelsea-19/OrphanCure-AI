# OrphanCure Full Pipeline Report: repodb_34cf4e0d850b0cdf

- Drug: Terbutaline
- Disease: Asthma attack
- Mode: full
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
      "summary": "Terbutaline, a beta-2 adrenergic receptor agonist, has a plausible mechanism for treating status asthmaticus by relaxing airway smooth muscle. Clinical literature indicates its use as a second-line therapy in pediatric status asthmaticus, though outcomes and comparisons with other agents are varied.",
      "evidence_counts": {
        "total_papers": 11,
        "supporting": 6,
        "contradicting": 0,
        "inconclusive": 5
      },
      "common_targets_count": 1
    },
    "2_normalized_hypothesis": {
      "statement": "Repurpose TERBUTALINE for Status Asthmaticus",
      "drug": {
        "id": "CHEMBL1760",
        "name": "TERBUTALINE",
        "aliases": [
          "Terbutaline sulfate",
          "Bricanyl",
          "Brethine",
          "Terbutaline hemisulfate",
          "Terbulin"
        ],
        "resolution_method": "auto"
      },
      "disease": {
        "id": "EFO_0008590",
        "name": "Status Asthmaticus",
        "aliases": [
          "Severe asthma attack",
          "Intractable asthma",
          "Prolonged asthma attack",
          "Asthma status",
          "Status asthmaticus"
        ],
        "resolution_method": "auto"
      }
    },
    "3_mechanistic_rationale": {
      "total_mechanisms": 1,
      "mechanisms": [
        {
          "target": "ADRB2",
          "drug_action": "AGONIST",
          "disease_score": 0.097,
          "pathway": "Terbutaline, a beta-2 adrenergic receptor agonist, relaxes airway smooth muscle by activating ADRB2, counteracting the bronchoconstriction characteristic of status asthmaticus."
        }
      ]
    },
    "4_target_overlap_summary": {
      "total_overlapping": 1,
      "top_targets": [
        {
          "symbol": "ADRB2",
          "name": "adrenoceptor beta 2",
          "drug_action": "AGONIST",
          "disease_association_score": 0.097
        }
      ]
    },
    "5_literature_evidence_summary": {
      "total_retrieved": 11,
      "polarity": {
        "supports": 6,
        "contradicts": 0,
        "inconclusive": 5
      },
      "support_ratio": "6 of 11 retrieved papers support the hypothesis",
      "queries_used": 11,
      "top_papers": [
        {
          "pmid": "32426910",
          "title": "Terbutaline and aminophylline as second-line therapies for status asthmaticus in the pediatric intensive care unit.",
          "year": "2020",
          "relevance_score": 8.0,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Title Match"
          ]
        },
        {
          "pmid": "28137226",
          "title": "Medications and Recent Patents for Status Asthmaticus in Children.",
          "year": "2017",
          "relevance_score": 7.5,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Clinical study"
          ]
        },
        {
          "pmid": "31948977",
          "title": "Volatile anaesthetic for treatment of respiratory failure from status asthmaticus requiring extracorporeal membrane oxygenation.",
          "year": "2020",
          "relevance_score": 6.0,
          "polarity": "SUPPORTS",
          "match_reasons": []
        },
        {
          "pmid": "40637351",
          "title": "Intravenous Bronchodilators in Pediatric Critical Asthma: A Systematic Review and Network Meta-Analysis.",
          "year": "2025",
          "relevance_score": 5.0,
          "polarity": "INCONCLUSIVE",
          "match_reasons": [
            "Clinical study",
            "Recent"
          ]
        },
        {
          "pmid": "37615529",
          "title": "Wide Institutional Variability in the Treatment of Pediatric Critical Asthma: A Multicenter Retrospective Study.",
          "year": "2024",
          "relevance_score": 5.0,
          "polarity": "SUPPORTS",
          "match_reasons": [
            "Recent"
          ]
        },
        {
          "pmid": "39348943",
          "title": "Pharmacological Management of Pediatric Critical Asthma.",
          "year": "2025",
          "relevance_score": 4.0,
          "polarity": "INCONCLUSIVE",
          "match_reasons": [
            "Recent"
          ]
        },
        {
          "pmid": "32974029",
          "title": "High-frequency oscillatory ventilation as a rescue for severe asthma crisis in a child.",
          "year": "2020",
          "relevance_score": 4.0,
          "polarity": "SUPPORTS",
          "match_reasons": []
        },
        {
          "pmid": "40323974",
          "title": "AARC and PALISI Clinical Practice Guideline: Pediatric Critical Asthma.",
          "year": "2025",
          "relevance_score": 3.5,
          "polarity": "INCONCLUSIVE",
          "match_reasons": [
            "Recent"
          ]
        },
        {
          "pmid": "28588119",
          "title": "High-Flow Nasal Cannula Utilization in Pediatric Critical Care.",
          "year": "2017",
          "relevance_score": 3.0,
          "polarity": "SUPPORTS",
          "match_reasons": []
        },
        {
          "pmid": "32461745",
          "title": "Escalation in Therapy Based on Intravenous Magnesium Sulfate Dosing in Pediatric Patients With Asthma Exacerbations.",
          "year": "2020",
          "relevance_score": 3.0,
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
      "overall": "Medium",
      "dimensions": {
        "mechanistic_strength": "High",
        "literature_strength": "Medium",
        "clinical_evidence": "Medium"
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
        "Terbutaline may be refractory in severe cases of status asthmaticus.",
        "Variability in institutional treatment protocols for status asthmaticus may impact terbutaline use and outcomes."
      ],
      "limitations": [
        "The available literature primarily focuses on pediatric patients.",
        "Many studies are retrospective or observational, limiting causal inference.",
        "The definition and management of 'status asthmaticus' can vary, affecting comparability of studies."
      ],
      "missing_data": [
        "Direct comparative efficacy studies of terbutaline versus other second-line therapies.",
        "Data on terbutaline's effectiveness in adult patients with status asthmaticus.",
        "Information on potential adverse effects of terbutaline in the context of status asthmaticus."
      ]
    },
    "9_recommended_next_steps": {
      "clinical_next_steps": [
        "Conduct prospective studies comparing terbutaline with other second-line agents for status asthmaticus.",
        "Investigate optimal dosing and administration routes for terbutaline in status asthmaticus.",
        "Evaluate the efficacy of terbutaline in different age groups and severity of status asthmaticus."
      ]
    },
    "10_claim_evidence_table": {
      "total_claims": 1,
      "claims": [
        {
          "claim_id": "CLM-54cc7a",
          "statement": "Terbutaline acts as a beta-2 adrenergic receptor agonist, leading to relaxation of airway smooth muscle, which is beneficial in counteracting bronchoconstriction in status asthmaticus.",
          "confidence_numeric": 0.8,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "VERIFIED",
          "targets": [
            "ADRB2"
          ],
          "citation_count": 3,
          "risk_flags": []
        }
      ]
    },
    "11_provenance_appendix": {
      "total_entries": 1,
      "entries": [
        {
          "claim_id": "CLM-54cc7a",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "da441ab7dc1d",
          "timestamp": "2026-06-03T14:14:50.714113+00:00",
          "paper_evidence": [
            {
              "pmid": "32426910",
              "snippet": "The purpose of this study was to assess outcomes of PICU patients receiving aminophylline versus terbutaline as second-tier therapies for status asthmaticus.",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            },
            {
              "pmid": "32974029",
              "snippet": "Despite treatment with intravenous methylprednisolone, continuous albuterol, terbutaline, aminophylline, and magnesium sulfate, she had persistent respiratory distress.",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            },
            {
              "pmid": "31948977",
              "snippet": "A 37-year-old male smoker with asthma presented with status asthmaticus refractory to terbutaline, intravenous magnesium, continuous bronchodilators, steroids, heliox and theophylline infusion.",
              "polarity": "SUPPORTS",
              "verification": "VERIFIED",
              "error": null
            }
          ],
          "mechanism_evidence": [
            {
              "target": "ADRB2",
              "action": "AGONIST"
            }
          ],
          "queries_used_count": 11
        }
      ]
    }
  },
  "metadata": {
    "run_id": "da441ab7dc1d",
    "created_at": "2026-06-03T14:14:29.306887+00:00",
    "drug": "TERBUTALINE",
    "disease": "Status Asthmaticus",
    "total_claims": 1,
    "quality_score": 0.9125,
    "reruns": 0
  }
}
```
