CREATE TABLE IF NOT EXISTS session_log (
	session_id INTEGER PRIMARY KEY AUTOINCREMENT, 
	training_block TEXT DEFAULT 'N/A',
	date DATE
);
	
CREATE TABLE IF NOT EXISTS lift_log (
	lift_id INTEGER PRIMARY KEY AUTOINCREMENT, 
	session_id INTEGER, 
	exercise_name TEXT,
	lift_group TEXT,
	category TEXT, 
	weight INTEGER,
	reps INTEGER,
	rpe_strain REAL,
	FOREIGN KEY (session_id) REFERENCES session_log(session_id)
);
	
CREATE TABLE IF NOT EXISTS info_log (
	bodyweight INTEGER,
	max_squat INTEGER,
	max_bench INTEGER, 
	max_dead INTEGER, 
	max_ohp INTEGER,
	max_row INTEGER,
	max_front_squat INTEGER
);
	
INSERT INTO info_log (
    bodyweight, 
    max_squat, 
    max_bench, 
    max_dead, 
    max_ohp, 
    max_row, 
    max_front_squat
)
SELECT 210, 425, 265, 545, 135, 245, 265
WHERE (SELECT COUNT(*) FROM info_log) = 0;
