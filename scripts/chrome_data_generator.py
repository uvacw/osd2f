"""Fake data factory for Chrome browsing history export data

Structure based on Chromium Version 88.0.4324.182.
(Only the urls table is created)
"""

import argparse
import datetime
import os
import random
import sqlite3

import faker

def generate(output_dir: str, overwrite: str, n_urls: int, show: bool):
    file_path = os.path.join(output_dir, "History")
    f = faker.Faker()
    
    if overwrite and os.path.exists(file_path):
        os.remove(file_path)

    conn = sqlite3.connect(file_path)
    create_table(conn)

    sec_passed = 0
    for i in range(0,n_urls):
        sec_passed += random.randint(0,1000) 
        add_data(conn, [f.url(),                          ## url
                        f.company(),                      ## title
                        random.randint(0,100),            ## visit_count
                        random.randint(0,100),            ## typed_count
                        increment_dateint(sec_passed)],   ## last_visit_time 
                        show)



def create_table(conn):
    c = conn.cursor()
    c.execute('select name from sqlite_master where name="urls"')
    if len(c.fetchall()) == 0:
        c.execute('''CREATE TABLE urls(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    url LONGVARCHAR,
                                    title LONGVARCHAR,
                                    visit_count INTEGER DEFAULT 0 NOT NULL,
                                    typed_count INTEGER DEFAULT 0 NOT NULL,
                                    last_visit_time INTEGER NOT NULL,
                                    hidden INTEGER DEFAULT 0 NOT NULL)''')
    else:
        c.execute('select id from urls')
        print('Table already exists (N = ', len(c.fetchall()),'), so data will now be appended')
        

def add_data(conn, l, show=False):
    sql = ''' INSERT INTO urls(url, title, visit_count, typed_count, last_visit_time)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, l)
    conn.commit()
    if show: view_row(conn, cur.lastrowid)

def view_row(conn, i):
    c = conn.cursor()
    c.execute('SELECT * FROM urls where id = ?', [i])
    for r in c.fetchall():
        print(r)

def increment_dateint(incr_sec):
    startdate = datetime.datetime(2020,1,1)
    epoch = datetime.datetime(1601,1,1)
    dt = startdate + datetime.timedelta(seconds=incr_sec)
    return (dt - epoch).total_seconds() * 1000

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Chrome history data export mock data generator "
        "this tool generate mock data to test import "
        "functionality of browser history files data exports. "
        "Note that not all types of exports are currently supported.",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="the directory in which to put generated data.",
        required=True,
    )
    parser.add_argument(
        "--overwrite",
        help="whether to overwrite the directory if it already exists. "
        "Removes *all* content before starting",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-n", "--n-urls", type=int, help="number of urls to generate", default=1000
    )
    parser.add_argument(
        "--show",
        help="If True, show each row created",
        default=False,
        action="store_true",
    )

    args = parser.parse_args()
    
    generate(args.output, args.overwrite, args.n_urls, args.show)