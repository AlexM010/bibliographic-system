import requests

from models.candidates import (
    ViafCandidate,
)


class ViafServiceError(Exception):
    pass


class ViafService:

    BASE_URL = "https://viaf.org"

    def __init__(
        self,
        timeout: int = 8,
    ):
        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": (
                    "BibliographicCollectionSystem/"
                    "1.0"
                ),
            }
        )

    def search_person(
        self,
        name: str,
    ) -> list[ViafCandidate]:

        name = (name or "").strip()

        if not name:
            return []

        url = (
            f"{self.BASE_URL}"
            f"/viaf/AutoSuggest"
        )

        try:
            response = self.session.get(
                url,
                params={
                    "query": name
                },
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

        except requests.HTTPError as error:

            status_code = (
                error.response.status_code
                if error.response is not None
                else None
            )

            raise ViafServiceError(
                f"VIAF search failed "
                f"(HTTP {status_code})."
            ) from error

        except requests.RequestException as error:

            raise ViafServiceError(
                f"Could not connect to VIAF: "
                f"{error}"
            ) from error

        except ValueError as error:

            raise ViafServiceError(
                "VIAF returned invalid JSON."
            ) from error

        # VIAF μπορεί να επιστρέψει:
        # "result": null
        #
        # οπότε το μετατρέπουμε σε [].
        results = (
            data.get("result")
            or []
        )

        candidates = []

        for item in results:

            if not isinstance(item, dict):
                continue

            viaf_id = item.get(
                "viafid"
            )

            if not viaf_id:
                continue

            candidate = ViafCandidate(
                viaf_id=str(viaf_id),

                display_name=(
                    item.get("displayForm")
                    or item.get("term")
                    or ""
                ),

                term=item.get(
                    "term"
                ),

                name_type=item.get(
                    "nametype"
                ),

                lc=item.get(
                    "lc"
                ),

                score=(
                    str(item.get("score"))
                    if item.get("score") is not None
                    else None
                ),
            )

            candidates.append(
                candidate
            )

        return candidates

    def get_record(
        self,
        viaf_id: str,
    ) -> dict:

        # Canonical VIAF URI
        url = (
            f"{self.BASE_URL}"
            f"/viaf/{viaf_id}"
        )

        try:
            response = self.session.get(
                url,
                headers={
                    "Accept":
                        "application/json"
                },
                timeout=self.timeout,
            )

            response.raise_for_status()

            return response.json()

        except (
            requests.RequestException,
            ValueError,
        ) as error:
            raise ViafServiceError(
                f"VIAF record request "
                f"failed: {error}"
            ) from error

    def normalize_record(
        self,
        record: dict,
    ) -> dict:

        cluster = None

        for key, value in record.items():

            if key.endswith(
                "VIAFCluster"
            ):
                cluster = value
                break

        if not isinstance(
            cluster,
            dict,
        ):
            return {}

        result = {
            "viaf_id": None,
            "preferred_names": [],
            "source_identifiers": {},
        }

        viaf_id = self._get_ns_value(
            cluster,
            "viafID",
        )

        if viaf_id is not None:
            result["viaf_id"] = str(
                viaf_id
            )

        headings = self._get_ns_value(
            cluster,
            "mainHeadings",
        )

        if isinstance(headings, dict):

            heading_data = (
                self._get_ns_value(
                    headings,
                    "data",
                )
            )

            if isinstance(
                heading_data,
                dict,
            ):
                heading_data = [
                    heading_data
                ]

            if isinstance(
                heading_data,
                list,
            ):
                for item in heading_data:

                    if not isinstance(
                        item,
                        dict,
                    ):
                        continue

                    name = (
                        self._get_ns_value(
                            item,
                            "text",
                        )
                    )

                    if (
                        name
                        and name
                        not in result[
                            "preferred_names"
                        ]
                    ):
                        result[
                            "preferred_names"
                        ].append(name)

        sources = self._get_ns_value(
            cluster,
            "sources",
        )

        if isinstance(sources, dict):

            source_items = (
                self._get_ns_value(
                    sources,
                    "source",
                )
            )

            if isinstance(
                source_items,
                dict,
            ):
                source_items = [
                    source_items
                ]

            if isinstance(
                source_items,
                list,
            ):
                for item in source_items:

                    if not isinstance(
                        item,
                        dict,
                    ):
                        continue

                    content = item.get(
                        "content"
                    )

                    if not content:
                        continue

                    if "|" in content:

                        source_name, source_id = (
                            content.split(
                                "|",
                                1,
                            )
                        )

                        result[
                            "source_identifiers"
                        ][source_name] = (
                            source_id
                        )

        return result

    @staticmethod
    def _get_ns_value(
        data: dict,
        suffix: str,
    ):
        for key, value in data.items():

            if (
                key == suffix
                or
                key.endswith(
                    f":{suffix}"
                )
            ):
                return value

        return None