import requests
import time
from typing import Dict, Optional
from tqdm import tqdm
import urllib.parse

# Import your SQLAlchemy database components
from data_base import Vehicle, SessionLocal, create_tables


def get_vehicle_specs(year: int, make: str, model: str) -> Optional[Dict]:
    url = (
        f"https://vpic.nhtsa.dot.gov/api/vehicles/GetCanadianVehicleSpecifications/"
        f"?year={year}&make={make}&model={model}&format=json"
    )
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching data for {year} {make} {model}: {e}")
    return None


def get_all_manufacturers(max_pages: int = 100) -> list:
    manufacturers = []
    page = 1
    while page <= max_pages:
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/GetAllManufacturers?format=json&page={page}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        results = data.get("Results", [])
        if not results:
            break
        manufacturers.extend(results)
        page += 1
    return manufacturers


def get_all_makes() -> list:
    manufacturers = get_all_manufacturers()
    names = []
    for mfr in manufacturers:
        if mfr.get("Mfr_CommonName"):
            names.append(mfr["Mfr_CommonName"].strip())
        elif mfr.get("Mfr_Name"):
            names.append(mfr["Mfr_Name"].strip())
    # Deduplicate while preserving order
    unique_names = list(dict.fromkeys(names))
    return sorted(unique_names)


def create_vehicle_database_db():
    makes = get_all_makes()
    years = range(1980, 2026)

    session = SessionLocal()
    vehicles_to_insert = []

    for year in tqdm(years, desc="Processing years"):
        for make in tqdm(makes, desc=f"Processing makes for {year}", leave=False):
            data = get_vehicle_specs(year, make, "")
            if data and data.get('Results'):
                for result in data['Results']:
                    specs = {spec['Name']: spec['Value'] for spec in result['Specs']}
                    try:
                        weight_kg = float(specs.get('CW', 0))
                        weight_tons = round(weight_kg * 0.001102, 1)
                        vehicle = Vehicle(
                            year=year,
                            make=specs.get('Make', make),
                            model=specs.get('Model', ''),
                            specific_model=specs.get('Model', ''),
                            curb_weight=weight_tons
                        )
                        vehicles_to_insert.append(vehicle)
                    except ValueError:
                        continue
            time.sleep(0.1)

    print(f"Inserting {len(vehicles_to_insert)} vehicle records into the database...")
    session.bulk_save_objects(vehicles_to_insert)
    session.commit()
    session.close()
    print("Data successfully loaded into the database.")


if __name__ == "__main__":
    create_tables()
    create_vehicle_database_db()
