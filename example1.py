import csv
import datetime as dt

### Parameters / Constant Values

DATE_FORMAT = "%d-%b-%y"

SHEET_1_LOC = "data/sheet1.csv"
SHEET_2_LOC = "data/sheet2.csv"
DATA_OUT = "data/out.csv"

EXCEPTIONS = ["", "1/1/9999"]

### Existing Keys

DOC_1 = "DOC"
DOC_2 = "DateCollected"
MMR_1 = "TissueID"
MMR_2 = "TissueID"

### New Keys

COL = "1_DateOfCollection"
ID = "0_PatientID"

### Utility Functions


def mmr_to_patient(mmr: str) -> str:
    """Extract middle 4 digits from MMR/TissueID"""
    return mmr[3:7]


def read_spreadsheet(file: str) -> list[dict]:
    """Read spreadsheet from given file path and convert to list of objects"""

    # Create empty list to store output
    data = []

    # Open spreadsheet file on location
    with open(file, encoding="cp1252") as csvfile:
        # Create reading facility (Object)
        reader = csv.DictReader(csvfile)

        # For each row on sheet
        for row in reader:
            # Convert MMR to friendly ID
            row[ID] = mmr_to_patient(row.get(MMR_1) or row.get(MMR_2) or "")

            # Convert string to date
            if not DOC_1 in row and not DOC_2 in row:
                row[COL] = None
            else:
                value = row.get(DOC_1) or row.get(DOC_2) or ""

                row[COL] = (
                    dt.datetime.strptime(value, DATE_FORMAT)
                    if value not in EXCEPTIONS
                    else None
                )

            # Add row object to list
            data.append(row)

    # Output rows of data
    return data


def write_spreadsheet(file: str, data: list[dict]):
    """Write spreadsheet"""
    headers = set()
    for row in data:
        headers.update(row.keys())

    headers = list(headers)
    headers.sort()

    with open(file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for row in data:
            writer.writerow(row)


def count_values(data: list[str]) -> dict[str, int]:
    """Convert list of values into map of items to count"""
    counts = {}
    for value in data:
        if value in counts:
            counts[value] += 1
        else:
            counts[value] = 1

    return counts


### Script

# Load data for two sheet
sheet_1_data = read_spreadsheet(SHEET_1_LOC)
sheet_2_data = read_spreadsheet(SHEET_2_LOC)
print(f"Sheet 1 length: {len(sheet_1_data)}")
print(f"Sheet 2 length: {len(sheet_2_data)}")

# Combine data from sheets
data = sheet_1_data
data.extend(sheet_2_data)
print(f"All Collections: {len(data)}")

# Find unique (patient id, date of collection) -> data map then extract values
unique_collections = list({(d[ID], d[COL]): d for d in data}.values())
unique_collections.sort(key=lambda d: (d[ID], d[COL]))
print(f"Unique collects by patient and date: {len(unique_collections)}")

# Find only patients with multiple values
patient_counts = count_values([d[ID] for d in unique_collections])
unique_collections = list(
    filter(lambda d: patient_counts[d[ID]] > 1, unique_collections)
)

# Write
write_spreadsheet(DATA_OUT, unique_collections)
