# SI 201 HW4 (Library Checkout System)
# Your name(s): Lucy Pike & Elli Hoke
# Your student id(s): 03123721 (Lucy) & 46546511 (Elli)
# Your email(s): lucypike@umich.edu & ehoke@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    listings = []                                                       # initializes an empty list called listings, which will be used to store the tuples of listing titles and listing ids that are extracted from the HTML file

    with open(html_path, "r", encoding="utf-8-sig") as f:               # opens and reads the HTML file 
        soup = BeautifulSoup(f, "html.parser")                          # creates a BeautifulSoup object to parse the HTML content and extract the DOM structure

    title_node = soup.select('[data-testid="listing-card-title"]')      # uses soup.select to find all elements with that attribute, which are the title elements for each listing on the search results page 

    for node in title_node:                                             # iterates through each title element found in the previous step
        title_text = node.get_text(strip=True)                          # extracts the text content of the title element, which is the listing title, and removes any leading or trailing whitespace using strip=True

        listing_id = None                                               # initializes a variable listing_id to None, which will be used to store the listing id once it is found
        element_id = node.get("id", "")                                 # retrieves the id attribute of the title element, which may contain the listing id in the format "title_<listing_id>"  
        if element_id.startswith("title_"):                             # checks if the id attribute starts with "title_", which indicates that it contains the listing id
            listing_id = element_id.split("title_", 1)[1]               # if the id attribute is in the correct format, it splits the string on "title_" and takes the second part (the listing id) and assigns it to the variable listing_id

        if not listing_id:                                              # if the listing_id was not found in the id attribute of the title element...
            parent = node                                               # ...it initializes a variable parent to the current title element, which will be used to traverse up the DOM tree to find the listing id in the href attribute of a parent <a> tag
            while parent is not None:                                   # continues to traverse up the DOM tree until it reaches the root (when parent becomes None)
                if parent.name == "a" and "/rooms/" in parent.get("href", ""):      # checks if the current parent element is an <a> tag and if its href attribute contains "/rooms/", which indicates that it contains the listing id in the URL 
                    href = parent.get("href", "")                                   # retrieves the href attribute of the <a> tag, which should contain the URL with the listing id
                    listing_id = href.split("/rooms/", 1)[1].split("?", 1)[0]       # if the href attribute is in the correct format, it splits the string on "/rooms/" and takes the second part, then further splits it on "?" to remove any query parameters, and takes the first part as the listing id, which is assigned to the variable listing_id
                    break                                               # breaks out of the loop once the listing id is found
                parent = parent.parent                                  # if the listing id is not found in the current parent element, it moves up to the next parent element and continues the search

        if listing_id:                                                  # if a listing id was successfully found through either method
            listings.append((title_text, listing_id))                   # it appends a tuple containing the listing title and listing id to the listings list

    return listings                                                     # returns the list of tuples containing listing titles and listing ids


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    html_file = f'html_files/listing_{listing_id}.html'  
    with open(html_file, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")
        
    policy_number = None

    policy_elm = soup.find(string=re.compile("Policy number"))
    if policy_elm:
        policy_text = policy_elm.get_text(strip=True)
        if "STR-" in policy_text:
            policy_number = policy_text.split("STR-")[1].split()[0]
            policy_number = "STR-" + policy_number
        elif "Pending" in policy_text:
            policy_number = "Pending"
        elif "Exempt" in policy_text: 
            policy_number = "Exempt"
    if policy_number is None:
        policy_number = "Exempt"

    if soup.find(string=re.compile("Superhost")):
        host_type = "Superhost"
    else:
        host_type = "regular"
    
    host_name = None
    host_elm = soup.find(string=re.gete.compile("Hosted by|Co-hosted by"))
    if host_elm:
        host_name = host_elm.get_text(strip=True)
        host_name = re.sub(r"Hosted by\s*|Co-hosted by\s*", "", host_name)
    if host_name is None:
        host_name = ""

    subtitle = ""
    soubtitle_elm = soup.find(string=re.compile(r"Private|Shared|Entire"))
    if soubtitle_elm:
        subtitle = soubtitle_elm.get_text(strip=True)
    if "Private" in subtitle:
        room_type = "Private Room"
    elif "Shared" in subtitle:
        room_type = "Shared Room"
    else:
        room_type = "Entire Room"

    location_rating = 0.0
    rating_elm = soup.find(string=re.compile(r"Location"))
    if rating_elm:
        parent = rating_elm.find_parent()
        if parent:
            rating_text = parent.get_text(strip=True)
            match = re.search(r"Location\s*([0-5]\.?[0-9]?)", rating_text)
            if match:
                location_rating = float(match.group(1)) 
    return {
        listing_id: {
            "policy_number": policy_number,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating      
        }
    }
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    database = []                                                   # creates an empty list called database, which will be used to store the tuples of listing info that are gathered from the HTML file and the individual listing detail files
    listings = load_listing_results(html_path)                      # calls the load_listing_results function with the provided html_path to get a list of tuples containing listing titles and listing ids, which is stored in the variable listings

    for listing_title, listing_id in listings:                      # iterates through each tuple of listing title and listing id in the listings list
        details = get_listing_details(listing_id)                   # calls the get_listing_details function with the current listing_id to get a dictionary containing the details of the listing, which is stored in the variable details
        listing_info = details.get(listing_id, {})                  # retrieves the dictionary of listing details for the current listing_id from the details dictionary, using an empty dictionary as a default value if the listing_id is not found, and stores it in the variable listing_info

        policy_number = listing_info.get("policy_number", "")       # retrieves the policy number from the listing_info dictionary, using an empty string as a default value if the key is not found, and stores it in the variable policy_number
        host_type = listing_info.get("host_type", "")               # retrieves the host type from the listing_info dictionary, using an empty string as a default value if the key is not found, and stores it in the variable host_type
        host_name = listing_info.get("host_name", "")               # retrieves the host name from the listing_info dictionary, using an empty string as a default value if the key is not found, and stores it in the variable host_name
        room_type = listing_info.get("room_type", "")               # retrieves the room type from the listing_info dictionary, using an empty string as a default value if the key is not found, and stores it in the variable room_type
        location_rating = listing_info.get("location_rating", 0.0)  # retrieves the location rating from the listing_info dictionary, using 0.0 as a default value if the key is not found, and stores it in the variable location_rating

        database.append((listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating))  # creates a tuple containing the listing title, listing id, policy number, host type, host name, room type, and location rating for the current listing and appends it to the database list

    return database                                                 # returns the list of tuples containing the listing information for all listings in the search results

def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    sorted_data = sorted(data, key=lambda row: row[6], reverse=True)        # sorts the input data (list of tuples) based on the value in the 7th position of each tuple (index 6, which corresponds to location_rating) in descending order, and stores the sorted list in the variable sorted_data

    headers = [                                                             # defines a list of column headers for the CSV file, which correspond to the elements in each tuple of the data list
        "listing_title",
        "listing_id",
        "policy_number",
        "host_type",
        "host_name",
        "room_type",
        "location_rating",
    ]

    with open(filename, "w", encoding="utf-8-sig", newline="") as csvfile:  # opens a new CSV file with the specified filename in write mode, using UTF-8 encoding to handle any special characters, and ensures that newlines are handled correctly across different operating systems by setting newline=""
        writer = csv.writer(csvfile)                                        # creates a CSV writer object that will be used to write data to the CSV file   
        writer.writerow(headers)                                            # writes the list of headers as the first row in the CSV file
        for row in sorted_data:                                             # iterates through each tuple in the sorted_data list, which contains the listing information sorted by location rating

            listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating = row            # unpacks the current tuple into individual variables for easier access to each piece of listing information
            writer.writerow([                                               # writes a new row to the CSV file for the current listing, containing the listing title, listing id, policy number, host type, host name, room type, and location rating
                listing_id,
                policy_number,
                host_type,
                host_name,
                room_type,
                "{:.1f}".format(location_rating) if isinstance(location_rating, (int, float)) else location_rating,     # formats the location rating to one decimal place if it is a number, otherwise it leaves it as is (in case it's not a valid number), and includes it in the row being written to the CSV file
            ])

def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    sums = {}                                    # creates a regular dictionary to store the total sum of location ratings for each room type
    counts = {}                                  # creates a regular dictionary to store the count of ratings for each room type
    
    for row in data:                             # iterates through each tuple in the input data list, which contains the listing info
        room_type = row[5]                       # retrieves the room type from the current tuple (index 5) and stores it in the variable room_type
        location_rating = row[6] 
        
        if location_rating != 0.0:
            if room_type not in sums:
                sums[room_type] = 0.0
                counts[room_type] = 0
            sums[room_type] += location_rating
            counts[room_type] += 1
    
    averages = {}
    for room_type in sums:
        if counts[room_type] > 0:
            averages[room_type] = sums[room_type] / counts[room_type]
    
    return averages

def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        self.assertEqual(len(self.listings), 18)                                        # Check that the number of listings extracted is 18

        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))     # Check that the first (title, id) tuple is ("Loft in Mission District", "1944564")

    def test_get_listing_details(self):
        details_467507 = get_listing_details("467507")["467507"]                            # checks that the details for listing id "467507" match the expected values for policy number, host type, room type, and location rating    
        self.assertEqual(details_467507.get("policy_number"), "STR-0005349")                # checks that the policy number for listing id "467507" is "STR-0005349" 

        details_1944564 = get_listing_details("1944564")["1944564"]                         # checks that the details for listing id "1944564" match the expected values for policy number, host type, room type, and location rating
        self.assertEqual(details_1944564.get("host_type"), "Superhost")                     # checks that the host type for listing id "1944564" is "Superhost"
        self.assertEqual(details_1944564.get("room_type"), "Entire Room")                   # checks that the room type for listing id "1944564" is "Entire Room"
        self.assertAlmostEqual(details_1944564.get("location_rating", 0.0), 4.9, places=1)  # checks that the location rating for listing id "1944564" is approximately 4.9, allowing for a small margin of error (up to 1 decimal place) due to potential variations in the HTML content or parsing process

    def test_create_listing_database(self):
        for row in self.detailed_data:
            self.assertEqual(len(row), 7)                # Check that each tuple has 7 elements

        self.assertEqual(                                # Check that the last tuple in the detailed_data list matches the expected values
            self.detailed_data[-1],
            (
                "Guest suite in Mission District",
                "467507",
                "STR-0005349",
                "Superhost",
                "Jennifer",
                "Entire Room",
                4.8,
            ),
        )

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")                          # defines the path for the output CSV file to be created in the same directory as the test file

        output_csv(self.detailed_data, out_path)                                    # calls the output_csv function with the detailed_data list and the defined output path to create a CSV file containing the listing information sorted by location rating 

        with open(out_path, "r", encoding="utf-8-sig", newline="") as csvfile:      # opens the created CSV file in read mode with UTF-8 encoding and proper newline handling to read its contents 
            reader = csv.reader(csvfile)                                            # creates a CSV reader object to read the contents of the CSV file
            rows = list(reader)                                                     # converts the reader object into a list of rows, where each row is a list of values corresponding to the columns in the CSV file

        self.assertGreater(len(rows), 1)                                            # checks that there is more than just the header row in the CSV file
        self.assertEqual(rows[1], ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"])  # checks that the first data row in the CSV file matches the expected values for the listing with the highest location rating

        os.remove(out_path)                                                         # removes the created CSV file after the test is complete to clean up the directory

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        pass


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)