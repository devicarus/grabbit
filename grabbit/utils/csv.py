from csv import reader
from pathlib import Path


def load_gdpr_saved_posts_csv(path: Path) -> list[str]:
    """ Loads post ids from the GDPR Saved Posts CSV file """
    with open(path, encoding="utf-8") as file:
        csv = reader(file)
        ids = [ensure_post_id(row[0]) for row in csv]
        del ids[0]
    return ids

def ensure_post_id(post_id_like: str) -> str:
    """ Makes sure the post id is prefixed with "t3_" """
    if post_id_like.startswith("t3_"):
        return post_id_like
    return f"t3_{post_id_like}"
