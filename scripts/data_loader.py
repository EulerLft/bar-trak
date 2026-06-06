# -*- coding: utf-8 -*-
"""
Edited on May 26, 2026
@author: salva
"""

import os 
import pandas as pd 
import sqlite3

## --- PATH SET UP ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
data_path = os.path.join(project_root, 'data')

db_path = os.path.join(data_path, 'training_analytics_DB.db')
file_path = os.path.join(data_path, 'lift_log.csv')
sql_path = os.path.join(script_dir, '01_build_schema.sql')

def upload_training(file_path, db_path):
    df = pd.read_csv(file_path)
    
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Convert date to datetime object
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y').dt.date
    
    # Fill numerical NaNs and cast to int
    df['weight'] = df['weight'].fillna(0).astype(int)
    
    # Use .str accessor for string cleaning 
    df['training_block'] = df['training_block'].str.strip().str.lower()
    df['exercise_name'] = df['exercise_name'].str.strip().str.lower()
    df['lift_group'] = df['lift_group'].str.strip().str.lower()
    df['category'] = df['category'].str.strip().str.lower()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(sql_path, 'r') as f:
        sql_script = f.read()
        
    try:
        cursor.executescript(sql_script)
    except sqlite3.OperationalError:
        # Prevent script from crashing when tables already exist
        pass 
        
    # Group by temporary session_id in the CSV to upload clusters 
    for csv_id in df['session_id'].unique():
        session_subset = df[df['session_id'] == csv_id]
        meta = session_subset.iloc[0]
        
        # Prevent duplicates by checking date 
        cursor.execute("SELECT session_id FROM session_log WHERE date = ?", (str(meta['date']),))
        if cursor.fetchone():
            print(f'Session on {meta["date"]} already exists. Skipping.')
            continue
        
        # Extract the training block from the CSV row, default to 'accumulation' if missing 
        current_block = str(meta['training_block']).strip().lower() if 'training_block' in meta else 'accumulation'
        
        # Insert master session record
        cursor.execute("""
            INSERT INTO session_log (date, training_block) 
            VALUES (?, ?)
        """, (str(meta['date']), current_block))
        
        new_master_id = cursor.lastrowid
        
        # Insert all sets belonging to this session 
        for _, row in session_subset.iterrows():
            cursor.execute("""
                INSERT INTO lift_log (session_id, exercise_name, lift_group, category, weight, reps, rpe_strain)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (new_master_id, row['exercise_name'], row['lift_group'], row['category'], int(row['weight']), int(row['reps']), row['rpe_strain']))
    
    conn.commit()
    conn.close()
    print("Database updated. New sessions have been succesffully archived.")
    
if __name__ == '__main__':
    upload_training(file_path, db_path)
    
