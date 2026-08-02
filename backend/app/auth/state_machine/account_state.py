from enum import Enum
from typing import NamedTuple


class AccountState(str, Enum):
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    ACTIVE = "active"
    LOCKED = "locked"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class StateTransitionResult(NamedTuple):
    allowed: bool
    from_state: AccountState
    to_state: AccountState
    reason: str


VALID_TRANSITIONS: dict[AccountState, set[AccountState]] = {
    AccountState.PENDING_VERIFICATION: {AccountState.VERIFIED, AccountState.DELETED},
    AccountState.VERIFIED: {AccountState.ACTIVE, AccountState.SUSPENDED, AccountState.DELETED},
    AccountState.ACTIVE: {AccountState.LOCKED, AccountState.SUSPENDED, AccountState.DELETED},
    AccountState.LOCKED: {AccountState.ACTIVE, AccountState.SUSPENDED, AccountState.DELETED},
    AccountState.SUSPENDED: {AccountState.ACTIVE, AccountState.DELETED},
    AccountState.DELETED: set(),  # Terminal state
}


class AccountStateMachine:
    """Manages legal user account status transitions and business rules."""

    @staticmethod
    def can_transition(current: AccountState, target: AccountState) -> StateTransitionResult:
        allowed = target in VALID_TRANSITIONS.get(current, set())
        if allowed:
            return StateTransitionResult(
                allowed=True,
                from_state=current,
                to_state=target,
                reason=f"Transition from {current.value} to {target.value} is valid.",
            )
        return StateTransitionResult(
            allowed=False,
            from_state=current,
            to_state=target,
            reason=f"Invalid account state transition from {current.value} to {target.value}.",
        )
