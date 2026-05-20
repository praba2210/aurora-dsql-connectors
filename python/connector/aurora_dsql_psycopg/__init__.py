# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from dsql_core._version import __version__
from dsql_core.occ_retry import OCCRetryConfig, is_occ_error

from .connection_class import DSQLAsyncConnection, DSQLConnection
from .transaction import transaction, transaction_async

# DBAPI compliance
connect = DSQLConnection.connect
apilevel = "2.0"
threadsafety = 2
paramstyle = "pyformat"


__all__ = [
    "connect",
    "DSQLConnection",
    "DSQLAsyncConnection",
    "transaction",
    "transaction_async",
    "OCCRetryConfig",
    "is_occ_error",
    "__version__",
]
