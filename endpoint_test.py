import unittest
import requests


class ApiTestCase(unittest.TestCase):
    """Unit test for testing api provided by World Class Government."""

    def setUp(self) -> None:
        self.URL = "https://wcg-apis.herokuapp.com"

        # create unreal citizen
        params = self.create_params_url("1105248761477", "Kel", "I.", "20/12/1995", "student", "somewhere")
        requests.post(self.URL + f"/registration?{params}")

    def get_citizen(self, citizen_id):
        """
        Send request to get the particular citizen information from the host.

        Args:
            citizen_id: id of the citizen to request for information

        Returns:
            response from the host
        """
        endpoint = self.URL + f"/citizen/{citizen_id}"
        return requests.get(endpoint)

    def create_params_url(self, citizen_id, name, surname, birth_date, occupation, address):
        """
        create citizen to be added to the database

        Args:
            citizen_id: the id of the citizen
            name: name of the citizen
            surname: surname of the citizen
            birth_date: citizen's birthday
            occupation: citizen's occupation
            address: address of citizen

        Returns:
            url containing parameters
        """
        return f"citizen_id={citizen_id}&name={name}&surname={surname}" \
               f"&birth_date={birth_date}&occupation={occupation}&address={address}"

    def test_add_citizen_with_invalid_citizen_id(self):
        """Try to add a citizen with invalid citizen id."""
        params = self.create_params_url("new citizen", "hi", "s", "1/2/2000", "fish", "water")
        response = requests.post(self.URL + f"/registration?{params}")
        self.assertEqual("registration failed: invalid citizen ID", response.json()["feedback"])

    def test_add_citizen_with_negative_citizen_id(self):
        """Try to add a citizen with negative citizen id."""
        params = self.create_params_url("-123456789012", "hi", "s", "1/2/2000", "fish", "water")
        response = requests.post(self.URL + f"/registration?{params}")
        self.assertEqual("registration failed: invalid citizen ID", response.json()["feedback"])

    def test_add_citizen_with_too_old_citizen(self):
        """Try to add a citizen who is 500 years old."""
        params = self.create_params_url("9878987898789", "im your ancestor", "s", "1/2/1490", "corpse", "grave")
        response = requests.post(self.URL + f"/registration?{params}")
        self.assertEqual("registration failed: invalid birth date", response.json()["feedback"])

    def test_register_with_name_as_script(self):
        """Try to register to be citizen with name as a script"""
        params = self.create_params_url("6677889090152", '<input type="text" id="fname" name="fname"><br><br>', "1",
                                        "1/2/2000", "fish", "water")
        response = requests.post(self.URL + f"/registration?{params}")
        # response should be like name should not be a script or something like invalid character
        self.assertEqual("reservation failed: name should not be a script", response.json()["feedback"])

    def test_register_with_sql_injection_drop_table(self):
        """Try to inject some sql script to drop table in their database."""
        params = self.create_params_url("1111111111111", "1; DROP TABLE citizen", "1; DROP TABLE citizen",
                                        "1/2/2000", "1; DROP TABLE citizen", "1; DROP TABLE citizen")
        response = requests.post(self.URL + f"/registration?{params}")
        # response should be like invalid character
        self.assertEqual("reservation failed: invalid character", response.json()["feedback"])

    def test_register_with_unicode_citizen_id(self):
        """Try to register using unicode included in citizen id."""
        params = self.create_params_url("\u00B212345678900\u00B2", "power of 2", "last", "1/2/2000", "math", "math")
        response = requests.post(self.URL + f"/registration?{params}")
        # response should be like unicode is not allowed
        self.assertEqual("reservation failed: unicode is not allowed for citizen id", response.json()["feedback"])

    def test_get_successfully_user_info(self):
        """Test if the endpoint can successfully send the right person's information."""
        response = self.get_citizen("1105248761477")
        self.assertEqual("1105248761477", response.json()["citizen-id"])

    def test_register_with_missing_name(self):
        """Try register to the server with name field missing"""
        params = self.create_params_url("0000000000000", "", "s", "1/2/1990", "student", "ground")
        response = requests.post(self.URL + f"/registration?{params}")
        self.assertEqual("registration failed: missing some attribute", response.json()["feedback"])

    def test_register_with_missing_id(self):
        """Try register to the server with citizen id field missing"""
        params = self.create_params_url("", "hello", "s", "1/2/1990", "student", "ground")
        response = requests.post(self.URL + f"/registration?{params}")
        self.assertEqual("registration failed: missing some attribute", response.json()["feedback"])

    def test_register_with_missing_surname(self):
        """Try register to the server with surname field missing"""
        params = self.create_params_url("0000000000000", "hello", "", "1/2/1990", "student", "ground")
        response = requests.post(self.URL + f"/registration?{params}")
        self.assertEqual("registration failed: missing some attribute", response.json()["feedback"])

    def test_register_with_missing_birthdate(self):
        """Try register to the server with birth date field missing"""
        params = self.create_params_url("0000000000000", "pqrst", "sk", "", "student", "ground")
        response = requests.post(self.URL + f"/registration?{params}")
        self.assertEqual("registration failed: missing some attribute", response.json()["feedback"])

    def test_register_with_missing_occupation(self):
        """Try register to the server with occupation field missing"""
        params = self.create_params_url("0000000000000", "pqrst", "sk", "1/2/1990", "", "ground")
        response = requests.post(self.URL + f"/registration?{params}")
        self.assertEqual("registration failed: missing some attribute", response.json()["feedback"])

    def test_register_with_missing_address(self):
        """Try register to the server with address field missing"""
        params = self.create_params_url("0000000000000", "pqrst", "sk", "1/2/1990", "student", "")
        response = requests.post(self.URL + f"/registration?{params}")
        self.assertEqual("registration failed: missing some attribute", response.json()["feedback"])

    def test_register_same_person(self):
        """Register a person who is already in the database"""
        params = self.create_params_url("1105248761477", "name", "surname", "1/2/1999", "nope", "space")
        response = requests.post(self.URL + f"/registration?{params}")
        self.assertEqual("registration failed: this person already registered", response.json()["feedback"])

    def test_get_user_info_with_negative_citizen_id(self):
        """Send request with invalid format citizen id type."""
        response = self.get_citizen(-123456789123)
        # the host should return anything except successfully executed
        # should be modified
        self.assertNotEqual(200, response.status_code)

    def test_delete_host_citizen_db(self):
        """Try to delete host citizen database."""
        # host should not let anyone delete their database
        requests.delete(self.URL + "/citizen")
        response = requests.get(self.URL + "/registration")
        self.assertNotEqual(0, len(response.json()))

    def test_successfully_make_reservation(self):
        """Test if the reservation can be made."""
        response = requests.post(self.URL + f"/reservation?citizen_id=1105248761477&site_name=hi&vaccine_name=Pfizer")
        self.assertEqual(200, response.status_code)
        # response = requests.get(self.URL + "/reservation")
        # self.assertEqual("1105248761477", response.json()["citizen-id"])

    def test_reserve_unknown_vaccine(self):
        """Test of the user can make the reservation for vaccine that is not provided."""
        response = requests.post(
            self.URL + f"/reservation?citizen_id=1105248761477&site_name=hi&vaccine_name=Something")
        self.assertEqual("report failed: invalid vaccine name", response.json()['feedback'])

    def test_same_person_two_reservation(self):
        """Same person can only have 1 reservation."""
        requests.post(self.URL + f"/reservation?citizen_id=1105248761477&site_name=hi&vaccine_name=Pfizer")
        response = requests.post(self.URL + f"/reservation?citizen_id=1105248761477&site_name=hi&vaccine_name=Pfizer")
        self.assertEqual("reservation failed: there is already a reservation for this citizen",
                         response.json()['feedback'])

    def test_cancel_reservation(self):
        """Try to cancel the reservation."""
        response = requests.delete(self.URL + "/reservation?citizen_id=1105248761477")
        self.assertEqual("cancel reservation successfully", response.json()["feedback"])

    def test_cancel_reservation_notexisted_person(self):
        """Cancel reservation for a person who is not register to the database."""
        response = requests.delete(self.URL + "/reservation?citizen_id=1105248761477")
        self.assertEqual("cancel reservation failed: invalid citizen ID", response.json()["feedback"])

    def test_cancel_reservation_string_citizen_id(self):
        """Cancel reservation using citizen id as a string."""
        response = requests.delete(self.URL + "/reservation?citizen_id=1a2b3c4d5e6f7")
        self.assertEqual("cancel reservation failed: invalid citizen ID", response.json()["feedback"])

    def test_cancel_reservation_without_making_any_reservation(self):
        """Try to cancel reservation but still not reserved."""
        # make sure that he is a citizen
        params = self.create_params_url("6677889090152", "hi", "1", "1/2/2000", "fish", "water")
        requests.post(self.URL + f"/registration?{params}")
        response = requests.delete(self.URL + "/reservation?citizen_id=6677889090152")
        self.assertEqual("cancel reservation failed: there is no reservation for this citizen",
                         response.json()["feedback"])

    def test_normal_report_taken_reserve(self):
        """Report the vaccine that has been taken."""
        requests.post(self.URL + f"/reservation?citizen_id=1105248761477&site_name=hi&vaccine_name=Pfizer")
        response = requests.post(self.URL + "/report_taken?citizen_id=1105248761477&vaccine_name=Pfizer&option=reserve")
        self.assertEqual("report success!", response.json()["feedback"])

    def test_normal_report_taken_walkin(self):
        """Report the vaccine that has been taken."""
        requests.post(self.URL + f"/reservation?citizen_id=1105248761477&site_name=hi&vaccine_name=Pfizer")
        response = requests.post(self.URL + "/report_taken?citizen_id=1105248761477&vaccine_name=Pfizer&option=walkin")
        self.assertEqual("report success!", response.json()["feedback"])

    def test_report_taken_invalid_option(self):
        """Try to report with invalid option."""
        requests.post(self.URL + f"/reservation?citizen_id=1105248761477&site_name=hi&vaccine_name=Pfizer")
        response = requests.post(self.URL + "/report_taken?citizen_id=1105248761477&vaccine_name=Pfizer&option=sth")
        self.assertEqual("report failed: invalid option", response.json()["feedback"])

    def test_normal_queue_report(self):
        """Post the queue report."""
        requests.post(self.URL + f"/reservation?citizen_id=1105248761477&site_name=hi&vaccine_name=Pfizer")
        response = requests.post(self.URL + "/queue_report?citizen_id=1105248761477&queue=2021-11-10%2010%3A00%3A00.00")
        self.assertEqual("report success!", response.json()["feedback"])

    def test_queue_report_invalid_date_format(self):
        """Post the queue report with invalid date format."""
        requests.post(self.URL + f"/reservation?citizen_id=1105248761477&site_name=hi&vaccine_name=Pfizer")
        response = requests.post(self.URL + "/queue_report?citizen_id=1105248761477&queue=10-11-2021 10:00:00.00")
        self.assertEqual("report failed: invalid queue datetime format", response.json()["feedback"])

    def test_queue_report_past_reserve(self):
        """Try to get a queue in the past."""
        requests.post(self.URL + f"/reservation?citizen_id=1105248761477&site_name=hi&vaccine_name=Pfizer")
        response = requests.post(self.URL + "/queue_report?citizen_id=1105248761477&queue=2021-10-10 10:00:00.00")
        self.assertEqual("report failed: can only reserve vaccine in the future", response.json()["feedback"])
