/* Calculates relative training week and intensity percentage for main lifts.
Groups data to track volume (sum_reps) against intensity blocks.
*/
DROP VIEW IF EXISTS v_lift_intensity;
CREATE VIEW v_lift_intensity AS 
SELECT
	-- Normalizes dates into 7-day windows starting from the first recorded session
	CAST((julianday(s.date) - (SELECT julianday(MIN(date)) FROM session_log)) / 7.0 AS INT) + 1 AS training_week,
	s.training_block,
	l.lift_group,
	l.exercise_name, 
	SUM(l.reps) AS sum_reps, 
	l.weight, 
	-- Calculates % of 1RM; floating point math used to prevent integer truncation
	CASE 
		WHEN TRIM(LOWER(l.exercise_name)) = 'back squat' THEN ROUND((l.weight * 100.0 / i.max_squat), 1)
		WHEN TRIM(LOWER(l.exercise_name)) = 'front squat' THEN ROUND((l.weight * 100.0 / i.max_front_squat), 1)
		WHEN TRIM(LOWER(l.exercise_name)) LIKE '%bench press' THEN ROUND((l.weight * 100.0 / i.max_bench), 1)
		WHEN TRIM(LOWER(l.exercise_name)) = 'deadlift' THEN ROUND((l.weight * 100.0 / i.max_dead), 1)
		ELSE NULL 
	END AS intensity_pct,
	ROUND(AVG(rpe_strain),1) as rpe
FROM lift_log l
JOIN session_log s 
	ON l.session_id = s.session_id
CROSS JOIN info_log i
WHERE TRIM(LOWER(l.lift_group)) IN ('squat', 'bench press', 'deadlift')
GROUP BY training_week, l.lift_group, l.exercise_name, intensity_pct, l.weight;

----------------------------------------------------------------------------------------------------------------

-- Tracks total rep volume per movement category (Anterior, Posterior, etc.) per relative week
DROP VIEW IF EXISTS v_category_volume;
CREATE VIEW v_category_volume AS 
SELECT 
	CAST((julianday(s.date) - (SELECT julianday(MIN(date)) FROM session_log)) / 7.0 AS INT) + 1 AS training_week,
	l.category,
	SUM(l.reps) AS sum_reps,
	SUM(l.weight * l.reps) AS tonnage
FROM lift_log l
JOIN session_log s 
	ON l.session_id = s.session_id
GROUP BY training_week, category;

----------------------------------------------------------------------------------------------------------------

/* Calculates the Acute:Chronic Workload Ratio (ACWR) partitioned by lift group.
This view helps identify overreaching in specific movements (Squat, Bench, Deadlift)
by comparing the current week's stress against a 4-week rolling average.
*/
DROP VIEW IF EXISTS v_weekly_workload_by_group;
CREATE VIEW v_weekly_workload_by_group AS
WITH group_totals AS(
SELECT 
	training_week, 
	
	lift_group,
	/* Volume Load is scaled by intensity_pct to represent 'Total Work' done.
        This accounts for the higher neurological tax of heavy sets vs. light sets.
     */
	SUM(sum_reps * weight * intensity_pct) AS volume_load
FROM v_lift_intensity
GROUP BY training_week, lift_group
)
SELECT
	training_week, 
	lift_group, 
	volume_load, 
	volume_load AS acute_load, 
	AVG(volume_load) OVER (
	PARTITION BY lift_group
	ORDER BY training_week
	ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
	) AS chronic_avg,
	ROUND((volume_load / AVG(volume_load) OVER (
	PARTITION BY lift_group
	ORDER BY training_week
	ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
	)), 2) AS ACWR
FROM group_totals;