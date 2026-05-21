# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""OCC retry-aware pool classes for psycopg."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, TypeVar

from psycopg import AsyncConnection, Connection
from psycopg_pool import AsyncConnectionPool, ConnectionPool

from aurora_dsql_occ_retry import OCCRetryConfig

from .connection_class import DSQLAsyncConnection, DSQLConnection

T = TypeVar("T")


class AuroraDSQLPool(ConnectionPool):
    """Aurora DSQL connection pool with OCC retry support.

    Subclasses psycopg_pool.ConnectionPool so isinstance checks, typing,
    and all upstream methods continue to work unchanged.
    """

    def __init__(self, *args, retry: OCCRetryConfig | bool | None = None, **kwargs):
        self._retry = retry
        super().__init__(*args, **kwargs)

    def run_transaction(
        self,
        callback: Callable[[Connection], T],
        *,
        retry: OCCRetryConfig | bool | None = None,
    ) -> T:
        """Execute callback in a transaction with OCC retry.

        Uses implicit transactions (psycopg autocommit=False default).

        Args:
            callback: Callable receiving a psycopg Connection.
            retry: Per-call override. None inherits pool config; True enables
                   with pool/default config; False disables;
                   OCCRetryConfig replaces pool config entirely.

        Returns:
            The return value of the callback.
        """
        raise NotImplementedError


class AuroraDSQLAsyncPool(AsyncConnectionPool):
    """Aurora DSQL async connection pool with OCC retry support.

    Subclasses psycopg_pool.AsyncConnectionPool so isinstance checks, typing,
    and all upstream methods continue to work unchanged.
    """

    def __init__(self, *args, retry: OCCRetryConfig | bool | None = None, **kwargs):
        self._retry = retry
        super().__init__(*args, **kwargs)

    async def run_transaction(
        self,
        callback: Callable[[AsyncConnection], Awaitable[T]],
        *,
        retry: OCCRetryConfig | bool | None = None,
    ) -> T:
        """Execute callback in a transaction with OCC retry.

        Uses implicit transactions (psycopg autocommit=False default).

        Args:
            callback: Async callable receiving a psycopg AsyncConnection.
            retry: Per-call override. None inherits pool config; True enables
                   with pool/default config; False disables;
                   OCCRetryConfig replaces pool config entirely.

        Returns:
            The return value of the callback.
        """
        raise NotImplementedError


def create_pool(
    conninfo: str = "",
    *,
    retry: OCCRetryConfig | bool | None = None,
    **kwargs: Any,
) -> AuroraDSQLPool:
    """Create Aurora DSQL connection pool with IAM authentication.

    Args:
        conninfo: Connection string or DSQL hostname.
        retry: Pool-level retry config. None disables; True enables defaults.
        **kwargs: Passed to psycopg_pool.ConnectionPool.
    """
    kwargs.setdefault("connection_class", DSQLConnection)
    return AuroraDSQLPool(conninfo, retry=retry, **kwargs)


def create_async_pool(
    conninfo: str = "",
    *,
    retry: OCCRetryConfig | bool | None = None,
    **kwargs: Any,
) -> AuroraDSQLAsyncPool:
    """Create Aurora DSQL async connection pool with IAM authentication.

    Args:
        conninfo: Connection string or DSQL hostname.
        retry: Pool-level retry config. None disables; True enables defaults.
        **kwargs: Passed to psycopg_pool.AsyncConnectionPool.
    """
    kwargs.setdefault("connection_class", DSQLAsyncConnection)
    return AuroraDSQLAsyncPool(conninfo, retry=retry, **kwargs)
