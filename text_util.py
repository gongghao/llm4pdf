def text_chunking(markdown_text):
    """
    对传入的markdown文本进行分块、清洗等处理，返回处理后的文本或分块列表。
    这里以按Markdown标题分块为例。
    """
    import re
    chunks = []
    pattern = re.compile(r'^(#+ .+)$', re.MULTILINE)
    headings = [m for m in pattern.finditer(markdown_text)]
    for i, h in enumerate(headings):
        start = h.end()
        end = headings[i+1].start() if i+1 < len(headings) else len(markdown_text)
        title = h.group(1)
        content = markdown_text[start:end].strip()
        if content:
            chunks.append({'title': title, 'content': content})
    return chunks
