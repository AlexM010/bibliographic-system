import os

from dotenv import load_dotenv


load_dotenv()


CROSSREF_EMAIL = os.getenv(
    "CROSSREF_EMAIL"
)

ORCID_ACCESS_TOKEN = os.getenv(
    "ORCID_ACCESS_TOKEN"
)

ORCID_CLIENT_ID = os.getenv(
    "ORCID_CLIENT_ID"
)

ORCID_CLIENT_SECRET = os.getenv(
    "ORCID_CLIENT_SECRET"
)