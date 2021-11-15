from typing import List


def chunk_message(message: str, char_limit: int = 4000) -> List[str]:
    lines = message.split("\n")
    capped_lines = []
    for line in lines:
        if len(line) < char_limit:
            capped_lines.append(line)
        else:
            lines += split_long_line(line, char_limit)
    chunks = []
    current_chunk: List[str] = []
    current_size = 0
    for line in capped_lines:
        if len(line) + current_size >= char_limit:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_size = 0
        current_chunk.append(line)
        current_size += len(line) + 1
    if len(current_chunk) > 0:
        chunks.append("\n".join(current_chunk))
    return chunks


def split_long_line(line: str, char_limit: int = 4000) -> List[str]:
    intervals = len(line) // char_limit + 1
    chunks = [line[(i * char_limit) : ((i + 1) * char_limit)] for i in range(intervals)]
    return chunks
