import os
import sqlite3
import urllib.request

import pandas as pd

BASE_URL = "https://huggingface.co/datasets/Mahadih534"
DATA_DIR = "data"
DB_DIR = "databases"

SOURCES = {
    "institutions": f"{BASE_URL}/Institutional-Information-of-Bangladesh/resolve/main/data.csv",
    "hospitals": f"{BASE_URL}/all-bangladeshi-hospitals/resolve/main/all-bangladesh-hosptals.csv",
    "restaurants": f"{BASE_URL}/Bangladeshi-Restaurant-Data/resolve/main/restaurants.csv",
}

SCHEMAS = {
    "institutions": {
        "rename": {
            "EIIN": "eiin",
            "INSTITUTE NAME": "name",
            "INSTITUTE_TYPE": "type",
            "EDUCATION_LEVEL": "education_level",
            "MANAGEMENT_TYPE": "management_type",
            "STUDENT_TYPE": "student_type",
            "AFFILIATION": "affiliation",
            "MPO_STATUS": "mpo_status",
            "DIVISION": "division",
            "DISTRICT": "district",
            "THANA": "thana",
            "UNION_NAME": "union_name",
            "MAUZA_NAME": "mauza",
            "AREA_STATUS": "area_status",
            "GEOGRPYCAL_STATUS": "geographical_status",
            "ADDRESS": "address",
            "POST": "post_office",
            "MOBILE": "mobile",
        },
        "types": {"eiin": "INTEGER PRIMARY KEY"},
    },
    "hospitals": {
        "rename": {
            "Id": "id",
            "Name": "name",
            "Name (Bangla)": "name_bangla",
            "Code": "code",
            "Agency": "agency",
            "Type": "type",
            "Private": "is_private",
            "Division": "division",
            "District": "district",
            "City Corporation": "city_corporation",
            "Upazila": "upazila",
            "Paurasava": "paurasava",
            "Union": "union_name",
        },
        "types": {"id": "INTEGER PRIMARY KEY", "code": "INTEGER", "is_private": "INTEGER"},
    },
    "restaurants": {
        "rename": {
            "place_id": "place_id",
            "name": "name",
            "address": "address",
            "rating": "rating",
            "number_of_reviews": "number_of_reviews",
            "affluence": "affluence",
            "latitude": "latitude",
            "longitude": "longitude",
        },
        "types": {
            "place_id": "TEXT PRIMARY KEY",
            "rating": "REAL",
            "number_of_reviews": "INTEGER",
            "affluence": "INTEGER",
            "latitude": "REAL",
            "longitude": "REAL",
        },
    },
}


def download(name, url):
    path = os.path.join(DATA_DIR, f"{name}.csv")
    if not os.path.exists(path):
        print(f"Downloading {name} ...")
        urllib.request.urlretrieve(url, path)
    return path


def clean(name, df):
    schema = SCHEMAS[name]
    df = df[list(schema["rename"])].rename(columns=schema["rename"])
    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
        df.loc[df[col] == "", col] = pd.NA
    if name == "institutions":
        for col in ["division", "district", "thana"]:
            df[col] = df[col].str.title()
        df = df.drop_duplicates("eiin")
    if name == "hospitals":
        df["code"] = df["code"].astype("Int64")
        df["city_corporation"] = df["city_corporation"].str.replace("Corperation", "Corporation")
    if name == "restaurants":
        df["number_of_reviews"] = df["number_of_reviews"].astype("Int64")
        df["affluence"] = df["affluence"].astype("Int64")
        df = df.drop_duplicates("place_id")
    return df


def write_db(name, df):
    path = os.path.join(DB_DIR, f"{name}.db")
    if os.path.exists(path):
        os.remove(path)
    types = SCHEMAS[name]["types"]
    columns = ", ".join(f'"{c}" {types.get(c, "TEXT")}' for c in df.columns)
    placeholders = ", ".join("?" for _ in df.columns)
    values = df.astype(object).where(df.notna(), None)
    rows = [tuple(v.item() if hasattr(v, "item") else v for v in row) for row in values.itertuples(index=False)]
    with sqlite3.connect(path) as conn:
        conn.execute(f"CREATE TABLE {name} ({columns})")
        conn.executemany(f"INSERT INTO {name} VALUES ({placeholders})", rows)
        for col in ("division", "district", "type"):
            if col in df.columns:
                conn.execute(f"CREATE INDEX idx_{name}_{col} ON {name}({col})")
    print(f"{path}: {len(df)} rows")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(DB_DIR, exist_ok=True)
    for name, url in SOURCES.items():
        df = pd.read_csv(download(name, url), low_memory=False)
        write_db(name, clean(name, df))


if __name__ == "__main__":
    main()
