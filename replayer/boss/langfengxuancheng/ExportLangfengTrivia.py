from __future__ import annotations

import argparse
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from replayer.boss.langfengxuancheng.Trivia import TRIVIA_DIR, TRIVIA_OUTPUT_DIR, build_single_sheet_rows


def parse_trivia_file(path: Path):
    fight = {
        "start_ts": int(path.stem),
        "boss": "",
        "win": 0,
        "players": set(),
        "events": [],
    }

    text = path.read_text(encoding="utf-8")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        event_type = parts[0]
        player_name = parts[1]
        try:
            event_time = float(parts[2])
        except ValueError:
            continue

        if event_type == "Boss":
            fight["boss"] = player_name
        elif event_type == "Win":
            fight["win"] = int(player_name)
        elif event_type == "Player":
            fight["players"].add(player_name)
        else:
            fight["events"].append((event_time, event_type, player_name))

    return fight


def load_fights(input_dir: Path):
    fights = []
    all_players = set()
    for path in sorted(input_dir.glob("*.txt")):
        fight = parse_trivia_file(path)
        fights.append(fight)
        all_players.update(fight["players"])
        for _, _, player_name in fight["events"]:
            all_players.add(player_name)
    fights.sort(key=lambda x: x["start_ts"])
    return fights, sorted(all_players)


def export_workbook(fights, players, output_path: Path):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "\u7edf\u8ba1"

    headers = [
        "\u573a\u6b21",
        "\u5f00\u59cb\u65f6\u95f4",
        "BOSS",
        "\u662f\u5426\u901a\u5173",
    ] + players
    sheet.append(headers)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    sheet.freeze_panes = "E2"

    for row in build_single_sheet_rows(fights):
        line = [row["index"], row["start"], row["boss"], row["win"]]
        for player_name in players:
            line.append(row["cells"].get(player_name, ""))
        sheet.append(line)

    wrap = Alignment(wrap_text=True, vertical="top")
    for row in sheet.iter_rows(min_row=2, min_col=5):
        for cell in row:
            cell.alignment = wrap

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)


def main():
    parser = argparse.ArgumentParser(description="Export Langfeng Xuancheng trivia logs to an Excel workbook.")
    parser.add_argument("--input-dir", default=str(TRIVIA_DIR), help="Directory containing raw trivia txt files.")
    parser.add_argument(
        "--output",
        default=str(TRIVIA_OUTPUT_DIR / "\u9606\u98ce\u60ac\u57ce\u4e2d\u6280\u80fd\u7edf\u8ba1.xlsx"),
        help="Target xlsx path.",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        raise SystemExit("Input directory not found: %s" % input_dir)

    fights, players = load_fights(input_dir)
    if not fights:
        raise SystemExit("No trivia txt files found in %s" % input_dir)

    output_path = Path(args.output)
    export_workbook(fights, players, output_path)
    print("Saved workbook -> %s" % output_path)


if __name__ == "__main__":
    main()
