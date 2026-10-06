import json
import math
import re

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


REPO_ROOT = (
    Path(__file__)
    .resolve()
    .parents[4]
)


KNOWLEDGE_FILES = [

    REPO_ROOT
    / "README.md",

    REPO_ROOT
    / "ml/reports/phase6_completion.json",

    REPO_ROOT
    / "ml/reports/phase7_completion.json",

    REPO_ROOT
    / "ml/reports/phase8_completion.json",

    REPO_ROOT
    / "ml/reports/phase9_completion.json",

    REPO_ROOT
    / "ml/reports/phase11_completion.json",

    REPO_ROOT
    / "ml/configs/breed_classifier_v2.json",

    REPO_ROOT
    / "ml/configs/bovine_detector_v1.json",

    REPO_ROOT
    / "ml/configs/phase7_config.json",

    REPO_ROOT
    / "ml/configs/phase7_calibration.json",

    REPO_ROOT
    / "ml/configs/phase7_unknown_threshold.json",
]


TOKEN_PATTERN = re.compile(
    r"\w+",
    re.UNICODE,
)


STOP_WORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "of",
    "to",
    "in",
    "and",
    "or",
    "for",
    "what",
    "how",
    "tell",
    "me",
    "explain",
}


@dataclass
class KnowledgeChunk:

    source: str

    content: str

    score: float = 0.0


def tokenize(
    text: str,
):

    return {

        token.lower()

        for token
        in TOKEN_PATTERN.findall(
            text
        )

        if (
            len(token) >= 2
            and
            token.lower()
            not in STOP_WORDS
        )
    }


def read_file(
    path: Path,
):

    if not path.exists():

        return ""


    try:

        text = path.read_text(
            encoding="utf-8"
        )

    except Exception:

        return ""


    if (
        path.suffix.lower()
        ==
        ".json"
    ):

        try:

            data = json.loads(
                text
            )


            return json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            )

        except Exception:

            return text


    return text


def split_text(
    text: str,
    max_chars: int = 1500,
    overlap: int = 220,
):

    cleaned = (
        text
        .replace(
            "\r\n",
            "\n"
        )
        .strip()
    )


    if not cleaned:

        return []


    chunks = []

    start = 0


    while (
        start
        <
        len(cleaned)
    ):

        end = min(
            len(cleaned),
            start
            +
            max_chars,
        )


        piece = (
            cleaned[
                start:end
            ]
            .strip()
        )


        if piece:

            chunks.append(
                piece
            )


        if (
            end
            >=
            len(cleaned)
        ):

            break


        start = max(
            end
            -
            overlap,

            start
            +
            1,
        )


    return chunks


@lru_cache(
    maxsize=1
)
def get_knowledge_chunks():

    chunks = []


    for path in (
        KNOWLEDGE_FILES
    ):

        text = read_file(
            path
        )


        if not text:

            continue


        try:

            source = str(
                path.relative_to(
                    REPO_ROOT
                )
            )

        except ValueError:

            source = str(
                path
            )


        for piece in (
            split_text(
                text
            )
        ):

            chunks.append(

                KnowledgeChunk(
                    source=
                        source,

                    content=
                        piece,
                )

            )


    return chunks


def score_chunk(
    query_tokens,
    chunk_tokens,
):

    if (
        not query_tokens
        or
        not chunk_tokens
    ):

        return 0.0


    common = (
        query_tokens
        &
        chunk_tokens
    )


    if not common:

        return 0.0


    base = (

        len(common)

        /

        math.sqrt(
            len(query_tokens)
            *
            len(chunk_tokens)
        )
    )


    important_terms = {

        "breedvision",
        "phase",
        "classifier",
        "detector",
        "cattle",
        "buffalo",
        "breed",
        "gradcam",
        "confidence",
        "unknown",
        "calibration",
        "supabase",
        "farmer",
        "animal",
        "banni",
        "bargur",
        "gir",
        "hallikar",
        "jaffarabadi",
        "murrah",
        "ongole",
        "sahiwal",
        "tharparkar",
    }


    bonus = (

        len(
            common
            &
            important_terms
        )

        *
        0.08
    )


    return (
        base
        +
        bonus
    )


def search_project_knowledge(
    query: str,
    limit: int = 4,
):

    query_tokens = tokenize(
        query
    )


    if not query_tokens:

        return []


    ranked = []


    for chunk in (
        get_knowledge_chunks()
    ):

        chunk_tokens = tokenize(
            chunk.content
        )


        score = score_chunk(
            query_tokens,
            chunk_tokens,
        )


        if score <= 0:

            continue


        ranked.append(

            KnowledgeChunk(
                source=
                    chunk.source,

                content=
                    chunk.content,

                score=
                    score,
            )

        )


    ranked.sort(
        key=lambda item:
            item.score,
        reverse=True,
    )


    return ranked[
        :limit
    ]