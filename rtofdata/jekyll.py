import shutil
from dataclasses import asdict
import xml.etree.ElementTree as ET

import yaml

from rtofdata.config import jekyll_dir, output_dir, assets_dir as src_assets
from rtofdata.fake.faker import create_all_data
from rtofdata.specification.data import Specification
from rtofdata.word import get_git_data

assets_dir = jekyll_dir / "assets/spec/"


dict_factory=lambda x: {k: v for (k, v) in x if v is not None}


def write_jekyll_specification(spec: Specification):
    write_records(spec)
    write_dimensions(spec)
    write_datatypes(spec)
    write_sample_data(spec)
    copy_assets()
    add_links_to_chart()
    write_gitinfo()


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

    try:
        shutil.rmtree(jekyll_dir / "assets/src")
    except FileNotFoundError:
        pass
    shutil.copytree(src_assets, jekyll_dir / "assets/src")


def write_records(spec: Specification):
    dir = jekyll_dir / "collections/_records/"
    dir.mkdir(parents=True, exist_ok=True)

    for r in spec.records:
        with open(dir / f"{r.id}.md", "wt") as file:
            print("---", file=file)
            yaml.dump(dict(layout="record", record_id=r.id), file, sort_keys=False)
            print("---", file=file)

    dir = jekyll_dir / "_data"
    dir.mkdir(parents=True, exist_ok=True)
    with open(dir / "records.yml", "wt") as file:
        records = [asdict(f.record, dict_factory=dict_factory) for f in spec.records_by_flow]
        yaml.dump(records, file)

    with open(dir / "fields.yml", "wt") as file:
        records = {
            f.field.id: {
                "record": f.record.id,
                **asdict(f.field, dict_factory=dict_factory),
            } for f in spec.fields if not f.field.foreign_keys
        }
        keys = sorted(records.keys())
        records = {k: records[k] for k in keys}
        yaml.dump(records, file)


def write_dimensions(spec: Specification):
    dir = jekyll_dir / "collections/_dimensions/"
    dir.mkdir(parents=True, exist_ok=True)

    for d in spec.dimensions:
        with open(dir / f"{d.id}.md", "wt") as file:
            print("---", file=file)
            yaml.dump(dict(layout="dimension", dimension_id=d.id), file, sort_keys=False)
            print("---", file=file)

    dir = jekyll_dir / "_data"
    dir.mkdir(parents=True, exist_ok=True)
    with open(dir / "dimensions.yml", "wt") as file:
        dims = [asdict(d, dict_factory=dict_factory) for d in spec.dimensions]
        dims.sort(key=lambda d: d['id'])
        yaml.dump(dims, file)


def write_datatypes(spec: Specification):
    dir = jekyll_dir / "_data"
    dir.mkdir(parents=True, exist_ok=True)
    with open(dir / "datatypes.yml", "wt") as file:
        dims = [asdict(d, dict_factory=dict_factory) for d in spec.datatypes]
        yaml.dump(dims, file)


def write_gitinfo():
    dir = jekyll_dir / "_data"
    dir.mkdir(parents=True, exist_ok=True)
    with open(dir / "git.yml", "wt") as file:
        yaml.dump(get_git_data(), file)


def write_sample_data(spec: Specification):
    dir = jekyll_dir / "_data"
    dir.mkdir(parents=True, exist_ok=True)

    sample_data = create_all_data()
    output_data = {}
    for table_name, items in sample_data.items():
        output_data[table_name] = [i for i in items.values()]

    with open(dir / "sample_data.yml", "wt") as file:
        yaml.dump(output_data, file)