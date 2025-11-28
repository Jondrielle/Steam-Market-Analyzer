# Steam-Market-Analyzer
Scrapes Steam game prices and user reviews, performs sentiment analysis, and visualizes trends with Python, Pandas, and Matplotlib.

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
- Dynamic Game Lookup
  - Input a game name to fetch its AppID from Steam
- Price Tracking
  - Get current price, discount, and original price
- Review Scraping
  - Collect a few user reviews (text, date, helpful votes)
- Data Storage
  - Save all scraped data to a CSV for analysis 


## Technologies Used
- Backend: Python, Requests, BeautifulSoup, Pandas, NumPy, CSV
- Frontend: Matplotlib
- Version Control: Git, GitHub

## Getting Started
#### Prerequisites: 

## Development 
