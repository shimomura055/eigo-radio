#!/usr/bin/env python3
"""
Generate comparison artifacts for News (Hanshin) and Discovery (Household) articles.
Creates Markdown and HTML comparison tables for existing article versions.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "er011_output" / "news_discovery_comparison_artifact_l0_01"

# Configuration for News (Hanshin)
NEWS_CONFIG = {
    "title": "News (Hanshin) Comparison",
    "reference": {
        "a2": BASE_DIR / "er003_output/n3_01/hanshin/a2/article.md",
        "b1b": BASE_DIR / "er003_output/n3_01/hanshin/b1b/article.md",
    },
    "baseline": {
        "a2": BASE_DIR / "er011_output/news_focus_hint_comparison_trial_06/a2/baseline/run1/article.md",
        "b1b": BASE_DIR / "er011_output/news_focus_hint_comparison_trial_06/b1b/baseline/run1/article.md",
    },
    "focus_hint": {
        "a2": BASE_DIR / "er011_output/news_focus_hint_comparison_trial_06/a2/focus_hint/run1/article.md",
        "b1b": BASE_DIR / "er011_output/news_focus_hint_comparison_trial_06/b1b/focus_hint/run2/article.md",
    },
    "focus_hint_run_summary": {
        "a2": BASE_DIR / "er011_output/news_focus_hint_comparison_trial_06/a2/focus_hint/run1/run_summary.json",
        "b1b": BASE_DIR / "er011_output/news_focus_hint_comparison_trial_06/b1b/focus_hint/run2/run_summary.json",
    },
    "baseline_run_summary": {
        "a2": BASE_DIR / "er011_output/news_focus_hint_comparison_trial_06/a2/baseline/run1/run_summary.json",
        "b1b": BASE_DIR / "er011_output/news_focus_hint_comparison_trial_06/b1b/baseline/run1/run_summary.json",
    },
}

# Configuration for Discovery (Household)
DISCOVERY_CONFIG = {
    "title": "Discovery (Household) Comparison",
    "original": {
        "a2": BASE_DIR / "er003_output/n3_01/household/a2/article.md",
        "b1b": BASE_DIR / "er003_output/n3_01/household/b1b/article.md",
    },
    "baseline": {
        "a2": BASE_DIR / "er011_output/discovery_layer3_focus_trial_07/a2/baseline/run1/article.md",
        "b1b": BASE_DIR / "er011_output/discovery_layer3_focus_trial_07/b1b/baseline/run1/article.md",
    },
    "discovery_focus": {
        "a2": BASE_DIR / "er011_output/discovery_layer3_focus_trial_07/a2/discovery_focus/run2/article.md",
        "b1b": BASE_DIR / "er011_output/discovery_layer3_focus_trial_07/b1b/discovery_focus/run1/article.md",
    },
    "discovery_focus_run_summary": {
        "a2": BASE_DIR / "er011_output/discovery_layer3_focus_trial_07/a2/discovery_focus/run2/run_summary.json",
        "b1b": BASE_DIR / "er011_output/discovery_layer3_focus_trial_07/b1b/discovery_focus/run1/run_summary.json",
    },
    "baseline_run_summary": {
        "a2": BASE_DIR / "er011_output/discovery_layer3_focus_trial_07/a2/baseline/run1/run_summary.json",
        "b1b": BASE_DIR / "er011_output/discovery_layer3_focus_trial_07/b1b/baseline/run1/run_summary.json",
    },
}


def safe_read_file(filepath: Path) -> str:
    """Read a file safely, return 'ファイルなし' if not found."""
    try:
        if filepath.exists():
            return filepath.read_text(encoding='utf-8')
        else:
            return "ファイルなし"
    except Exception as e:
        return f"ファイルなし (エラー: {e})"


def safe_read_json(filepath: Path) -> Optional[Dict]:
    """Read a JSON file safely, return None if not found."""
    try:
        if filepath.exists():
            return json.loads(filepath.read_text(encoding='utf-8'))
        else:
            return None
    except Exception as e:
        return None


def count_words(text: str) -> int:
    """Count words in text."""
    words = text.split()
    return len(words)


def extract_article_sections(content: str) -> Dict[str, str]:
    """Extract article sections from content."""
    sections = {
        "full_story": content,
        "preview": content[:200] + "..." if len(content) > 200 else content,
    }

    # Try to extract sections marked with ###
    point_pattern = r'### (.*?)(?=###|## |$)'
    points = re.findall(point_pattern, content, re.DOTALL)

    if len(points) >= 2:
        sections["point_one"] = points[0].strip()[:200]
        sections["point_two"] = points[1].strip()[:200]

    # Try to extract "In one line"
    if_pattern = r'## In one line[….]?\s*(.*?)$'
    in_one = re.search(if_pattern, content, re.DOTALL | re.IGNORECASE)
    if in_one:
        sections["in_one_line"] = in_one.group(1).strip()[:200]

    return sections


def get_section_word_counts(run_summary: Optional[Dict]) -> Dict[str, int]:
    """Extract section word counts from run_summary."""
    if not run_summary or "section_word_counts" not in run_summary:
        return {}
    return run_summary.get("section_word_counts", {})


def get_overlap_ratios(filepath: Path) -> Dict[str, float]:
    """Extract point overlap ratios from point_overlap_qa.json."""
    overlap_file = filepath.parent / "point_overlap_qa.json"
    data = safe_read_json(overlap_file)

    if not data:
        return {}

    return {
        "p1_vs_p2": data.get("point_one_vs_point_two", {}).get("overlap_ratio", 0),
        "p2_vs_p1": data.get("point_two_vs_point_one", {}).get("overlap_ratio", 0),
    }


def get_run_status(run_summary: Optional[Dict]) -> str:
    """Extract run status from run_summary."""
    if not run_summary:
        return "情報なし"
    return run_summary.get("status", "情報なし")


def get_fact_verdict(run_summary: Optional[Dict]) -> str:
    """Extract fact verdict from run_summary."""
    if not run_summary:
        return "情報なし"
    return run_summary.get("fact_verdict", "情報なし")


def create_markdown_table(
    levels: List[str],
    configs: Dict[str, Path],
    base_configs: Dict[str, Any],
    comparison_type: str
) -> str:
    """Create markdown comparison table."""

    if comparison_type == "news":
        title = "# News (Hanshin) Comparison\n"
        ref_key = "reference"
        focus_key = "focus_hint"
        config = NEWS_CONFIG
    else:  # discovery
        title = "# Discovery (Household) Comparison\n"
        ref_key = "original"
        focus_key = "discovery_focus"
        config = DISCOVERY_CONFIG

    md = title
    md += f"\n**Source Path**: {OUTPUT_DIR}\n\n"
    md += "| Level | Reference | Baseline (run1) | Focus/Discovery (latest OK) |\n"
    md += "|-------|-----------|-----------------|-----------------------------|\n"

    for level in levels:
        ref_path = config[ref_key][level]
        baseline_path = config["baseline"][level]
        focus_path = config[focus_key][level]

        ref_exists = "✓" if ref_path.exists() else "✗"
        baseline_exists = "✓" if baseline_path.exists() else "✗"
        focus_exists = "✓" if focus_path.exists() else "✗"

        ref_status = "OK (ref)" if ref_path.exists() else "Missing"
        baseline_status = "OK" if baseline_path.exists() else "Missing"
        focus_status = "OK" if focus_path.exists() else "Missing"

        md += f"| {level.upper()} | {ref_status} | {baseline_status} | {focus_status} |\n"

    # Add detailed metrics for each level
    md += "\n## Detailed Metrics\n\n"

    for level in levels:
        md += f"### {level.upper()}\n\n"

        ref_path = config[ref_key][level]
        baseline_path = config["baseline"][level]
        focus_path = config[focus_key][level]

        baseline_summary = safe_read_json(config["baseline_run_summary"][level])
        focus_summary = safe_read_json(config[focus_key + "_run_summary"][level])

        # Baseline metrics
        md += "#### Baseline (run1)\n"
        if baseline_summary:
            md += f"- Status: {get_run_status(baseline_summary)}\n"
            md += f"- Fact Verdict: {get_fact_verdict(baseline_summary)}\n"
            section_counts = get_section_word_counts(baseline_summary)
            if section_counts:
                md += f"- Word Counts: intro={section_counts.get('intro', 'N/A')}, "
                md += f"p1={section_counts.get('point_one', 'N/A')}, "
                md += f"p2={section_counts.get('point_two', 'N/A')}, "
                md += f"in_one_line={section_counts.get('in_one_line', 'N/A')}\n"
        else:
            md += "- No summary data\n"

        md += f"- Path: `{baseline_path}`\n\n"

        # Focus/Discovery metrics
        md += f"#### {focus_key.replace('_', ' ').title()} (latest OK)\n"
        if focus_summary:
            md += f"- Status: {get_run_status(focus_summary)}\n"
            md += f"- Fact Verdict: {get_fact_verdict(focus_summary)}\n"
            section_counts = get_section_word_counts(focus_summary)
            if section_counts:
                md += f"- Word Counts: intro={section_counts.get('intro', 'N/A')}, "
                md += f"p1={section_counts.get('point_one', 'N/A')}, "
                md += f"p2={section_counts.get('point_two', 'N/A')}, "
                md += f"in_one_line={section_counts.get('in_one_line', 'N/A')}\n"

            overlap = get_overlap_ratios(focus_path)
            if overlap:
                md += f"- Point Overlap: P1 vs P2={overlap.get('p1_vs_p2', 0):.3f}, "
                md += f"P2 vs P1={overlap.get('p2_vs_p1', 0):.3f}\n"
        else:
            md += "- No summary data\n"

        md += f"- Path: `{focus_path}`\n\n"

    return md


def create_html_table(
    levels: List[str],
    comparison_type: str
) -> str:
    """Create HTML comparison table."""

    if comparison_type == "news":
        title = "News (Hanshin) Comparison"
        ref_key = "reference"
        focus_key = "focus_hint"
        config = NEWS_CONFIG
    else:  # discovery
        title = "Discovery (Household) Comparison"
        ref_key = "original"
        focus_key = "discovery_focus"
        config = DISCOVERY_CONFIG

    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .status-ok {{ color: green; font-weight: bold; }}
        .status-ng {{ color: red; font-weight: bold; }}
        .section-title {{ font-size: 1.1em; font-weight: bold; margin-top: 20px; margin-bottom: 10px; }}
        .path {{ font-family: monospace; font-size: 0.9em; color: #666; }}
        .metrics {{ font-size: 0.9em; line-height: 1.6; }}
    </style>
</head>
<body>
    <h1>{}</h1>
    <p>Output: <code>{}</code></p>
""".format(title, title, OUTPUT_DIR)

    html += """
    <table>
        <tr>
            <th>Level</th>
            <th>Reference</th>
            <th>Baseline (run1)</th>
            <th>Focus/Discovery (latest OK)</th>
        </tr>
"""

    for level in levels:
        ref_path = config[ref_key][level]
        baseline_path = config["baseline"][level]
        focus_path = config[focus_key][level]

        ref_status = '<span class="status-ok">✓ OK</span>' if ref_path.exists() else '<span class="status-ng">✗ Missing</span>'
        baseline_status = '<span class="status-ok">✓ OK</span>' if baseline_path.exists() else '<span class="status-ng">✗ Missing</span>'
        focus_status = '<span class="status-ok">✓ OK</span>' if focus_path.exists() else '<span class="status-ng">✗ Missing</span>'

        html += f"""        <tr>
            <td><strong>{level.upper()}</strong></td>
            <td>{ref_status}</td>
            <td>{baseline_status}</td>
            <td>{focus_status}</td>
        </tr>
"""

    html += "    </table>\n"

    # Add detailed sections
    for level in levels:
        baseline_path = config["baseline"][level]
        focus_path = config[focus_key][level]
        baseline_summary = safe_read_json(config["baseline_run_summary"][level])
        focus_summary = safe_read_json(config[focus_key + "_run_summary"][level])

        html += f"""
    <div class="section-title">{level.upper()} - Detailed Metrics</div>

    <div class="metrics">
        <strong>Baseline (run1)</strong><br>
"""
        if baseline_summary:
            html += f"        Status: <span class='status-ok'>{get_run_status(baseline_summary)}</span><br>\n"
            html += f"        Fact Verdict: {get_fact_verdict(baseline_summary)}<br>\n"
            section_counts = get_section_word_counts(baseline_summary)
            if section_counts:
                html += f"        Word Counts: intro={section_counts.get('intro', 'N/A')}, "
                html += f"p1={section_counts.get('point_one', 'N/A')}, "
                html += f"p2={section_counts.get('point_two', 'N/A')}, "
                html += f"in_one_line={section_counts.get('in_one_line', 'N/A')}<br>\n"
        html += f"        <span class='path'>Path: {baseline_path}</span><br><br>\n"

        html += f"""        <strong>{focus_key.replace('_', ' ').title()} (latest OK)</strong><br>
"""
        if focus_summary:
            html += f"        Status: <span class='status-ok'>{get_run_status(focus_summary)}</span><br>\n"
            html += f"        Fact Verdict: {get_fact_verdict(focus_summary)}<br>\n"
            section_counts = get_section_word_counts(focus_summary)
            if section_counts:
                html += f"        Word Counts: intro={section_counts.get('intro', 'N/A')}, "
                html += f"p1={section_counts.get('point_one', 'N/A')}, "
                html += f"p2={section_counts.get('point_two', 'N/A')}, "
                html += f"in_one_line={section_counts.get('in_one_line', 'N/A')}<br>\n"

            overlap = get_overlap_ratios(focus_path)
            if overlap:
                html += f"        Point Overlap: P1 vs P2={overlap.get('p1_vs_p2', 0):.3f}, "
                html += f"P2 vs P1={overlap.get('p2_vs_p1', 0):.3f}<br>\n"

        html += f"        <span class='path'>Path: {focus_path}</span>\n"
        html += "    </div>\n"

    html += """
</body>
</html>
"""
    return html


