/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package software.amazon.dsql.jdbc;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.sql.SQLException;
import org.junit.jupiter.api.Test;

class OCCRetryTest {

    @Test
    void isOCCError_null_returnsFalse() {
        assertFalse(OCCRetry.isOCCError(null));
    }

    @Test
    void isOCCError_nullSqlState_returnsFalse() {
        SQLException e = new SQLException("some error", (String) null);
        assertFalse(OCCRetry.isOCCError(e));
    }

    @Test
    void isOCCError_mutationConflict_returnsTrue() {
        SQLException e = new SQLException("conflict", "OC000");
        assertTrue(OCCRetry.isOCCError(e));
    }

    @Test
    void isOCCError_schemaConflict_returnsTrue() {
        SQLException e = new SQLException("conflict", "OC001");
        assertTrue(OCCRetry.isOCCError(e));
    }

    @Test
    void isOCCError_serializationFailure_returnsTrue() {
        SQLException e = new SQLException("conflict", "40001");
        assertTrue(OCCRetry.isOCCError(e));
    }

    @Test
    void isOCCError_unrecognizedState_returnsFalse() {
        SQLException e = new SQLException("something else", "42000");
        assertFalse(OCCRetry.isOCCError(e));
    }

    @Test
    void isOCCError_messageContainsOC000_returnsTrue() {
        SQLException e = new SQLException("ERROR: OC000 mutation conflict detected", "XX000");
        assertTrue(OCCRetry.isOCCError(e));
    }

    @Test
    void isOCCError_messageContainsOC001_returnsTrue() {
        SQLException e = new SQLException("ERROR: OC001 schema conflict", "XX000");
        assertTrue(OCCRetry.isOCCError(e));
    }

    @Test
    void isOCCError_nullMessage_returnsFalse() {
        SQLException e = new SQLException(null, "XX000");
        assertFalse(OCCRetry.isOCCError(e));
    }
}
