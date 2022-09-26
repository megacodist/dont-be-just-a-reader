"""This Python script reads US presidents names and other information
from Encyclopaedia Britannica and saves the scraped data to a database.
"""

from contextlib import closing
from pathlib import Path
import platform
from pprint import pprint
import sqlite3

from lxml import etree
from lxml.etree import _Element
from megacodist.console import WaitPromptingThrd
import requests
from threading import Event


_MODULE_DIR = Path(__file__).resolve().parent


def CreateDB() -> Path:
    """Creates presidents.sqlite database and returns its path."""
    dbfile = _MODULE_DIR / 'presidents.sqlite'
    if dbfile.exists():
        n = 1
        while True:
            nStr = str(n).rjust(3, '0')
            dbfile = _MODULE_DIR / f'presidents_{nStr}.sqlite'
            if not dbfile.exists():
                break
            n += 1
    conn = sqlite3.connect(dbfile)
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS Presidents (
        id INTEGER PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        birthplace VARCHAR(255),
        party VARCHAR(255),
        term VARCHAR(10) NOT NULL);
    '''
    cursor.execute(query)
    return dbfile


def CheckDB(dbfile: str | Path) -> bool:
    """Checks the SQLite database to have at least one table with
    the below structure:

    CREATE TABLE IF NOT EXISTS Presidents (
        id INTEGER PRIMARY KEY,
    
        name VARCHAR(255) NOT NULL,
    
        birthplace VARCHAR(255),
    
        party VARCHAR(255),
    
        term VARCHAR(10) NOT NULL);
    """
    conn = sqlite3.connect(dbfile)
    cursor = conn.cursor()
    # Checking the existence of 'Presidents' table...
    query = '''
    SELECT name
        FROM sqlite_master
        WHERE type='table';
    '''
    tableNames = cursor.execute(query).fetchall()
    tableNames = [
        result[0]
        for result in tableNames]
    try:
        tableNames.index('Presidents')
    except ValueError:
        return False
    # Checking columns...
    query = 'PRAGMA table_info(Presidents);'
    cols = cursor.execute(query).fetchall()
    if not (
            cols[0][1] == 'id'
            and cols[0][2] == 'INTEGER'
            and cols[0][5] == 1):
        return False
    if not (
            cols[1][1] == 'name'
            and cols[1][2] == 'VARCHAR(255)'
            and cols[1][3] == 1
            and cols[1][5] == 0):
        return False
    if not (
            cols[2][1] == 'birthplace'
            and cols[2][2] == 'VARCHAR(255)'
            and cols[2][3] == 0
            and cols[2][5] == 0):
        return False
    if not (
            cols[3][1] == 'party'
            and cols[3][2] == 'VARCHAR(255)'
            and cols[3][3] == 0
            and cols[3][5] == 0):
        return False
    if not (
            cols[4][1] == 'term'
            and cols[4][2] == 'VARCHAR(10)'
            and cols[4][3] == 1
            and cols[4][5] == 0):
        return False
    # No problem
    return True


def FindDB() -> Path:
    presDB = _MODULE_DIR / 'presidents.sqlite'
    if presDB.exists() and CheckDB(presDB):
        return presDB
    possibleDBs = _MODULE_DIR.glob('presidents_[0123456789].sqlite')
    for presDB in possibleDBs:
        if CheckDB(presDB):
            return presDB
    return CreateDB()


def GetPresidents() -> list[str, str, str, str]:
    PRES_URL = (
        r'https://www.britannica.com/place/United-States/Presidents-of-the-United-States')
    # Reading Python events page...
    pltfrm = platform.system_alias(
            platform.system(),
            platform.release(),
            platform.version())
    headers = {
        'User-Agent': (
            'Mozilla/5.0, '
            + f'({pltfrm}) '
            + (
                '(compatible; planets-crawler; '
                + '+https://github.com/megacodist/a-bit-more-of-an-interest)'))}
    req = requests.get(
        PRES_URL,
        headers=headers)
    html = req.text
    root: _Element = etree.HTML(html)
    table = root.xpath(
        r'//table[contains(caption, "Presidents of the United States")]')[0]
    data = [
        [
            [
                a
                for text_ in td.xpath(r'descendant-or-self::*/text()')
                if (a := text_.strip())
            ][0]
            for td in tr.xpath(r'td[position() > 1]')
        ]
        for tr in table.xpath(r'descendant::tbody/tr')]
    return data


if __name__ == '__main__':
    _DB = FindDB()
    finished = Event()
    waitingPrompt= WaitPromptingThrd(
        finished,
        waitMsg='Looking up')
    waitingPrompt.start()
    presInfos = GetPresidents()
    finished.set()
    waitingPrompt.join()
    pprint(presInfos)
    # Saving to the DB...
    with sqlite3.connect(_DB) as conn:
        with closing(conn.cursor()) as cursor:
            query = '''
            INSERT INTO Presidents VALUES
                (?, ?, ?, ?, ?)
            '''
            cursor.executemany(query, presInfos)
