#!/usr/bin/env python
"""
Database setup and verification script.
This script:
1. Checks voters table schema
2. Adds missing columns (pno, state, d_name)
3. Shows registered voters
4. Helps debug OTP issues
"""

import pymysql
import pandas as pd

def setup_database():
    try:
        db = pymysql.connect(host='localhost', user='root', password='root', port=3306, database='smart_voting_system')
        
        print("=" * 80)
        print("DATABASE SETUP AND VERIFICATION")
        print("=" * 80)
        
        # 1. Check voters table structure
        print("\n1. CURRENT VOTERS TABLE STRUCTURE:")
        print("-" * 80)
        voters_schema = pd.read_sql_query("DESC voters", db)
        print(voters_schema.to_string(index=False))
        
        # 2. Add missing columns
        cursor = db.cursor()
        columns = [row[0] for row in cursor.execute("DESC voters") or cursor.fetchall()]
        
        required_cols = {
            'pno': "VARCHAR(20)",
            'state': "VARCHAR(100)",
            'd_name': "VARCHAR(100)"
        }
        
        print("\n2. CHECKING REQUIRED COLUMNS:")
        print("-" * 80)
        for col, dtype in required_cols.items():
            if col in columns:
                print(f"  ✓ {col:15} - EXISTS")
            else:
                print(f"  ✗ {col:15} - MISSING (adding...)")
                try:
                    cursor.execute(f"ALTER TABLE voters ADD COLUMN {col} {dtype}")
                    db.commit()
                    print(f"    ✓ Added {col}")
                except Exception as e:
                    print(f"    ✗ Error: {e}")
        
        # 3. Show registered voters
        print("\n3. REGISTERED VOTERS:")
        print("-" * 80)
        voters = pd.read_sql_query("SELECT aadhar_id, first_name, email, pno, verified FROM voters", db)
        if voters.empty:
            print("  No voters registered yet.")
        else:
            print(voters.to_string(index=False))
        
        # 4. Show nominees
        print("\n4. NOMINEES:")
        print("-" * 80)
        noms = pd.read_sql_query("SELECT sno, member_name, party_name, symbol_name FROM nominee", db)
        if noms.empty:
            print("  No nominees added yet.")
        else:
            print(noms.to_string(index=False))
        
        # 5. Show votes
        print("\n5. VOTES CAST:")
        print("-" * 80)
        votes = pd.read_sql_query("SELECT vote, aadhar FROM vote", db)
        if votes.empty:
            print("  No votes cast yet.")
        else:
            print(votes.to_string(index=False))
        
        print("\n" + "=" * 80)
        print("✓ DATABASE SETUP COMPLETE")
        print("=" * 80)
        
        cursor.close()
        db.close()
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("\nPlease ensure:")
        print("  1. MySQL is running")
        print("  2. Database 'smart_voting_system' exists")
        print("  3. User 'root' with password 'root' can connect")

if __name__ == '__main__':
    setup_database()
