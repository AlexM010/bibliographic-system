import json

import requests

from models.candidates import (
    GettyCandidate,
)


class GettyServiceError(Exception):
    pass


class GettyService:

    RECONCILE_URL = (
        "https://services.getty.edu/"
        "vocab/reconcile/"
    )

    def __init__(
        self,
        timeout: int = 8,
    ):
        self.timeout = timeout
        self.session = requests.Session()

    def search_aat(
        self,
        query: str,
        limit: int = 20,
    ) -> list[GettyCandidate]:

        query = query.strip()

        if not query:
            return []

        payload = {
            "q0": {
                "query": query,
                "type": "/aat",
                "limit": limit,
            }
        }

        try:
            response = self.session.post(
                self.RECONCILE_URL,

                data={
                    "queries":
                        json.dumps(
                            payload
                        )
                },

                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

        except (
            requests.RequestException,
            ValueError,
        ) as error:
            raise GettyServiceError(
                f"Getty AAT search failed: "
                f"{error}"
            ) from error

        results = (
            data
            .get("q0", {})
            .get("result", [])
        )

        candidates = []

        for item in results:

            external_id = item.get(
                "id"
            )

            name = item.get(
                "name"
            )

            if (
                not external_id
                or not name
            ):
                continue

            candidate = GettyCandidate(
                external_id=external_id,
                name=name,

                score=item.get(
                    "score"
                ),

                match=bool(
                    item.get(
                        "match",
                        False,
                    )
                ),

                uri=(
                    "http://vocab.getty.edu/"
                    f"{external_id}"
                ),
            )

            candidates.append(
                candidate
            )

        return candidates