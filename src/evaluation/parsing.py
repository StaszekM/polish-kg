import ast
import json
from argparse import ArgumentParser
from typing import Tuple, Union
from xml.etree import ElementTree as ET

from src.evaluation.regex_matching import parse_string
from src.make_paths_relative_to_root import *


def __parse_single_model_output(output) -> Union[Tuple[str, str, str], None]:
    return parse_string(output)


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

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--extracted_relations_json", type=str, required=True)
    parser.add_argument("--reference_txt", type=str, required=True)
    parser.add_argument("--output_refs_xml", type=str, required=True)
    parser.add_argument("--output_cands_xml", type=str, required=True)
    parser.add_argument("--DEBUG", type=int)

    args = parser.parse_args()

    parse_extracted_relations(
        extracted_relations_json=args.extracted_relations_json,
        reference_txt=args.reference_txt,
        output_refs_xml=args.output_refs_xml,
        output_cands_xml=args.output_cands_xml,
        DEBUG=args.DEBUG,
    )