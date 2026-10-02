from typing import Dict, Any, Optional
import requests


def remove_background(
    api_key: str,
    image_data: bytes,
    content_moderation: Optional[bool] = False
) -> Dict[str, Any]:
    """
    Remove background from an image using Brai AI API.

    Args:
        api_key: Your Brai AI API key.
        image_data: The raw bytes of the image file.
        content_moderation: Whether to enable content moderation (default False).

    Returns:
        JSON response as dict from the API, usually containing 'result_url'.

    Raises:
        Exception if the API request fails.
    """

    url = "https://engine.prod.bria-api.com/v1/image/background-remove"

    headers = {
        "api_token": api_key,
        "Accept": "application/json"
    }

    files = {
        "image": ("image.png", image_data, "image/png")
    }

    data = {}
    if content_moderation:
        data["content_moderation"] = True

    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Background removal failed: {str(e)}")
