import unittest
from mappers.crossref_mapper import crossref_to_publication

class TestCrossrefMapper(unittest.TestCase):

    # Check that a Crossref record maps to the expected publication fields.
    def test_crossref_mapping(self):
        crossref_data = {'title': ['Digitisation of Traditional Craft Processes'], 'type': 'journal-article', 'published-print': {'date-parts': [[2020]]}, 'container-title': ['ACM Journal on Computing and Cultural Heritage'], 'volume': '13', 'issue': '2', 'page': '1-22', 'DOI': '10.1145/3384209', 'author': [{'given': 'Xenophon', 'family': 'Zabulis', 'ORCID': 'https://orcid.org/0000-0002-1520-4327'}, {'given': 'Carlo', 'family': 'Meghini'}]}
        publication = crossref_to_publication(crossref_data, raw_citation='Example APA citation')
        self.assertEqual(publication.year, 2020)
        self.assertEqual(publication.doi, '10.1145/3384209')
        self.assertEqual(publication.authors[0].family_name, 'Zabulis')
        self.assertEqual(publication.authors[0].given_name, 'Xenophon')
        self.assertEqual(publication.authors[0].orcid_id, '0000-0002-1520-4327')
        self.assertIn('crossref', publication.metadata_sources)
if __name__ == '__main__':
    unittest.main()
