# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""OCC retry-aware transaction for asyncpg pools."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, TypeVar

from dsql_core.occ_retry import OCCRetryConfig

T = TypeVar("T")


async def transaction(
    pool: Any,
    callback: Callable[[Any], Awaitable[T]],
    *,
    retry: OCCRetryConfig | None = None,
) -> T:
    """Execute callback in a transaction with OCC retry.

    Uses explicit BEGIN/COMMIT/ROLLBACK (asyncpg autocommits by default).

    Args:
        pool: An asyncpg.Pool instance.
        callback: Async callable receiving a connection.
        retry: Retry config. None uses default OCCRetryConfig().

    Returns:
        The return value of the callback.
    """
    raise NotImplementedError
