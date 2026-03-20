import gzip
import json
import os
import sys

DUMPS_DATE = "2026-02-28"

# assumes pwd = "./backend" NOT "./backend/scripts"
DUMPS_DIR = os.path.join("data", "dumps")
OUTPUT_PATH = os.path.join("data", "books_corpus.json")

WORKS_DUMP = os.path.join(DUMPS_DIR, f"ol_dump_works_{DUMPS_DATE}.txt.gz")
AUTHORS_DUMP = os.path.join(DUMPS_DIR, f"ol_dump_authors_{DUMPS_DATE}.txt.gz")

MAX_BOOKS = 10 # 50_000

def build_author_lookup():
    print(f"Processing authors from AUTHORS_DUMP...\n")
    if not os.path.exists(AUTHORS_DUMP):
        print(f"ERROR: Open Library Authors dump not found at {AUTHORS_DUMP}")
        print("Make sure to download it first via: https://openlibrary.org/developers/dumps")
        sys.exit(1)
    
    authors = {}
    count = 0
    errors = 0

    with gzip.open(AUTHORS_DUMP, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            count += 1

            if count > 100:
                break
            try:
                parts = line.strip().split("\t")
                if len(parts) < 5:
                    errors += 1
                    continue

                print(parts)
            except (json.JSONDecodeError, IndexError):
                errors += 1
                continue
    print(f"  Done: {count:,} authors scanned, {errors:,} parsing errors found.")

def process_works() -> list[dict]:
    print(f"\nProcessing works from WORKS_DUMP...\n")
    if not os.path.exists(WORKS_DUMP):
        print(f"ERROR: Open Library Works dump not found at {WORKS_DUMP}")
        print(f"Make sure to download it first via: https://openlibrary.org/developers/dumps")
        sys.exit(1)
    
    corpus = []
    count = 0
    errors = 0

    # open works dump gz file in text mode with replacement characters
    with gzip.open(WORKS_DUMP, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            count += 1

            if count >= MAX_BOOKS:
                print(f"\n   Reached {MAX_BOOKS:,} book cap, stopping early")
                break

            try:
                parts = line.strip().split('\t')
                print(parts)
            except (json.JSONDecodeError, IndexError):
                errors += 1
                continue

    print(f"\n   Done: {count:,} books collected from {count:,} works records")
    print(f"\n   with {errors:,} parse errors found")
    return corpus

if __name__ == "__main__":
    build_author_lookup()
    process_works()