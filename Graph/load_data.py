#!/usr/bin/env python3
"""
Load data from PostgreSQL (Substreams) database and save to local files
This script connects to the PostgreSQL database created by substreams-sink-sql
and exports all data to JSON and CSV files for analysis.
"""

import psycopg2
import json
import csv
import pandas as pd
from datetime import datetime
from pathlib import Path
import os
from typing import Dict, List, Any

# ============================================================================
# CONFIGURATION
# ============================================================================

# Database connection settings (matching our Docker setup)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'substreams',
    'user': 'postgres',
    'password': 'password'
}

# Output directory for saved data
OUTPUT_DIR = Path(__file__).parent / "exported_data"
OUTPUT_DIR.mkdir(exist_ok=True)

# Tables to export
TABLES_TO_EXPORT = [
    'instructions',
    'transfers', 
    'mints',
    'burns',
    'initialized_accounts',
    '_blocks_',
    '_cursor_'
]

# ============================================================================
# DATABASE CONNECTION FUNCTIONS
# ============================================================================

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print(f"✅ Connected to PostgreSQL database: {DB_CONFIG['database']}")
        return conn
    except psycopg2.Error as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def get_table_data(conn, table_name: str) -> List[Dict[str, Any]]:
    """Fetch all data from a specific table"""
    try:
        cursor = conn.cursor()
        
        # Get column names
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in cursor.fetchall()]
        
        # Get all data
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY 1")
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        data = []
        for row in rows:
            row_dict = {}
            for i, value in enumerate(row):
                # Convert datetime objects to string for JSON serialization
                if hasattr(value, 'isoformat'):
                    row_dict[columns[i]] = value.isoformat()
                else:
                    row_dict[columns[i]] = value
            data.append(row_dict)
        
        cursor.close()
        print(f"📊 Fetched {len(data)} rows from table '{table_name}'")
        return data
        
    except psycopg2.Error as e:
        print(f"❌ Error fetching data from {table_name}: {e}")
        return []

def get_table_stats(conn) -> Dict[str, int]:
    """Get row counts for all tables"""
    try:
        cursor = conn.cursor()
        stats = {}
        
        for table in TABLES_TO_EXPORT:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            stats[table] = count
            
        cursor.close()
        return stats
        
    except psycopg2.Error as e:
        print(f"❌ Error getting table stats: {e}")
        return {}

# ============================================================================
# DATA EXPORT FUNCTIONS
# ============================================================================

def save_to_json(data: List[Dict[str, Any]], filename: str):
    """Save data to JSON file"""
    filepath = OUTPUT_DIR / f"{filename}.json"
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        print(f"💾 Saved JSON: {filepath}")
    except Exception as e:
        print(f"❌ Error saving JSON {filename}: {e}")

def save_to_csv(data: List[Dict[str, Any]], filename: str):
    """Save data to CSV file"""
    if not data:
        print(f"⚠️ No data to save for {filename}")
        return
        
    filepath = OUTPUT_DIR / f"{filename}.csv"
    try:
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        print(f"💾 Saved CSV: {filepath}")
    except Exception as e:
        print(f"❌ Error saving CSV {filename}: {e}")

def save_summary_report(stats: Dict[str, int], export_time: str):
    """Save a summary report of the data export"""
    summary = {
        "export_timestamp": export_time,
        "database_config": {
            "host": DB_CONFIG["host"],
            "port": DB_CONFIG["port"],
            "database": DB_CONFIG["database"]
        },
        "table_stats": stats,
        "total_records": sum(stats.values()),
        "tables_exported": len(stats),
        "export_location": str(OUTPUT_DIR.absolute())
    }
    
    filepath = OUTPUT_DIR / "export_summary.json"
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"📋 Export summary saved: {filepath}")
        
        # Also print summary to console
        print("\n" + "="*60)
        print("📊 EXPORT SUMMARY")
        print("="*60)
        print(f"Export Time: {export_time}")
        print(f"Total Records: {summary['total_records']}")
        print("Table Breakdown:")
        for table, count in stats.items():
            print(f"  - {table}: {count} rows")
        print(f"Files saved to: {OUTPUT_DIR.absolute()}")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error saving summary: {e}")

