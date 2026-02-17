from datetime import datetime
from typing import Set
from lxml import etree
from lxml.etree import ElementTree
from pathlib import Path

senator_sql_list = []
vote_sql_list = []
votecast_sql_list = []

import mysql.connector
connection = mysql.connector.connect(user='root', host='localhost')

folder_path = Path("./xml")
xml_files = list(folder_path.glob("*.xml"))

def convertVoteCast(vote_cast):
    """
    Convert a roll-call vote label from the XML into a single-character code.

    The Senate vote XML use "Yea" and "Nay". Our SQL schema stores votes as a single character.
    Mapping:
        - "Yea" -> "Y"
        - "Nay" -> "N"
        - anything else -> "A"

    Args:
        vote_cast: The vote label string from the XML (e.g., "Yea", "Nay").

    Returns:
        A one-character vote code: "Y", "N", or "A".
    """
    if vote_cast == 'Yea':
        return 'Y'

    if vote_cast == 'Nay':
        return 'N'

    return 'A'


def convertDate(date):
    """
       Convert an XML date string into ISO-8601 format (YYYY-MM-DD).

       The vote XML date field is typically in a "Month day, year" format
       (e.g., "January 31, 2024"). This function normalizes it into ISO date string.

       Args:
           date: Date string from the XML (e.g., "January 31, 2024").

       Returns:
           ISO date string formatted as "YYYY-MM-DD".
    """
    date_split = date.split(',')
    day = date_split[0] + date_split[1]

    return datetime.strptime(day, '%B %d %Y').strftime('%Y-%m-%d')

senator_ids: Set[str] = set()
for xml_file in xml_files:
    with (open(xml_file, 'rb') as f):
        tree: ElementTree = etree.parse(f)
    root = tree.getroot()
    vote = (root.find("congress").text,
                         root.find("session").text,
                         root.find("congress_year").text,
            convertDate(root.find("vote_date").text),
                         root.find("vote_number").text
                         )
    vote_sql_list.append(vote)

    senators = tree.xpath("//member")
    for senator in senators:
        if senator.find("lis_member_id").text not in senator_ids:
            senator_sql_list.append((senator.find("lis_member_id").text,
                                     senator.find("first_name").text,
                                     senator.find("last_name").text,
                                     senator.find("party").text,
                                     senator.find("state").text))
            senator_ids.add(senator.find("lis_member_id").text)

        votecast_sql_list.append((
            senator.find("lis_member_id").text, vote[0], vote[1], vote[4], convertVoteCast(senator.find("vote_cast").text)
        ))


cursor = connection.cursor()

with open('Schema.sql', 'r') as f:
    cursor.execute(f.read())

connection.commit()  # somehow executing the file breaks the cursor, so have to restart here
cursor.close()

connection = mysql.connector.connect(user='root', host='localhost', database='Homework_1')
cursor = connection.cursor()

cursor.executemany("Insert into VOTE (CongressNumber, SessionNumber, Year, Date, VoteNumber) values (%s, %s, %s, %s, %s)", vote_sql_list)
cursor.executemany("Insert into SENATOR (MemberId, FirstName, LastName, Party, State) values (%s, %s, %s, %s, %s)", senator_sql_list)
cursor.executemany("Insert into VOTECAST (MemberId, CongressNumber, SessionNumber, VoteNumber, VoteChar)  values (%s, %s, %s, %s, %s)", votecast_sql_list)

connection.commit()
cursor.close()