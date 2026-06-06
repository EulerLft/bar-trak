# -*- coding: utf-8 -*-
"""
Created on Fri May 15 15:37:16 2026
@author: salva
"""

import matplotlib.pyplot as plt 
import seaborn as sns 
import pandas as pd
import streamlit as st 

def round_to_nearest_5(num):
    """Helper function to calculate clean limits for the volume plot."""
    return 5 * round(num / 5)

def render_volume_plot_1(df_intensity, lift_name):
    # --- Aggregate Data --- 
    # Calculate the weekly total reps
    df_totals = df_intensity.groupby('training_week')['sum_reps'].sum().reset_index()
    df_totals[['exercise_name', 'lift_group']] = ['totals', lift_name]
    
    # Combine the original dataframe with the new total rows
    df_plot = pd.concat([df_intensity, df_totals], ignore_index=True)
    
    y_rep_min = df_plot['sum_reps'].min()
    y_rep_max = df_plot['sum_reps'].max()
    
    # --- Volume Plot ---
    # Create a figure layout with two stacked subplots
    fig, ax1 = plt.subplots(figsize=(10, 7))
    
    sns.barplot(
        data=df_plot, 
        x='training_week', 
        y='sum_reps', 
        hue='exercise_name', 
        ax=ax1,
        zorder=2
    )
    
    for container in ax1.containers:
        ax1.bar_label(container, fmt='%d', padding=0, weight='bold', fontsize=20)
        
    ax1.set_ylim(round_to_nearest_5(y_rep_min*0.25), round_to_nearest_5(y_rep_max*1.25))
    ax1.set_xlabel("Week #", fontsize=25, labelpad=20)
    ax1.set_ylabel("Total Reps", fontsize=25, labelpad=20)
    ax1.tick_params(axis='both', which='major', labelsize=20)
    ax1.grid(True, alpha=0.3, zorder=0)
    ax1.legend(title='', fontsize=22)
    
    fig.tight_layout()
    st.pyplot(fig, use_container_width=False)
    
def render_volume_plot_2(df_intensity, lift_name):
    
    y_pct_min = df_intensity['intensity_pct'].min()
    y_pct_max = df_intensity['intensity_pct'].max()
    
    # Create a figure layout with two stacked subplots
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # --- Intensity Trend ---
    for exercise in df_intensity['exercise_name'].unique():
        df_sub = df_intensity[df_intensity['exercise_name'] == exercise]
        sns.regplot(
            data=df_sub, 
            x='training_week', 
            y='intensity_pct', 
            ax=ax, 
            scatter_kws = {'s': 150},
            line_kws = {'linewidth': 5, 'linestyle': '--'},
            ci=None, 
            scatter=True, 
            label=exercise
        )
        
    ax.set_ylim(round_to_nearest_5(y_pct_min*0.8), round_to_nearest_5(y_pct_max*1.2))
    ax.set_xticks(df_intensity['training_week'].unique())
    ax.set_xlabel("Training Week", fontsize=25, labelpad=20)
    ax.set_ylabel("%1RM", fontsize=25, labelpad=20)
    ax.tick_params(axis='both', which='major', labelsize=20)
    ax.grid(True, alpha=0.3)
    ax.legend(title='', fontsize=22)
    
    fig.tight_layout()
    st.pyplot(fig, use_container_width=False)

def render_acwr_plot_1(df_acwr, lift_name):
    # VISUALIZATION 1: ACWR TREND ---
    fig, ax1 = plt.subplots(figsize=(10, 7))
    
    sns.barplot(df_acwr, x='training_week', y='ACWR', zorder=2)
    
    # Explicitly layer the trend elements on top of the bars using zorder
    ax1.axhline(y=1.4, color='red', linestyle='--', zorder=1)
    ax1.axhline(y=0.8, color='tab:orange', linestyle='--', zorder=1)
    ax1.axhspan(0.4, 0.8, color='tab:orange', alpha=0.25, label='Underreach Zone', zorder=3)
    ax1.axhspan(1.4, 2.0, color='tab:red', alpha=0.25, label='Overreach Zone', zorder=3)
    
    sns.pointplot(
        df_acwr, x='training_week', y='ACWR', color='black', linestyle='--', markersize=10,
        linewidth=2, markerfacecolor='white', markeredgecolor='black', zorder=4
    )
    
    for container in ax1.containers:
        ax1.bar_label(container, fmt='[%.2f]', padding=10, fontsize=15)
    
    ax1.set_ylabel('ACWR Value', fontsize=20, labelpad=20)
    ax1.set_xlabel('Training Week', fontsize=20, labelpad=20)
    ax1.set_ylim(0.4, 1.8)
    ax1.tick_params(axis='both', which='major', labelsize=20)
    ax1.grid(axis='y', alpha=0.3)
    ax1.legend(loc=1, fontsize=22);
    
    fig.tight_layout()
    st.pyplot(fig, use_container_width=False)

def render_acwr_plot_2(df_acwr, lift_name):
    # VISUALIZATION 1: ACWR TREND ---
    fig, ax2 = plt.subplots(figsize=(10, 7))
    
    sns.regplot(data=df_acwr, x='training_week', y='ACWR', ax=ax2, 
                scatter_kws={'s': 100, 'edgecolor': 'black', 'facecolor': 'white', 'zorder': 3}, line_kws={'zorder': 2}
    )
        
    ax2.set_xticks(df_acwr['training_week'].unique())
    ax2.set_ylabel('ACWR Value', fontsize=20, labelpad=20)
    ax2.set_xlabel('Training Week', fontsize=20, labelpad=20);
    ax2.tick_params(axis='both', which='major', labelsize=20)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=False)