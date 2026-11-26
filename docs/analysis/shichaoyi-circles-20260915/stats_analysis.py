"""Independent, standard-library-only comparison of circle color models.

Run: python docs/analysis/shichaoyi-circles-20260915/stats_analysis.py
Sequences are conditioned on the extractor's chronological circle ordering.
Numerical likelihoods do not account for informative battle termination,
within-battle dependence, or selecting these models after inspecting the data.
"""

import hashlib
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
QUOTA = 20
LN2 = math.log(2)
TOTAL_COMBINATIONS = math.comb(40, 20)


def phase_summary(phase):
    seq = phase["sequence"]
    counts = Counter()
    free_counts = Counter()
    quota_hit_at = None
    first_full_color = None
    consistent = True
    for index, color in enumerate(seq, 1):
        if max(counts.values(), default=0) < QUOTA:
            free_counts[color] += 1
        elif counts[color] >= QUOTA:
            consistent = False
        counts[color] += 1
        if quota_hit_at is None and counts[color] == QUOTA:
            quota_hit_at = index
            first_full_color = color
    n, red, white = len(seq), counts["R"], counts["W"]
    quota_valid = consistent and red <= QUOTA and white <= QUOTA
    quota_ll = -sum(free_counts.values()) * LN2 if quota_valid else -math.inf
    shuffle_ll = (math.log(math.comb(40 - n, 20 - red)) - math.log(TOTAL_COMBINATIONS)
                  if n <= 40 and red <= 20 and white <= 20 else -math.inf)
    free_seq = seq[:quota_hit_at] if quota_hit_at is not None else seq
    return {
        "battle_id": phase["battle_id"], "phase": phase["phase"],
        "status": phase["status"], "sequence": seq, "n": n,
        "red": red, "white": white,
        "quota_hit_at": quota_hit_at, "quota_hit_color": first_full_color,
        "observed_after_first_quota": n - quota_hit_at if quota_hit_at else 0,
        "last_run_length": len(re.search(r"(R+|W+)$", seq)[0]),
        "max_run_length": max(map(len, re.findall(r"R+|W+", seq))),
        "max_run_before_or_at_quota": max(map(len, re.findall(r"R+|W+", free_seq))),
        "red_in_first_20": seq[:20].count("R") if n >= 20 else None,
        "free_red": free_counts["R"], "free_white": free_counts["W"],
        "quota_consistent": quota_valid,
        "log_likelihood": {
            "quota_fair_coin": quota_ll,
            "uniform_shuffle_20_each": shuffle_ll,
            "iid_fair_coin": -n * LN2,
        },
    }


def exact_fair_binomial_two_sided(successes, trials):
    lower = min(successes, trials - successes)
    return min(1.0, 2 * sum(math.comb(trials, k) for k in range(lower + 1)) / 2 ** trials)


def terminal_run_pmf(model):
    """For complete 20+20 sequences, L = positions after first color reaches 20."""
    if model == "shuffle":
        return {length: 2 * math.comb(39 - length, 19) / TOTAL_COMBINATIONS
                for length in range(1, 21)}
    if model == "quota":
        return {length: 2 * math.comb(39 - length, 19) / 2 ** (40 - length)
                for length in range(1, 21)}
    raise ValueError(model)


def convolution(pmf, n):
    result = {0: 1.0}
    for _ in range(n):
        updated = Counter()
        for a, pa in result.items():
            for b, pb in pmf.items():
                updated[a + b] += pa * pb
        result = dict(updated)
    return result


def completion_tail_summary(phases):
    complete = [p for p in phases if p["n"] == 40]
    if not complete:
        return None
    lengths = [p["observed_after_first_quota"] for p in complete]
    observed_sum, n = sum(lengths), len(lengths)
    result = {
        "n_complete": n, "lengths": lengths, "sum": observed_sum,
        "mean": statistics.mean(lengths),
        "assumption": "Tail probability calculations assume independent, unselected complete phases.",
    }
    for model in ("shuffle", "quota"):
        pmf = terminal_run_pmf(model)
        summed = convolution(pmf, n)
        result[model] = {
            "expected_length": sum(k * p for k, p in pmf.items()),
            "single_length_at_least_10_probability": sum(p for k, p in pmf.items() if k >= 10),
            "sum_at_least_observed_probability": sum(p for k, p in summed.items() if k >= observed_sum),
            "sum_at_most_observed_probability": sum(p for k, p in summed.items() if k <= observed_sum),
        }
    return result


