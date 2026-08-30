import os

import psycopg2
from psycopg2.extras import RealDictCursor


class DatabaseService:
    """
    Handles PostgreSQL database operations for NetSentinel.
    """

    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "netsentinel")
        self.user = os.getenv("DB_USER", "admin")
        self.password = os.getenv("DB_PASSWORD", "admin123")

    def get_connection(self):
        """
        Create and return a PostgreSQL database connection.
        """
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
        )

    def test_connection(self):
        """
        Test whether NetSentinel can connect to PostgreSQL.
        """
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                result = cursor.fetchone()

            return result[0] == 1

        finally:
            connection.close()

    def get_tables(self):
        """
        Return the tables available in the public schema.
        """
        connection = self.get_connection()

        try:
            with connection.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:

                cursor.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                    """
                )

                return [
                    row["table_name"]
                    for row in cursor.fetchall()
                ]

        finally:
            connection.close()

    # ========================================================
    # Performance Results
    # ========================================================

    def insert_performance_result(
        self,
        test_type,
        average_latency,
        p95_latency,
        total_requests,
        failed_requests,
        packet_loss,
        error_rate,
    ):
        """
        Store k6/network performance results in PostgreSQL.
        """

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO performance_results (
                        test_type,
                        average_latency_ms,
                        p95_latency_ms,
                        total_requests,
                        failed_requests,
                        packet_loss_percent,
                        error_rate_percent
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        test_type,
                        average_latency,
                        p95_latency,
                        total_requests,
                        failed_requests,
                        packet_loss,
                        error_rate,
                    ),
                )

            connection.commit()

        finally:
            connection.close()

    # ========================================================
    # Postman Results
    # ========================================================

    def insert_postman_result(
        self,
        total_requests,
        failed_requests,
        total_assertions,
        failed_assertions,
        average_response_time,
    ):
        """
        Store Postman test results in PostgreSQL.
        """

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO postman_results (
                        total_requests,
                        failed_requests,
                        total_assertions,
                        failed_assertions,
                        average_response_time_ms
                    )
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (
                        total_requests,
                        failed_requests,
                        total_assertions,
                        failed_assertions,
                        average_response_time,
                    ),
                )

            connection.commit()

        finally:
            connection.close()

    # ========================================================
    # Network Connectivity
    # ========================================================

    def insert_network_connectivity(
        self,
        source,
        destination,
        status,
        latency_ms,
        packet_loss=0,
    ):
        """
        Store network connectivity results in PostgreSQL.
        """

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO network_connectivity (
                        source,
                        destination,
                        status,
                        latency_ms,
                        packet_loss_percent
                    )
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (
                        source,
                        destination,
                        status,
                        latency_ms,
                        packet_loss,
                    ),
                )

            connection.commit()

        finally:
            connection.close()

    # ========================================================
    # Test Runs
    # ========================================================

    def start_test_run(
        self,
        test_name,
        test_type,
    ):
        """
        Create a new test run and return its ID.
        """

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO test_runs (
                        test_name,
                        test_type,
                        status
                    )
                    VALUES (%s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        test_name,
                        test_type,
                        "RUNNING",
                    ),
                )

                run_id = cursor.fetchone()[0]

            connection.commit()

            return run_id

        finally:
            connection.close()

    def complete_test_run(self, run_id):
        """
        Mark a test run as completed.
        """

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE test_runs
                    SET
                        status = %s,
                        completed_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (
                        "COMPLETED",
                        run_id,
                    ),
                )

            connection.commit()

        finally:
            connection.close()

    def get_test_runs(self):
        """
        Return recent test runs.
        """

        connection = self.get_connection()

        try:
            with connection.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        test_name,
                        test_type,
                        status,
                        started_at,
                        completed_at,
                        created_at
                    FROM test_runs
                    ORDER BY id DESC;
                    """
                )

                return cursor.fetchall()

        finally:
            connection.close()

    # ========================================================
    # AI Reports
    # ========================================================

    def insert_ai_report(
        self,
        report_type,
        report_content,
    ):
        """
        Store an AI-generated report in PostgreSQL.

        report_type:
            executive_summary
            detailed_report
        """

        if not report_content or not report_content.strip():
            raise ValueError(
                "AI report content cannot be empty."
            )

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO ai_reports (
                        report_type,
                        report_content
                    )
                    VALUES (%s, %s)
                    RETURNING id;
                    """,
                    (
                        report_type,
                        report_content.strip(),
                    ),
                )

                report_id = cursor.fetchone()[0]

            connection.commit()

            return report_id

        finally:
            connection.close()

    def get_latest_ai_report(
        self,
        report_type,
    ):
        """
        Return the latest AI report of the specified type.
        """

        connection = self.get_connection()

        try:
            with connection.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        report_type,
                        report_content,
                        created_at
                    FROM ai_reports
                    WHERE report_type = %s
                    ORDER BY created_at DESC
                    LIMIT 1;
                    """,
                    (report_type,),
                )

                return cursor.fetchone()

        finally:
            connection.close()

    def get_ai_reports(self):
        """
        Return all AI reports, newest first.
        """

        connection = self.get_connection()

        try:
            with connection.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        report_type,
                        report_content,
                        created_at
                    FROM ai_reports
                    ORDER BY created_at DESC;
                    """
                )

                return cursor.fetchall()

        finally:
            connection.close()