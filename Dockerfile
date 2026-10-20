FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn
COPY . .
ENV AGENT_BASE_URL=http://host.docker.internal:11434/v1
EXPOSE 8000
CMD ["uvicorn", "step16_serve:app", "--host", "0.0.0.0", "--port", "8000"]
