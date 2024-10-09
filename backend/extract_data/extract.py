import re
import os
import csv
import functools
import logging
from typing import Optional, Tuple
from dataclasses import dataclass, asdict, fields
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Thread
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError, ChunkedEncodingError
from urllib3.exceptions import ProtocolError
from tenacity import (
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_incrementing,
    retry_if_exception_type,
)
import sqlite3
import pandas as pd

from utils import reformat_date, refresh_cookies, clean_status


def setup_logging():
    logging.basicConfig(
        filename="rera_parser.log",
        filemode="w",
        level=logging.INFO,
        format="[%(asctime)s] - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger("").addHandler(console)


setup_logging()
log = logging.getLogger("RERA_PARSER")

CSV_FILE = "karnataka_projects.csv"
DB_FILE = "../rera_projects.db"
TABLE_NAME = "karnataka_projects"


@dataclass
class ProjectDetails:
    project_id: str
    project_name: Optional[str] = None
    promoter_name: Optional[str] = None
    project_type: Optional[str] = None
    project_subtype: Optional[str] = None
    rera_acknowledgement_number: Optional[str] = None
    rera_registration_number: Optional[str] = None
    land_under_litigation: Optional[str] = None
    district: Optional[str] = None
    taluk: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    source_of_water: Optional[str] = None
    approving_authority: Optional[str] = None
    total_area_of_land: Optional[str] = None
    total_number_of_inventories: Optional[str] = None
    plan_approval_date: Optional[str] = None
    project_start_date: Optional[str] = None
    proposed_completion_date: Optional[str] = None
    total_project_cost: Optional[str] = None
    cost_of_land: Optional[str] = None
    estimated_cost_of_construction: Optional[str] = None
    complaints_on_this_promoter: Optional[str] = None
    complaints_on_this_project: Optional[str] = None
    rera_approval_status: Optional[str] = None


class ReraDataParser:
    BASE_URL = "https://rera.karnataka.gov.in"

    def __init__(self):
        self.session = requests.Session()
        self.session.request = functools.partial(self.session.request, timeout=30)
        self.session.headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": ReraDataParser.BASE_URL,
            "Referer": ReraDataParser.BASE_URL,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Connection": "keep-alive",
        }

    def get_cookies(self):
        """Sets or refreshes the cookies for the session by making a GET request to the base URL."""
        try:
            response = self.session.get(f"{self.BASE_URL}/home?language=en")
            response.raise_for_status()
            self.session.cookies.update(response.cookies)
            log.info("Successfully refreshed cookies.")
        except Exception as e:
            log.error(f"Failed to get cookies: {e}")

    @refresh_cookies
    @retry(
        before_sleep=before_sleep_log(log, logging.INFO),
        retry=retry_if_exception_type(
            (ConnectionError, ChunkedEncodingError, ProtocolError)
        ),
        stop=stop_after_attempt(3),
        wait=wait_incrementing(start=0.5, increment=0.25, max=1),
        reraise=True,
    )
    def _post_request(self, endpoint: str, data: dict) -> str:
        response = self.session.post(f"{self.BASE_URL}/{endpoint}", data=data)
        response.raise_for_status()
        return response.text

    def get_project_details(self, project_id: str) -> str:
        return self._post_request("projectDetails", {"action": project_id})

    def get_project_view_details(self, rera_reg_no: str) -> Optional[str]:
        data = {
            "project": "",
            "firm": "",
            "appNo": "",
            "regNo": rera_reg_no,
            "district": "0",
            "subdistrict": "0",
            "btn1": "Search",
        }
        try:
            return self._post_request("projectViewDetails", data)
        except Exception as e:
            log.error(f"Exception in projectViewDetails for {rera_reg_no}")
        return None

    @refresh_cookies
    def get_view_all_projects(self) -> Optional[str]:
        """Fetches the 'View All Projects' page content."""
        try:
            response = self.session.get(f"{self.BASE_URL}/viewAllProjects")
            return response.text
        except Exception as e:
            log.error(f"Failed to fetch 'View All Projects' page: {e}")
        return None

    def extract_value(self, soup: BeautifulSoup, label: str) -> Optional[str]:
        tags = soup.find_all(string=lambda text: label in text)
        for tag in tags:
            parent = tag.find_parent()
            if (
                parent
                and parent.name == "span"
                and "user_name" in parent.get("class", [])
            ):
                b_tag = parent.find_next("b")
                if b_tag and b_tag.text.strip():
                    return b_tag.text.strip()
            elif (
                parent
                and parent.name == "p"
                and "text-right" in parent.get("class", [])
            ):
                next_p = parent.find_next("p")
                if next_p:
                    return next_p.text.strip()
        return None

    def extract_data_from_project_view_details(
        self, html_content: str
    ) -> Optional[str]:
        fields_to_extract = "STATUS"
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            table = soup.find("table", {"id": "approvedTable"})
            if not table:
                return None
            header_row = table.find("thead").find("tr")
            headers = [th.text.strip().upper() for th in header_row.find_all("th")]
            status_index = headers.index(fields_to_extract)

            for row in table.find("tbody").find_all("tr"):
                columns = row.find_all("td")
                if len(columns) > status_index:
                    return columns[status_index].text.strip()
        except Exception as e:
            log.error(f"Unable to locate project status field. {e}")
        return None

    def extract_complains(self, soup: BeautifulSoup, label: str) -> Optional[str]:
        try:
            complaints_div = soup.find("div", {"id": "menu-complaints"})
            complaints_count_str = complaints_div.find(
                "a", string=lambda text: label in text
            )
            if complaints_count_str:
                return complaints_count_str.text.strip().split("(")[-1].strip(")")
            else:
                log.debug(f"No complaints for: {label}")
        except Exception as e:
            log.error(f"Unable to locate complaints. {e}")
        return None

    def extract_project_details(self, project_id: str) -> ProjectDetails:
        html_content = self.get_project_details(project_id)
        soup = BeautifulSoup(html_content, "html.parser")

        details = ProjectDetails(project_id=project_id)
        details.project_name = self.extract_value(soup, "Project Name")
        details.promoter_name = self.extract_value(soup, "Promoter Name")
        details.project_type = self.extract_value(soup, "Project Type")
        details.project_subtype = self.extract_value(soup, "Project Sub Type")
        details.rera_acknowledgement_number = self.extract_value(
            soup, "Acknowledgement Number"
        )
        details.rera_registration_number = self.extract_value(
            soup, "Registration Number"
        )
        details.land_under_litigation = self.extract_value(
            soup, "Is there any Litigations on Land/Property/Khatha"
        )
        details.district = self.extract_value(soup, "District")
        details.taluk = self.extract_value(soup, "Taluk")
        details.latitude = self.extract_value(soup, "Latitude")
        details.longitude = self.extract_value(soup, "Longitude")
        details.source_of_water = self.extract_value(soup, "Source of Water")
        details.approving_authority = self.extract_value(soup, "Approving Authority")
        details.total_area_of_land = self.extract_value(
            soup, "Total Area Of Land (Sq Mtr)"
        )
        details.total_number_of_inventories = self.extract_value(
            soup, "Total Number of Inventories/Flats/Sites/Plots/Villas"
        )
        details.plan_approval_date = reformat_date(
            self.extract_value(soup, "Plan Approval Date")
        )
        details.project_start_date = reformat_date(
            self.extract_value(soup, "Project Start Date")
        )
        details.proposed_completion_date = reformat_date(
            self.extract_value(soup, "Proposed Completion Date")
        )
        details.total_project_cost = self.extract_value(soup, "Total Project Cost")
        details.cost_of_land = self.extract_value(soup, "Cost of Land")
        details.estimated_cost_of_construction = self.extract_value(
            soup, "Estimated Cost of Construction"
        )
        details.complaints_on_this_promoter = self.extract_complains(
            soup, "Complaints On this Promoter"
        )
        details.complaints_on_this_project = self.extract_complains(
            soup, "Complaints On this Project"
        )

        if details.rera_registration_number:
            view_details_html = self.get_project_view_details(
                details.rera_registration_number
            )
            details.rera_approval_status = clean_status(
                self.extract_data_from_project_view_details(view_details_html)
            )

        return details

    def get_latest_approved_project(self) -> Optional[Tuple[str, str]]:
        try:
            # Get the view all projects page
            html_content = self.get_view_all_projects()

            # Find the first occurrence of 'PRM/KA/RERA/'
            match = re.search(r"PRM/KA/RERA/\d+/\d+/PR/\d{6}/\d{6}", html_content)
            if not match:
                log.error("No RERA registration number found")
                return None

            latest_rera_reg_no = match.group(0)
            log.info(f"Latest RERA registration number: {latest_rera_reg_no}")

            # Get project view details
            view_details_html = self.get_project_view_details(latest_rera_reg_no)
            if not view_details_html:
                log.error("Failed to get project view details")
                return None

            # Extract project ID
            soup = BeautifulSoup(view_details_html, "html.parser")
            view_details_link = soup.find("a", title="View Project Details")
            if not view_details_link:
                log.error("View Project Details link not found")
                return None

            project_id = view_details_link.get("id")
            if not project_id:
                log.error("Project ID not found in the link")
                return None

            log.info(f"Latest approved project ID: {project_id}")
            return project_id, latest_rera_reg_no

        except Exception as e:
            log.error(f"Error getting latest approved project ID: {e}")
            return None


