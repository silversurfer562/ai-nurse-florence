"""Simple helper: convert MeSH descriptor XML to a minimal JSON mapping.

This is a convenience script for development only. Official MeSH is distributed by NLM
and may require parsing RDF/XML — this script demonstrates a minimal approach.
"""
import sys
import json
try:
    import xmltodict
except ImportError:
    print("Please install xmltodict: pip install xmltodict")
    sys.exit(2)

from pathlib import Path


def convert(input_path: str, output_path: str):
    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(input_path)

    doc = xmltodict.parse(p.read_text(encoding="utf8"))

    # This is a gross simplification — adapt to actual MeSH structure used.
    mapping = {}
    descriptors = doc.get('DescriptorRecordSet', {}).get('DescriptorRecord', [])
    if not isinstance(descriptors, list):
        descriptors = [descriptors]

    for d in descriptors:
        name = d.get('DescriptorName', {}).get('String', '')
        ui = d.get('DescriptorUI') or d.get('DescriptorReferred', {}).get('DescriptorUI')
        if name and ui:
            mapping[name] = {"mesh_id": ui, "synonyms": []}

    Path(output_path).write_text(json.dumps(mapping, indent=2), encoding='utf8')
    print(f"Wrote {len(mapping)} descriptors to {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: convert_mesh_xml_to_json.py input.xml output.json")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
