from auth.firebase_auth import (
    FirebaseAuthService,
)

from cloud.storage_client import (
    StorageClient,
)

from models.author import Author
from models.publication import Publication


def main():

    print(
        "Logging in..."
    )

    auth_service = (
        FirebaseAuthService()
    )

    user = auth_service.login()

    print(
        f"Logged in as: "
        f"{user.email}"
    )

    storage = StorageClient()

    publication = Publication(
        raw_citation=(
            "Test Firebase publication"
        ),

        title=(
            "My First Firebase Publication"
        ),

        year=2026,

        authors=[
            Author(
                family_name="Tester",
                given_name="Alex",
            )
        ],
    )

    print(
        "\nSaving publication..."
    )

    publication_id = (
        storage.save_publication(
            publication,
            user.id_token,
        )
    )

    print(
        f"Saved: {publication_id}"
    )

    print(
        "\nPublications:"
    )

    publications = (
        storage.list_publications(
            user.id_token
        )
    )

    for publication in publications:

        print(
            "-",
            publication.get("title"),
            publication.get("id"),
        )


if __name__ == "__main__":
    main()