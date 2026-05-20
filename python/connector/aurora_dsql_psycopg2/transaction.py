# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""OCC retry-aware transaction for psycopg2 pools."""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from dsql_core.occ_retry import OCCRetryConfig

T = TypeVar("T")


def transaction(
    pool: Any,
    callback: Callable[[Any], T],
    *,
    retry: OCCRetryConfig | None = None,
) -> T:
    """Execute callback in a transaction with OCC retry.

    Uses pool.getconn()/pool.putconn() and conn.commit()/conn.rollback().

    Args:
        pool: An AuroraDSQLThreadedConnectionPool instance.
        callback: Callable receiving a connection.
        retry: Retry config. None uses default OCCRetryConfig().

    Returns:
        The return value of the callback.
    """
    raise NotImplementedError
