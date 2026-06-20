# OrphanCure Full Pipeline Report: repodb_34cf4e0d850b0cdf

- Drug: Terbutaline
- Disease: Asthma attack
- Mode: no_verifier
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
      "summary": "Terbutaline, a beta-2 adrenergic receptor agonist, has a plausible mechanism for treating status asthmaticus by relaxing airway smooth muscle. Clinical literature indicates its use as a second-line therapy in pediatric status asthmaticus, though outcomes vary and it has been used in refractory cases.",
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
          "Terbutaline"
        ],
        "resolution_method": "auto"
      },
      "disease": {
        "id": "EFO_0008590",
        "name": "Status Asthmaticus",
        "aliases": [
          "Severe Asthma Attack",
          "Prolonged Asthma Attack",
          "Intractable Asthma",
          "Asthma Status",
          "Status Asthmaticus Attack"
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
      "count": 1,
      "claims": [
        {
          "claim_id": "CTR-be528b",
          "statement": "Terbutaline was used in a case of status asthmaticus refractory to multiple treatments, including terbutaline itself, suggesting limitations in its efficacy in severe or refractory cases.",
          "evidence_count": 1
        }
      ]
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
            "reason": "2/2 claims have paper evidence"
          },
          "citation_validity": {
            "score": 1.0,
            "reason": "5 total citations"
          },
          "mechanistic_specificity": {
            "score": 0.5,
            "reason": "1/2 claims reference targets"
          },
          "contradiction_handling": {
            "score": 0.8,
            "reason": "Contradictory evidence discussed"
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
        "weak_dimensions": [],
        "rerun_targets": []
      }
    },
    "8_risk_flags_limitations": {
      "risk_flags": [
        "Tachycardia",
        "Tremor",
        "Hypokalemia",
        "Hyperglycemia"
      ],
      "limitations": [
        "The available literature primarily focuses on pediatric patients.",
        "Some studies are retrospective and may have inherent biases.",
        "The evidence for terbutaline's effectiveness is mixed, with some cases showing refractoriness."
      ],
      "missing_data": [
        "Direct comparative studies of terbutaline versus other second-line therapies for status asthmaticus.",
        "Data on terbutaline's efficacy in adult patients with status asthmaticus.",
        "Long-term outcomes associated with terbutaline use in status asthmaticus."
      ]
    },
    "9_recommended_next_steps": {
      "clinical_next_steps": [
        "Conduct prospective studies to evaluate the efficacy and safety of terbutaline as a second-line or adjunctive therapy for status asthmaticus.",
        "Investigate optimal dosing and administration routes for terbutaline in status asthmaticus.",
        "Compare terbutaline's effectiveness against other second-line agents in status asthmaticus."
      ]
    },
    "10_claim_evidence_table": {
      "total_claims": 2,
      "claims": [
        {
          "claim_id": "CLM-c7d9db",
          "statement": "Terbutaline's agonism of ADRB2 can lead to relaxation of airway smooth muscle, counteracting bronchoconstriction in status asthmaticus.",
          "confidence_numeric": 0.8,
          "confidence_label": "HIGH",
          "polarity": "INCONCLUSIVE",
          "verification_status": "UNVERIFIED",
          "targets": [
            "ADRB2"
          ],
          "citation_count": 4,
          "risk_flags": []
        },
        {
          "claim_id": "CTR-be528b",
          "statement": "Terbutaline was used in a case of status asthmaticus refractory to multiple treatments, including terbutaline itself, suggesting limitations in its efficacy in severe or refractory cases.",
          "confidence_numeric": 0.5,
          "confidence_label": "MEDIUM",
          "polarity": "CONTRADICTS",
          "verification_status": "UNVERIFIED",
          "targets": [],
          "citation_count": 1,
          "risk_flags": []
        }
      ]
    },
    "11_provenance_appendix": {
      "total_entries": 2,
      "entries": [
        {
          "claim_id": "CLM-c7d9db",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "01ce9da8cd19",
          "timestamp": "2026-06-03T14:35:55.527312+00:00",
          "paper_evidence": [
            {
              "pmid": "32426910",
              "snippet": "The purpose of this study was to assess outcomes of PICU patients receiving aminophylline versus terbutaline as second-tier therapies for status asthmaticus.",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            },
            {
              "pmid": "32974029",
              "snippet": "Despite treatment with intravenous methylprednisolone, continuous albuterol, terbutaline, aminophylline, and magnesium sulfate, she had persistent respiratory distress.",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            },
            {
              "pmid": "40637351",
              "snippet": "Adjunct intravenous (IV) bronchodilators are often used when initial management with systemic corticosteroids and inhaled short-acting beta agonists (SABA) fail to provide improvement in a patient's c",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
              "error": null
            },
            {
              "pmid": "39348943",
              "snippet": "If clinical symptoms do not improve, then pediatric practitioners often prescribe adjunctive medications, including inhaled anticholinergics, intravenous ketamine, intravenous magnesium, intravenous s",
              "polarity": "SUPPORTS",
              "verification": "UNVERIFIED",
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
        },
        {
          "claim_id": "CTR-be528b",
          "source_agent": "SynthesisCriticAgent",
          "source_run": "01ce9da8cd19",
          "timestamp": "2026-06-03T14:35:55.527312+00:00",
          "paper_evidence": [
            {
              "pmid": "31948977",
              "snippet": "A 37-year-old male smoker with asthma presented with status asthmaticus refractory to terbutaline, intravenous magnesium, continuous bronchodilators, steroids, heliox and theophylline infusion.",
              "polarity": "CONTRADICTS",
              "verification": "UNVERIFIED",
              "error": null
            }
          ],
          "mechanism_evidence": [],
          "queries_used_count": 0
        }
      ]
    }
  },
  "metadata": {
    "run_id": "01ce9da8cd19",
    "created_at": "2026-06-03T14:35:33.839560+00:00",
    "drug": "TERBUTALINE",
    "disease": "Status Asthmaticus",
    "total_claims": 2,
    "quality_score": 0.9125,
    "reruns": 0
  }
}
```
