


Bibliographic Collections
A desktop application for organizing, enriching, and managing academic publications.

This project was developed as part of a bachelor's thesis. Its main goal is to provide a simple interface where users can add publications, review their bibliographic metadata, enrich author and subject information using external authority services, and keep a personal bibliographic library.

Features
Add a publication from an APA-style citation

Extract bibliographic metadata from the citation

Retrieve and improve publication metadata using Crossref

Enrich author information with:

ORCID

VIAF

Add thematic annotations using Getty AAT

Store personal notes and tags for each publication

Link the full paper either:

from a local PDF file

through an online URL such as Google Drive, OneDrive, or a publisher page

View, edit, and delete saved publications

Search through the local publication library

Sign in with Google

Store user publications through Firebase Cloud Functions and Firestore

Technologies
The desktop client is written in Python using PySide6 for the graphical interface.

Main technologies and services used in the project:

Python

PySide6

Firebase Authentication

Firebase Cloud Functions

Cloud Firestore

Google OAuth

Crossref API

ORCID API

VIAF

Getty Art & Architecture Thesaurus (AAT)

Application Workflow
The main publication workflow is:

APA citation
     |
     v
APA Parser
     |
     v
Publication object
     |
     +----> Crossref metadata
     |
     +----> ORCID author enrichment
     |
     +----> VIAF author enrichment
     |
     +----> Getty AAT annotations
     |
     v
User review / editing
     |
     v
Storage Client
     |
     v
Firebase Cloud Function
     |
     v
Cloud Firestore
The desktop client does not access Firestore directly. Publication requests are sent to Firebase Cloud Functions together with the user's Firebase authentication token.

Project Structure
.
├── app.py
├── main_gui.py
├── architecture.txt
├── requirements.txt
│
├── auth/
│   └── firebase_auth.py
│
├── cloud/
│   └── storage_client.py
│
├── config/
│   └── settings.py
│
├── credentials/
│   └── google_oauth_client.json
│
├── data/
│   └── publications/
│
├── functions/
│   ├── main.py
│   └── requirements.txt
│
├── mappers/
│   └── crossref_mapper.py
│
├── models/
│   ├── annotation.py
│   ├── author.py
│   ├── candidates.py
│   └── publication.py
│
├── parsers/
│   └── apa_parser.py
│
├── serializers/
│   └── json_serializer.py
│
├── services/
│   ├── crossref_service.py
│   ├── enrichment_service.py
│   ├── getty_service.py
│   ├── orcid_service.py
│   ├── publication_service.py
│   └── viaf_service.py
│
├── tests/
│   ├── test_apa_parser.py
│   ├── test_crossref_mapper.py
│   └── test_publications.txt
│
└── ui/
    ├── login_window.py
    ├── main_window.py
    ├── theme.py
    │
    ├── dialogs/
    │   └── candidate_dialog.py
    │
    ├── pages/
    │   ├── edit_publication_page.py
    │   ├── new_publication_page.py
    │   ├── publications_page.py
    │   └── view_publication_page.py
    │
    └── widgets/
        ├── full_text_widget.py
        ├── publication_card.py
        └── user_profile.py
Main Components
main_gui.py
Main entry point for the desktop application. It starts the PySide6 application, displays the login window, and opens the main interface after authentication.

auth/
Handles Google sign-in and Firebase Authentication.

models/
Contains the main data structures used by the application, including publications, authors, annotations, and API search candidates.

parsers/
Contains the APA citation parser used to extract initial publication metadata from user input.

services/
Contains the application logic for communicating with external services such as Crossref, ORCID, VIAF, and Getty AAT.

mappers/
Converts external API responses into the application's internal data models.

cloud/
Contains the client used to communicate with the Firebase backend.

functions/
Contains the Firebase Cloud Functions used for authenticated publication storage and retrieval.

ui/
Contains the PySide6 interface, including the login window, main window, publication pages, dialogs, reusable widgets, and application theme.

Installation
1. Clone the repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
2. Create a virtual environment
Linux / macOS:

python3 -m venv .venv
source .venv/bin/activate
Windows:

py -m venv .venv
.\.venv\Scripts\activate
3. Install the required packages
pip install -r requirements.txt
The desktop client requires:

requests
PySide6
python-dotenv
google-auth-oauthlib
python-dotenv is the PyPI package name for the dotenv module, and google-auth-oauthlib provides the google_auth_oauthlib Python package.

A minimal requirements.txt can therefore contain:

requests
PySide6
python-dotenv
google-auth-oauthlib
The Firebase Cloud Functions have their own dependencies in:

functions/requirements.txt
Configuration
The application expects local configuration for Firebase, Google OAuth, and the backend endpoints.

Create a .env file in the project root with the configuration required by config/settings.py.

Example:

FIREBASE_API_KEY=
SAVE_PUBLICATION_URL=
LIST_PUBLICATIONS_URL=
DELETE_PUBLICATION_URL=
CROSSREF_EMAIL=
Google OAuth credentials are expected at:

credentials/google_oauth_client.json
These files should not be committed to a public repository.

A recommended .gitignore entry is:

.env
credentials/
.venv/
venv/
__pycache__/
*.pyc
data/publications/
Running the Application
Start the graphical application with:

python3 main_gui.py
On Windows:

python main_gui.py
The application opens the Google sign-in flow in the browser and returns to the desktop client after authentication.

Publication Data
Internally, publications are represented as structured data rather than as plain citation strings.

A publication may contain information such as:

{
  "title": "Example Publication",
  "year": 2026,
  "authors": [],
  "journal": "Example Journal",
  "volume": "1",
  "issue": "2",
  "pages": "1-10",
  "doi": "10.xxxx/example",
  "metadata_sources": ["crossref"],
  "annotations": [],
  "user_metadata": {
    "notes": "",
    "tags": []
  }
}
A reference to the full paper can also be stored without uploading the file itself:

{
  "full_text": {
    "type": "local",
    "location": "/home/user/papers/example.pdf"
  }
}
or:

{
  "full_text": {
    "type": "url",
    "location": "https://drive.google.com/..."
  }
}
External Services
Crossref
Used to retrieve structured bibliographic metadata, primarily through publication DOI information.

ORCID
Used to identify researchers and enrich author records with persistent researcher identifiers.

VIAF
Used as an authority source for author identification and alternative name forms.

Getty AAT
Used as a controlled vocabulary for thematic publication annotations.

Firebase Backend
The backend is implemented with Firebase Cloud Functions.

The general storage flow is:

Desktop Client
      |
      | HTTPS + Firebase ID token
      v
Cloud Function
      |
      | Verify authenticated user
      v
Cloud Firestore
Publications are stored separately for each authenticated user.

The Firestore structure follows the general form:

users/
  {uid}/
    publications/
      {publication_id}
Tests
Some project components include standalone tests.

Examples:

python3 tests/test_crossref_mapper.py
and:

python3 test_login.py
The exact tests that can be run depend on whether they require network access or authentication credentials.

Current Scope
The current version focuses on managing a personal publication library and enriching publication metadata.

The application does not upload or store full PDF files. It only stores a reference to a local file or an online location.

The project is intended as an academic prototype and as a basis for further work on bibliographic organization, controlled vocabularies, and publication management.

Thesis Project
This repository contains the implementation developed for a bachelor's thesis on the organization and annotation of academic publications.

The project explores how structured bibliographic metadata, authority identifiers, and controlled vocabularies can be combined in a practical desktop application while keeping the user involved in validating and selecting external metadata.