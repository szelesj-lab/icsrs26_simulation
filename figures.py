# Developer: József Szeles, Department of System Engineering and Department of Electrical Engineering, University of Pannonia
"""Figures from results/runs.json.

    python figures.py results      -> results/fig2_base.pdf (paper, Fig. 2) and results/overview.png
"""
import json, os, sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# categorical slots in fixed order (validated: CVD and normal-vision separation pass on white);
# every series also has its own line style, so identity never rests on color alone
STYLE = {"scaffold": dict(color="#2a78d6", ls="-", lw=1.8, label="This work"),
         "rl_twin_every": dict(color="#eb6834", ls="-", lw=1.2, label="DT on every decision"),
         "scaffold_retire": dict(color="#1baf7a", ls="--", lw=1.4, label="This work, DT retired after day 60"),
         "rl_alone": dict(color="#eda100", ls=":", lw=1.6, label="RL alone (no DT)")}
INK, MUTED, GRID = "#1f1f1e", "#5f5e5a", "#e4e3df"


def _font():
    names = {f.name for f in font_manager.fontManager.ttflist}
    for n in ("Nimbus Roman", "Nimbus Roman No9 L", "TeX Gyre Termes", "Times New Roman", "STIXGeneral", "DejaVu Serif"):
        if n in names:
            return n
    return "serif"


def _axes(ax):
    ax.spines[["top", "right"]].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED); ax.spines[s].set_linewidth(0.6)
    ax.tick_params(colors=MUTED, labelcolor=INK, width=0.6, length=2.5)
    ax.grid(axis="y", color=GRID, lw=0.5); ax.set_axisbelow(True)


def mean_curve(rows, sc, a, key):
    rs = [r for r in rows if r["scenario"] == sc and r["approach"] == a]
    return np.cumsum(np.mean([r[key] for r in rs], 0))


def fig2(rows, out):
    plt.rcParams.update({"font.family": _font(), "font.size": 8, "pdf.fonttype": 42, "mathtext.fontset": "stix",
                         "axes.labelcolor": INK, "text.color": INK})
    fig, ax = plt.subplots(2, 1, figsize=(3.45, 3.25), sharex=True)
    d = np.arange(1, 121)
    for a in ["rl_twin_every", "scaffold", "scaffold_retire"]:
        ax[0].plot(d, mean_curve(rows, "base", a, "daily_q"), **{k: v for k, v in STYLE[a].items()})
    ax[0].set_ylabel("cumulative DT requests"); ax[0].set_ylim(0, 2050)
    ax[0].legend(frameon=False, loc="upper left", fontsize=7, handlelength=2.4)
    ax[0].text(0.99, 0.04, "(a) twin effort", transform=ax[0].transAxes, ha="right", va="bottom", fontsize=7.5)
    for a in ["rl_alone", "rl_twin_every", "scaffold", "scaffold_retire"]:
        ax[1].plot(d, mean_curve(rows, "base", a, "daily_v"), **{k: v for k, v in STYLE[a].items() if k != "label"})
    ax[1].text(118, 37, "RL alone (no DT)", ha="right", va="center", fontsize=7)      # direct label
    ns = mean_curve(rows, "base", "scaffold", "daily_v_no_safe")
    ax[1].fill_between(d, 0, ns, color="#c3c2b7", alpha=0.55, lw=0, label="this work, no safe level")
    ax[1].set_ylabel("cumulative violation hours"); ax[1].set_xlabel("day of the season")
    ax[1].legend(frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.40), fontsize=7, handlelength=2.4)
    ax[1].text(0.99, 0.04, "(b) safety", transform=ax[1].transAxes, ha="right", va="bottom", fontsize=7.5)
    for a_ in ax:
        _axes(a_); a_.axvline(60, color=MUTED, lw=0.6, ls=(0, (1, 2)))
    ax[1].set_xlim(0, 121)
    fig.tight_layout(pad=0.3, h_pad=0.4)
    fig.savefig(os.path.join(out, "fig2_base.pdf")); fig.savefig(os.path.join(out, "fig2_base.png"), dpi=200)
    plt.close(fig)


def overview(rows, out):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.6), sharey=True)
    for k, sc in enumerate(["base", "episodes", "hinge"]):
        for a in ["rl_twin_every", "scaffold", "scaffold_retire"]:
            rs = [r for r in rows if r["scenario"] == sc and r["approach"] == a]
            q = np.mean([r["daily_q"] for r in rs], 0)
            wk = q[:119].reshape(17, 7).sum(1)
            ax[k].plot(np.arange(17), wk, **STYLE[a])
        ax[k].set_yscale("symlog", linthresh=1); ax[k].set_xlabel("week"); ax[k].set_title(f"Twin requests per week ({sc})")
        _axes(ax[k])
    ax[0].set_ylabel("twin requests per week"); ax[0].legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(out, "overview.png"), dpi=150); plt.close(fig)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "results"
    rows = json.load(open(os.path.join(out, "runs.json")))
    fig2(rows, out); overview(rows, out); print("saved")
