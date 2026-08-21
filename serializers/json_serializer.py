import json
from pathlib import Path
from models.publication import Publication
SCHEMA_VERSION = '1.0'

# Serialize a publication to the application JSON format.
def publication_to_json(publication: Publication) -> str:
    data = {'schema_version': SCHEMA_VERSION, 'publication': publication.to_dict()}
    return json.dumps(data, indent=2, ensure_ascii=False)

# Write a publication JSON document to disk.
def save_publication_json(publication: Publication, directory: str='data/publications') -> Path:
    output_directory = Path(directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    output_file = output_directory / f'{publication.id}.json'
    output_file.write_text(publication_to_json(publication), encoding='utf-8')
    return output_file
