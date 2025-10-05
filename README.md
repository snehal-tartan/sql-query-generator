# SQL Query Generator 

## Project Structure 

```
sql-query-generator-project/
├─ backend/
│  ├─ app.py                # FastAPI entry point
│  ├─ database.py           # DB engine & schema helpers
│  ├─ query_generator.py    # SQL generation & execution (OpenAI + SQLAlchemy)
│  ├─ graph_generator.py    # Headless graph PNG base64 generator
│  ├─ routers/
│  │  ├─ auth.py            # Connect DB, status
│  │  ├─ query.py           # Generate & execute SQL endpoints
│  │  └─ graph.py           # Generate graph endpoint
│  └─ requirements.txt
├─ frontend/
│  └─ ui.py                 # Streamlit frontend (legacy/testing)
├─ react-frontend/
│  ├─ src/
│  │  ├─ api/
│  │  │  ├─ client.ts       # Axios client setup
│  │  │  └─ services.ts     # API service functions
│  │  ├─ components/
│  │  │  ├─ Sidebar/        # Left sidebar navigation
│  │  │  ├─ Header/         # Top header with user info
│  │  │  └─ QueryGenerator/ # Main query generation component
│  │  ├─ App.tsx            # Main app layout
│  │  └─ main.tsx           # App entry point
│  ├─ package.json
│  └─ .env                  # VITE_API_URL=http://127.0.0.1:8000
├─ .env                     # OPEN_AI_API_KEY (never commit)
└─ README.md
```

## Run Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn backend.app:app --reload
```
Backend runs at: `http://127.0.0.1:8000`  
API Docs: `http://127.0.0.1:8000/docs`

## Run Frontend (React - Production)
```bash
cd react-frontend
npm install  # if not already done
npm run dev
```
React app runs at: `http://localhost:5173`

## Run Frontend (Streamlit - Legacy/Testing)
```bash
cd frontend
streamlit run ui.py
```

## Environment Setup

### Backend (.env in project root)
```
OPEN_AI_API_KEY=sk-...
API_URL=http://127.0.0.1:8000
```

### React Frontend (.env in react-frontend/)
```
VITE_API_URL=http://127.0.0.1:8000
```

## Component Architecture (React)

### 1. **Sidebar** (`src/components/Sidebar/`)
- Logo placeholder (customizable)
- Navigation menu (empty, ready for items)
- Collapsible design

### 2. **Header** (`src/components/Header/`)
- User profile display
- Account management

### 3. **QueryGenerator** (`src/components/QueryGenerator/`)
- Natural language prompt input
- SQL query generation
- Real-time API integration
- Error handling

### 4. **API Layer** (`src/api/`)
- `client.ts`: Axios configuration
- `services.ts`: Type-safe API functions

## Features

✅ Clean, production-ready UI matching design specs  
✅ Component-based React architecture  
✅ TypeScript for type safety  
✅ Material-UI for consistent design  
✅ React Query for data fetching  
✅ FastAPI backend with CORS  
✅ OpenAI-powered SQL generation  
✅ MySQL database integration  

## Next Steps

1. Add sidebar navigation items
2. Implement database connection UI in React
3. Add SQL execution & table display
4. Integrate graph generation
5. Add authentication/authorization
6. Deploy to production

The frontend expects the backend at `http://127.0.0.1:8000`. Adjust via `.env` files if needed.
