"""命令行工具：从 MD 文件生成听力练习 WAV 音频。

使用方法：
    python scripts/generate_audio.py data/listening/example.md

可选参数：
    --output-dir   输出目录（默认: output/listening/<md文件名>）
    --model-dir    CosyVoice 模型目录（默认: models/CosyVoice-300M）
    --repo-dir     CosyVoice 仓库目录（默认: third_party/CosyVoice）
    --male-wav     男声参考音频路径
    --female-wav   女声参考音频路径
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# 将 src/ 添加到 Python 路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from utils.md_parser import parse_listening_md
from utils.tts_generator import TTSGenerator


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="从 MD 文件生成听力练习 WAV 音频"
    )
    parser.add_argument("md_file", help="MD 文件路径")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="输出目录（默认: output/listening/<md文件名>）",
    )
    parser.add_argument(
        "--model-dir",
        default=str(PROJECT_ROOT / "models" / "CosyVoice-300M"),
        help="CosyVoice 模型目录",
    )
    parser.add_argument(
        "--repo-dir",
        default=None,
        help="CosyVoice 仓库目录",
    )
    parser.add_argument("--male-wav", default=None, help="男声参考音频路径")
    parser.add_argument("--female-wav", default=None, help="女声参考音频路径")

    args = parser.parse_args()

    # 解析 MD
    print(f"解析 MD 文件: {args.md_file}")
    doc = parse_listening_md(args.md_file)
    print(f"  标题: {doc.title}")
    print(f"  题目数: {len(doc.questions)}")

    if not doc.questions:
        print("错误: 没有找到题目内容")
        sys.exit(1)

    for q in doc.questions:
        print(f"  题目 {q.index}: {len(q.question_lines)} 行题目, {len(q.answer_lines)} 行答案")

    # 确定输出目录
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        md_name = Path(args.md_file).stem
        output_dir = PROJECT_ROOT / "output" / "listening" / md_name

    print(f"\n输出目录: {output_dir}")

    # 创建 TTS 生成器
    tts = TTSGenerator(
        model_dir=args.model_dir,
        cosyvoice_repo_dir=args.repo_dir,
        prompt_male_path=args.male_wav,
        prompt_female_path=args.female_wav,
    )

    if not tts.is_available():
        print("\n错误: CosyVoice3 不可用。请先运行安装脚本:")
        print("  python scripts/setup_tts.py")
        sys.exit(1)

    # 生成音频
    print("\n开始生成音频...")

    def on_progress(current: int, total: int):
        print(f"  进度: {current}/{total}")

    all_paths = tts.generate_document_audio(
        doc, str(output_dir), progress_callback=on_progress
    )

    print("\n生成完成！")
    for q_index, paths in all_paths.items():
        print(f"\n  题目 {q_index}:")
        for key, path in paths.items():
            print(f"    {key}: {path}")


if __name__ == "__main__":
    main()
