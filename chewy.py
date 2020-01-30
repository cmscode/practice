"""
Class for fetching data from the Star wars API, write to csv, and post to httpbin
and who better to do it with than our boy Chewy???!!!

todo: debug (verbose output) swticher.

Other notes: yes, i still like my camelCase variables! :)
"""

import requests
import pickle
from os import path
import unittest


class Chewy:

    def __init__(self):
        self.rootApiUrl = "https://swapi.co/api/"
        self.people = []
        self.characters = []
        self.filename = "characters_final.csv"
        # for debugging: save trips to the api
        #pickle_in = open("people.pickle", "rb")
        #self.people = pickle.load(pickle_in)

    """
    run all operations
    """
    def run_all(self):
        self.get_all_people()
        self.populate_character_data()
        self.output_csv(self.by_height)
        self.make_post()

    def get_all_people(self):

        # debug
        print("fetching all people from api")

        initial_endpoint = self.rootApiUrl + "people"
        people = self.get_endpoint_data_json(initial_endpoint)
        self.add_people(people["results"])

        next = True
        while next:
            if people['next'] is not None:
                # for debug
                print("fetching next pageset @ %s" % people['next'])
                people = self.get_endpoint_data_json(people["next"])
                self.add_people(people["results"])
            else:
                next = False

        # debug
        print("fetch complete. total number of people is %s" % len(self.people))
        # save pickle file for debugging to avoid round trips to api
        # todo: put a switcher in here for debug mode if desired
        #pickle_out = open("people.pickle", "wb")
        #pickle.dump(self.people, pickle_out)

    """
    add people from a page request to the api to the list of all people
    """
    def add_people(self, person_list):
        for person in person_list:
            self.people.append(person)

    """
    retrieve endpoint data in json format
    """
    def get_endpoint_data_json(self, endpoint):
        resp = requests.get(endpoint)
        return resp.json()

    """
    write out a csv file
    todo: could put a boolean to just post data directly, instead of writing out file
    """
    def output_csv(self, data):
        header = "name,species,height,appearances\n"
        file_contents = header
        for person in data:
                # get species name
                person["species_name"] = self.getSpecies(person["species_url"])
                line = "%s,%s,%s,%s\n" % (person["name"], person["species_name"], person["height"], person["appearances"])
                file_contents += line

        # debug
        # print(file_contents)
        print("saving %s" % self.filename)

        file_out = open(self.filename, 'w')
        file_out.write(file_contents)
        file_out.close()

    """
    post the csv file to httpbin
    note: could put a check to make sure 
    """
    def make_post(self):
        # debug
        print("posting to httpbin!")
        # check if file is there first
        if path.exists(self.filename) is True:
            payload = open(self.filename, 'rb')
            r = requests.post("http://httpbin.org/post", data=payload)
            payload.close()
            status = r.status_code
            if status == 200:
                return 200
            else:
                return status
        else:
            # debug
            # print("file dne!")
            return False

    """
    gets species name for a character.
    """
    def getSpecies(self, url):
        if url == "unknown":
            return "unknown"
        else:
            # debug
            print("getting species data for %s" % url)
            species_data = self.get_endpoint_data_json(url)
            return species_data["name"]

    """
    iterate through the list of person data from api
    and create a new list of custom character dictionaries 
    for proper output to the csv file
    """
    def populate_character_data(self):
        # debug
        print("massaging data, sir!")

        for person in self.people:
            character = {}
            if len(person["species"]) != 0:
                character["species_url"] = person["species"][0]
            else:
                character["species_url"] = "unknown"
            character["name"] = person["name"]
            height = person["height"]
            # catch unknown height!
            if height == "unknown":
                height = 0.0
            # convert height to float for proper sorting
            character["height"] = float(height)
            character["appearances"] = len(person["films"])
            self.characters.append(character)

        sort_by_appearences = sorted(self.characters, key=lambda i: i['appearances'], reverse=True)
        # get top ten
        clipped = sort_by_appearences[0:10]
        self.by_height = sorted(clipped, key=lambda i: i['height'], reverse=True)


"""
unit tests for the Chewy class
objectives: make sure the api works before running your code!
"""


class TestChewy(unittest.TestCase):

    def setUp(self):
        self.chewy = Chewy()

    # test the api to see if its responding
    def test_api_ping(self):
        resp = requests.get((self.chewy.rootApiUrl + "people"))
        self.assertEqual(resp.status_code, 200)

    """
    test the get species endpoint. 
    """
    def test_get_species(self):
        url = self.chewy.rootApiUrl + "species/3"
        name = self.chewy.getSpecies(url)
        # debug
        #print(name)
        self.assertEqual(name, "Wookiee")

    """
    post a file to httpbin and make sure its recieved ok
    """
    def test_httpbin(self):
        status = self.chewy.make_post()
        self.assertEqual(status, 200)

    def test_httpbin_badfile(self):
        # set filename to dne
        self.chewy.filename = "dne"
        status = self.chewy.make_post()
        #print(status)
        self.assertEqual(status, False)


if __name__ == "__main__":

    theForce = Chewy()
    theForce.run_all()

    # test stuff
    # unittest.main()

