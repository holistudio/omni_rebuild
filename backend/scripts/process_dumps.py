import gzip
import json
import os
import sys
import time

DUMPS_DATE = "2026-02-28"

# assumes pwd = "./backend" NOT "./backend/scripts"
DUMPS_DIR = os.path.join("data", "dumps")
OUTPUT_PATH = os.path.join("data", "books_corpus.json")

WORKS_DUMP = os.path.join(DUMPS_DIR, f"ol_dump_works_{DUMPS_DATE}.txt.gz")
AUTHORS_DUMP = os.path.join(DUMPS_DIR, f"ol_dump_authors_{DUMPS_DATE}.txt.gz")

MAX_BOOKS = 10 # 50_000

def build_author_lookup() -> dict[str, str]:
    print(f"Processing authors from AUTHORS_DUMP...\n")
    start_time = time.time()
    if not os.path.exists(AUTHORS_DUMP):
        print(f".  ERROR: Open Library Authors dump not found at {AUTHORS_DUMP}")
        print("Make sure to download it first via: https://openlibrary.org/developers/dumps")
        sys.exit(1)
    
    authors = {}
    count = 0
    line_errors = 0
    record_errors = 0
    unknown_authors = 0

    with gzip.open(AUTHORS_DUMP, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            count += 1
            try:
                parts = line.strip().split("\t")
                if len(parts) < 5:
                    line_errors += 1
                    continue

                record_type = parts[0]
                key = parts[1]
                json_str = parts[4]

                if record_type != "/type/author":
                    print('record_type')
                    record_errors += 1
                    continue

                data = json.loads(json_str)
                name = data.get("name")
                if name:
                    authors[key] = name
                else:
                    unknown_authors += 1

            except (json.JSONDecodeError, IndexError):
                parse_errors += 1
                continue

            if count % 1_000_000 == 0:
                print(f".  ({(time.time()-start_time):.2f}) Processed {count:,} author records, {len(authors):,} names collected...")
                break

    print(f".  Done ({(time.time()-start_time):.2f}): {count:,} authors scanned")
    print(f".  {line_errors:,} txt line errors, {record_errors:,} record type errors, {parse_errors:,} JSON parsing errors, {unknown_authors:,} unknown authors found.")
    return authors

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