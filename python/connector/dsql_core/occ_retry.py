# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Automatic OCC retry support for Aurora DSQL Python connectors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class OCCRetryConfig:
    """Retry configuration. Defaults match Rust/Node connectors.

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
        """Validate all fields on construction."""
        raise NotImplementedError


def is_occ_error(error: Exception) -> bool:
    """Detect OCC conflict via err.sqlstate (psycopg/asyncpg) or err.pgcode (psycopg2).

    Matches codes: OC000, OC001, 40001.

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


def _retry_sync(
    acquire: Callable[[], Any],
    release: Callable[[Any], None],
    commit: Callable[[Any], None],
    rollback: Callable[[Any], None],
    callback: Callable[[Any], T],
    config: OCCRetryConfig,
) -> T:
    """Internal sync retry loop. Called by per-driver pool.transaction() methods.

    Args:
        acquire: Obtain a connection from the pool.
        release: Return a connection to the pool.
        commit: Commit the transaction on a connection.
        rollback: Rollback the transaction on a connection.
        callback: User callable receiving a connection.
        config: Retry configuration.

    Returns:
        The return value of the callback on success.

    Raises:
        Exception: Last OCC error if all retries exhausted; non-OCC errors immediately.
    """
    raise NotImplementedError


async def _retry_async(
    acquire: Callable[[], Awaitable[Any]],
    release: Callable[[Any], Awaitable[None]],
    commit: Callable[[Any], Awaitable[None]],
    rollback: Callable[[Any], Awaitable[None]],
    callback: Callable[[Any], Awaitable[T]],
    config: OCCRetryConfig,
) -> T:
    """Internal async retry loop. Called by per-driver pool.transaction() methods.

    Args:
        acquire: Obtain a connection from the pool.
        release: Return a connection to the pool.
        commit: Commit the transaction on a connection.
        rollback: Rollback the transaction on a connection.
        callback: Async user callable receiving a connection.
        config: Retry configuration.

    Returns:
        The return value of the callback on success.

    Raises:
        Exception: Last OCC error if all retries exhausted; non-OCC errors immediately.
    """
    raise NotImplementedError
