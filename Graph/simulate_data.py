#!/usr/bin/env python3
"""
Simulate some sample data in the PostgreSQL database for demonstration
This inserts fake SPL token data to show how the export system works
"""

import psycopg2
from datetime import datetime, timedelta
import random
import string

# Database connection settings
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'substreams',
    'user': 'postgres',
    'password': 'password'
}

def generate_random_address():
    """Generate a fake Solana address-like string"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=44))

def generate_random_hash():
    """Generate a fake transaction hash"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=64))

def insert_sample_data():
    """Insert sample data into the database"""
    print("🚀 Inserting sample data into PostgreSQL database...")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Insert sample blocks
        print("📦 Inserting sample blocks...")
        base_time = datetime.now() - timedelta(hours=1)
        
        for i in range(5):
            block_num = 158569587 + i
            block_time = base_time + timedelta(minutes=i*10)
            
            cursor.execute("""
                INSERT INTO _blocks_ (number, hash, timestamp) 
                VALUES (%s, %s, %s)
                ON CONFLICT (number) DO NOTHING
            """, (block_num, generate_random_hash(), block_time))
        
        # Insert sample instructions
        print("📝 Inserting sample instructions...")
        instructions_data = []
        for i in range(10):
            instruction_id = f"instruction_{i}_{generate_random_hash()[:8]}"
            tx_hash = generate_random_hash()
            block_num = 158569587 + (i % 5)
            block_time = base_time + timedelta(minutes=(i % 5)*10)
            
            instructions_data.append((instruction_id, tx_hash, block_num, block_time))
            
            cursor.execute("""
                INSERT INTO instructions (instruction_id, transaction_hash, _block_number_, _block_timestamp_)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (instruction_id) DO NOTHING
            """, (instruction_id, tx_hash, block_num, block_time))
        
        # Insert sample transfers
        print("💸 Inserting sample transfers...")
        for i in range(15):
            instruction_id = instructions_data[i % len(instructions_data)][0]
            from_addr = generate_random_address()
            to_addr = generate_random_address()
            amount = round(random.uniform(0.01, 1000.0), 6)
            from_owner = generate_random_address()
            to_owner = generate_random_address()
            block_num = 158569587 + (i % 5)
            block_time = base_time + timedelta(minutes=(i % 5)*10)
            
            cursor.execute("""
                INSERT INTO transfers (
                    instruction_id, "from", "to", amount, from_owner, to_owner,
                    _block_number_, _block_timestamp_
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (instruction_id, from_addr, to_addr, amount, from_owner, to_owner, block_num, block_time))
        
        # Insert sample mints
        print("🪙 Inserting sample mints...")
        for i in range(8):
            instruction_id = instructions_data[i % len(instructions_data)][0]
            to_addr = generate_random_address()
            amount = round(random.uniform(100.0, 10000.0), 6)
            to_owner = generate_random_address()
            block_num = 158569587 + (i % 5)
            block_time = base_time + timedelta(minutes=(i % 5)*10)
            
            cursor.execute("""
                INSERT INTO mints (
                    instruction_id, "to", amount, to_owner,
                    _block_number_, _block_timestamp_
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (instruction_id, to_addr, amount, to_owner, block_num, block_time))
        
        # Insert sample burns
        print("🔥 Inserting sample burns...")
        for i in range(5):
            instruction_id = instructions_data[i % len(instructions_data)][0]
            from_addr = generate_random_address()
            amount = round(random.uniform(10.0, 500.0), 6)
            from_owner = generate_random_address()
            block_num = 158569587 + (i % 5)
            block_time = base_time + timedelta(minutes=(i % 5)*10)
            
            cursor.execute("""
                INSERT INTO burns (
                    instruction_id, "from", amount, from_owner,
                    _block_number_, _block_timestamp_
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (instruction_id, from_addr, amount, from_owner, block_num, block_time))
        
        # Insert sample initialized accounts
        print("🆕 Inserting sample initialized accounts...")
        for i in range(6):
            instruction_id = instructions_data[i % len(instructions_data)][0]
            account = generate_random_address()
            mint = generate_random_address()
            owner = generate_random_address()
            block_num = 158569587 + (i % 5)
            block_time = base_time + timedelta(minutes=(i % 5)*10)
            
            cursor.execute("""
                INSERT INTO initialized_accounts (
                    instruction_id, account, mint, owner,
                    _block_number_, _block_timestamp_
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (instruction_id, account, mint, owner, block_num, block_time))
        
        # Insert a cursor entry
        print("📍 Inserting cursor data...")
        cursor.execute("""
            INSERT INTO _cursor_ (name, cursor) 
            VALUES (%s, %s)
            ON CONFLICT (name) DO UPDATE SET
                cursor = EXCLUDED.cursor
        """, ('map_spl_instructions', 'sample_cursor_data_block_158569591'))
        
        conn.commit()
        print("✅ Sample data inserted successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM instructions")
        instructions_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM transfers")
        transfers_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM mints")
        mints_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM burns")
        burns_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM initialized_accounts")
        accounts_count = cursor.fetchone()[0]
        
        print("\n📊 DATA SUMMARY:")
        print(f"  - Instructions: {instructions_count}")
        print(f"  - Transfers: {transfers_count}")
        print(f"  - Mints: {mints_count}")
        print(f"  - Burns: {burns_count}")
        print(f"  - Initialized Accounts: {accounts_count}")
        print("\n🎯 Ready to export data with: python load_data.py")
        
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    insert_sample_data()
