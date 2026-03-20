import json

def agent_comment_ad(agent_id: str, ad_id: str, comment_text: str, **kwargs) -> str:
    """
    Use this tool to post a comment on an advertisement.

    Args:
        agent_id (str): The ID of the agent performing the action.
        ad_id (str): The unique identifier of the ad for the comment.
        comment_text (str): The content of the comment.

    Returns:
        str: A JSON string confirming the action was successful.
    """
    return json.dumps({"status": "success", "action": "comment", "agent": agent_id, "ad": ad_id, "comment": comment_text})