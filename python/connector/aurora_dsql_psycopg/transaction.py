# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""OCC retry-aware transactions for psycopg pools."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, TypeVar

from dsql_core.occ_retry import OCCRetryConfig

T = TypeVar("T")


def transaction(
    pool: Any,
    callback: Callable[[Any], T],
    *,
    retry: OCCRetryConfig | None = None,
) -> T:
    """Execute callback in a transaction with OCC retry (sync).

    Uses implicit transactions (psycopg autocommit=False default).

    Args:
        pool: A psycopg_pool.ConnectionPool instance.
        callback: Callable receiving a connection.
        retry: Retry config. None uses default OCCRetryConfig().

    Returns:
        The return value of the callback.
    """
    raise NotImplementedError


async def transaction_async(
    pool: Any,
    callback: Callable[[Any], Awaitable[T]],
    *,
    retry: OCCRetryConfig | None = None,
) -> T:
    """Execute callback in a transaction with OCC retry (async).

    Uses implicit transactions (psycopg autocommit=False default).

    Args:
        pool: A psycopg_pool.AsyncConnectionPool instance.
        callback: Async callable receiving a connection.
        retry: Retry config. None uses default OCCRetryConfig().

    Returns:
        The return value of the callback.
    """
    raise NotImplementedError
