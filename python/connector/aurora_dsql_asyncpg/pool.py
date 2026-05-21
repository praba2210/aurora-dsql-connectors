# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any, Awaitable, Callable, TypeVar

import asyncpg

from aurora_dsql_occ_retry import OCCRetryConfig

from .connector import connect as dsql_connect

T = TypeVar("T")


class AuroraDSQLPool(asyncpg.Pool):
    """Aurora DSQL connection pool with OCC retry support.

    Subclasses asyncpg.Pool so isinstance checks, typing, and all
    upstream methods continue to work unchanged.
    """

    __slots__ = ("_retry",)

    def __init__(self, *connect_args, retry: OCCRetryConfig | bool | None = None, **kwargs):
        self._retry = retry
        super().__init__(*connect_args, **kwargs)

    async def run_transaction(
        self,
        callback: Callable[[asyncpg.Connection], Awaitable[T]],
        *,
        retry: OCCRetryConfig | bool | None = None,
    ) -> T:
        """Execute callback in a transaction with OCC retry.

        Uses explicit BEGIN/COMMIT/ROLLBACK (asyncpg autocommits by default).

        Args:
            callback: Async callable receiving an asyncpg Connection.
            retry: Per-call override. None inherits pool config; True enables
                   with pool/default config; False disables;
                   OCCRetryConfig replaces pool config entirely.

        Returns:
            The return value of the callback.
        """
        raise NotImplementedError


async def create_pool(
    dsn=None,
    *,
    retry: OCCRetryConfig | bool | None = None,
    min_size=10,
    max_size=10,
    max_queries=50000,
    max_inactive_connection_lifetime=300.0,
    setup=None,
    init=None,
    reset=None,
    loop=None,
    connection_class=asyncpg.Connection,
    record_class=asyncpg.Record,
    **connect_kwargs: Any,
) -> AuroraDSQLPool:
    """Create Aurora DSQL connection pool with fresh token generation."""

    async def reset_connection(conn):
        await conn.execute("RESET ALL;")

    return await AuroraDSQLPool(
        dsn,
        retry=retry,
        min_size=min_size,
        max_size=max_size,
        max_queries=max_queries,
        max_inactive_connection_lifetime=max_inactive_connection_lifetime,
        connect=dsql_connect,
        setup=setup,
        init=init,
        reset=reset or reset_connection,
        loop=loop,
        connection_class=connection_class,
        record_class=record_class,
        **connect_kwargs,
    )
