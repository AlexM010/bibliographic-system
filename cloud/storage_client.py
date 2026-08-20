import os

import requests

from dotenv import load_dotenv


load_dotenv()


class StorageClientError(
    Exception
):
    pass


class StorageClient:

    def __init__(self):

        self.save_publication_url = (
            os.getenv(
                "SAVE_PUBLICATION_URL"
            )
        )

        self.list_publications_url = (
            os.getenv(
                "LIST_PUBLICATIONS_URL"
            )
        )

        self.delete_publication_url = (
            os.getenv(
                "DELETE_PUBLICATION_URL"
            )
        )

    # ========================================================
    # HEADERS
    # ========================================================

    @staticmethod
    def _headers(
        id_token,
    ):

        if not id_token:
            raise StorageClientError(
                "Firebase ID token is missing."
            )

        return {
            "Authorization":
                f"Bearer {id_token}",

            "Content-Type":
                "application/json",
        }

    # ========================================================
    # SAVE PUBLICATION
    # ========================================================

    def save_publication(
        self,
        publication,
        id_token,
    ):

        if not self.save_publication_url:

            raise StorageClientError(
                "SAVE_PUBLICATION_URL "
                "is not configured."
            )

        # Accept both Publication
        # domain objects and dictionaries.
        if hasattr(
            publication,
            "to_dict",
        ):

            publication_data = (
                publication.to_dict()
            )

        elif isinstance(
            publication,
            dict,
        ):

            publication_data = (
                publication
            )

        else:

            raise StorageClientError(
                "Invalid publication object."
            )

        try:

            response = requests.post(
                self.save_publication_url,
                headers=self._headers(
                    id_token
                ),
                json={
                    "publication":
                        publication_data
                },
                timeout=30,
            )

        except requests.RequestException as error:

            raise StorageClientError(
                "Could not connect to "
                f"storage service: {error}"
            )

        return self._process_response(
            response
        )

    # ========================================================
    # LIST PUBLICATIONS
    # ========================================================

    def list_publications(
        self,
        id_token,
    ):

        if not self.list_publications_url:

            raise StorageClientError(
                "LIST_PUBLICATIONS_URL "
                "is not configured."
            )

        try:

            response = requests.get(
                self.list_publications_url,
                headers=self._headers(
                    id_token
                ),
                timeout=30,
            )

        except requests.RequestException as error:

            raise StorageClientError(
                "Could not connect to "
                f"storage service: {error}"
            )

        data = self._process_response(
            response
        )

        if not isinstance(
            data,
            list,
        ):

            raise StorageClientError(
                "Invalid publications response."
            )

        return data

    # ========================================================
    # DELETE PUBLICATION
    # ========================================================

    def delete_publication(
        self,
        publication_id,
        id_token,
    ):

        if not publication_id:

            raise StorageClientError(
                "Publication ID is required."
            )

        if not self.delete_publication_url:

            raise StorageClientError(
                "DELETE_PUBLICATION_URL "
                "is not configured."
            )

        try:

            response = requests.delete(
                self.delete_publication_url,
                headers=self._headers(
                    id_token
                ),
                json={
                    "publication_id":
                        publication_id
                },
                timeout=30,
            )

        except requests.RequestException as error:

            raise StorageClientError(
                "Could not connect to "
                f"storage service: {error}"
            )

        return self._process_response(
            response
        )

    # ========================================================
    # RESPONSE
    # ========================================================

    @staticmethod
    def _process_response(
        response,
    ):

        try:

            data = (
                response.json()
            )

        except ValueError:

            data = None

        if not response.ok:

            if isinstance(
                data,
                dict,
            ):

                message = (
                    data.get(
                        "error"
                    )
                    or
                    f"HTTP {response.status_code}"
                )

            else:

                message = (
                    f"HTTP {response.status_code}"
                )

            raise StorageClientError(
                message
            )

        return data