def csv_writer(filename: str, queue: Queue):
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        fieldnames = [field.name for field in fields(ProjectDetails)]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()

        while True:
            data = queue.get()
            if data is None:
                break
            writer.writerow(asdict(data))
            file.flush()
            queue.task_done()

    queue.task_done()


failed_project_ids = list()


def process_project(parser: ReraDataParser, project_id: str, queue: Queue):
    try:
        project_details = parser.extract_project_details(project_id)
        queue.put(project_details)
        log.info(f"Project ;{project_id}; processed")
    except Exception as e:
        failed_project_ids.append(project_id)
        log.error(f"Project ;{project_id}; FAILED: {e}")


def run_concurrently(project_ids, filename=CSV_FILE):
    parser = ReraDataParser()
    queue = Queue()

    # Start the CSV writer thread
    writer_thread = Thread(target=csv_writer, args=(filename, queue), daemon=True)
    writer_thread.start()

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(process_project, parser, str(project_id), queue)
            for project_id in project_ids
        ]

        # Wait for all tasks to complete
        for future in futures:
            future.result()

    # Signal the CSV writer thread that we're done
    queue.put(None)
    # Wait for all tasks in the queue to be processed
    queue.join()
    # Wait for the writer thread to finish
    writer_thread.join()

    # Write failed project IDs to a file
    if len(failed_project_ids) > 0:
        with open("failed_project_ids.txt", "w") as f:
            f.writelines(failed_project_ids)


