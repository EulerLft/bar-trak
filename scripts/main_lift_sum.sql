SELECT 
	l.session_id, 
	s.date, 
	TRIM(l.exercise_name) AS exercise, 
	l.movement_category, 
	l.weight, 
	SUM(l.reps) AS total_reps
FROM lift_log l
JOIN session_log s ON l.session_id = s.session_id
WHERE TRIM(l.exercise_name) IN ('back squat', 'bench press', 'deadlift')
GROUP BY s.date, TRIM(l.exercise_name);