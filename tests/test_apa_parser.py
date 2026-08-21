import unittest
from parsers.apa_parser import ApaParser

class TestApaParser(unittest.TestCase):

    # Create the parser used by the APA parsing test.
    def setUp(self):
        self.parser = ApaParser()

    # Check that a sample APA citation is parsed into the expected fields.
    def test_zabulis_publication(self):
        citation = 'Zabulis, X., Meghini, C., Partarakis, N., Beisswenger, C., Dubois, A., Fasciolo, M., & Kloster, A. (2020). Digitisation of Traditional Craft Processes. ACM Journal on Computing and Cultural Heritage, 13(2), 1–22. https://doi.org/10.1145/3384209'
        publication = self.parser.parse(citation)
        self.assertEqual(publication.title, 'Digitisation of Traditional Craft Processes')
        self.assertEqual(publication.year, 2020)
        self.assertEqual(publication.journal, 'ACM Journal on Computing and Cultural Heritage')
        self.assertEqual(publication.volume, '13')
        self.assertEqual(publication.issue, '2')
        self.assertEqual(publication.pages, '1-22')
        self.assertEqual(publication.doi, '10.1145/3384209')
        self.assertEqual(publication.authors[0].family_name, 'Zabulis')
        self.assertEqual(publication.authors[0].given_name, 'X.')
        self.assertEqual(publication.authors[1].family_name, 'Meghini')
        self.assertEqual(publication.authors[6].family_name, 'Kloster')
if __name__ == '__main__':
    unittest.main()
