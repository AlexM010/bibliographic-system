from config.settings import (
    CROSSREF_EMAIL,
)

from parsers.apa_parser import (
    ApaParseError,
    ApaParser,
)

from services.crossref_service import (
    CrossrefService,
)

from services.publication_service import (
    PublicationService,
)

from services.orcid_service import (
    OrcidService,
    OrcidServiceError,
)

from services.viaf_service import (
    ViafService,
    ViafServiceError,
)

from services.getty_service import (
    GettyService,
    GettyServiceError,
)

from services.enrichment_service import (
    EnrichmentService,
)

from serializers.json_serializer import (
    publication_to_json,
    save_publication_json,
)

from auth.firebase_auth import (
    FirebaseAuthService,
    FirebaseAuthError,
)

from cloud.storage_client import (
    StorageClient,
    StorageClientError,
)


def choose_candidate(
    candidates,
    formatter,
):
    if not candidates:
        print("No results found.")
        return None

    print()

    for index, candidate in enumerate(
        candidates,
        start=1,
    ):
        print(
            f"{index}. "
            f"{formatter(candidate)}"
        )

    print("0. None")

    while True:

        value = input(
            "\nSelect result: "
        ).strip()

        try:
            index = int(value)

        except ValueError:

            print(
                "Please enter a number."
            )

            continue

        if index == 0:
            return None

        if 1 <= index <= len(
            candidates
        ):
            return candidates[
                index - 1
            ]

        print(
            "Invalid selection."
        )


def build_services():

    apa_parser = ApaParser()

    crossref = CrossrefService(
        user_email=CROSSREF_EMAIL
    )

    publication_service = (
        PublicationService(
            apa_parser=apa_parser,
            crossref_service=crossref,
        )
    )

    # Public ORCID API
    # No access token required for now.
    orcid = OrcidService()

    viaf = ViafService()

    getty = GettyService()

    enrichment = EnrichmentService(
        orcid_service=orcid,
        viaf_service=viaf,
        getty_service=getty,
    )

    return (
        publication_service,
        enrichment,
    )


def login_user():

    print("\n")
    print("=" * 60)
    print("Google Login")
    print("=" * 60)

    auth_service = (
        FirebaseAuthService()
    )

    try:

        user = (
            auth_service.login()
        )

    except FirebaseAuthError as error:

        print(
            f"\nLogin failed: "
            f"{error}"
        )

        return None

    print(
        f"\nLogged in as: "
        f"{user.email}"
    )

    if user.display_name:

        print(
            f"Name: "
            f"{user.display_name}"
        )

    return user


def enrich_authors(
    publication,
    enrichment,
):

    for author in publication.authors:

        print("\n")
        print("=" * 60)

        print(
            f"Author: "
            f"{author.display_name}"
        )

        print("=" * 60)

        # ---------------------
        # ORCID
        # ---------------------

        if author.orcid_id:

            print(
                f"ORCID already available "
                f"from metadata: "
                f"{author.orcid_id}"
            )

        else:

            answer = input(
                "Search ORCID? [y/N]: "
            ).strip().lower()

            if answer == "y":

                try:

                    candidates = (
                        enrichment
                        .search_author_orcid(
                            author
                        )
                    )

                    selected = (
                        choose_candidate(
                            candidates,
                            lambda c: (
                                f"{c.display_name} "
                                f"[{c.orcid_id}] "
                                f"{', '.join(c.institutions[:3])}"
                            ),
                        )
                    )

                    if selected:

                        enrichment.enrich_author_with_orcid(
                            author,
                            selected,
                        )

                        print(
                            "ORCID selected: "
                            f"{selected.orcid_id}"
                        )

                except OrcidServiceError as error:

                    print(
                        f"ORCID error: "
                        f"{error}"
                    )

        # ---------------------
        # VIAF
        # ---------------------

        if author.viaf_id:

            print(
                f"VIAF already available: "
                f"{author.viaf_id}"
            )

        else:

            answer = input(
                "Search VIAF? [y/N]: "
            ).strip().lower()

            if answer == "y":

                try:

                    candidates = (
                        enrichment
                        .search_author_viaf(
                            author
                        )
                    )

                    selected = (
                        choose_candidate(
                            candidates,
                            lambda c: (
                                f"{c.display_name} "
                                f"[VIAF {c.viaf_id}]"
                            ),
                        )
                    )

                    if selected:

                        enrichment.enrich_author_with_viaf(
                            author,
                            selected,
                        )

                        print(
                            "VIAF selected: "
                            f"{selected.viaf_id}"
                        )

                except ViafServiceError as error:

                    print(
                        f"VIAF error: "
                        f"{error}"
                    )


