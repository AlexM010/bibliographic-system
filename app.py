from config.settings import CROSSREF_EMAIL
from parsers.apa_parser import ApaParseError, ApaParser
from services.crossref_service import CrossrefService
from services.publication_service import PublicationService
from services.orcid_service import OrcidService, OrcidServiceError
from services.viaf_service import ViafService, ViafServiceError
from services.getty_service import GettyService, GettyServiceError
from services.enrichment_service import EnrichmentService
from serializers.json_serializer import publication_to_json, save_publication_json
from auth.firebase_auth import FirebaseAuthService, FirebaseAuthError
from cloud.storage_client import StorageClient, StorageClientError

# Show the available candidates and let the user choose one.
def choose_candidate(candidates, formatter):
    if not candidates:
        print('No results found.')
        return None
    print()
    for index, candidate in enumerate(candidates, start=1):
        print(f'{index}. {formatter(candidate)}')
    print('0. None')
    while True:
        value = input('\nSelect result: ').strip()
        try:
            index = int(value)
        except ValueError:
            print('Please enter a number.')
            continue
        if index == 0:
            return None
        if 1 <= index <= len(candidates):
            return candidates[index - 1]
        print('Invalid selection.')

# Create the services used by the command-line workflow.
def build_services():
    apa_parser = ApaParser()
    crossref = CrossrefService(user_email=CROSSREF_EMAIL)
    publication_service = PublicationService(apa_parser=apa_parser, crossref_service=crossref)
    orcid = OrcidService()
    viaf = ViafService()
    getty = GettyService()
    enrichment = EnrichmentService(orcid_service=orcid, viaf_service=viaf, getty_service=getty)
    return (publication_service, enrichment)

# Sign in with Google and return the authenticated Firebase user.
def login_user():
    print('\n')
    print('=' * 60)
    print('Google Login')
    print('=' * 60)
    auth_service = FirebaseAuthService()
    try:
        user = auth_service.login()
    except FirebaseAuthError as error:
        print(f'\nLogin failed: {error}')
        return None
    print(f'\nLogged in as: {user.email}')
    if user.display_name:
        print(f'Name: {user.display_name}')
    return user

# Optionally enrich each author with ORCID and VIAF data.
def enrich_authors(publication, enrichment):
    for author in publication.authors:
        print('\n')
        print('=' * 60)
        print(f'Author: {author.display_name}')
        print('=' * 60)
        if author.orcid_id:
            print(f'ORCID already available from metadata: {author.orcid_id}')
        else:
            answer = input('Search ORCID? [y/N]: ').strip().lower()
            if answer == 'y':
                try:
                    candidates = enrichment.search_author_orcid(author)
                    selected = choose_candidate(candidates, lambda c: f"{c.display_name} [{c.orcid_id}] {', '.join(c.institutions[:3])}")
                    if selected:
                        enrichment.enrich_author_with_orcid(author, selected)
                        print(f'ORCID selected: {selected.orcid_id}')
                except OrcidServiceError as error:
                    print(f'ORCID error: {error}')
        if author.viaf_id:
            print(f'VIAF already available: {author.viaf_id}')
        else:
            answer = input('Search VIAF? [y/N]: ').strip().lower()
            if answer == 'y':
                try:
                    candidates = enrichment.search_author_viaf(author)
                    selected = choose_candidate(candidates, lambda c: f'{c.display_name} [VIAF {c.viaf_id}]')
                    if selected:
                        enrichment.enrich_author_with_viaf(author, selected)
                        print(f'VIAF selected: {selected.viaf_id}')
                except ViafServiceError as error:
                    print(f'VIAF error: {error}')

# Search Getty AAT and add the term selected by the user.
def enrich_getty(publication, enrichment):
    print('\n')
    print('=' * 60)
    print('Getty AAT annotations')
    print('=' * 60)
    while True:
        query = input('\nGetty search term (empty to finish): ').strip()
        if not query:
            break
        try:
            candidates = enrichment.search_getty_aat(query)
            selected = choose_candidate(candidates, lambda c: f'{c.name} [{c.external_id}] score={c.score}')
            if selected:
                enrichment.add_getty_annotation(publication, selected)
                print(f'Added annotation: {selected.name}')
        except GettyServiceError as error:
            print(f'Getty error: {error}')

# Read notes and tags and attach them to the publication.
def add_user_metadata(publication):
    print('\n')
    print('=' * 60)
    print('Extra information')
    print('=' * 60)
    notes = input('Notes: ').strip()
    tags_text = input('Tags separated by comma: ').strip()
    tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
    publication.user_metadata['notes'] = notes
    publication.user_metadata['tags'] = tags

# Save the publication through the authenticated storage client.
def save_to_cloud(publication, user):
    print('\n')
    print('=' * 60)
    print('Cloud storage')
    print('=' * 60)
    answer = input('Save publication to Firestore? [Y/n]: ').strip().lower()
    if answer == 'n':
        print('Cloud save skipped.')
        return
    try:
        storage = StorageClient()
        publication_id = storage.save_publication(publication, user.id_token)
        print('\nPublication saved successfully.')
        print(f'Publication ID: {publication_id}')
    except StorageClientError as error:
        print(f'\nCloud save failed: {error}')

# Optionally save a local JSON copy of the publication.
def export_json(publication):
    answer = input('\nExport publication to local JSON? [y/N]: ').strip().lower()
    if answer != 'y':
        return
    file_path = save_publication_json(publication)
    print(f'JSON exported to: {file_path}')

# Run the command-line publication workflow.
def main():
    print('Bibliographic Collection System')
    print('-------------------------------')
    user = login_user()
    if not user:
        return
    publication_service, enrichment = build_services()
    citation = input('\nPaste APA citation:\n\n')
    try:
        publication = publication_service.create_from_apa(citation)
    except ApaParseError as error:
        print(f'\nAPA parsing error: {error}')
        return
    print('\nInitial Publication:\n')
    print(publication_to_json(publication))
    enrich_authors(publication, enrichment)
    enrich_getty(publication, enrichment)
    add_user_metadata(publication)
    print('\nFinal enriched publication:\n')
    print(publication_to_json(publication))
    save_to_cloud(publication, user)
    export_json(publication)
if __name__ == '__main__':
    main()
