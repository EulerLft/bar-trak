# -*- coding: utf-8 -*-
"""
Created on Fri May 15 12:52:39 2026
@author: salva
"""

import os
import sqlite3
import pandas as pd 
import streamlit as st
from plot_utils import render_volume_plot_1, render_volume_plot_2, render_acwr_plot_1, render_acwr_plot_2
from progression_calculator import generate_training_cycle

# --- PATH SETUP ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
ASSETS_DIR = os.path.join(PROJECT_DIR, 'assets')
database_path = os.path.join(DATA_DIR, 'training_analytics_DB.db')
config_path = os.path.join(SCRIPT_DIR, 'lift_configs.json')


# Establish connection with SQLite Database
conn = sqlite3.connect(database_path)

# Navigation and Data Fetching
def reset_to_home():
    st.session_state.view = 'wide'
    
def reset_to_analysis():
    st.session_state.view = 'analysis'
    
def reset_to_projection():
    st.session_state.view = 'projection'
    
if "view" not in st.session_state:
    st.session_state.view = 'wide'

def get_volume_data():
    query = "SELECT * FROM v_category_volume"
    return pd.read_sql_query(query, conn)

def get_intensity_data():
    query = "SELECT * FROM v_lift_intensity"
    return pd.read_sql_query(query, conn)

def get_acwr_data():
    query = "SELECT * FROM v_weekly_workload_by_group"
    return pd.read_sql_query(query, conn)

df_intensity = get_intensity_data()
df_acwr =get_acwr_data()

# --- APP UI ---
st.set_page_config(page_title='FORGE-TRAK', layout='wide')

st.markdown("""
    <style>
           .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                margin-top: 0rem;
            }
    </style>
    """, unsafe_allow_html=True)

# Selection for specific lift group 
#choice = st.sidebar.selectbox("Select Choice", ['main lift', 'exercise name'])

# --- LAYER 1: Global View --- 
if st.session_state.view == 'wide':
    st.title("FORGE-TRAK")
    st.subheader("Data-Driven Powerlifting Performance Metrics")
    
    left_buffer, center_container, right_buffer = st.columns([1, 3, 1])
    
    with center_container:
        img_path = os.path.join(ASSETS_DIR, "main_asset.png")
        st.image(img_path, use_container_width=True)
        
        st.info("##### Select a Procedure to Follow (Analysis/Projection)") 
        
        c1, c2 = st.columns(2)
            
        with c1:
            if st.button("Analysis", use_container_width=True):
                st.session_state.view = 'analysis'
                st.rerun()
                    
        with c2:
            if st.button("Projection", use_container_width=True):
                st.session_state.view = 'projection'
                st.rerun()
    
        st.divider()

# --- LAYER 2a: Analysis View --- 
elif st.session_state.view == 'analysis':
    st.title("FORGE-TRAK")
    st.subheader("Data-Driven Powerlifting Performance Metrics")

    # Top-bar navigation header for the sub-window
    nav_c1, nav_c2 = st.columns([1, 4])
    with nav_c1:
        if st.button("← Back Home", use_container_width=True):
            reset_to_home()
            st.rerun()
            
    with nav_c2:
        st.subheader(" ")
    
    st.subheader(" ")
        
    left_buffer, center_container, right_buffer = st.columns([1, 3, 1])
    with center_container:
        st.info("##### Select a Lift Group to conduct analysis.") 
        
        c1, c2, c3 = st.columns(3)        
        with c1:
            st.image(os.path.join(ASSETS_DIR, "squat.png"), use_container_width=True)
            if st.button("Squat", use_container_width=True):
                st.session_state.view = 'squat'
                st.rerun()
        with c2:
            st.image(os.path.join(ASSETS_DIR, "bench_press.png"), use_container_width=True)
            if st.button("Bench Press", use_container_width=True):
                st.session_state.view = 'bench press'
                st.rerun()
        with c3:
            st.image(os.path.join(ASSETS_DIR, "deadlift.png"), use_container_width=True)
            if st.button("Deadlift", use_container_width=True):
                st.session_state.view = 'deadlift'
                st.rerun()
    
        st.divider()
    
# --- LAYER 3a: Isolated Lift Analysis Window ---
elif st.session_state.view in ["squat", "bench press", "deadlift"]:

    current_lift = st.session_state.view
    
    st.title("FORGE-TRAK")
    st.subheader(f"{current_lift.title()} Performance")

    # Top-bar navigation header for the sub-window
    nav_c1, nav_c2, nav_c3 = st.columns([1, 1, 4])
    with nav_c1:
        if st.button("← Back Home", use_container_width=True):
            reset_to_home()
            st.rerun()
            
    with nav_c2:
        if st.button("← Back", use_container_width=True):
            reset_to_analysis()
            st.rerun()
    
    with nav_c3:
        st.subheader(" ")
    
    # Initialize sub_view immediately so it exists when the buttons render
    if "sub_view" not in st.session_state:
        st.session_state.sub_view = 'volume'

    st.divider()
    
    # Filter data based on the selected sub-window focus
    filtered_acwr = df_acwr[df_acwr['lift_group'] == current_lift]
    filtered_intensity = df_intensity[df_intensity['lift_group'] == current_lift]
    
    left_buffer, center_container, right_buffer = st.columns([1, 5, 1])
    with center_container:

        c1, c2 = st.columns(2)
        
        with c1: 
            st.subheader("Volume")
            render_volume_plot_1(filtered_intensity, current_lift)
    
        with c2: 
            st.subheader("Intensity")
            render_volume_plot_2(filtered_intensity, current_lift)
    
        c3, c4 = st.columns(2)
        
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Fatigure & Workload Management")
            render_acwr_plot_1(filtered_acwr, current_lift)
            
        with c4: 
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Fit Line")
            render_acwr_plot_2(filtered_acwr, current_lift)
            
        st.divider()
    
