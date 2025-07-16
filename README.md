# EpiSymp: Epidemiological Symptom Tracker & Outbreak Prediction System

EpiSymp is a comprehensive web application designed for real-time epidemiological surveillance. It allows the public to report symptoms through an intelligent chatbot, while providing healthcare professionals with a powerful dashboard to monitor disease trends, visualize geographical hotspots, and predict potential outbreaks using machine learning.

The system is centered around the city of Bulawayo, Zimbabwe, with functionalities for data collection, analysis, visualization, and automated alerting.

## Table of Contents

  * [Key Features](https://www.google.com/search?q=%23key-features)
      * [Public-Facing Features](https://www.google.com/search?q=%23public-facing-features)
      * [Admin & Health Professional Features](https://www.google.com/search?q=%23admin--health-professional-features)
  * [How It Works](https://www.google.com/search?q=%23how-it-works)
      * [Symptom Collection Workflow](https://www.google.com/search?q=%23symptom-collection-workflow)
      * [Outbreak Prediction Workflow](https://www.google.com/search?q=%23outbreak-prediction-workflow)
      * [Unidentified Disease Workflow](https://www.google.com/search?q=%23unidentified-disease-workflow)
  * [Technology Stack](https://www.google.com/search?q=%23technology-stack)
      * [Backend](https://www.google.com/search?q=%23backend)
      * [Frontend](https://www.google.com/search?q=%23frontend)
      * [Database](https://www.google.com/search?q=%23database)
  * [Project Structure](https://www.google.com/search?q=%23project-structure)
  * [Setup and Installation](https://www.google.com/search?q=%23setup-and-installation)
  * [API Endpoints](https://www.google.com/search?q=%23api-endpoints)

## Key Features

### Public-Facing Features

  * **Interactive Chatbot:** Users can describe their symptoms in natural language. The chatbot uses Natural Language Processing (NLP) to identify and understand the symptoms.
  * **Symptom Analysis:** The system analyzes reported symptoms, corrects spelling errors, and provides a potential diagnosis based on a pre-existing knowledge base.
  * **Health Facility Recommendation:** Users are advised to visit a local health facility (e.g., Mpilo Central Hospital) for a formal checkup.
  * **Educational Resources:** A search feature allows users to look up information about specific diseases.

### Admin & Health Professional Features

  * **Secure Login:** Authenticated access to the administrative dashboard.
  * **Dashboard Analytics:**
      * **Real-time Statistics:** View the total number of cases and statistics on the most prevalent condition.
      * **Geospatial Mapping:** Interactive map of Bulawayo's wards, visualizing the geographic distribution and density of diagnosed cases for selected diseases using GeoPandas.
      * **Data Visualization:** Dynamic bar charts showing cases per suburb and line graphs illustrating disease trends over time (daily, weekly, monthly).
      * **Tabular Data:** View detailed tables of the most common diseases, their infection counts, and the most affected suburbs.
  * **Outbreak Prediction:**
      * A machine learning model (loaded from `trained_model.pkl`) predicts the number of cases for the next day in each ward.
      * It uses a dynamic threshold based on ward population and disease severity to flag potential outbreaks.
      * **Automated Email Alerts:** Automatically sends an email notification via SMTP to a designated address when a potential outbreak is detected.
  * **Custom Reporting:** Generate detailed reports for a specific disease over a custom date range, complete with maps, graphs, and data tables.
  * **Diagnosis & Review Workflow:**
      * **Unidentified Symptom Clusters:** The system isolates and lists symptom sets that do not match any known disease.
      * **Doctor's Diagnosis:** A section for a doctor to review these unidentified clusters and provide a formal diagnosis.
      * **Review & Approval:** A workflow to approve or deny new diagnoses, which then updates the system's knowledge base, improving future automated diagnoses.

## How It Works

### Symptom Collection Workflow

1.  A user visits the website and selects their residential ward on a map of Bulawayo. This creates a unique, anonymous session.
2.  The user interacts with the chatbot, describing their symptoms.
3.  The backend receives the message, corrects spelling mistakes using `pyspellchecker`, and processes the text with a custom-trained **`spaCy`** model to extract `SYMPTOM` entities.
4.  The extracted symptoms are queried against the `symptoms.db` SQLite database to find the most likely disease.
5.  A potential diagnosis is returned to the user, and the entire interaction (symptoms, diagnosis, location, date) is logged in the database for analysis.

### Outbreak Prediction Workflow

1.  The system fetches the last 7 days of case data for a specific disease, organized by ward.
2.  This historical data is fed into a pre-trained machine learning model (`trained_model.pkl`).
3.  The model predicts the expected number of cases for the next day (`Day 8`) for each of the 29 wards.
4.  The system calculates a unique **outbreak threshold** for each ward by multiplying the ward's population by a percentage derived from the disease's severity score.
5.  If any ward's predicted case number exceeds its calculated threshold, an outbreak is flagged. An alert containing the disease and suburb is generated and sent via email.

### Unidentified Disease Workflow

1.  If the chatbot cannot match symptoms to a known disease, it logs the symptoms under a unique `Unindentified` code.
2.  These cases appear in a special table on the admin dashboard for review by a health professional.
3.  A professional can select an unidentified case, provide a diagnosis (e.g., "Seasonal Flu"), and submit it.
4.  This submission moves to a "Review" queue. Once approved, the system updates all records with the new diagnosis and adds the symptom-disease association to its knowledge base, making the system smarter over time.

## Technology Stack

### Backend

  * **Framework:** Flask
  * **Language:** Python 3
  * **Key Libraries:**
      * `pandas`: For data manipulation and analysis.
      * `geopandas`: For handling geospatial data and creating the choropleth map.
      * `spacy`: For Natural Language Processing (NER) to extract symptoms.
      * `scikit-learn` (via `pickle`): For loading and running the pre-trained outbreak prediction model.
      * `matplotlib`: For generating plots (though the frontend likely uses a JS library).
      * `pyspellchecker`: For correcting user input spelling.
      * `smtplib`: For sending email alerts.

### Frontend

  * **Markup/Styling:** HTML5, CSS3
  * **Framework:** Bootstrap
  * **Scripting:** JavaScript (for fetching data from backend API endpoints, rendering charts, and handling user interactions).

### Database

  * **Type:** Relational Database
  * **System:** SQLite 3 (`symptoms.db`)

## Project Structure

```
/project-root
│
├── EpiSymp.py              # Main Flask application file containing all backend logic.
├── trained_model.pkl       # Pre-trained machine learning model for outbreak prediction.
├── symptoms.db             # SQLite database file.
│
├── /templates/
│   ├── index.html          # Public-facing homepage with chatbot.
│   ├── login.html          # Admin login page.
│   ├── predict.html        # Main admin dashboard.
│   └── report.html         # Page to display generated reports.
│
├── /static/
│   ├── /css/               # CSS stylesheets.
│   ├── /js/                # JavaScript files for frontend logic.
│   └── /images/            # Image assets.
│
├── /new_model/ouput/
│   └── /model-best/        # Trained spaCy NLP model for symptom extraction.
│
├── /zwe_admbnda_adm3_zimstat_ocha_20180911/
│   └── ...                 # Shapefiles for Bulawayo geography.
│
└── requirements.txt        # List of Python dependencies.
```

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```


4.  **Download the spaCy model:**
    Ensure the `spacy` model referenced in the code (`new_model/ouput/model-best`) is present in the specified directory.

5.  **Initialize the Database:**
    Make sure the `symptoms.db` file is present and its schema is correctly set up with all required tables (e.g., `Survey`, `Users`, `Diseases`, `Suburb_list`, etc.).

6.  **Run the Flask application:**

    ```bash
    flask run
    # Or in debug mode
    python EpiSymp.py
    ```

    The application will be accessible at `http://127.0.0.1:5000`.

## API Endpoints

The application uses several API endpoints to dynamically load data for the frontend:

  * `/`: Main homepage.
  * `/save_data`: Saves the user's selected ward to the session.
  * `/get_response`: Endpoint for the chatbot interaction.
  * `/search`: Searches for disease information.
  * `/login`: Handles admin authentication.
  * `/predict`: Renders the main dashboard for authenticated users.
  * `/statsearch`: Searches for a disease and returns all relevant map, chart, and table data as JSON.
  * `/run`: Triggers the outbreak prediction model and sends an email if necessary.
  * `/report`: Generates and displays a custom report.
  * `/diag`, `/review`, `/approve`, `/deny`: Endpoints that manage the diagnosis and review workflow.
