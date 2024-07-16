def remove_entity_tags(string: str) -> str:
    string = string.replace("<e1>", "").replace("</e1>", "")
    string = string.replace("<e2>", "").replace("</e2>", "")
    return string
