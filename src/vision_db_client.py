"""
Vision PostgreSQL Database Client

This module provides a client for connecting to and querying the Vision PostgreSQL database.
It replaces the CSV-based approach with direct database queries for real-time data access.
"""

import psycopg2
import pandas as pd
from typing import Dict, List, Optional, Any
import logging
from contextlib import contextmanager


class VisionDBClient:
    """Client for connecting to and querying the Vision PostgreSQL database."""
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """
        Initialize the Vision database client.
        
        Args:
            host: Database host address
            port: Database port number
            database: Database name
            user: Database username
            password: Database password
        """
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        self._connection = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        connection = None
        try:
            connection = psycopg2.connect(**self.connection_params)
            yield connection
        except Exception as e:
            self.logger.error(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    def test_connection(self) -> bool:
        """
        Test the database connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.logger.info("Database connection successful!")
                return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_table_list(self) -> List[str]:
        """
        Get list of all tables in the database.
        
        Returns:
            List[str]: List of table names
        """
        try:
            with self.get_connection() as conn:
                query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
                """
                df = pd.read_sql_query(query, conn)
                return df['table_name'].tolist()
        except Exception as e:
            self.logger.error(f"Error getting table list: {e}")
            return []
    
    def get_table_schema(self, table_name: str) -> pd.DataFrame:
        """
        Get schema information for a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            pd.DataFrame: Table schema information
        """
        try:
            with self.get_connection() as conn:
                query = """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
                """
                df = pd.read_sql_query(query, conn, params=[table_name])
                return df
        except Exception as e:
            self.logger.error(f"Error getting schema for table {table_name}: {e}")
            return pd.DataFrame()
    
    def execute_query(self, query: str, params: Optional[List] = None) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            pd.DataFrame: Query results
        """
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)
                self.logger.info(f"Query executed successfully. Returned {len(df)} rows.")
                return df
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def get_allocations(self, start_date: Optional[str] = None, end_date: Optional[str] = None, simulation_id: Optional[int] = 28) -> pd.DataFrame:
        """
        Get allocation data from Vision database.
        
        Args:
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
            simulation_id: Simulation ID to filter by (default: 28)
            
        Returns:
            pd.DataFrame: Allocation data
        """
        base_query = """
        SELECT 
            a.*,
            CONCAT(e.first_name, ' ', e.last_name) as employee_name,
            e.first_name,
            e.last_name,
            e.employee_number,
            p.name as project_name,
            p.project_number,
            c.name as client_name
        FROM allocations a
        LEFT JOIN employees e ON a.employee_id = e.id
        LEFT JOIN projects p ON a.project_id = p.id
        LEFT JOIN clients c ON p.client_id = c.id
        """
        
        conditions = []
        params = []
        
        # CRITICAL: Filter by simulation_id first
        if simulation_id is not None:
            conditions.append("a.simulation_id = %s")
            params.append(simulation_id)
        
        # Filter based on start_date and end_date of allocations
        # An allocation is relevant if it overlaps with our date range
        if start_date and end_date:
            conditions.append("(a.start_date <= %s AND (a.end_date IS NULL OR a.end_date >= %s))")
            params.extend([end_date, start_date])
        elif start_date:
            conditions.append("(a.end_date IS NULL OR a.end_date >= %s)")
            params.append(start_date)
        elif end_date:
            conditions.append("a.start_date <= %s")
            params.append(end_date)
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " ORDER BY a.start_date, e.first_name, e.last_name"
        
        return self.execute_query(base_query, params)
    
    def get_employees(self, simulation_id: Optional[int] = 28) -> pd.DataFrame:
        """
        Get employee data from Vision database.
        
        Args:
            simulation_id: Simulation ID to filter by (default: 28)
        
        Returns:
            pd.DataFrame: Employee data
        """
        query = """
        SELECT 
            id,
            simulation_id,
            original_id,
            employee_number,
            first_name,
            last_name,
            CONCAT(first_name, ' ', last_name) as name,
            office_id,
            start_date,
            end_date,
            created_at,
            updated_at,
            deleted_at,
            promoted_at
        FROM employees
        """
        
        params = []
        if simulation_id is not None:
            query += " WHERE simulation_id = %s"
            params.append(simulation_id)
        
        query += " ORDER BY first_name, last_name"
        
        return self.execute_query(query, params)
    
    def get_projects(self, simulation_id: Optional[int] = 28) -> pd.DataFrame:
        """
        Get project data from Vision database.
        
        Args:
            simulation_id: Simulation ID to filter by (default: 28)
        
        Returns:
            pd.DataFrame: Project data
        """
        query = """
        SELECT 
            p.*,
            c.name as client_name
        FROM projects p
        LEFT JOIN clients c ON p.client_id = c.id
        """
        
        params = []
        if simulation_id is not None:
            query += " WHERE p.simulation_id = %s"
            params.append(simulation_id)
        
        query += " ORDER BY p.name"
        
        return self.execute_query(query, params)
    
    def get_clients(self, simulation_id: Optional[int] = 28) -> pd.DataFrame:
        """
        Get client data from Vision database.
        
        Args:
            simulation_id: Simulation ID to filter by (default: 28)
        
        Returns:
            pd.DataFrame: Client data
        """
        query = """
        SELECT 
            c.id,
            c.name,
            c.office_id,
            c.original_id,
            c.simulation_id,
            c.created_at,
            c.updated_at,
            c.deleted_at,
            c.promoted_at,
            o.name as office_name,
            o.country,
            o.location
        FROM clients c
        LEFT JOIN office o ON c.office_id = o.id
        """
        
        params = []
        if simulation_id is not None:
            query += " WHERE c.simulation_id = %s"
            params.append(simulation_id)
        
        query += " ORDER BY name"
        
        return self.execute_query(query, params)
    
    def get_max_simulation_id(self) -> int:
        """
        Get the maximum available simulation ID from the database.
        
        Returns:
            int: Maximum simulation ID available
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check allocations table first (most likely to have simulation_id)
                self.logger.info("Checking allocations table for maximum simulation_id...")
                cursor.execute("SELECT MAX(simulation_id) FROM allocations WHERE simulation_id IS NOT NULL")
                result = cursor.fetchone()
                if result and result[0] is not None:
                    self.logger.info(f"Found maximum simulation_id {result[0]} in allocations table")
                    return result[0]
                
                # Fallback to employees table
                self.logger.info("Checking employees table for maximum simulation_id...")
                cursor.execute("SELECT MAX(simulation_id) FROM employees WHERE simulation_id IS NOT NULL")
                result = cursor.fetchone()
                if result and result[0] is not None:
                    self.logger.info(f"Found maximum simulation_id {result[0]} in employees table")
                    return result[0]
                
                # Fallback to projects table
                self.logger.info("Checking projects table for maximum simulation_id...")
                cursor.execute("SELECT MAX(simulation_id) FROM projects WHERE simulation_id IS NOT NULL")
                result = cursor.fetchone()
                if result and result[0] is not None:
                    self.logger.info(f"Found maximum simulation_id {result[0]} in projects table")
                    return result[0]
                
                # Fallback to clients table
                self.logger.info("Checking clients table for maximum simulation_id...")
                cursor.execute("SELECT MAX(simulation_id) FROM clients WHERE simulation_id IS NOT NULL")
                result = cursor.fetchone()
                if result and result[0] is not None:
                    self.logger.info(f"Found maximum simulation_id {result[0]} in clients table")
                    return result[0]
                
                # If no simulation_id found, return default
                self.logger.warning("No simulation_id found in any table, returning default value 28")
                return 28
                
        except Exception as e:
            self.logger.error(f"Error getting maximum simulation ID: {e}")
            return 28

    def get_confidences(self, simulation_id: Optional[int] = 28) -> pd.DataFrame:
        """
        Get confidence data from Vision database.
        
        Args:
            simulation_id: Simulation ID to filter by (default: 28)
        
        Returns:
            pd.DataFrame: Confidence data
        """
        query = """
        SELECT 
            id,
            simulation_id,
            original_id,
            name,
            numerator,
            denominator,
            pre_leave_value,
            factor,
            created_at,
            updated_at,
            deleted_at,
            promoted_at
        FROM confidences
        """
        
        params = []
        if simulation_id is not None:
            query += " WHERE simulation_id = %s"
            params.append(simulation_id)
        
        query += " ORDER BY name"
        
        return self.execute_query(query, params)
    
    def get_calendars(self, simulation_id: Optional[int] = 28) -> pd.DataFrame:
        """
        Get calendar data from Vision database.
        
        Args:
            simulation_id: Simulation ID to filter by (default: 28)
        
        Returns:
            pd.DataFrame: Calendar data
        """
        query = """
        SELECT 
            id,
            simulation_id,
            original_id,
            name,
            start_date,
            end_date,
            created_at,
            updated_at,
            deleted_at,
            promoted_at
        FROM calendars
        """
        
        params = []
        if simulation_id is not None:
            query += " WHERE simulation_id = %s"
            params.append(simulation_id)
        
        query += " ORDER BY name"
        
        return self.execute_query(query, params)
    
    def get_calendar_holidays(self, simulation_id: Optional[int] = 28) -> pd.DataFrame:
        """
        Get calendar holidays data from Vision database.
        
        Args:
            simulation_id: Simulation ID to filter by (default: 28)
        
        Returns:
            pd.DataFrame: Calendar holidays data
        """
        query = """
        SELECT 
            h.*,
            c.name as calendar_name
        FROM calendar_holidays h
        LEFT JOIN calendars c ON h.calendar_id = c.id
        """
        
        params = []
        if simulation_id is not None:
            query += " WHERE h.simulation_id = %s"
            params.append(simulation_id)
        
        query += " ORDER BY h.date, c.name"
        
        return self.execute_query(query, params)
    
    def get_currencies(self, simulation_id: Optional[int] = 28) -> pd.DataFrame:
        """
        Get currency data from Vision database.
        
        Args:
            simulation_id: Simulation ID to filter by (default: 28)
        
        Returns:
            pd.DataFrame: Currency data
        """
        query = """
        SELECT 
            id,
            code,
            name,
            symbol,
            is_active,
            created_at,
            updated_at,
            deleted_at,
            simulation_id,
            original_id,
            promoted_at
        FROM currencies
        """
        
        params = []
        if simulation_id is not None:
            query += " WHERE simulation_id = %s"
            params.append(simulation_id)
        
        query += " ORDER BY code"
        
        return self.execute_query(query, params)
    
    def get_exchange_rates(self, simulation_id: Optional[int] = 28) -> pd.DataFrame:
        """
        Get exchange rates data from Vision database.
        
        Args:
            simulation_id: Simulation ID to filter by (default: 28)
        
        Returns:
            pd.DataFrame: Exchange rates data
        """
        query = """
        SELECT 
            er.*,
            fc.code as from_currency_code,
            fc.name as from_currency_name,
            tc.code as to_currency_code,
            tc.name as to_currency_name
        FROM exchange_rates er
        LEFT JOIN currencies fc ON er.from_currency_id = fc.id
        LEFT JOIN currencies tc ON er.to_currency_id = tc.id
        """
        
        params = []
        if simulation_id is not None:
            query += " WHERE er.simulation_id = %s"
            params.append(simulation_id)
        
        query += " ORDER BY er.date DESC, fc.code, tc.code"
        
        return self.execute_query(query, params)
    
    def get_office(self, simulation_id: Optional[int] = 28) -> pd.DataFrame:
        """
        Get office data from Vision database.
        
        Args:
            simulation_id: Simulation ID to filter by (default: 28)
        
        Returns:
            pd.DataFrame: Office data
        """
        query = """
        SELECT 
            o.*,
            c.name as calendar_name
        FROM office o
        LEFT JOIN calendars c ON o.calendar_id = c.id
        """
        
        params = []
        if simulation_id is not None:
            query += " WHERE o.simulation_id = %s"
            params.append(simulation_id)
        
        query += " ORDER BY o.name"
        
        return self.execute_query(query, params)
    
    def get_salaries(self, simulation_id: Optional[int] = 28) -> pd.DataFrame:
        """
        Get salary data from Vision database.
        
        Args:
            simulation_id: Simulation ID to filter by (default: 28)
        
        Returns:
            pd.DataFrame: Salary data
        """
        query = """
        SELECT 
            s.*,
            CONCAT(e.first_name, ' ', e.last_name) as employee_name,
            e.first_name,
            e.last_name,
            e.employee_number,
            c.code as currency_code,
            c.name as currency_name,
            c.symbol as currency_symbol
        FROM salaries s
        LEFT JOIN employees e ON s.employee_id = e.id
        LEFT JOIN currencies c ON s.currency_id = c.id
        """
        
        params = []
        if simulation_id is not None:
            query += " WHERE s.simulation_id = %s"
            params.append(simulation_id)
        
        query += " ORDER BY e.first_name, e.last_name, s.start_date"
        
        return self.execute_query(query, params)
    
    def get_table_sample(self, table_name: str, limit: int = 10) -> pd.DataFrame:
        """
        Get a sample of data from any table.
        
        Args:
            table_name: Name of the table
            limit: Number of rows to return
            
        Returns:
            pd.DataFrame: Sample data
        """
        query = f"SELECT * FROM {table_name} LIMIT %s"
        return self.execute_query(query, [limit])
    
    def get_simulation(self, simulation_id: Optional[int] = 28) -> pd.DataFrame:
        """
        Get simulation data from Vision database.
        
        Args:
            simulation_id: Simulation ID to filter by (default: 28)
        
        Returns:
            pd.DataFrame: Simulation data
        """
        query = """
        SELECT 
            id,
            name,
            start_date,
            end_date,
            projection,
            is_saved,
            created_at,
            updated_at,
            deleted_at,
            user_account_id,
            description,
            is_promoted,
            promoted_at,
            promoted_to_main,
            is_auto_preserved,
            preserved_at,
            preserved_from_main_version,
            parent_simulation_id
        FROM simulation
        """
        
        params = []
        if simulation_id is not None:
            query += " WHERE id = %s"
            params.append(simulation_id)
        
        query += " ORDER BY created_at DESC"
        
        return self.execute_query(query, params)
    
    def get_titles(self, simulation_id: Optional[int] = 28) -> pd.DataFrame:
        """
        Get titles data from Vision database.
        
        Args:
            simulation_id: Simulation ID to filter by (default: 28)
        
        Returns:
            pd.DataFrame: Titles data
        """
        query = """
        SELECT 
            id,
            simulation_id,
            original_id,
            name,
            description,
            "order",
            promoted_at,
            created_at,
            updated_at,
            deleted_at
        FROM titles
        """
        
        params = []
        if simulation_id is not None:
            query += " WHERE simulation_id = %s"
            params.append(simulation_id)
        
        query += " ORDER BY \"order\", name"
        
        return self.execute_query(query, params)


# Configuration for Vision database connection
VISION_DB_CONFIG = {
    'host': 'es-estimator-prod.cr4ky28gqfse.af-south-1.rds.amazonaws.com',
    'port': 5432,
    'database': 'es_dashboard',  # Vision data is in es_dashboard database
    'user': 'readonly_user',
    'password': 'zxL%rZiergbpRv1'
}


def create_vision_client() -> VisionDBClient:
    """
    Create and return a Vision database client instance.
    
    Returns:
        VisionDBClient: Configured database client
    """
    return VisionDBClient(**VISION_DB_CONFIG)


if __name__ == "__main__":
    # Test the database connection
    print("Testing Vision database connection...")
    
    client = create_vision_client()
    
    if client.test_connection():
        print("✅ Connection successful!")
        
        # Get table list
        print("\n📋 Available tables:")
        tables = client.get_table_list()
        for table in tables:
            print(f"  - {table}")
        
        # Test some basic queries if tables exist
        if tables:
            print(f"\n🔍 Sample from first table ({tables[0]}):")
            sample = client.get_table_sample(tables[0], 5)
            print(sample.head())
            
            # Test maximum simulation ID
            print(f"\n🎯 Maximum simulation ID: {client.get_max_simulation_id()}")
            
    else:
        print("❌ Connection failed!")
