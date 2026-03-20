import json
import os

def write_shared_knowledge(content: str, **kwargs) -> str:
    """
    Writes or appends content to the shared knowledge base.
    Use this to contribute to the collective memory or shared personality.

    Args:
        content (str): The information to add to the shared knowledge base.

    Returns:
        str: A confirmation message.
    """
    SHARED_KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'shared_knowledge.txt')
    with open(SHARED_KNOWLEDGE_PATH, 'a') as f:
        f.write(f"\n{content}")
    return "Shared knowledge updated successfully."