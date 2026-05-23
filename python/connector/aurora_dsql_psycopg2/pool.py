# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Callable, TypeVar

import psycopg2
from botocore.credentials import CredentialProvider
from psycopg2 import pool
from psycopg2.extensions import connection

from dsql_core.connection_properties import ConnectionProperties, build_application_name
from dsql_core.token_manager import TokenManager
from aurora_dsql_occ_retry import OCCRetryConfig

T = TypeVar("T")


class AuroraDSQLThreadedConnectionPool(pool.ThreadedConnectionPool):
    """Custom ThreadedConnectionPool that generates fresh IAM tokens per connection."""

    def __init__(
        self,
        minconn,
        maxconn,
        *args,
        retry: OCCRetryConfig | bool | None = None,
        custom_credentials_provider: CredentialProvider | None = None,
        **kwargs,
    ):
        self._retry = retry

        if custom_credentials_provider is not None:
            kwargs["custom_credentials_provider"] = custom_credentials_provider

        dsql_params, pool_params = ConnectionProperties.parse_properties(None, kwargs)
        self._dsql_params = dsql_params

        # Set application_name with optional ORM prefix
        orm_prefix = pool_params.get("application_name")
        pool_params["application_name"] = build_application_name("psycopg2", orm_prefix)

        # Initialize with dummy password, will be replaced per connection
        super().__init__(minconn, maxconn, *args, **pool_params)

    def _connect(self, key=None):
        """Create connection with fresh IAM token."""
        token = TokenManager.get_token(self._dsql_params)

        # Update kwargs with fresh token
        self._kwargs["password"] = token

        # Create connection
        conn = psycopg2.connect(*self._args, **self._kwargs)
        if key is not None:
            self._used[key] = conn
            self._rused[id(conn)] = key
        else:
            self._pool.append(conn)
        return conn

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and close all connections."""
        self.closeall()
        return False

    def run_transaction(
        self,
        callback: Callable[[connection], T],
        *,
        retry: OCCRetryConfig | bool | None = None,
    ) -> T:
        """Execute callback in a transaction with OCC retry.

        Uses getconn()/putconn() and conn.commit()/conn.rollback().

        Args:
            callback: Callable receiving a psycopg2 connection.
            retry: Per-call override. None inherits pool config; True enables
                   with pool/default config; False disables;
                   OCCRetryConfig replaces pool config entirely.

        Returns:
            The return value of the callback.
        """
        raise NotImplementedError
