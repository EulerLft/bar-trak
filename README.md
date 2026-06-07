# BAR-TRAK 

<p align="center">
  <img src="assets/logo.JPG" alt="BAR-TRAK logo" width="500">
</p>

## Data-driven powerlifting performance metrics 
`bar-trak` is a Python-based computational engine and interactive Streamlit dashboard designed for lifters and coaches. 
The application streamlines training tracking by conducting block periodization analytics, managing volume distribution, and computing autoregulated load projections based on recent performance metrics.

**[🚀 Live Interactive App: https://credit-risk-engine-eulerlft.streamlit.app/](https://credit-risk-engine-eulerlft.streamlit.app/)**

--- 

## Core Features 

* **Block Periodization Analytics:** Examine historical training trends, tracking changes in volume, average intensity and fatigue accumulation across distinct micro cycles.
* **Relational Storage Layout:** Leverages a structured local SQLite database to maintain queryable lifting logs and configurations, eliminating reliance on flat tracking sheets. 
* **Fatigue & Workload Monitoring:** Computes real-time workload stress variables and best-fit regression lines to ensure lifters scale training metrics effectively while preventing overtraining.
* **Deterministic Program Development:** Generates comprehensive multi-week training schedules built directly from an initial performance baseline, transitioning smoothly from accumulation blocks to specialized intensity phases.

---

## Training Methodology: Understanding ACWR 

A core component of the `bar-trak` analytical framework relies on monitoring the **Acute-to-Chronic Workload Ratio (ACWR)**. This metric is a well-established sports science standard used to quantify injury risk and manage fatigue. 
It is defined as follows: 

$$\text{ACWR} = \frac{\text{Acute Worjload (Current Week Tonnage)}}{\text{Chronic Workload (Rolling 4-Week Average Tonnage)}}$$ \
Where **tonnage** is defined as : $$\text{tonnage} = \text{total reps} * \text{weight}$$  

The engine tracks ACWR to ensure training progressions stay within mathematically safe thresholds: 
* **The Sweet Spot ($0.8 - 1.3$):** Training load is safely advancing, maximizing strength adaptations while maintaining low injury risk. 
* **The Danger Zone ($\ge 1.5$):** The current week's training volume has spiked too rapidly relative to historical capacity, significantly increasing the probability of overtraining, fatigue failure, or injury.

## Powerlifting Program Development

The application provides a dedicated interface for building long-term training macrocycles. By inputting recent performance parameters from a standard RPE 7 session, including weight, total repetitions, and target timeline. The backend calculation engine establishes an automated training template.\
The system maps out target metrics week-by-week, utilizing built-in load configuration limits to transition the lifter safely from high-volume accumulation phases into specialized intensity and final peak blocks; provided %1RM and volume are suitable for a peaking block. \
The interface screenshot below illustrates the macrocycle configuration panel. Users can input specific lift performance metrics and training durations to immediately view and download a completely structured weekly weight, set, and repetition protocol. 

![Powerlifting Projection (1)](assets/screenshot_1.JPG)

The subsequent breakdown view shows how the model maps out specific intensity thresholds and fatigue projections. This allows coaches and athletes to evaluate the entire trajectory of the block periodization before executing the sessions. The program can be downloaded as a csv file using the dedicated button.

![Powerlifting Projection (2)](assets/screenshot_2.JPG)

Upon completion of session, users should input their training into the database, the ensure the tracked ACWR and volume matches the projection. 


## Technical Stack 
* **Frontend Interface:** Streamlit (interactive web dashboard framework) 
* **Database Management:** SQLite / SQL (relational data modeling and automated view aggregation) 
* **Data Science Stack:** Python, Pandas, NumPy (analytical computations and statistical modeling)
 * **Data Visualization:** Plotly / Matplotlib (dynamic performance charting) 


```text
bar-trak/
├── .streamlit/
│   └── config.toml          # Global UI configuration parameters
├── assets/                  # Application branding and media assets
├── data/
│   └── training_analytics_DB.db  # Core relational SQLite database
├── scripts/
│   ├── navigator.py         # Main entry point and layout routing script
│   ├── data_loader.py       # ETL pipelines and database connection tools
│   ├── plot_utils.py        # Custom data visualization rendering utilities
│   └── progression_calculator.py  # Autoregulation algorithms and projection logic
├── temp/                    # Local staging area for experimental development scripts
└── README.md
```
---

## Getting Started

1. **Prerequisities** 
	Ensure you have Python 3.10+ installed on your local environment.

2. **Clone the Repository**
	``` bash
	git clone [https://github.com/your-username/bar-trak.git](https://github.com/your-username/bar-trak.git)
	cd bar-trak
	``` 

3. **Install Required Dependencies**
	``` bash
	pip install streamlit pandas numpy matplotlib plotly
	```

4. **Initialize the Computational Engine**
	Run the main nagivation script from the root directory to launch the local development server: 
	``` bash
	streamlit run scripts/navigator.py
	```

---

## Future Roadmap
* **Dynamic Autoregulation:** Transition the program development module into a real-time autoregulated projection engine that automatically scales upcoming targets based on active database check-ins and session RPE variance.
* **Cloud Database Migration:** Move local SQLite storage to a centralized, cloud-hosted relational database server to support multi-user profile synchronization and remote coaching access.
* **Dedicated Mobile Interface:** Launch a mobile-optimized frontend expansion designed specifically for gym-floor usage, providing interactive program cards and streamlined training entry fields.