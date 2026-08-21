import requests
from models.candidates import OrcidCandidate

class OrcidServiceError(Exception):
    pass

class OrcidService:
    BASE_URL = 'https://pub.orcid.org/v3.0'

    # Create a reusable HTTP session for ORCID requests.
    def __init__(self, timeout: int=8):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/vnd.orcid+json', 'User-Agent': 'BibliographicCollectionSystem/1.0'})

    # Search ORCID by author name and return normalized candidates.
    def search_person(self, given_names: str, family_name: str) -> list[OrcidCandidate]:
        given_names = (given_names or '').strip()
        family_name = (family_name or '').strip()
        if not family_name:
            return []
        if given_names and (not self._is_initials_only(given_names)):
            query = f'given-names:"{given_names}" AND family-name:"{family_name}"'
        else:
            # Initials such as 'X.' are too restrictive for ORCID, so search by surname only.
            query = f'family-name:"{family_name}"'
        print(f'ORCID query: {query}')
        url = f'{self.BASE_URL}/expanded-search/'
        try:
            response = self.session.get(url, params={'q': query}, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.HTTPError as error:
            status_code = error.response.status_code if error.response is not None else None
            raise OrcidServiceError(f'ORCID search failed (HTTP {status_code}).') from error
        except requests.RequestException as error:
            raise OrcidServiceError(f'Could not connect to ORCID: {error}') from error
        except ValueError as error:
            raise OrcidServiceError('ORCID returned invalid JSON.') from error
        return self._map_search_results(data)

    # Convert ORCID search results to candidate objects.
    def _map_search_results(self, data: dict) -> list[OrcidCandidate]:
        candidates = []
        # ORCID may return null instead of an empty list.
        results = data.get('expanded-result') or []
        for item in results:
            if not isinstance(item, dict):
                continue
            orcid_id = item.get('orcid-id')
            if not orcid_id:
                continue
            candidate = OrcidCandidate(orcid_id=orcid_id, given_names=item.get('given-names') or '', family_names=item.get('family-names') or '', credit_name=item.get('credit-name'), other_names=item.get('other-name') or [], institutions=item.get('institution-name') or [], emails=item.get('email') or [])
            candidates.append(candidate)
        return candidates

    # Fetch and normalize the full public ORCID record.
    def get_record(self, orcid_id: str) -> dict:
        orcid_id = self._normalize_orcid_id(orcid_id)
        if not orcid_id:
            raise OrcidServiceError('ORCID iD cannot be empty.')
        url = f'{self.BASE_URL}/{orcid_id}/record'
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as error:
            status_code = error.response.status_code if error.response is not None else None
            if status_code == 404:
                raise OrcidServiceError(f'ORCID record {orcid_id} was not found.') from error
            raise OrcidServiceError(f'ORCID record request failed (HTTP {status_code}).') from error
        except requests.RequestException as error:
            raise OrcidServiceError(f'Could not connect to ORCID: {error}') from error
        except ValueError as error:
            raise OrcidServiceError('ORCID returned invalid JSON.') from error

    # Keep the useful person, institution and identifier fields from an ORCID record.
    def normalize_record(self, record: dict) -> dict:
        result = {'orcid_id': None, 'given_names': None, 'family_name': None, 'other_names': [], 'biography': None, 'researcher_urls': [], 'country': None, 'external_identifiers': {}, 'institutions': []}
        identifier = record.get('orcid-identifier', {}) or {}
        result['orcid_id'] = identifier.get('path')
        person = record.get('person', {}) or {}
        name = person.get('name')
        if name:
            given_names = name.get('given-names')
            if given_names:
                result['given_names'] = given_names.get('value')
            family_name = name.get('family-name')
            if family_name:
                result['family_name'] = family_name.get('value')
        other_names = person.get('other-names', {}).get('other-name', []) or []
        for item in other_names:
            if not isinstance(item, dict):
                continue
            value = item.get('content')
            if value and value not in result['other_names']:
                result['other_names'].append(value)
        biography = person.get('biography')
        if biography:
            result['biography'] = biography.get('content')
        researcher_urls = person.get('researcher-urls', {}).get('researcher-url', []) or []
        for item in researcher_urls:
            if not isinstance(item, dict):
                continue
            url = item.get('url', {}).get('value')
            if not url:
                continue
            result['researcher_urls'].append({'name': item.get('url-name'), 'url': url})
        addresses = person.get('addresses', {}).get('address', []) or []
        if addresses:
            country = addresses[0].get('country', {}).get('value')
            result['country'] = country
        external_ids = person.get('external-identifiers', {}).get('external-identifier', []) or []
        for item in external_ids:
            if not isinstance(item, dict):
                continue
            id_type = item.get('external-id-type')
            id_value = item.get('external-id-value')
            if id_type and id_value:
                result['external_identifiers'][id_type] = id_value
        activities = record.get('activities-summary', {}) or {}
        employments = activities.get('employments', {}).get('affiliation-group', []) or []
        for group in employments:
            if not isinstance(group, dict):
                continue
            summaries = group.get('summaries', []) or []
            for summary in summaries:
                if not isinstance(summary, dict):
                    continue
                employment = summary.get('employment-summary', {}) or {}
                organization = employment.get('organization', {}) or {}
                organization_name = organization.get('name')
                if organization_name and organization_name not in result['institutions']:
                    result['institutions'].append(organization_name)
        return result

    @staticmethod
    # Check whether a given name contains only initials.
    def _is_initials_only(given_names: str) -> bool:
        """
        Επιστρέφει True όταν το given name
        φαίνεται να αποτελείται μόνο από initials.

        Examples:

        X.       -> True
        X. A.    -> True
        C.       -> True

        Ilia     -> False
        Xenophon -> False
        Carlo    -> False
        """
        if not given_names:
            return True
        cleaned = given_names.replace('.', '').replace(' ', '').replace('-', '').strip()
        if not cleaned:
            return True
        return cleaned.isalpha() and len(cleaned) <= 3

    @staticmethod
    # Remove the ORCID URL prefix from an identifier.
    def _normalize_orcid_id(orcid_id: str) -> str:
        if not orcid_id:
            return ''
        orcid_id = orcid_id.strip()
        prefixes = ['https://orcid.org/', 'http://orcid.org/']
        for prefix in prefixes:
            if orcid_id.startswith(prefix):
                orcid_id = orcid_id[len(prefix):]
                break
        return orcid_id.strip('/')
