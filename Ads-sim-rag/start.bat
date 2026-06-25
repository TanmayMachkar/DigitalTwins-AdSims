@echo off
start "TwinSphere Backend" cmd /k "uvicorn backend.main:app --port 8000"
timeout /t 2
start "TwinSphere Frontend" cmd /k "cd frontend && npm run dev"
echo TwinSphere starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
