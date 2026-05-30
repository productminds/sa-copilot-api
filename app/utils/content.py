def content_to_str(content: object) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    return str(content)
