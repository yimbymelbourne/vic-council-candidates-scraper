import csv
from datetime import datetime
from bs4 import BeautifulSoup
from datetime import datetime
import logging

from utils import get_html, get_soup, get_email, get_phone


def parse_and_write_MCC(link: str) -> dict:
    logging.info("Scraping MCC...")
    html = get_html(link)
    soup = get_soup(html)

    leadership_soup = soup.find("div", id="LeadershipContainer")
    councillor_soup = soup.find("div", id="CouncillorContainer")

    # leadership
    leadership_data = []
    leadership_table = leadership_soup.find("tbody")
    for row in leadership_table.find_all("tr", class_="candidate-row"):
        columns = row.find_all("td")
        if len(columns) >= 2:
            candidate_name = columns[0].text.split("Team: ")[0].strip()
            candidate_name_printable = (
                candidate_name.split(", ")[1]
                + " "
                + candidate_name.split(", ")[0].title()
            ).replace(",", "")

            candidate_info = columns[1].text.strip()

            phone = get_phone(candidate_info)
            email = get_email(candidate_info)
            contact = candidate_info.split("\n")[0]

            candidate_data = {
                "name": candidate_name,
                "name_printable": candidate_name_printable,
                "team": columns[0].text.split("Team: ")[1].strip(),
                "contact": contact,
                "phone": phone,
                "email": email,
            }

            leadership_data.append(candidate_data)

    with open(f"MCC-leadership-{datetime.now()}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "candidate_name",
                "candidate_name_printable",
                "candidate_team",
                "candidate_contact_name",
                "candidate_phone",
                "candidate_email",
            ]
        )
        for data in leadership_data:
            writer.writerow(
                [
                    data["name"],
                    data["name_printable"],
                    data["team"],
                    data["contact"],
                    data["phone"],
                    data["email"],
                ]
            )

    # councillors
    councillor_data = []
    councillor_table = councillor_soup.find("tbody")
    for row in councillor_table.find_all("tr"):
        columns = row.find_all("td")
        if len(columns) >= 3:
            candidate_name = columns[0].text.strip()
            candidate_name_printable = (
                candidate_name.split(", ")[1]
                + " "
                + candidate_name.split(", ")[0].title()
            ).replace(",", "")

            candidate_team = columns[1].text.strip()

            candidate_info = columns[2].text.strip()

            phone = get_phone(candidate_info)
            email = get_email(candidate_info)
            contact = candidate_info.split("\n")[0]

            candidate_data = {
                "name": candidate_name,
                "name_printable": candidate_name_printable,
                "team": candidate_team,
                "contact": contact,
                "phone": phone,
                "email": email,
            }

            councillor_data.append(candidate_data)

    with open(f"MCC-councillors-{datetime.now()}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "candidate_name",
                "candidate_name_printable",
                "candidate_team",
                "candidate_contact_name",
                "candidate_phone",
                "candidate_email",
            ]
        )
        for data in councillor_data:
            writer.writerow(
                [
                    data["name"],
                    data["name_printable"],
                    data["team"],
                    data["contact"],
                    data["phone"],
                    data["email"],
                ]
            )
    return None
