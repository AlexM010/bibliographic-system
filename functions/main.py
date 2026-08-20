import json

from firebase_functions import https_fn
from firebase_admin import (
    initialize_app,
    auth,
    firestore,
)


# ============================================================
# FIREBASE INITIALIZATION
# ============================================================

initialize_app()


def get_db():
    return firestore.client()


# ============================================================
# HELPERS
# ============================================================

def json_response(
    data,
    status=200,
):
    return https_fn.Response(
        json.dumps(
            data,
            ensure_ascii=False,
        ),
        status=status,
        content_type="application/json",
    )


def get_authenticated_uid(
    req,
):

    authorization = req.headers.get(
        "Authorization"
    )

    if not authorization:
        raise ValueError(
            "Missing Authorization header."
        )

    if not authorization.startswith(
        "Bearer "
    ):
        raise ValueError(
            "Invalid Authorization header."
        )

    id_token = authorization.split(
        "Bearer ",
        1,
    )[1].strip()

    if not id_token:
        raise ValueError(
            "Missing Firebase ID token."
        )

    decoded_token = (
        auth.verify_id_token(
            id_token
        )
    )

    return decoded_token["uid"]


# ============================================================
# SAVE PUBLICATION
# ============================================================

@https_fn.on_request()
def save_publication(
    req: https_fn.Request,
) -> https_fn.Response:

    if req.method != "POST":

        return json_response(
            {
                "error":
                    "Method not allowed."
            },
            status=405,
        )

    try:

        # ----------------------------------------------------
        # AUTH
        # ----------------------------------------------------

        uid = get_authenticated_uid(
            req
        )

        # ----------------------------------------------------
        # BODY
        # ----------------------------------------------------

        data = (
            req.get_json(
                silent=True
            )
            or {}
        )

        publication = (
            data.get(
                "publication"
            )
        )

        if not isinstance(
            publication,
            dict,
        ):

            return json_response(
                {
                    "error":
                        "publication must be an object."
                },
                status=400,
            )

        publication_id = (
            publication.get(
                "id"
            )
        )

        if not publication_id:

            return json_response(
                {
                    "error":
                        "Publication ID is required."
                },
                status=400,
            )

        # ----------------------------------------------------
        # FIRESTORE
        # ----------------------------------------------------

        db = get_db()

        publication_ref = (
            db
            .collection("users")
            .document(uid)
            .collection("publications")
            .document(
                str(publication_id)
            )
        )

        publication_ref.set(
            publication
        )

        return json_response(
            {
                "success": True,
                "publication_id":
                    str(publication_id),
            }
        )

    except ValueError as error:

        return json_response(
            {
                "error":
                    str(error)
            },
            status=401,
        )

    except Exception as error:

        print(
            "save_publication error:",
            error,
        )

        return json_response(
            {
                "error":
                    str(error)
            },
            status=500,
        )


# ============================================================
# LIST PUBLICATIONS
# ============================================================

@https_fn.on_request()
def list_publications(
    req: https_fn.Request,
) -> https_fn.Response:

    if req.method != "GET":

        return json_response(
            {
                "error":
                    "Method not allowed."
            },
            status=405,
        )

    try:

        # ----------------------------------------------------
        # AUTH
        # ----------------------------------------------------

        uid = get_authenticated_uid(
            req
        )

        # ----------------------------------------------------
        # FIRESTORE
        # ----------------------------------------------------

        db = get_db()

        publications_ref = (
            db
            .collection("users")
            .document(uid)
            .collection("publications")
        )

        documents = (
            publications_ref.stream()
        )

        publications = []

        for document in documents:

            publication = (
                document.to_dict()
                or {}
            )

            # Compatibility with older documents
            # that do not contain their own ID.
            if not publication.get(
                "id"
            ):
                publication["id"] = (
                    document.id
                )

            publications.append(
                publication
            )

        # ----------------------------------------------------
        # SORT BY YEAR
        # ----------------------------------------------------

        def sort_year(
            publication,
        ):

            try:

                return int(
                    publication.get(
                        "year"
                    )
                    or 0
                )

            except (
                ValueError,
                TypeError,
            ):

                return 0

        publications.sort(
            key=sort_year,
            reverse=True,
        )

        return json_response(
            publications
        )

    except ValueError as error:

        return json_response(
            {
                "error":
                    str(error)
            },
            status=401,
        )

    except Exception as error:

        print(
            "list_publications error:",
            error,
        )

        return json_response(
            {
                "error":
                    str(error)
            },
            status=500,
        )


# ============================================================
# DELETE PUBLICATION
# ============================================================

@https_fn.on_request()
def delete_publication(
    req: https_fn.Request,
) -> https_fn.Response:

    if req.method != "DELETE":

        return json_response(
            {
                "error":
                    "Method not allowed."
            },
            status=405,
        )

    try:

        # ----------------------------------------------------
        # AUTH
        # ----------------------------------------------------

        uid = get_authenticated_uid(
            req
        )

        # ----------------------------------------------------
        # BODY
        # ----------------------------------------------------

        data = (
            req.get_json(
                silent=True
            )
            or {}
        )

        publication_id = (
            data.get(
                "publication_id"
            )
        )

        if not publication_id:

            return json_response(
                {
                    "error":
                        "publication_id is required."
                },
                status=400,
            )

        # ----------------------------------------------------
        # FIRESTORE
        # ----------------------------------------------------

        db = get_db()

        publication_ref = (
            db
            .collection("users")
            .document(uid)
            .collection("publications")
            .document(
                str(publication_id)
            )
        )

        publication_snapshot = (
            publication_ref.get()
        )

        if not publication_snapshot.exists:

            return json_response(
                {
                    "error":
                        "Publication not found."
                },
                status=404,
            )

        # ----------------------------------------------------
        # DELETE
        # ----------------------------------------------------

        publication_ref.delete()

        return json_response(
            {
                "success": True,
                "publication_id":
                    str(publication_id),
            }
        )

    except ValueError as error:

        return json_response(
            {
                "error":
                    str(error)
            },
            status=401,
        )

    except Exception as error:

        print(
            "delete_publication error:",
            error,
        )

        return json_response(
            {
                "error":
                    str(error)
            },
            status=500,
        )