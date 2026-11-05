import re
from dataclasses import dataclass

from razdel import sentenize, tokenize

SUMMARY_MAX = 400
MIN_WORD_LENGTH = 4
TOP_KEYWORDS = 8
TOP_TAGS = 3
TOP_KEY_POINTS = 3

WORD_RE = re.compile(r"^[a-zа-яё]+$")

STOPWORDS = frozenset(
    {
        "а",
        "без",
        "более",
        "больше",
        "будто",
        "бы",
        "был",
        "была",
        "были",
        "было",
        "быть",
        "в",
        "вам",
        "вас",
        "вдруг",
        "ведь",
        "во",
        "вот",
        "все",
        "всего",
        "всех",
        "всю",
        "вы",
        "где",
        "да",
        "даже",
        "для",
        "до",
        "его",
        "ее",
        "ей",
        "ему",
        "если",
        "есть",
        "еще",
        "ещё",
        "же",
        "за",
        "зачем",
        "здесь",
        "и",
        "из",
        "или",
        "им",
        "иногда",
        "их",
        "к",
        "как",
        "какая",
        "какой",
        "когда",
        "кто",
        "куда",
        "ли",
        "лучше",
        "между",
        "меня",
        "мне",
        "мой",
        "моя",
        "мы",
        "на",
        "над",
        "надо",
        "нас",
        "не",
        "него",
        "нее",
        "ней",
        "нет",
        "ни",
        "нибудь",
        "ним",
        "них",
        "ничего",
        "но",
        "ну",
        "о",
        "об",
        "один",
        "он",
        "она",
        "они",
        "опять",
        "от",
        "перед",
        "по",
        "под",
        "после",
        "потом",
        "потому",
        "почти",
        "при",
        "про",
        "раз",
        "разве",
        "с",
        "сам",
        "свое",
        "своё",
        "свою",
        "себе",
        "себя",
        "сейчас",
        "со",
        "совсем",
        "так",
        "такой",
        "там",
        "тебя",
        "тем",
        "теперь",
        "то",
        "тогда",
        "того",
        "тоже",
        "только",
        "том",
        "тот",
        "три",
        "тут",
        "ты",
        "у",
        "уж",
        "уже",
        "хорошо",
        "хоть",
        "чего",
        "чем",
        "через",
        "что",
        "чтоб",
        "чтобы",
        "чуть",
        "эта",
        "эти",
        "это",
        "этого",
        "этой",
        "этом",
        "этот",
        "эту",
        "я",
    }
)


@dataclass(frozen=True)
class AnalysisResult:
    summary: str
    keywords: list[str]
    tags: list[str]
    key_points: list[str]


def analyze(title: str, body: str) -> AnalysisResult:
    text = body.strip()
    sentences = [part.text.strip() for part in sentenize(text) if part.text.strip()]
    keywords = _keywords(f"{title}\n{text}")
    return AnalysisResult(
        summary=_summary(sentences, text),
        keywords=keywords,
        tags=keywords[:TOP_TAGS],
        key_points=_key_points(sentences, keywords),
    )


def _summary(sentences: list[str], text: str) -> str:
    if sentences:
        chosen = " ".join(sentences[:2])
    else:
        chosen = text
    if len(chosen) <= SUMMARY_MAX:
        return chosen
    return f"{chosen[: SUMMARY_MAX - 1].rstrip()}…"


def _keywords(text: str) -> list[str]:
    counts: dict[str, int] = {}
    order: dict[str, int] = {}
    for token in tokenize(text):
        word = token.text.casefold()
        if len(word) < MIN_WORD_LENGTH or word in STOPWORDS or WORD_RE.fullmatch(word) is None:
            continue
        if word not in order:
            order[word] = len(order)
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts, key=lambda word: (-counts[word], order[word]))
    return ranked[:TOP_KEYWORDS]


def _key_points(sentences: list[str], keywords: list[str]) -> list[str]:
    if not sentences:
        return []
    keys = set(keywords)
    scored: list[tuple[int, int]] = []
    for index, sentence in enumerate(sentences):
        words = {
            token.text.casefold()
            for token in tokenize(sentence)
            if WORD_RE.fullmatch(token.text.casefold())
        }
        scored.append((len(words & keys), index))
    scored.sort(key=lambda item: (-item[0], item[1]))
    chosen = sorted(index for _, index in scored[:TOP_KEY_POINTS])
    return [sentences[index] for index in chosen]