def retry_failed_projects():
    with open("failed_project_ids.txt") as f:
        project_ids = f.readlines()
    log.info(f"Retrying {len(project_ids)} failures")
    run_concurrently(project_ids)


def adhoc(project_id: int):
    parser = ReraDataParser()
    print(parser.extract_project_details(str(project_id)))


def csv_to_sqlite(csv_filename: str, db_filename: str):
    log.info(f"Converting {csv_filename} to SQLite database {db_filename}")

    df = pd.read_csv(csv_filename)
    conn = sqlite3.connect(db_filename)
    df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
    conn.close()

    log.info(f"Conversion complete. Data stored in table '{TABLE_NAME}' in {DB_FILE}")


def parse_rera_date(rera_ack_or_reg_no):
    date_str = rera_ack_or_reg_no.split("/")[-2]
    try:
        return pd.to_datetime(date_str, format="%d%m%y")
    except Exception as e:
        log.error(f"Error parsing date {date_str}: {e}")
        return pd.NaT


def filter_projects_to_update(df) -> Tuple[int, int]:
    parser = ReraDataParser()
    latest_project_id, latest_rera_reg_no = parser.get_latest_approved_project()
    latest_project_registration_date = parse_rera_date(latest_rera_reg_no)
    log.info(
        f"Latest approved project registration date: {latest_project_registration_date}"
    )

    # Data before this ID do not follow fixed date format
    df = df[df["project_id"].astype(int) >= 10000]

    # Filter unknown status projects
    unknown_df = df[
        (df["rera_approval_status"] == "UNKNOWN")
        & (df["rera_acknowledgement_number"].notna())
    ].copy()

    # Parse the date for unknown projects
    unknown_df["rera_acknowledgement_date"] = unknown_df[
        "rera_acknowledgement_number"
    ].apply(parse_rera_date)

    # Sort unknown projects by registration date
    unknown_df = unknown_df.sort_values("rera_acknowledgement_date")

    # Calculate the date 90 days before the latest approved project
    lookup_start_date = latest_project_registration_date - timedelta(days=90)
    log.info(f"Lookup start date: {lookup_start_date}")

    # Find the oldest project within 90 days of the latest approved project
    lookup_start_project = unknown_df[
        unknown_df["rera_acknowledgement_date"] >= lookup_start_date
    ]

    lookup_start_project_id = lookup_start_project["project_id"].iloc[0]
    log.info(f"Lookup start project ID: {lookup_start_project_id}")
    log.info(f"Lookup end project ID: {latest_project_id}")

    return lookup_start_project_id, latest_project_id


def update_csv_with_new_data():
    df = pd.read_csv(CSV_FILE)

    start_project_id, end_project_id = filter_projects_to_update(df)

    # Convert project_id to int for proper comparison
    df["project_id"] = df["project_id"].astype(int)

    # Filter projects to update
    projects_to_update = df[
        (df["project_id"].astype(int) >= int(start_project_id))
        & (df["project_id"].astype(int) <= int(end_project_id))
    ]
    project_ids = projects_to_update["project_id"].tolist()

    # Create a temporary file for new data
    temp_file = "_tmp.csv"

    log.info(f"Updating projects {project_ids[0]} to {project_ids[-1]}")
    # Run the concurrent update process
    run_concurrently(project_ids, temp_file)

    # Read the temporary file
    updated_df = pd.read_csv(temp_file)
    updated_df = updated_df.sort_values("project_id")

    # Update the original DataFrame with new data
    df.set_index("project_id", inplace=True)
    updated_df.set_index("project_id", inplace=True)

    df.update(updated_df)
    df.reset_index(inplace=True)

    # Save the updated DataFrame back to the original CSV file
    df.to_csv(CSV_FILE, index=False)

    log.info(f"CSV file updated successfully")

    # Remove the temporary file
    os.remove(temp_file)


if __name__ == "__main__":
    update_csv_with_new_data()
    csv_to_sqlite(CSV_FILE, DB_FILE)
    # adhoc(12460)
