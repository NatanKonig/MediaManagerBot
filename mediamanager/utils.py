import re


async def clean_caption(caption: str) -> str:
    # Regex para remover a parte "By: Nome - @Username"
    cleaned_caption = re.sub(r"By: [^\n]+ - @\S+", "", caption)
    return cleaned_caption
