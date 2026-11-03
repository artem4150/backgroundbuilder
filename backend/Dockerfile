FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt
COPY backend/main.py ./
COPY backend/app ./app
COPY frontend/app/catalog.json /data/catalog.json
COPY frontend/shared/palettes.json /data/palettes.json
COPY frontend/public/assets /data/assets
ENV PALETTES_PATH=/data/palettes.json
ENV ASSET_DIR=/data/assets CATALOG_PATH=/data/catalog.json
RUN useradd --create-home service
USER service
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
