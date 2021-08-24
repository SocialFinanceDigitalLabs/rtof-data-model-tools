import shutil
from dataclasses import asdict
import xml.etree.ElementTree as ET

import yaml

from rtofdata.config import jekyll_dir, output_dir
from rtofdata.spec_parser import Specification

assets_dir = jekyll_dir / "assets/spec/"

dict_factory=lambda x: {k: v for (k, v) in x if v is not None}

def write_jekyll_specification(spec: Specification):
    write_records(spec)
    write_dimensions(spec)
    copy_assets()
    add_links_to_chart()


def add_links_to_chart():
    namespaces = {'svg': 'http://www.w3.org/2000/svg'}
    ET.register_namespace('', 'http://www.w3.org/2000/svg')

    tree = ET.parse(assets_dir / 'record-relationships.svg')
    root = tree.getroot()
    root.attrib['width'] = "auto"
    root.attrib['height'] = "auto"

    root_graph = root.find('svg:g', namespaces)
    background = root_graph.find('svg:polygon', namespaces)
    root_graph.remove(background)

    sub_graphs = root_graph.findall('svg:g', namespaces)
    for sg in sub_graphs:
        root_graph.remove(sg)

        filename = f"/records/{sg.attrib['id']}.html"
        link = ET.Element("a")
        link.attrib['href'] = "{{ '" + filename + "' | relative_url }}"
        root_graph.append(link)
        link.append(sg)

    (jekyll_dir / '_includes/dynamic').mkdir(parents=True, exist_ok=True)
    with open(jekyll_dir / '_includes/dynamic/record-relationships.svg', 'wb') as f:
        tree.write(f, encoding='utf-8')


def copy_assets():
    try:
        shutil.rmtree(assets_dir)
    except FileNotFoundError:
        pass

    shutil.copytree(output_dir, assets_dir)
    (assets_dir / ".gitignore").unlink(missing_ok=True)


def write_records(spec: Specification):
    dir = jekyll_dir / "collections/_records/"
    dir.mkdir(parents=True, exist_ok=True)

    for r in spec.records:
        with open(dir / f"{r.id}.md", "wt") as file:
            print("---", file=file)
            yaml.dump(dict(record=asdict(r), layout="record"), file)
            print("---", file=file)

    dir = jekyll_dir / "_data"
    dir.mkdir(parents=True, exist_ok=True)
    with open(dir / "records.yml", "wt") as file:
        records = [asdict(f.record, dict_factory=dict_factory) for f in spec.records_by_flow]
        yaml.dump(records, file)


def write_dimensions(spec: Specification):
    dir = jekyll_dir / "collections/_dimensions/"
    dir.mkdir(parents=True, exist_ok=True)

    for d in spec.dimensions:
        with open(dir / f"{d.id}.md", "wt") as file:
            print("---", file=file)
            yaml.dump(dict(dimensions=asdict(d), layout="dimension"), file)
            print("---", file=file)

    dir = jekyll_dir / "_data"
    dir.mkdir(parents=True, exist_ok=True)
    with open(dir / "dimensions.yml", "wt") as file:
        dims = [asdict(d, dict_factory=dict_factory) for d in spec.dimensions]
        dims.sort(key=lambda d: d['id'])
        yaml.dump(dims, file)
