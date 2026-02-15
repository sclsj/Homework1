from datetime import datetime
from typing import Set

senators_to_sql = []
votes_to_sql = []
votes_cast_to_sql = []
from lxml import etree
from lxml.etree import ElementTree
from pathlib import Path

import mysql.connector

connection = mysql.connector.connect(user='root', host='localhost')

folder_path = Path("./xml")

xml_files = list(folder_path.glob("*.xml"))


def convertVoteCast(vote_cast):
    if vote_cast == 'Yea':
        return 'Y'

    if vote_cast == 'Nay':
        return 'N'

    return 'A'


def convertDate(date):
    date_split = date.split(',')
    day = date_split[0] + date_split[1]

    return datetime.strptime(day, '%B %d %Y').strftime('%Y-%m-%d')

def insertVoteCast(cursor, vote):
    cursor.execute("Insert into VOTECAST (MemberId, CongressNumber, SessionNumber, VoteNumber, VoteChar) values (%s, %s, %s, %s, %s)", vote)

def insertVote(cursor, vote):
    cursor.execute("Insert into VOTE (CongressNumber, SessionNumber, Year, Date, VoteNumber) values (%s, %s, %s, %s, %s)", vote)

def insertSenator(cursor, senator):
    # print(senator)
    cursor.execute("Insert into SENATOR (MemberId, FirstName, LastName, Party, State) values (%s, %s, %s, %s, %s)", senator)

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
    votes_to_sql.append(vote)
    senators = tree.xpath("//member")
    for senator in senators:
        if senator.find("lis_member_id").text not in senator_ids:
            senators_to_sql.append((senator.find("lis_member_id").text,
                                    senator.find("first_name").text,
                                    senator.find("last_name").text,
                                    senator.find("party").text,
                                    senator.find("state").text))
            senator_ids.add(senator.find("lis_member_id").text)
        votes_cast_to_sql.append((
            senator.find("lis_member_id").text, vote[0], vote[1], vote[4], convertVoteCast(senator.find("vote_cast").text)
        ))


cursor = connection.cursor()

with open('Schema.sql', 'r') as f:
    cursor.execute(f.read())

connection.commit()
cursor.close()

connection = mysql.connector.connect(user='root', host='localhost', database='Homework_1')
cursor = connection.cursor()

for senator in senators_to_sql:
    insertSenator(cursor, senator)
for vote in votes_to_sql:
    insertVote(cursor, vote)
for vote in votes_cast_to_sql:
    insertVoteCast(cursor, vote)
connection.commit()
cursor.close()