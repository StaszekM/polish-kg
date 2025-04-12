from typing import List, Tuple


def parse_prompt_file(file_path: str) -> List[Tuple[str, str]]:
    with open(file_path, "r") as f:
        content = f.read()

        raw_segments = content.strip().split("\n----------\n")

        parsed_segments: List[Tuple[str, str]] = []
        for seg in raw_segments:
            lines = seg.strip().split("\n", 1)
            if len(lines) == 2:
                header, body = lines
            else:
                header = lines[0]
                body = ""
            parsed_segments.append((header, body))

        return parsed_segments
