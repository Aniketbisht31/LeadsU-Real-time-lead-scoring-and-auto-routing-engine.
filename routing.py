"""Lead assignment rules."""

REPS = ["alex_chen", "sam_taylor", "jordan_lee"]
_round_robin_index = 0


def assign_rep(tier: str) -> str:
    """Assign Hot leads to a senior AE, rotate Warm leads, and nurture Cold leads."""
    global _round_robin_index

    normalized_tier = tier.strip().lower()
    if normalized_tier == "hot":
        return "senior_ae"
    if normalized_tier == "warm":
        rep = REPS[_round_robin_index]
        _round_robin_index = (_round_robin_index + 1) % len(REPS)
        return rep
    if normalized_tier == "cold":
        return "nurture_queue"
    raise ValueError("tier must be Hot, Warm, or Cold")