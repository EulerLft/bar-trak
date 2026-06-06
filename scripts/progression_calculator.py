# -*- coding: utf-8 -*-
"""
Created on Tue May 26 11:35:39 2026

@author: salva
"""

import json
import pandas as pd 

def generate_training_cycle(lift_name, max_lift, baseline_weight, baseline_reps, cycle_weeks):
    """
    Generates a deterministic powerlifting progression macrocycle across a set number of weeks.
    Enforces distinct intensity percentage floor rules for consecutive intensity blocks.
    Loads lift configurations from an external JSON file.
    """
    records = []
    workload_history = []
    
    import os
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, 'lift_configs.json')
        with open(config_path, 'r') as f:
            lift_configs = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"The configuration file was not found at {config_path}.")
    
    lift_key = lift_name.lower().strip()
    
    if lift_key in lift_configs:
        config = lift_configs[lift_key]
    else:
        config = lift_configs['back squat']
    
    current_phase = 'volume'
    current_volume_target = config['volume']['max_volume_limit']
    current_volume_start = config['volume']['start_volume']
    current_intensity_volume_target = config['intensity']['max_volume_limit']
    
    base_pct = baseline_weight / max_lift
    top_pct = base_pct + 0.05
    base_volume = baseline_reps
    
    peak_volume_top_volume = 5
    break_active = False
    overreached = False
    top_sets = 0

    intensity_blocks_completed = 0
    intensity_top_pct = 0.86
    intensity_base_pct = 0.81

    display_week = 1
    repeat_week = False
    weeks_in_current_block = 1
    peak_weeks_count = 0

    for week in range(1, cycle_weeks + 1):
        
        if display_week == 1:
            current_workload = base_volume * baseline_weight
            chronic_workload = current_workload
            acwr_result = 1.0
        else:
            if repeat_week:
                current_workload = workload_history[-1]
                chronic_workload = sum(workload_history[-5:-1]) / 4 if len(workload_history) >= 5 else current_workload
                acwr_result = current_workload / chronic_workload
            else:
                prior_weeks = workload_history[-4:]
                chronic_workload = sum(prior_weeks) / len(prior_weeks)

        if repeat_week:
            repeat_week = False

        # ------------------------------------------
        # BLOCK EXECUTION: VOLUME ACCUMULATION
        # ------------------------------------------
        if current_phase == 'volume':
            if display_week == 1:
                top_volume = 0
                top_sets = 0
                base_weight = baseline_weight
                top_weight = top_pct * max_lift
                current_workload = base_volume * base_weight
                acwr_result = 1.0
            else:
                if break_active:
                    break_active = False
                else:
                    if base_pct >= config['volume']['break_threshold_pct'] and weeks_in_current_block <= 4:
                        pass
                    else:
                        if base_volume < current_volume_start:
                            base_volume += config['volume']['volume_growth']
                            top_sets = 0
                        else:
                            base_volume = current_volume_start
                            if overreached:
                                if (base_pct + 0.025) > config['volume']['break_threshold_pct']:
                                    current_phase = 'intensity'
                                    weeks_in_current_block = 1
                                    overreached = False
                                    
                                    if intensity_blocks_completed == 0:
                                        intensity_top_pct = 0.86
                                        intensity_base_pct = 0.81
                                    else:
                                        intensity_top_pct = 0.88
                                        intensity_base_pct = 0.83
                                        
                                    top_volume = peak_volume_top_volume
                                    base_volume = max(0, current_intensity_volume_target - top_volume)
                                    top_weight = intensity_top_pct * max_lift
                                    base_weight = intensity_base_pct * max_lift
                                    
                                    if base_weight > top_weight:
                                        base_weight = top_weight
                                        
                                    current_workload = (top_volume * top_weight) + (base_volume * base_weight)
                                    acwr_result = current_workload / chronic_workload
                                else:
                                    if (base_pct + 0.025) <= config['volume']['absolute_ceiling_pct']:
                                        base_pct += 0.025
                                        top_pct += 0.025
                                    top_sets = 0
                                    overreached = False
                            else:
                                top_sets += 1
                
                if current_phase == 'volume':
                    top_volume = top_sets * 5
                    top_weight = top_pct * max_lift
                    base_weight = base_pct * max_lift
                    
                    if base_weight > top_weight: 
                        base_weight = top_weight                
                    current_workload = (top_volume * top_weight) + (base_volume * base_weight)
                    acwr_result = current_workload / chronic_workload

            if current_phase == 'volume':
                if (top_volume + base_volume) >= current_volume_target:
                    overreached = True

                if acwr_result > config['volume']['acwr_max']:
                    if base_volume == current_volume_start and not overreached and top_sets == 0:
                        base_pct -= 0.025
                        top_pct -= 0.025
                        overreached = True
                    elif base_volume > current_volume_start:
                        base_volume -= config['volume']['volume_growth']
                    else:
                        top_sets = max(0, top_sets - 1)
                    
                    repeat_week = True
                    continue

                if top_volume > 0:
                    peak_volume_top_volume = top_volume
                    records.append({
                        "Week": f"Week {display_week}", "Lift": lift_name.title(), "Block": "volume", "Type": "top",
                        "%1RM": round(top_pct * 100), "Weight (Lbs)": 5 * round(top_weight / 5),
                        "Volume": round(top_volume, 0), "ACWR": round(acwr_result, 2)
                    })
                
                records.append({
                    "Week": f"Week {display_week}", "Lift": lift_name.title(), "Block": "volume", "Type": "base",
                    "%1RM": round(base_pct * 100), "Weight (Lbs)": 5 * round(base_weight / 5),
                    "Volume": round(base_volume, 0), "ACWR": round(acwr_result, 2)
                })

                if base_pct >= config['volume']['break_threshold_pct'] and weeks_in_current_block >= 4:
                    if intensity_blocks_completed == 0:
                        intensity_top_pct = 0.86
                        intensity_base_pct = 0.81
                    else:
                        intensity_top_pct = 0.88
                        intensity_base_pct = 0.83

                    if intensity_top_pct >= 0.88 and intensity_blocks_completed > 0:
                        current_phase = 'intensity'
                    elif current_intensity_volume_target < 15:
                        current_phase = 'peak'
                    else:
                        current_phase = 'intensity'
                    weeks_in_current_block = 0

        # ------------------------------------------
        # BLOCK EXECUTION: INTENSITY REALIZATION
        # ------------------------------------------
        if current_phase == 'intensity':
            if not (base_pct >= config['volume']['break_threshold_pct'] and current_phase == 'intensity' and weeks_in_current_block == 1 and not overreached):
                if break_active:
                    break_active = False
                else:
                    if intensity_base_pct >= intensity_top_pct and weeks_in_current_block <= 4:
                        pass
                    else:
                        if weeks_in_current_block > 1 and intensity_base_pct < intensity_top_pct:
                            intensity_base_pct += config['intensity']['intensity_growth_pct']
                        if intensity_base_pct > intensity_top_pct:
                            intensity_base_pct = intensity_top_pct
                        
                top_volume = peak_volume_top_volume
                base_volume = max(0, current_intensity_volume_target - top_volume)
                
                top_weight = intensity_top_pct * max_lift
                base_weight = intensity_base_pct * max_lift
                
                if base_weight > top_weight:
                    base_weight = top_weight
                
                current_workload = (top_volume * top_weight) + (base_volume * base_weight)
                acwr_result = current_workload / chronic_workload

            if acwr_result > config['intensity']['acwr_max']:
                if intensity_base_pct > 0.81:
                    intensity_base_pct -= config['intensity']['intensity_growth_pct']
                
                repeat_week = True
                continue

            if top_volume > 0:
                records.append({
                    "Week": f"Week {display_week}", "Lift": lift_name.title(), "Block": "intensity", "Type": "top",
                    "%1RM": round(intensity_top_pct * 100), "Weight (Lbs)": 5 * round(top_weight / 5),
                    "Volume": round(top_volume, 0), "ACWR": round(acwr_result, 2)
                })
            if base_volume > 0:
                records.append({
                    "Week": f"Week {display_week}", "Lift": lift_name.title(), "Block": "intensity", "Type": "base",
                    "%1RM": round(intensity_base_pct * 100), "Weight (Lbs)": 5 * round(base_weight / 5),
                    "Volume": round(base_volume, 0), "ACWR": round(acwr_result, 2)
                })
            
            if intensity_base_pct >= intensity_top_pct and weeks_in_current_block >= 4:
                intensity_blocks_completed += 1
                potential_volume_drop = current_volume_target - 5
                potential_intensity_volume = current_intensity_volume_target - 5
                
                if potential_intensity_volume < 15 or intensity_top_pct >= 0.88:
                    current_phase = 'peak'
                else: 
                    next_break_threshold = config['volume']['break_threshold_pct'] + 0.025
                    next_absolute_ceiling = config['volume']['absolute_ceiling_pct'] + 0.025
                    
                    if next_break_threshold > 0.85 or next_absolute_ceiling > 0.88:
                        current_phase = 'peak'
                    else: 
                        current_phase = 'volume'
                        current_volume_target = potential_volume_drop
                        current_intensity_volume_target = potential_intensity_volume

                        base_pct = config['volume']['break_threshold_pct']
                        top_pct = base_pct + 0.025

                        config['volume']['break_threshold_pct'] = next_break_threshold
                        config['volume']['absolute_ceiling_pct'] = next_absolute_ceiling

                        base_volume = current_volume_start
                        top_sets = 0
                        overreached = False
                weeks_in_current_block = 0

        # ------------------------------------------
        # BLOCK EXECUTION: PEAK
        # ------------------------------------------
        elif current_phase == 'peak':
            if break_active:
                break_active = False
            else:
                if peak_weeks_count == 0:
                    intensity_top_pct = config['peak']['top_pct']
                    intensity_base_pct = config['peak']['base_pct']
                elif weeks_in_current_block > 1:
                    intensity_top_pct += config['peak']['intensity_growth_pct']
                    intensity_base_pct += config['peak']['intensity_growth_pct']

            top_volume = config['peak']['top_volume']
            base_volume = config['peak']['base_volume']
            
            top_weight = intensity_top_pct * max_lift
            base_weight = intensity_base_pct * max_lift
            
            if base_weight > top_weight:
                base_weight = top_weight
            
            current_workload = (top_volume * top_weight) + (base_volume * base_weight)
            acwr_result = current_workload / chronic_workload
            
            if acwr_result > config['peak']['acwr_max']:
                intensity_top_pct -= config['peak']['intensity_growth_pct']
                intensity_base_pct -= config['peak']['intensity_growth_pct']
                
                repeat_week = True
                continue
            
            records.append({
                "Week": f"Week {display_week}", "Lift": lift_name.title(), "Block": "peak", "Type": "top",
                "%1RM": round(intensity_top_pct * 100), "Weight (Lbs)": 5 * round(top_weight / 5),
                "Volume": round(top_volume, 0), "ACWR": round(acwr_result, 2)
            })
            records.append({
                "Week": f"Week {display_week}", "Lift": lift_name.title(), "Block": "peak", "Type": "base",
                "%1RM": round(intensity_base_pct * 100), "Weight (Lbs)": 5 * round(base_weight / 5),
                "Volume": round(base_volume, 0), "ACWR": round(acwr_result, 2)
            })
            
            peak_weeks_count += 1
            if peak_weeks_count >= 4:
                workload_history.append(current_workload)
                break

        workload_history.append(current_workload)
        display_week += 1
        weeks_in_current_block += 1

    return pd.DataFrame(records)