def enrich_getty(
    publication,
    enrichment,
):

    print("\n")
    print("=" * 60)
    print("Getty AAT annotations")
    print("=" * 60)

    while True:

        query = input(
            "\nGetty search term "
            "(empty to finish): "
        ).strip()

        if not query:
            break

        try:

            candidates = (
                enrichment
                .search_getty_aat(
                    query
                )
            )

            selected = (
                choose_candidate(
                    candidates,
                    lambda c: (
                        f"{c.name} "
                        f"[{c.external_id}] "
                        f"score={c.score}"
                    ),
                )
            )

            if selected:

                enrichment.add_getty_annotation(
                    publication,
                    selected,
                )

                print(
                    "Added annotation: "
                    f"{selected.name}"
                )

        except GettyServiceError as error:

            print(
                f"Getty error: "
                f"{error}"
            )


def add_user_metadata(
    publication,
):

    print("\n")
    print("=" * 60)
    print("Extra information")
    print("=" * 60)

    notes = input(
        "Notes: "
    ).strip()

    tags_text = input(
        "Tags separated by comma: "
    ).strip()

    tags = [
        tag.strip()
        for tag in tags_text.split(",")
        if tag.strip()
    ]

    publication.user_metadata[
        "notes"
    ] = notes

    publication.user_metadata[
        "tags"
    ] = tags


def save_to_cloud(
    publication,
    user,
):

    print("\n")
    print("=" * 60)
    print("Cloud storage")
    print("=" * 60)

    answer = input(
        "Save publication to Firestore? [Y/n]: "
    ).strip().lower()

    if answer == "n":

        print(
            "Cloud save skipped."
        )

        return

    try:

        storage = StorageClient()

        publication_id = (
            storage.save_publication(
                publication,
                user.id_token,
            )
        )

        print(
            "\nPublication saved "
            "successfully."
        )

        print(
            f"Publication ID: "
            f"{publication_id}"
        )

    except StorageClientError as error:

        print(
            f"\nCloud save failed: "
            f"{error}"
        )


def export_json(
    publication,
):

    answer = input(
        "\nExport publication "
        "to local JSON? [y/N]: "
    ).strip().lower()

    if answer != "y":
        return

    file_path = (
        save_publication_json(
            publication
        )
    )

    print(
        f"JSON exported to: "
        f"{file_path}"
    )


def main():

    print(
        "Bibliographic Collection System"
    )

    print(
        "-------------------------------"
    )

    # =========================================
    # LOGIN
    # =========================================

    user = login_user()

    if not user:
        return

    # =========================================
    # SERVICES
    # =========================================

    (
        publication_service,
        enrichment,
    ) = build_services()

    # =========================================
    # APA INPUT
    # =========================================

    citation = input(
        "\nPaste APA citation:\n\n"
    )

    try:

        publication = (
            publication_service
            .create_from_apa(
                citation
            )
        )

    except ApaParseError as error:

        print(
            f"\nAPA parsing error: "
            f"{error}"
        )

        return

    # =========================================
    # INITIAL PUBLICATION
    # =========================================

    print(
        "\nInitial Publication:\n"
    )

    print(
        publication_to_json(
            publication
        )
    )

    # =========================================
    # AUTHOR ENRICHMENT
    # =========================================

    enrich_authors(
        publication,
        enrichment,
    )

    # =========================================
    # GETTY
    # =========================================

    enrich_getty(
        publication,
        enrichment,
    )

    # =========================================
    # USER METADATA
    # =========================================

    add_user_metadata(
        publication
    )

    # =========================================
    # FINAL RESULT
    # =========================================

    print(
        "\nFinal enriched publication:\n"
    )

    print(
        publication_to_json(
            publication
        )
    )

    # =========================================
    # FIREBASE STORAGE
    # =========================================

    save_to_cloud(
        publication,
        user,
    )

    # =========================================
    # OPTIONAL LOCAL EXPORT
    # =========================================

    export_json(
        publication
    )


if __name__ == "__main__":
    main()