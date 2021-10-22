import unittest
import requests


class ApiTestCase(unittest.TestCase):
    """Unit test for testing api provided by World Class Government."""

    def setUp(self) -> None:
        self.URL = "https://wcg-apis.herokuapp.com"
        # should be changed
        self.citizen_id = 1103703125435

    def test_get_successfully_user_info(self):
        """test if the endpoint can successfully send the right person's information."""
        endpoint = self.URL + f"/citizen/{self.citizen_id}"
        response = requests.get(endpoint)
        information = response.json()
        self.assertEqual(response.status_code, 200)

    def test_get_user_info(self):
        """test if the endpoint can send the right person's information."""
        endpoint = self.URL + f"/citizen/{self.citizen_id}"
        response = requests.get(endpoint)
        information = response.json()
        self.assertEqual("samutprakarn", information["address"])