def main():
    """Main execution."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    levels = ["a2", "b1b"]

    # Generate News comparison
    print("Generating News (Hanshin) comparison...")
    news_md = create_markdown_table(levels, NEWS_CONFIG, {}, "news")
    news_html = create_html_table(levels, "news")

    news_md_path = OUTPUT_DIR / "news_comparison.md"
    news_html_path = OUTPUT_DIR / "news_comparison.html"

    news_md_path.write_text(news_md, encoding='utf-8')
    news_html_path.write_text(news_html, encoding='utf-8')

    print(f"  [OK] Saved: {news_md_path}")
    print(f"  [OK] Saved: {news_html_path}")

    # Generate Discovery comparison
    print("Generating Discovery (Household) comparison...")
    discovery_md = create_markdown_table(levels, DISCOVERY_CONFIG, {}, "discovery")
    discovery_html = create_html_table(levels, "discovery")

    discovery_md_path = OUTPUT_DIR / "discovery_comparison.md"
    discovery_html_path = OUTPUT_DIR / "discovery_comparison.html"

    discovery_md_path.write_text(discovery_md, encoding='utf-8')
    discovery_html_path.write_text(discovery_html, encoding='utf-8')

    print(f"  [OK] Saved: {discovery_md_path}")
    print(f"  [OK] Saved: {discovery_html_path}")

    print("\nComparison artifacts generated successfully!")
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"\nGenerated files:")
    print(f"  - {news_md_path}")
    print(f"  - {news_html_path}")
    print(f"  - {discovery_md_path}")
    print(f"  - {discovery_html_path}")


if __name__ == "__main__":
    main()
