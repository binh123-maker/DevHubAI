import re
from typing import Generator
from app.services.ai.models.response import UnifiedResponse

class ResponseFormatter:
    @staticmethod
    def sanitize(text: str) -> str:
        """
        Remove <think>...</think> reasoning blocks, normalize whitespace,
        and trim unnecessary blank lines while preserving LaTeX formulas,
        citations, and Unicode mathematical symbols.
        """
        if not text:
            return ""
        
        # Remove reasoning blocks
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        
        # Clean up any leftover unbalanced <think> or </think> tags
        cleaned = cleaned.replace("<think>", "").replace("</think>", "")
        
        # Trim unnecessary blank lines (normalize three or more consecutive newlines to double newlines)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned.strip()

    @staticmethod
    def sanitize_stream(stream: Generator[UnifiedResponse, None, None]) -> Generator[UnifiedResponse, None, None]:
        """
        Stateful stream generator that sanitizes and filters reasoning blocks (<think>...</think>)
        even if the tags are split across chunk boundaries.
        """
        in_think = False
        buffer = ""
        for chunk in stream:
            content = chunk.content
            if not content:
                yield chunk
                continue
            
            buffer += content
            
            # While there are tags to process
            while True:
                if not in_think:
                    think_start = buffer.find("<think>")
                    if think_start != -1:
                        # Yield everything before <think>
                        if think_start > 0:
                            chunk_copy = chunk.model_copy(update={"content": buffer[:think_start]})
                            yield chunk_copy
                        buffer = buffer[think_start + 7:]
                        in_think = True
                    else:
                        # Suffix check to avoid yielding split tag prefixes (e.g. "<th", "<think")
                        possible_prefix = False
                        for i in range(1, 7):
                            if "<think>".startswith(buffer[-i:]):
                                yield_len = len(buffer) - i
                                if yield_len > 0:
                                    chunk_copy = chunk.model_copy(update={"content": buffer[:yield_len]})
                                    yield chunk_copy
                                buffer = buffer[yield_len:]
                                possible_prefix = True
                                break
                        if not possible_prefix:
                            chunk_copy = chunk.model_copy(update={"content": buffer})
                            yield chunk_copy
                            buffer = ""
                        break
                else:
                    think_end = buffer.find("</think>")
                    if think_end != -1:
                        buffer = buffer[think_end + 8:]
                        in_think = False
                    else:
                        # Suffix check to avoid discarding split ending tag prefixes (e.g. "</th")
                        possible_prefix = False
                        for i in range(1, 8):
                            if "</think>".startswith(buffer[-i:]):
                                buffer = buffer[-i:]
                                possible_prefix = True
                                break
                        if not possible_prefix:
                            buffer = ""
                        break
