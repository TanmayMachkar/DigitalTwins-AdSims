import json
import os

def read_shared_knowledge(**kwargs) -> str:
    """
    Reads the shared knowledge base accessible to all agents.
    Use this to understand collective trends or shared personality traits.

    Returns:
        str: The content of the shared knowledge file.
    """
    SHARED_KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), '..', 'Data', 'shared_knowledge.txt')
    try:
        with open(SHARED_KNOWLEDGE_PATH, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "No shared knowledge found."