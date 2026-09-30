"""听力练习 MD 文档解析器。

MD 格式规则：
- ``---``  分隔不同题目
- ``[M]``  标记男声说话（对话内容，用于生成音频）
- ``[F]``  标记女声说话
- 未标记的非空文本行默认视为女声（F）对话/独白正文
- ``A)`` / ``B)`` / ``C)`` / ``D)``  选项行——不念，跳过
- ``Answer: X``  正确答案——仅解析供 GUI 显示，不念
- ``#``    开头为文档标题（不生成音频）
- ``## Question N``  题目标题（不生成音频，用于命名输出文件）
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SpeechLine:
    """一行说话内容。"""

    speaker: str  # "M" 或 "F"
    text: str


@dataclass
class Question:
    """一道听力题目。"""

    index: int  # 题号（从 1 开始）
    dialogue_lines: list[SpeechLine] = field(default_factory=list)  # 对话/独白正文（生成音频用）
    answer: str = ""  # 正确答案，如 "B"（仅供 GUI 显示，不念）


@dataclass
class ListeningDocument:
    """一份完整的听力练习文档。"""

    title: str = ""
    questions: list[Question] = field(default_factory=list)


# ── 正则 ──────────────────────────────────────────────
_RE_SPEAKER = re.compile(r"^\[(M|F)\]\s*(.+)$")
_RE_TITLE = re.compile(r"^#\s+(.+)$")
_RE_QUESTION_TITLE = re.compile(r"^##\s+[Qq]uestion\s+(\d+)")
_RE_HR_QUESTION = re.compile(r"^---+\s*$")
_RE_OPTION = re.compile(r"^([A-D])\)\s*(.+)$")
_RE_ANSWER = re.compile(r"^[Aa]nswer\s*:\s*([A-D])\s*$")


def _parse_speech_lines(lines: list[str]) -> list[SpeechLine]:
    """从文本行中提取 SpeechLine 列表。"""
    result: list[SpeechLine] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        m = _RE_SPEAKER.match(stripped)
        if m:
            result.append(SpeechLine(speaker=m.group(1), text=m.group(2).strip()))
    return result


def parse_listening_md(filepath: str | Path) -> ListeningDocument:
    """解析听力练习 MD 文件。

    Parameters
    ----------
    filepath : str | Path
        MD 文件路径。

    Returns
    -------
    ListeningDocument
        解析后的结构化文档。
    """
    filepath = Path(filepath)
    text = filepath.read_text(encoding="utf-8")

    # ── 提取文档标题 ────────────────────────────────
    doc = ListeningDocument()
    for line in text.splitlines():
        m = _RE_TITLE.match(line.strip())
        if m:
            doc.title = m.group(1).strip()
            break

    # ── 按 ``---`` 分割为题目块 ──────────────────────
    all_lines = text.splitlines()
    question_blocks: list[list[str]] = []
    current_block: list[str] = []

    for line in all_lines:
        if _RE_HR_QUESTION.match(line.strip()):
            if current_block:
                question_blocks.append(current_block)
                current_block = []
            continue
        # 跳过文档标题行
        if _RE_TITLE.match(line.strip()):
            continue
        current_block.append(line)

    if current_block:
        question_blocks.append(current_block)

    # ── 解析每个题目块 ──────────────────────────────
    question_blocks = [b for b in question_blocks if any(l.strip() for l in b)]

    for block in question_blocks:
        dialogue_lines: list[SpeechLine] = []
        answer = ""
        question_index = 0

        for line in block:
            stripped = line.strip()

            # 检测题号
            m_q = _RE_QUESTION_TITLE.match(stripped)
            if m_q:
                question_index = int(m_q.group(1))
                continue

            # 检测说话行 [M]/[F]
            m_spk = _RE_SPEAKER.match(stripped)
            if m_spk:
                dialogue_lines.append(
                    SpeechLine(speaker=m_spk.group(1), text=m_spk.group(2).strip())
                )
                continue

            # 选项 A) B) C) D) —— 不念，直接跳过
            if _RE_OPTION.match(stripped):
                continue

            # 答案 Answer: X —— 仅解析供 GUI 显示，不念
            m_ans = _RE_ANSWER.match(stripped)
            if m_ans:
                answer = m_ans.group(1)
                continue

            # 其他非空文本 → 视为女声（F）对话/独白正文
            if stripped:
                dialogue_lines.append(SpeechLine(speaker="F", text=stripped))

        # 如果没有从 ``## Question N`` 解析到题号，自动递增
        if question_index == 0:
            question_index = len(doc.questions) + 1

        q = Question(
            index=question_index,
            dialogue_lines=dialogue_lines,
            answer=answer,
        )
        doc.questions.append(q)

    return doc
