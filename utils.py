import csv
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from datetime import datetime
import logging


def get_html(url):
    response = requests.get(url)
    return response.text


def get_soup(html):
    return BeautifulSoup(html, "html.parser")


def get_email(info: str) -> str:
    email = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", info)
    return email.group() if email else ""


def get_phone(info: str) -> str:
    phone = re.search(r"\d{4} \d{3} \d{3}", info)
    return phone.group() if phone else ""