def create_sample_queries_file():
    """Create a file with sample SQL queries for analysis"""
    sample_queries = [
        {
            "description": "Get all transfers in the last 24 hours",
            "sql": "SELECT * FROM transfers WHERE _block_timestamp_ > NOW() - INTERVAL '24 hours' ORDER BY _block_timestamp_ DESC;"
        },
        {
            "description": "Count transfers by token amount ranges",
            "sql": "SELECT CASE WHEN amount < 1 THEN 'Small (<1)' WHEN amount < 100 THEN 'Medium (1-100)' ELSE 'Large (>100)' END as size_category, COUNT(*) FROM transfers GROUP BY 1;"
        },
        {
            "description": "Top 10 most active accounts (by transfer count)",
            "sql": "SELECT account, COUNT(*) as transfer_count FROM (SELECT \"from\" as account FROM transfers UNION ALL SELECT \"to\" as account FROM transfers) t GROUP BY account ORDER BY transfer_count DESC LIMIT 10;"
        },
        {
            "description": "Minting activity summary",
            "sql": "SELECT DATE(_block_timestamp_) as date, COUNT(*) as mint_count, SUM(amount) as total_minted FROM mints GROUP BY DATE(_block_timestamp_) ORDER BY date;"
        },
        {
            "description": "Recent initialized accounts",
            "sql": "SELECT * FROM initialized_accounts ORDER BY _block_timestamp_ DESC LIMIT 20;"
        }
    ]
    
    filepath = OUTPUT_DIR / "sample_queries.json"
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(sample_queries, f, indent=2, ensure_ascii=False)
        print(f"📝 Sample queries saved: {filepath}")
    except Exception as e:
        print(f"❌ Error saving sample queries: {e}")

# ============================================================================
# MAIN EXPORT FUNCTION
# ============================================================================

def export_all_data():
    """Main function to export all data from the database"""
    print("🚀 Starting data export from PostgreSQL database...")
    print(f"🎯 Target database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    # Get database connection
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        export_time = datetime.now().isoformat()
        
        # Get table statistics
        print("\n📊 Getting table statistics...")
        stats = get_table_stats(conn)
        
        # Export each table
        print(f"\n📤 Exporting {len(TABLES_TO_EXPORT)} tables...")
        for table_name in TABLES_TO_EXPORT:
            print(f"\n🔄 Processing table: {table_name}")
            data = get_table_data(conn, table_name)
            
            if data:
                # Save as both JSON and CSV
                save_to_json(data, f"{table_name}_data")
                save_to_csv(data, f"{table_name}_data")
            else:
                print(f"⚠️ No data found in table: {table_name}")
        
        # Save summary report
        print(f"\n📋 Creating summary report...")
        save_summary_report(stats, export_time)
        
        # Create sample queries file
        print(f"\n📝 Creating sample queries...")
        create_sample_queries_file()
        
        print(f"\n✅ Data export completed successfully!")
        print(f"📁 All files saved to: {OUTPUT_DIR.absolute()}")
        
    except Exception as e:
        print(f"❌ Error during export: {e}")
    finally:
        conn.close()
        print("🔒 Database connection closed")

def monitor_data_continuously(interval_seconds: int = 60):
    """Continuously monitor and export data at specified intervals"""
    print(f"👁️ Starting continuous monitoring (every {interval_seconds} seconds)")
    print("Press Ctrl+C to stop...")
    
    import time
    try:
        while True:
            print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Running export...")
            export_all_data()
            print(f"😴 Waiting {interval_seconds} seconds until next export...")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")

# ============================================================================
# CLI INTERFACE
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Export Substreams PostgreSQL data to local files")
    parser.add_argument("--monitor", "-m", action="store_true", help="Continuously monitor and export data")
    parser.add_argument("--interval", "-i", type=int, default=60, help="Monitor interval in seconds (default: 60)")
    
    args = parser.parse_args()
    
    if args.monitor:
        monitor_data_continuously(args.interval)
    else:
        export_all_data()