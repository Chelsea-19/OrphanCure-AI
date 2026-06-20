"""OpenTargets GraphQL service — preserved from app6.py with modularisation."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

import requests

from app.config.settings import Settings
from app.models.entities import EntityCandidate
from app.models.state import UnifiedRunState
from app.utils.helpers import rate_limit

logger = logging.getLogger(__name__)


class OpenTargetsService:
    """Query the OpenTargets Platform GraphQL API."""

    def __init__(self, settings: Settings):
        self._url = settings.api_opentargets

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_candidates(self, term: str, entity_type: str) -> List[EntityCandidate]:
        """Search OT for drug or disease candidates."""
        gql = """
        query Search($q: String!, $entities: [String!]) {
          search(queryString: $q, entityNames: $entities, page: {index: 0, size: 5}) {
            hits { id, name, score, entity }
          }
        }
        """
        try:
            resp = requests.post(
                self._url,
                json={"query": gql, "variables": {"q": term, "entities": [entity_type]}},
                timeout=10,
            )
            if resp.status_code == 200:
                hits = resp.json().get("data", {}).get("search", {}).get("hits", [])
                return [EntityCandidate(id=h["id"], name=h["name"], score=h["score"]) for h in hits]
        except Exception as exc:
            logger.error("OpenTargets search failed for '%s': %s", term, exc)
        return []

    # ------------------------------------------------------------------
    # Detail queries
    # ------------------------------------------------------------------

    def get_drug_details(self, drug_id: str) -> Dict:
        """Fetch mechanisms of action for a drug."""
        gql = """
        query Drug($id: String!) {
          drug(chemblId: $id) {
            name
            mechanismsOfAction { rows { targets { approvedSymbol } actionType } }
          }
        }
        """
        try:
            resp = requests.post(self._url, json={"query": gql, "variables": {"id": drug_id}}, timeout=15)
            if resp.ok:
                return resp.json().get("data", {}).get("drug", {})
        except Exception as exc:
            logger.error("Drug detail fetch failed for %s: %s", drug_id, exc)
        return {}

    def get_disease_details(self, disease_id: str) -> Dict:
        """Fetch associated targets for a disease."""
        gql = """
        query Disease($id: String!) {
          disease(efoId: $id) {
            name
            associatedTargets(page: {index: 0, size: 200}) {
              rows { target { approvedSymbol, approvedName }, score }
            }
          }
        }
        """
        try:
            resp = requests.post(self._url, json={"query": gql, "variables": {"id": disease_id}}, timeout=15)
            if resp.ok:
                return resp.json().get("data", {}).get("disease", {})
        except Exception as exc:
            logger.error("Disease detail fetch failed for %s: %s", disease_id, exc)
        return {}

    def get_disease_known_drugs(self, disease_id: str) -> List[Dict]:
        """Fetch known drugs associated with a disease from OpenTargets."""
        gql = """
        query DiseaseKnownDrugs($id: String!) {
          disease(efoId: $id) {
            knownDrugs(page: {index: 0, size: 50}) {
              rows {
                drug { id, name }
                mechanismOfAction
              }
            }
          }
        }
        """
        try:
            resp = requests.post(self._url, json={"query": gql, "variables": {"id": disease_id}}, timeout=15)
            if resp.ok:
                disease_data = resp.json().get("data", {}).get("disease", {})
                if disease_data and "knownDrugs" in disease_data:
                    return disease_data["knownDrugs"].get("rows", [])
        except Exception as exc:
            logger.error("Known drugs fetch failed for %s: %s", disease_id, exc)
        return []
