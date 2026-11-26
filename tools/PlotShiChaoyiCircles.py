"""Render standalone figures from MineShiChaoyiCircles evidence (no source edits)."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Patch, Rectangle
import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, default=Path("docs/analysis/shichaoyi-circles-20260915"))
    ap.add_argument("--output", type=Path, default=Path("build/research/shichaoyi-circles-20260915"))
    args = ap.parse_args()
    data = json.loads((args.input / "evidence.json").read_text(encoding="utf-8"))
    phases, circles = data["phases"], data["circles"]
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
                         "axes.unicode_minus": False, "font.size": 11,
                         "figure.facecolor": "#ffffff", "axes.facecolor": "#ffffff"})
    colors = {"R": "#d84b51", "W": "#fffefa"}
    fig, ax = plt.subplots(figsize=(16, 7.8))
    for row, p in enumerate(phases):
        seq = p["sequence"]
        for col in range(40):
            color = colors[seq[col]] if col < len(seq) else "#dce1e7"
            ax.add_patch(Rectangle((col+.07, row+.12), .86, .76, facecolor=color,
                                   edgecolor="#77808a", linewidth=.6,
                                   hatch="///" if col >= len(seq) else None))
        quota = next((i for i in range(1, len(seq)+1) if seq[:i].count("R") == 20 or seq[:i].count("W") == 20), None)
        if quota is not None and quota < len(seq):
            ax.add_patch(Rectangle((quota+.02, row+.05), len(seq)-quota-.04, .9,
                                   fill=False, edgecolor="#1768ac", linewidth=2))
        status = "生成截断" if len(seq) < 40 else ("末圈未见结算" if p["n_unresolved_observed"] else "40圈结算可见")
        ax.text(40.5, row+.5, f'{p["red"]:2d}红 {p["white"]:2d}白  ·  {status}', va="center", fontsize=10)
    ax.set_xlim(0, 40); ax.set_ylim(len(phases), 0)
    ax.set_xticks(np.arange(0, 40)+.5, [str(i) if i == 1 or i % 5 == 0 else "" for i in range(1, 41)])
    ax.set_yticks(np.arange(len(phases))+.5, [f'{p["battle_id"]}  第{p["phase"]}轮' for p in phases])
    ax.tick_params(length=0, pad=8)
    for spine in ax.spines.values(): spine.set_visible(False)
    ax.set_xlabel("本轮生成顺序（灰色斜线 = 未观测，不补齐）", labelpad=12)
    fig.suptitle("史朝义 · 红白圈的 13 轮观测序列", x=.12, ha="left", fontsize=20, weight="bold")
    ax.set_title("9轮生成满40个，均20红20白；蓝框标出某色已满20后，实际观测到的另一色尾段", loc="left", pad=20, fontsize=11)
    fig.legend(handles=[Patch(facecolor=colors["R"], edgecolor="#77808a", label="红：139311"),
                        Patch(facecolor=colors["W"], edgecolor="#77808a", label="白：139314（内部名黑／幽煞）")],
               loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(.48, .005))
    fig.subplots_adjust(left=.145, right=.78, top=.85, bottom=.13)
    fig.savefig(args.output / "color_sequences.png", dpi=160)
    plt.close(fig)

    example = [c for c in circles if c["battle_id"] == "B46" and c["phase"] == 1]
    fig, ax = plt.subplots(figsize=(11, 10))
    for c in example:
        x0 = c["after_cast_s"]
        x1 = (c["despawn_ms"]-c["cast_ms"])/1000
        code = "R" if c["color"] == "red" else "W"
        ax.barh(c["order"], x1-x0, left=x0, height=.65, facecolor=colors[code], edgecolor="#66717d", linewidth=.6)
        if c["first_resolve_ms"] is not None:
            ax.plot((c["first_resolve_ms"]-c["cast_ms"])/1000, c["order"], "|", color="#172b3a", markersize=7)
    ax.axvspan(0, 2, color="#e2ebf4", alpha=.8, label="解包配置：2秒读条")
    ax.set(xlim=(0, 39), ylim=(41, 0), xlabel="距戾芒天坠读条开始（秒）", ylabel="本轮第几个圈")
    ax.set_yticks([1, 5, 10, 15, 20, 25, 30, 35, 40])
    ax.set_xticks(np.arange(0, 40, 2))
    ax.grid(axis="x", color="#e3e6e9", linewidth=.7); ax.set_axisbelow(True)
    ax.set_title("一轮完整时间线：B46 第1轮\n约2.5秒后开始，每0.75秒一个；每圈约5.5秒后判定", loc="left", fontsize=15, pad=15)
    fig.text(.12, .025, "横条：入场到退场。竖线：首次圈判定／爆炸事件。全部时间来自原始JCL。", fontsize=10)
    fig.tight_layout(rect=(0, .05, 1, 1))
    fig.savefig(args.output / "circle_lifetimes.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(15, 7), sharex=True, sharey=True)
    for phase, ax in enumerate(axes, 1):
        rows = [c for c in circles if c["battle_id"] == "B46" and c["phase"] == phase]
        for c in rows:
            code = "R" if c["color"] == "red" else "W"
            x, y = (c["x"]-7408)/64, (c["y"]-53794)/64
            ax.scatter(x, y, s=230, color=colors[code], edgecolor="#475869", linewidth=.8)
            ax.text(x, y, str(c["order"]), ha="center", va="center", fontsize=7, color="#1c2630")
        ax.add_patch(Circle((0, 0), 28, fill=False, linestyle="--", edgecolor="#8395a7", linewidth=1.1))
        ax.plot(0, 0, marker="+", color="#1768ac", markersize=10)
        ax.set_title(f"第{phase}轮 · 20红20白", fontsize=13)
        ax.set_xlabel("相对初始中心 x（尺）")
        ax.set_xlim(-31, 31); ax.set_ylim(-31, 31)
        ax.set_aspect("equal"); ax.grid(alpha=.18); ax.set_axisbelow(True)
    axes[0].set_ylabel("相对初始中心 y（尺）")
    fig.suptitle("同一场战斗的三轮位置观测（B46）", fontsize=18)
    fig.text(.05, .04, "圈内数字为生成序号；以原始坐标(7408, 53794)为中心，64单位=1尺，方向未经游戏画面对齐。\n虚线是28尺参考圆，作为候选出生范围对照；并非已确认的服务器边界。标记大小不代表实际圈半径。", fontsize=10, linespacing=1.6)
    fig.tight_layout(rect=(0, .13, 1, .92))
    fig.savefig(args.output / "spatial_examples.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