# --- LAYER 2b: Projection View --- 
elif st.session_state.view == 'projection':
    st.title("FORGE-TRAK")
    st.subheader("Data-Driven Powerlifting Performance Metrics")

    # Top-bar navigation header for the sub-window
    nav_c1, nav_c2= st.columns([1, 4])
    
    with nav_c1:
        if st.button("← Back Home", use_container_width=True):
            reset_to_home()
            st.rerun()

    with nav_c2:
        st.subheader(" ")

    
    st.subheader("Powerlifting Projection")
    
    left_buffer, center_container, right_buffer = st.columns([1, 4, 1])
    
    with center_container:
        # Fetch the current 1RM parameters from the database to calculate percentanges for scaling 
        df_maxes = pd.read_sql_query("SELECT max_squat, max_bench, max_dead, max_ohp, max_row, max_front_squat FROM info_log", conn)
        if not df_maxes.empty:
            max_map = {
                "back squat" : df_maxes.iloc[0]['max_squat'],
                "bench press" : df_maxes.iloc[0]['max_bench'],
                "deadlift" : df_maxes.iloc[0]['max_dead'],
                "OHP" : df_maxes.iloc[0]['max_ohp'],
                "bent over row": df_maxes.iloc[0]['max_row'],
                "front squat": df_maxes.iloc[0]['max_front_squat']
                }
        
        with st.form(key="projection_input_form"):
            st.markdown('##### Define a Baseline Week Snapshot (RPE 7)')
        
            cycle_weeks = st.slider("Macrocycle Duration (weeks)", min_value=4, max_value=30, value=1)
            
            # Row 1: Back Squat Input
            c1, c2, c3 = st.columns(3)
            with c1:
                st.text_input("Lift", value='Back Squat', disabled=True, key="lbl_squat")   
            with c2: 
                squat_weight = st.number_input("Working Weight (Lbs)", min_value=0, max_value=1000, step=5, key='wt_squat')
            with c3:
                squat_reps = st.number_input("Input # of reps", min_value=0, max_value=100, step=1, key='reps_squat')
                
            c1, c2, c3 = st.columns(3)
            with c1:
                st.text_input("Lift", value='Bench Press', disabled=True, key='lbl_bench')   
            with c2: 
                bench_weight = st.number_input("Working Weight (Lbs)", min_value=0, max_value=1000, step=5, key='wt_bench')
            with c3:
                bench_reps = st.number_input("Input # of reps", min_value=0, max_value=100, step=1, )

            c1, c2, c3 = st.columns(3)
            with c1:
                st.text_input("Lift", value='Deadlift', disabled=True, key='lbl_dead')   
            with c2: 
                dead_weight = st.number_input("Working Weight (Lbs)", min_value=0, max_value=1000, step=5, key='wt_dead')
            with c3:
                dead_reps = st.number_input("Input # of reps", min_value=0, max_value=100, step=1, key='reps_dead')
            
            submit_form = st.form_submit_button("Generate Block Projection", use_container_width=True)    

        if submit_form:
            # Structure inputs into an iterable collection 
            inputs_to_process = [
                {"name": "back squat", "weight": squat_weight, "reps": squat_reps},
                {"name": "bench press", "weight": bench_weight, "reps": bench_reps},
                {"name": "deadlift", "weight": dead_weight, "reps": dead_reps}
                ]
            
            all_cycles = []
            
            for lift in inputs_to_process:
                current_max = max_map[lift["name"]]
                
                df_lift_projection = generate_training_cycle(
                    lift_name=lift['name'],
                    max_lift=current_max,
                    baseline_weight=lift['weight'],
                    baseline_reps=lift['reps'],
                    cycle_weeks=cycle_weeks                    
                )
                all_cycles.append(df_lift_projection)
                
            df_projection = pd.concat(all_cycles, ignore_index=True)
            df_projection['week_num'] = df_projection['Week'].str.extract(r'(\d+)').astype(int)
            df_projection = df_projection.sort_values(by=['week_num', 'Lift', 'Type']).drop(columns=['week_num'])
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.success("### Prescribed Macrocycle Projections")
            st.dataframe(df_projection, use_container_width=True, hide_index=True, height=450)
            
            csv_data = df_projection.to_csv(index=False).encode('utf-8')
            
            btn_c1, btn_c2 = st.columns([1, 4])
            with btn_c1:
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="forge_trak_macrocycle.csv",
                    mime="text/csv",
                    use_container_width=True
                    )
            
        st.divider()

conn.close()
