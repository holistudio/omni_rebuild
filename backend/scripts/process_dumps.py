import gzip
import json
import os
import sys

DUMPS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "dumps")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "books_corpus.json")

WORKS_DUMP = os.path.join(DUMPS_DIR, "ol_dump_works_latest.txt.gz")
AUTHORS_DUMP = os.path.join(DUMPS_DIR, "ol_dump_authors_latest.txt.gz")