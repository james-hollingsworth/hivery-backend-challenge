"""
Unit test for challenge.management.commands.importdata
"""


from unittest import TestCase, mock
import challenge.management.commands.importdata as importdata


MOCK_COMPANY_FILE = [
    {
        "index": 0,
        "company": "NETBOOK"
    },
    {
        "index": 1,
        "company": "PERMADYNE"
    },
    {
        "index": 2,
        "company": "LINGOAGE"
    }
]

MOCK_PERSON_FILE = [
    {
        "index": 0,
        "name": "Jeff"
    },
    {
        "index": 1,
        "name": "Capes"
    }
]


class TestImportData(TestCase):

    @mock.patch('challenge.dataconversion.json_converter._get_person')
    @mock.patch('challenge.dataconversion.json_converter.create_person')
    @mock.patch('challenge.dataconversion.json_converter.associate_person_and_company')
    @mock.patch('challenge.dataconversion.json_converter.associate_person_with_friends')
    @mock.patch('challenge.dataconversion.json_converter.associate_person_and_tags')
    @mock.patch('challenge.dataconversion.json_converter.associate_person_and_food')
    def test_process_people(self, mock_associate_food, mock_associate_tags, mock_associate_friends,
                            mock_associate_company, mock_create_person, mock_get_person):
        mock_person = mock.Mock()
        mock_create_person.return_value = mock_person
        mock_get_person.return_value = mock_person

        c = importdata.Command()
        c._process_people(MOCK_PERSON_FILE)

        self.assertEqual([mock.call({'index': 0, 'name': 'Jeff'}),
                          mock.call({'index': 1, 'name': 'Capes'})], mock_create_person.call_args_list)

        self.assertEqual([mock.call(mock_person, {"index": 0, "name": "Jeff"}),
                          mock.call(mock_person, {"index": 1, "name": "Capes"})], mock_associate_tags.call_args_list)

        self.assertEqual([mock.call(mock_person, {"index": 0, "name": "Jeff"}),
                          mock.call(mock_person, {"index": 1, "name": "Capes"})], mock_associate_company.call_args_list)

        self.assertEqual([mock.call(mock_person, {"index": 0, "name": "Jeff"}),
                          mock.call(mock_person, {"index": 1, "name": "Capes"})], mock_associate_friends.call_args_list)

        self.assertEqual([mock.call(mock_person, {"index": 0, "name": "Jeff"}),
                          mock.call(mock_person, {"index": 1, "name": "Capes"})], mock_associate_food.call_args_list)

    @mock.patch('challenge.dataconversion.json_converter.create_company')
    def test_process_companies(self, mock_create_company):
        c = importdata.Command()
        c._process_companies(MOCK_COMPANY_FILE)

        self.assertEqual([mock.call({"index": 0, "company": "NETBOOK"}),
                          mock.call({"index": 1, "company": "PERMADYNE"}),
                          mock.call({"index": 2, "company": "LINGOAGE"})], mock_create_company.call_args_list)
