# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Automatic OCC retry support for Aurora DSQL Python connectors."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OCCRetryConfig:
    """Retry configuration for OCC conflict handling.

    Args:
        max_retries: Retries after initial attempt (3 = 4 total). Range [0, 100].
        base_delay_ms: Base for exponential backoff in ms. Must be > 0.
        max_delay_ms: Delay cap before jitter. Range [base_delay_ms, 100].
        jitter_factor: Random jitter as fraction of delay. Range [0.0, 1.0].

    Raises:
        ValueError: If any parameter is outside its valid range.
    """

    max_retries: int = 3
    base_delay_ms: int = 1
    max_delay_ms: int = 100
    jitter_factor: float = 0.25

    def __post_init__(self) -> None:
        pass


def resolve_retry_config(
    pool_config: OCCRetryConfig | bool | None,
    per_call: OCCRetryConfig | bool | None,
) -> OCCRetryConfig | None:
    """Resolve effective retry config from pool and per-call settings.

    Resolution:
        per_call         → behavior
        None             → pool config as-is (None if pool has none)
        True             → pool config if set, else OCCRetryConfig() defaults
        False            → None (disabled)
        OCCRetryConfig   → use as-is (full replacement, ignores pool)

    Args:
        pool_config: Constructor-level config (OCCRetryConfig, True, or None).
        per_call: Per-call override (OCCRetryConfig, True, False, or None).

    Returns:
        Resolved OCCRetryConfig or None if retry is disabled.
    """
    raise NotImplementedError


def is_occ_error(error: Exception) -> bool:
    """Detect OCC conflict via sqlstate/pgcode attributes.

    Checks err.sqlstate (psycopg/asyncpg) or err.pgcode (psycopg2) for
    codes OC000, OC001, or 40001. For 40001, parses the error message
    for embedded (OC000)/(OC001) markers.

    Args:
        error: Any exception instance to check.

    Returns:
        True if the error represents an OCC conflict.
    """
    raise NotImplementedError


def _calculate_backoff(config: OCCRetryConfig, attempt: int) -> float:
    """Compute backoff delay (ms) for a retry attempt.

    Formula: min(base_delay_ms * 2^min(attempt-1, 31), max_delay_ms) + random jitter

    Args:
        config: Retry configuration with delay parameters.
        attempt: Current attempt number (1-indexed).

    Returns:
        Delay in milliseconds including jitter.
    """
    raise NotImplementedError


def _retry_sync(execute: Callable[[], T], config: OCCRetryConfig) -> T:
    """Internal sync retry loop.

    Each driver constructs an `execute` closure that handles
    acquire/begin/callback/commit/rollback/release. This kernel
    only retries the thunk on OCC errors.

    Args:
        execute: Callable that runs the full transaction attempt.
        config: Retry configuration.

    Returns:
        The return value of execute on success.

    Raises:
        Exception: Last OCC error if all retries exhausted; non-OCC errors immediately.
    """
    raise NotImplementedError


async def _retry_async(
    execute: Callable[[], Awaitable[T]], config: OCCRetryConfig
) -> T:
    """Internal async retry loop.

    Each driver constructs an `execute` coroutine factory that handles
    acquire/begin/callback/commit/rollback/release. This kernel
    only retries the thunk on OCC errors.

    Args:
        execute: Async callable that runs the full transaction attempt.
        config: Retry configuration.

    Returns:
        The return value of execute on success.

    Raises:
        Exception: Last OCC error if all retries exhausted; non-OCC errors immediately.
    """
    raise NotImplementedError
