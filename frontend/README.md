# Frontend — SOC Triage Dashboard 

React single-page dashboard for displaying network connection triage results from the backend REST API. 

## Structure 

* `src/App.js` - Main UI layout, API fetching logic, and mock fallback handlers.
* `src/App.css` - Stylesheet formatted for high-contrast WCAG AAA compliance. 
* `public/index.html` - Base HTML template with accessible semantic landmarks. 

## Development 

Run `npm start` from this directory to start the local development server at `http://localhost:3000`. 

By default, the UI attempts to connect to the backend at `http://localhost:5000/api/triage'.