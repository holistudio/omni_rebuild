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
RATINGS_DUMP = os.path.join(DUMPS_DIR, f"ol_dump_ratings_{DUMPS_DATE}.txt.gz")

MAX_BOOKS = 50_000

# minimum character length of descriptions allowed in corpus
MIN_DESC_LENGTH = 20

def build_ratings_lookup() -> dict[str, float]:
    print("Processing ratings from RATINGS_DUMP...\n")
    start_time = time.time()
    ratings = {}
    count = 0
    with gzip.open(RATINGS_DUMP, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            count += 1
            parts = line.strip().split("\t")
 
            work_key = parts[0]
            rating = float(parts[2])
            if work_key in ratings:
                ratings[work_key].append(rating)
            else:
                ratings[work_key] = [rating]
            if count % 100_000 == 0:
                print(f".  ({(time.time()-start_time):.2f}) Processed {count:,} rating records)")
    final_count = 0
    final_ratings = {}
    for key in ratings:
        stars = ratings[key]
        if len(stars) > 1:
            avg_rating = sum(stars)/len(stars)
            if avg_rating >= 3.0:
                final_ratings[key]= avg_rating
                final_count += 1
    print(f"Total rating records: {count}")
    print(f"Final records: {final_count}")
    return final_ratings

def build_author_lookup() -> dict[str, str]:
    print("Processing authors from AUTHORS_DUMP...\n")
    start_time = time.time()
    if not os.path.exists(AUTHORS_DUMP):
        print(f".  ERROR: Open Library Authors dump not found at {AUTHORS_DUMP}")
        print("Make sure to download it first via: https://openlibrary.org/developers/dumps")
        sys.exit(1)
    
    authors = {}
    count = 0

    parse_errors = 0
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

    print(f".  Done ({(time.time()-start_time):.2f}): {count:,} authors scanned")
    print(f".  {line_errors:,} txt line errors, {record_errors:,} record type errors, {parse_errors:,} JSON parsing errors, {unknown_authors:,} unknown authors found.")
    return authors

def extract_description(data: dict) -> str | None:
    desc = data.get("description")
    if desc is None:
        return None
    if isinstance(desc, dict):
        desc = desc.get("value")
    if isinstance(desc, str) and len(desc) >= MIN_DESC_LENGTH:
        return desc
    return None

def extract_author_keys(data: dict) -> list[str]:
    author_keys = []
    for entry in data.get("authors", []):
        author_ref = entry.get("author")
        if isinstance(author_ref, dict):
            # assum standard nested dict format
            key = author_ref.get("key", "")
            if key:
                author_keys.append(key)
        # flat format fallback
        elif "key" in entry and entry.get("type", {}).get("key") != "/type/author_role":
            author_keys.append(entry["key"])
    return author_keys

def process_works(author_lookup: dict[str, str], rating_lookup: dict[str, float]) -> list[dict]:
    print("\nProcessing works from WORKS_DUMP...\n")
    start_time = time.time()
    if not os.path.exists(WORKS_DUMP):
        print(f"ERROR: Open Library Works dump not found at {WORKS_DUMP}")
        print("Make sure to download it first via: https://openlibrary.org/developers/dumps")
        sys.exit(1)
    
    corpus = []
    count = 0

    parse_errors = 0
    line_errors = 0
    record_errors = 0
    no_title = 0
    short_desc = 0


    # open works dump gz file in text mode with replacement characters
    with gzip.open(WORKS_DUMP, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            count += 1

            if len(corpus) >= MAX_BOOKS:
                print(f"\n.   Reached {MAX_BOOKS:,} book cap, stopping early")
                break

            try:
                parts = line.strip().split('\t')

                if len(parts) < 5:
                    line_errors += 1
                    continue

                record_type = parts[0]
                key = parts[1]
                json_str = parts[4]

                if record_type != "/type/work":
                    record_errors += 1
                    continue

                data = json.loads(json_str)

                title = data.get("title")
                if not title:
                    no_title += 1
                    continue

                description = extract_description(data)
                if not description:
                    short_desc += 1
                    continue

                avg_rating = rating_lookup.get(key)
                if not avg_rating:
                    continue

                subjects = data.get("subjects", [])
                if not isinstance(subjects, list):
                    if isinstance(subjects, str):
                        subjects = [subjects]
                    else:
                        print(f"\nWeird subject: {subjects}\n")
                        subjects = []
                subjects = [s for s in subjects if isinstance(s, str)][:10]

                author_keys = extract_author_keys(data)
                author_names = [
                    author_lookup.get(ak, "Unknown author")
                    for ak in author_keys
                ]
                author_str = ", ".join(author_names) if author_names else "Unknown author"

                genre = subjects[0] if subjects else "General"

                corpus.append({
                    "title": title,
                    "author": author_str,
                    "genre": genre,
                    "subjects": subjects,
                    "summary": description,
                    "open_library_key": key,
                })
            except (json.JSONDecodeError, IndexError):
                errors += 1
                continue
            if count % (MAX_BOOKS//10) == 0:
                print(f".  ({(time.time()-start_time):.2f}) Processed {count:,} records with {len(corpus):,} books added...")

    print(f"\n.   Done ({(time.time()-start_time):.2f}): {len(corpus):,} books collected from {count:,} works records")
    print(f".   {line_errors:,} txt line errors, {record_errors:,} record type errors, {parse_errors:,} JSON parsing errors, {no_title:,} no titles found, {short_desc:,} short/no descriptions found.\n")
    return corpus

if __name__ == "__main__":
    

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # build author lookup table
    author_lookup = build_author_lookup()

    # build ratings lookup table
    ratings = build_ratings_lookup()

    # create final works corpus with complete author names
    corpus = process_works(author_lookup, ratings)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(corpus, f, indent=2)
    print(f"\nCorpus saved to {OUTPUT_PATH}")
    print(f"  {len(corpus):,} books collected")

    if corpus:
        print("\nSample record:")
        print(json.dumps(corpus[0], indent=2))