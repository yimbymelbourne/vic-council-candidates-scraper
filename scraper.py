import csv
from pprint import pprint
from datetime import datetime
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from scraper_mcc import parse_and_write_MCC
from utils import get_html, get_soup, get_email, get_phone

INDEX_URL = "https://www.vec.vic.gov.au/voting/2024-local-council-elections"


# Helpers
def setup_logging():
    logging.basicConfig(
        filename="scraper.log",
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    # Create a StreamHandler for console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )

    # Add the console handler to the root logger
    logging.getLogger().addHandler(console_handler)


def write_candidates_to_csv(all_data: list):
    with open(f"candidates-{datetime.now()}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "council",
                "ward",
                "candidate_name",
                "candidate_name_printable",
                "candidate_statement",
                "candidate_email",
                "candidate_phone",
                "candidate_party_best_guess",
            ]
        )
        for data in all_data:
            writer.writerow(
                [
                    data["council"],
                    data["ward"],
                    data["candidate_name"],
                    data["candidate_name_printable"],
                    data["candidate_statement"],
                    data["candidate_email"],
                    data["candidate_phone"],
                    data["candidate_party"],
                ]
            )


# Parsers
def parse_candidate_party(candidate_details: str) -> str:
    if "labor" in candidate_details:
        return "Labor"
    if "greens" in candidate_details:
        return "Greens"
    if "liberal" in candidate_details:
        return "Liberal"
    if "libertarian" in candidate_details:
        return "Libertarian"
    # Note: it would have been very funny to do a tonne of nested `if` statements for different brands of socialist but I have restrained myself (https://www.youtube.com/watch?v=iS-0Az7dgRY)
    if "socialist" in candidate_details:
        return "Socialist"

    return ""


def parse_candidate_details(columns: list) -> dict:
    candidate_name = columns[0].text.strip()
    candidate_name_printable = (
        candidate_name.split(", ")[1] + " " + candidate_name.split(", ")[0].title()
    )

    candidate_statement = columns[1].text.strip()

    contact_details = columns[2].text.strip()

    # Extract email and phone from contact details
    candidate_email = get_email(contact_details)
    candidate_phone = get_phone(contact_details)
    candidate_party = parse_candidate_party(contact_details)

    return {
        "candidate_name": candidate_name,
        "candidate_name_printable": candidate_name_printable,
        "candidate_email": candidate_email,
        "candidate_phone": candidate_phone,
        "candidate_party": candidate_party,
        "candidate_statement": candidate_statement,
    }


def parse_candidate_statements(statement_rows: list) -> list:
    statements = []
    for row in statement_rows:
        unformatted = row.find_all("td")[1].text.strip()
        formatted = (
            unformatted.replace("\n", " ")
            .replace("\r", " ")
            .replace("\t", " ")
            .replace("Candidate Statement", "")
        )
        if not formatted:
            formatted = "No statement available"
        statements.append(formatted)
    return statements


def parse_wards(soup: BeautifulSoup, council_name: str) -> list:
    wards = soup.find_all("h2", class_="h3")
    logging.info(f"-> Scraping {len(wards)} wards...")

    data = []

    for ward in wards:
        ward_name = ward.get("id")

        # Find the corresponding table for the ward
        table = soup.find("div", id=f'{ward_name.lower().replace(" ", "-")}')
        if table:
            statement_rows = table.find_all("tr", class_="candidate-row hidden")
            statements = parse_candidate_statements(statement_rows)
            if len(statements) == 0:
                # hacky but it works
                statements.extend(["No statement available"] * 5)

            rows = table.find_all("tr", class_="candidate-row")

            logging.info(
                f"   -> Scraping {round((len(rows)-2)/2)} candidates from {ward_name}..."
            )

            statement_counter = 0
            for row in rows:
                columns = row.find_all("td")

                if len(columns) == 3:
                    candidate_dict = parse_candidate_details(columns)

                    candidate_dict = {
                        "council": council_name,
                        "ward": ward_name,
                        "candidate_name": candidate_dict["candidate_name"],
                        "candidate_name_printable": candidate_dict[
                            "candidate_name_printable"
                        ],
                        "candidate_statement": (
                            statements[statement_counter]
                            if candidate_dict["candidate_statement"]
                            == "See questionnaire response"
                            else candidate_dict["candidate_statement"]
                        ),
                        "candidate_email": candidate_dict["candidate_email"],
                        "candidate_phone": candidate_dict["candidate_phone"],
                        "candidate_party": candidate_dict["candidate_party"],
                    }

                    if (
                        candidate_dict["candidate_statement"]
                        != "See questionnaire response"
                    ):
                        statement_counter += 1

                    data.append(candidate_dict)

    return data


def parse_council(council_link: str) -> list:
    html = get_html(council_link)
    soup = get_soup(html)
    soup = soup.find("main")
    council_name = soup.find("h1").text.split(" election")[0]
    logging.info(f"Scraping {council_name}...")

    council_data = parse_wards(soup, council_name)

    return council_data


# Getters
def get_all_council_links(index_url: str) -> list:
    html = get_html(index_url)
    soup = get_soup(html)
    soup = soup.find("main")
    links = []
    for a in soup.find_all("a", href=True):
        # ignore irrelevant links
        if "/voting/2024-local-council-elections/" not in a["href"]:
            continue
        link = a["href"]
        link = "https://www.vec.vic.gov.au" + link + "/nominations"
        links.append(link)
    return links


def main():
    council_links = get_all_council_links(INDEX_URL)

    all_data = []

    for link in council_links:
        if "melbourne-city-council" in link:
            parse_and_write_MCC(link)
            continue
        council_data = parse_council(link)
        all_data.extend(council_data)

    write_candidates_to_csv(all_data)


if __name__ == "__main__":
    setup_logging()

    main()
