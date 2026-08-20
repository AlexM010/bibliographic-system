from typing import Optional

import requests


class CrossrefService:

    BASE_URL = "https://api.crossref.org"

    def __init__(
        self,
        user_email: Optional[str] = None,
        timeout: int = 8,
    ):
        self.user_email = user_email
        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "BibliographicCollectionSystem/1.0"
                )
            }
        )

    def _base_params(self) -> dict:
        params = {}

        if self.user_email:
            params["mailto"] = (
                self.user_email
            )

        return params

    def get_by_doi(
        self,
        doi: str,
    ) -> Optional[dict]:

        if not doi:
            return None

        clean_doi = self._normalize_doi(doi)

        url = (
            f"{self.BASE_URL}"
            f"/works/{clean_doi}"
        )

        try:
            response = self.session.get(
                url,
                params=self._base_params(),
                timeout=self.timeout,
            )

            response.raise_for_status()

            body = response.json()

            return body.get("message")

        except (
            requests.RequestException,
            ValueError,
        ) as error:

            print(
                f"Crossref DOI request failed: "
                f"{error}"
            )

            return None

    def search_by_title(
        self,
        title: str,
        rows: int = 5,
    ) -> list[dict]:

        if not title:
            return []

        url = (
            f"{self.BASE_URL}/works"
        )

        params = self._base_params()

        params.update(
            {
                "query.title": title,
                "rows": rows,
            }
        )

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            body = response.json()

            message = body.get(
                "message",
                {}
            )

            return message.get(
                "items",
                []
            )

        except (
            requests.RequestException,
            ValueError,
        ) as error:

            print(
                f"Crossref title search failed: "
                f"{error}"
            )

            return []

    def _normalize_doi(
        self,
        doi: str,
    ) -> str:

        doi = doi.strip()

        prefixes = [
            "https://doi.org/",
            "http://doi.org/",
            "http://dx.doi.org/",
            "https://dx.doi.org/",
            "doi:",
        ]

        lower_doi = doi.lower()

        for prefix in prefixes:
            if lower_doi.startswith(
                prefix
            ):
                doi = doi[
                    len(prefix):
                ]

                break

        return doi.strip()