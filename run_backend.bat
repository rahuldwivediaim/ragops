@echo off
echo ========================================
echo Starting RAG Framework Backend
echo ========================================

call .venv\Scripts\activate

python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8002
