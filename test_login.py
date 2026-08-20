from auth.firebase_auth import (
    FirebaseAuthService,
    FirebaseAuthError,
)


def main():

    auth_service = (
        FirebaseAuthService()
    )

    try:
        user = auth_service.login()

    except FirebaseAuthError as error:

        print(
            "\nLogin failed:"
        )

        print(error)

        return

    print(
        "\nLogin successful!"
    )

    print(
        f"UID: {user.uid}"
    )

    print(
        f"Email: {user.email}"
    )

    print(
        f"Name: {user.display_name}"
    )

    print(
        f"Token expires in: "
        f"{user.expires_in} seconds"
    )


if __name__ == "__main__":
    main()