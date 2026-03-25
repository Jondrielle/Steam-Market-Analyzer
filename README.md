# Steam-Market-Analyzer
Scrapes Steam game prices and user reviews, performs sentiment analysis, and visualizes trends with Python and Pandas.

## Project Structure 
<details>

```
Analyzer/
├── backend/
│   ├── logic/
│   │   └── calculator.py
│   ├── models/
│   │   └── arithmetic_models.py
│   ├── routes/
│   │   └── arithmetic_routes.py
│   ├── __init__.py
│   └── main.py
├── backend_test/
│   ├── test_calculator_logic.py
│   ├── test_routs.py
├── frontend/
│   ├── src/
│   │   ├── components
│   │   │   └── Calculator.vue
│   │   ├── services
│   │   │   └── api.js
│   │   ├── App.vue
│   │   └── main.js
│   ├── public/
│   └── package.json
├── Dockerfile
├── .dockerignore
├── main.py
├── .gitignore
├── README.md
└── requirements.txt
  
```
</details> 

## Features 
- Search games using a custom backend API
- Add games to personal list
- Remove games from the list
- View price history trends for selected games
- Toggle price history by period(daily,monthly,yearly)
- View review summary(total,positive,negative reviews)
- Toast notifications for user actions(e.g. game added)
- Click outside to close search results dropdown


## Technologies Used
- Backend: Python, Requests, BeautifulSoup, Pandas, NumPy, CSV, FastAPI
- Frontend: Vue,JavaScript, HTML/CSS, Tailwind CSS
- Version Control: Git, GitHub
- Data & APIs: Steam Store API, Custom REST API(FastAPI)

## Getting Started
#### Prerequisites: 

## Development 
