import re
import json
import ast
from typing import Union
from xml.etree import ElementTree as ET

from src.make_paths_relative_to_root import *

single_or_double_bracket_regex = re.compile(r"^(\[\[[^\[\]]+\]\])|^(\[[^\[\]]+\])")


def __parse_single_model_output(output) -> Union[list, None]:
    triplet_string = getattr(
        re.match(single_or_double_bracket_regex, output), "string", None
    )

    if triplet_string is None:
        return None

    try:
        data = ast.literal_eval(triplet_string)
    except:
        return None

    if not isinstance(data, list):
        return None

    if isinstance(data[0], list):
        data = data[0]

    if len(data) != 3:
        return None

    return list(map(str, data))


def __stringify_triple(triple_list: list):
    return " | ".join(triple_list)


def __create_webnlg_compatible_triplets(pairs):
    cands_root = ET.Element("benchmark")
    cands_entries = ET.SubElement(cands_root, "entries")

    refs_root = ET.Element("benchmark")
    refs_entries = ET.SubElement(refs_root, "entries")

    for i, (output, ref) in enumerate(pairs):
        cand_entry = ET.SubElement(cands_entries, "entry")
        cand_entry.set("category", "Unknown")
        cand_entry.set("eid", f"Id{i}")

        gen_tripleset = ET.SubElement(cand_entry, "generatedtripleset")
        gtriple = ET.SubElement(gen_tripleset, "gtriple")

        if output is not None:
            try:
                gtriple.text = __stringify_triple(output)
            except Exception as e:
                print(output)
                raise e

        ref_entry = ET.SubElement(refs_entries, "entry")
        ref_entry.set("category", "Unknown")
        ref_entry.set("eid", f"Id{i}")
        ref_entry.set("shape", "(X (X))")
        ref_entry.set("shape_type", "NA")
        ref_entry.set("size", "1")

        originaltripleset = ET.SubElement(ref_entry, "originaltripleset")
        otriple = ET.SubElement(originaltripleset, "otriple")
        otriple.text = __stringify_triple(ref)

        modifiedtripleset = ET.SubElement(ref_entry, "modifiedtripleset")
        mtriple = ET.SubElement(modifiedtripleset, "mtriple")
        mtriple.text = __stringify_triple(ref)

    return cands_root, refs_root


def parse_extracted_relations(
    extracted_relations_json: str,
    reference_txt: str,
    output_refs_xml: str,
    output_cands_xml: str,
    DEBUG: bool = False,
):
    with open(extracted_relations_json) as f:
        relations = json.load(f)

    with open(reference_txt) as f:
        reference = list(map(ast.literal_eval, f.read().splitlines()))

    pairs = []
    for resp, ref in zip(relations["responses"], reference):
        output = __parse_single_model_output(resp)
        pairs.append((output, ref[0]))

    if DEBUG:
        pairs = pairs[:50]

    cands_root, refs_root = __create_webnlg_compatible_triplets(pairs)

    cands_tree = ET.ElementTree(cands_root)
    cands_tree.write(output_cands_xml, encoding="utf-8", xml_declaration=True)

    refs_tree = ET.ElementTree(refs_root)
    refs_tree.write(output_refs_xml, encoding="utf-8", xml_declaration=True)