def adaptive_draw_summary(phases):
    """Descriptive frequencies only: number of draws is an adaptive stopping time."""
    bins = {"all_nonzero_imbalance": Counter(), "imbalance_1_to_3": Counter(),
            "imbalance_at_least_4": Counter()}
    prequota = Counter()
    for p in phases:
        counts = Counter()
        for index, color in enumerate(p["sequence"], 1):
            if max(counts.values(), default=0) == 20:
                break
            delta = counts["R"] - counts["W"]
            if delta != 0:
                minority = "W" if delta > 0 else "R"
                prior_n = index - 1
                shuffle_minority_p = (20 - counts[minority]) / (40 - prior_n)
                for key in ("all_nonzero_imbalance", "imbalance_1_to_3" if abs(delta) <= 3 else "imbalance_at_least_4"):
                    bins[key]["n"] += 1
                    bins[key]["minority_next"] += color == minority
                    bins[key]["shuffle_expected_minority_sum"] += shuffle_minority_p
            if index > 20:
                prequota["after_first_20_draws"] += 1
                prequota["after_first_20_red"] += color == "R"
            counts[color] += 1
    return {
        key: dict(value,
                  observed_minority_rate=value["minority_next"] / value["n"] if value["n"] else None,
                  quota_expected_minority_rate=0.5,
                  shuffle_mean_predicted_minority_rate=value["shuffle_expected_minority_sum"] / value["n"] if value["n"] else None)
        for key, value in bins.items()
    }


def group_summary(phases):
    models = ("quota_fair_coin", "uniform_shuffle_20_each", "iid_fair_coin")
    likelihoods = {model: sum(p["log_likelihood"][model] for p in phases) for model in models}
    free_red = sum(p["free_red"] for p in phases)
    free_white = sum(p["free_white"] for p in phases)
    free_n = free_red + free_white
    fitted_p = free_red / free_n
    fitted_ll = free_red * math.log(fitted_p) + free_white * math.log1p(-fitted_p)
    first_20 = [p["red_in_first_20"] for p in phases if p["red_in_first_20"] is not None]
    n_complete = sum(p["n"] == 40 for p in phases)
    result = {
        "phase_keys": [f'{p["battle_id"]}:{p["phase"]}' for p in phases],
        "n_phases": len(phases), "n_battles": len({p["battle_id"] for p in phases}),
        "observed_circles": sum(p["n"] for p in phases),
        "iid_probability_all_complete_phases_have_20_each_nominal": (TOTAL_COMBINATIONS / 2 ** 40) ** n_complete,
        "log_likelihood": likelihoods,
        "quota_vs_shuffle_likelihood_ratio": math.exp(likelihoods[models[0]] - likelihoods[models[1]]),
        "quota_vs_iid_likelihood_ratio": math.exp(likelihoods[models[0]] - likelihoods[models[2]]),
        "quota_coin_fitted_probability_red": fitted_p,
        "quota_coin_free_red": free_red, "quota_coin_free_white": free_white,
        "fitted_vs_fair_quota_likelihood_ratio": math.exp(fitted_ll - likelihoods[models[0]]),
        "first_20": {
            "red_counts": first_20,
            "mean": statistics.mean(first_20),
            "sample_variance": statistics.variance(first_20) if len(first_20) > 1 else None,
            "expected_mean_both_models": 10,
            "quota_model_variance": 5,
            "shuffle_model_variance": 100 / 39,
            "iid_fair_coin_two_sided_p_value_nominal": exact_fair_binomial_two_sided(sum(first_20), 20 * len(first_20)),
        },
        "complete_tail_analysis": completion_tail_summary(phases),
        "before_quota_minority_rates": adaptive_draw_summary(phases),
    }
    return result


def first_per_battle(phases):
    seen, result = set(), []
    for p in phases:
        if p["battle_id"] not in seen:
            seen.add(p["battle_id"])
            result.append(p)
    return result


