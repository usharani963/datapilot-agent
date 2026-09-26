# 🤖 DataPilot — Agentic AI Data Analysis Assistant

DataPilot is an **Agentic AI Data Analysis Assistant** that allows users to upload a CSV dataset and ask questions in natural language.

The system automatically:

1. Creates an analysis plan.
2. Understands the user's question.
3. Selects the appropriate analysis tool.
4. Executes the tool on the dataset.
5. Observes the result.
6. Decides the next action.
7. Generates a natural-language answer.

---

## 🚀 Features

- 📁 Upload CSV datasets
- 🤖 Agent-based decision making
- 🧠 Automatic analysis planning
- 📊 Statistical analysis
- 🔗 Correlation analysis
- 📈 Group-by analysis
- 🔎 Data filtering
- 📉 Data visualization
- 💬 Natural-language questions
- 🔄 Multi-step agent execution
- 🛡️ Error handling and tool validation
- ⚡ Groq LLM integration

---

## 🏗️ Architecture

```text
User
  ↓
Streamlit UI
  ↓
DataPilot Agent
  ↓
Planner
  ↓
Decision Maker
  ↓
Tool Selection
  ↓
┌─────────────────────────────┐
│ dataset_info                │
│ statistics                  │
│ group_by                    │
│ correlation                 │
│ filter                      │
│ visualization               │
└─────────────────────────────┘
  ↓
Tool Results
  ↓
Agent Observations
  ↓
Final Answer
```

---

## 🛠️ Technologies Used

- Python
- Pandas
- Streamlit
- LangChain
- Groq API
- OpenAI GPT-OSS 20B
- python-dotenv
- Matplotlib

---

## 📂 Project Structure

```text
datapilot-agent/
│
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── planner.py
│   ├── state.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── dataset_info.py
│       ├── statistics.py
│       ├── group_by.py
│       ├── correlation.py
│       ├── filter.py
│       └── visualization.py
│
├── data/
│   └── sample.csv
│
├── streamlit_app.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## 📊 Example Dataset

DataPilot can work with datasets containing columns such as:

```text
state
crop
area
production
rainfall
fertilizer
pesticide
yield
```

Example:

```csv
state,crop,area,production,rainfall,fertilizer,pesticide,yield
Andhra Pradesh,Rice,120,420,820,150,30,3.50
Telangana,Rice,110,390,850,145,28,3.55
Karnataka,Rice,100,350,680,130,25,3.50
Tamil Nadu,Rice,90,330,920,125,22,3.67
Maharashtra,Cotton,180,510,620,190,40,2.83
```

---

## 💬 Example Questions

### Average yield by state

```text
Which state has the highest average yield?
```

DataPilot uses the `group_by` tool.

Example result:

```text
Tamil Nadu has the highest average yield.
Average yield: 3.53
```

### Correlation analysis

```text
What are the strongest relationships with crop yield?
```

DataPilot calculates correlations between `yield` and other numeric variables.

Example:

```text
Area        -0.9499
Pesticide   -0.9237
Fertilizer  -0.9052
Production  -0.8539
Rainfall     0.8101
```

### Visualization

```text
Show average yield by state as a bar chart.
```

The agent performs the required grouped analysis and generates a visualization.

---

## 🧠 Agent Workflow

For every user question, DataPilot follows an agent loop:

```text
Question
   ↓
Create Plan
   ↓
Choose Tool
   ↓
Execute Tool
   ↓
Store Observation
   ↓
Check Result
   ↓
Need More Analysis?
   ├── Yes → Choose Next Tool
   │
   └── No → Generate Final Answer
```

The agent uses previous observations to avoid unnecessary repeated tool calls.

---

## 🔧 Available Tools

### `dataset_info`

Provides information about:

- Number of rows
- Number of columns
- Column names
- Data types
- Missing values

### `statistics`

Calculates statistics for numeric columns.

### `group_by`

Groups categorical data and calculates:

- Mean
- Sum
- Maximum
- Minimum

### `correlation`

Calculates Pearson correlation between two numeric columns.

### `filter`

Filters dataset rows based on a column and value.

### `visualization`

Creates data for charts such as bar charts.

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/usharani963/datapilot-agent.git
```

Move into the project:

```bash
cd datapilot-agent
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Do **not** commit your `.env` file to GitHub.

Add this to `.gitignore`:

```text
.env
venv/
__pycache__/
*.pyc
```

---

## ▶️ Run the Application

Start Streamlit:

```bash
streamlit run streamlit_app.py
```

The application will open in your browser.

Usually:

```text
http://localhost:8501
```

---

## 🔐 Security

The Groq API key is loaded from an environment variable.

```python
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
```

The API key should never be directly written inside the source code or committed to GitHub.

---

## 🎯 Project Objective

The main objective of DataPilot is to demonstrate how **Agentic AI can automate data analysis**.

Instead of requiring users to manually select Python functions or statistical methods, the agent interprets the natural-language question and dynamically selects the appropriate analysis tool.

---

## 🔮 Future Improvements

- Support more visualization types
- Automatic data cleaning
- More statistical analysis tools
- Machine learning analysis
- Automatic anomaly detection
- Export analysis reports
- Support Excel files
- Conversational follow-up questions
- Multi-dataset analysis
- Improved agent memory

---

## 👩‍💻 Author

**Usha Rani**

GitHub: https://github.com/usharani963

---

## ⭐ Project

If you find this project useful, consider giving the repository a ⭐ on GitHub.