def main():
    output = ROOT.parents[2] / "build" / "research" / ROOT.name
    output.mkdir(parents=True, exist_ok=True)
    source = ROOT / "evidence.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    phases = [phase_summary(p) for p in data["phases"]]
    complete = [p for p in phases if p["n"] == 40]
    result = {
        "source_file": source.name,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "model_definitions": {
            "quota_fair_coin": "Each color has quota 20. Draw R/W independently at p=0.5 while both below 20; after a color reaches 20, force the other color until 40 total.",
            "uniform_shuffle_20_each": "All choose(40,20) ordered arrangements of 20 R and 20 W equally likely; next P(R)=(20-red_so_far)/(40-draws_so_far).",
            "iid_fair_coin": "Every observed circle independently R/W at p=0.5, with no total quota.",
        },
        "formulas": {
            "complete_quota_probability": "2^(-T), T is the first position where either color reaches 20; forced tail length L=40-T.",
            "complete_shuffle_probability": "1/choose(40,20)",
            "prefix_shuffle_probability": "choose(40-n,20-r)/choose(40,20), for prefix with n draws and r red",
            "complete_L_shuffle_pmf": "2*choose(39-L,19)/choose(40,20), L=1..20",
            "complete_L_quota_pmf": "2*choose(39-L,19)/2^(40-L), L=1..20",
            "iid_complete_20_each_probability": TOTAL_COMBINATIONS / 2 ** 40,
        },
        "phase_statistics": phases,
        "group_statistics": {
            "all_observed_prefixes": group_summary(phases),
            "all_complete_phases": group_summary(complete),
            "first_complete_phase_per_battle": group_summary(first_per_battle(complete)),
            "first_phase_per_reached_battle": group_summary(first_per_battle(phases)),
        },
        "direct_sequence_constraints": {
            "all_complete_sequences_have_20_each": all(p["red"] == p["white"] == 20 for p in complete),
            "all_prefixes_respect_quota_20": all(p["quota_consistent"] for p in phases),
            "max_run_before_or_at_quota": max(p["max_run_before_or_at_quota"] for p in phases),
            "streak_example": {"battle": "B32", "phase": 1, "sequence": "WRRRRRRRRRRWWWRW", "red_run_start_order": 2, "red_run_end_order": 11},
            "rejected_deterministic_rules": ["Strict alternation", "A hard same-color run limit of nine or fewer, even before reaching quota"],
            "not_rejected": ["A hard run cap of ten or greater", "Other dependent or precomputed generators", "Variable-probability generators producing similar sequence distributions"],
        },
        "limitations": [
            "Data-only candidate model comparison, not source-code confirmation or out-of-sample validation.",
            "Complete 40-circle phases come from only six battles; repeated phases in a battle need not be independent.",
            "Battle survival and reaching a complete phase may depend on circle order; the extraction sample also consists of progression attempts.",
            "Prefix likelihood assumes the observed stopping mechanism adds no model-dependent information after conditioning on the observed colors; this cannot be verified here.",
            "Tail p-values and first-20 binomial p-values are nominal independent-trial calculations, not selection-corrected causal or definitive tests.",
            "Quota 20 and model candidates were chosen after inspecting these observations; likelihood ratios do not include this model-selection uncertainty.",
            "Stable marginal/conditional probabilities cannot distinguish a runtime coin algorithm from other generators with the same observed sequence distribution.",
            "No pre-cap next-color prediction is justified; apparent streaks and first-half bias alone cannot determine the next circle.",
        ],
    }
    # Verify finite-distribution normalization and the observed quota accounting.
    assert all(abs(sum(terminal_run_pmf(m).values()) - 1) < 1e-12 for m in ("shuffle", "quota"))
    assert all(p["n"] == p["free_red"] + p["free_white"] + p["observed_after_first_quota"] for p in phases)
    assert len(phases) == 13 and sum(p["n"] for p in phases) == 438
    target = output / "stats.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, group in result["group_statistics"].items():
        print(key, "quota/shuffle LR:", group["quota_vs_shuffle_likelihood_ratio"])
        print("  tail:", group["complete_tail_analysis"])
        print("  before quota:", group["before_quota_minority_rates"])
    print("Wrote", target)


if __name__ == "__main__":
    main()
