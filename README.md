# Semantic Search Engine

**Semantic Search Engine** - A search engine to find your desired style only by describing what you have in your mind!

---

## Features

- **Scalable Data Service** - Supports custom datasets with vector-based indexing.
- **Backend REST API** - Provides a semantic search backend service.
- **Frontend Page** - Offers a simple user interface for visualizing search results.

---

## Table of Contents

- [How to Run](#how-to-run)
  - [Deployment Mode](#deployment-mode)
  - [Local Development Mode](#local-development-mode)
    - [Running the Data Service](#running-the-data-service)
    - [Running the Backend Service](#running-the-backend-service)
- [Demonstration](#demonstration)
- [Environment Variables](#environment-variables)
- [License](#license)

---

## How to Run

### Deployment Mode

If you want to run the project in **deployment mode**, just use the following command:

```bash
docker compose up searchengine
```

This will start the entire system in deployment mode.

---

### Local Development Mode

To run the project locally for development purposes, you must run the **data service** and **backend service** separately.

---

#### Running the Data Service

1. Navigate to the `data` directory:
   ```bash
   cd data
   ```
2. Run the service:
   ```bash
   python main.py
   ```

> **Note:**  
> - The data service relies on custom product data, which is not publicly available. You must provide your own dataset to proceed.  
> - The service uses **Pinecone** for vector database storage. You need to set up a Pinecone account and include your API key in a `.env` file. (See [Environment Variables](#environment-variables) for more information.)

This runs the data service locally on `http://localhost:5000`.

---

#### Running the Backend Service

1. Navigate to the backend service directory:
   ```bash
   cd search_engine/semantic_search_backend
   ```
2. Apply database migrations:
   ```bash
   python manage.py migrate
   ```
3. Collect static files (skip this step if unnecessary for development):
   ```bash
   python manage.py collectstatic --noinput
   ```
4. Run the backend server:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

This runs the backend service locally on `http://localhost:8000`.

---

### Access the Application

Once both services are running, you can access the application in your browser:

- Navigate to: **[http://localhost:8000/static/page.html](http://localhost:8000/static/page.html)**

This page allows you to interact with the search engine.

---

## Demonstration

Below are some preview images of how the interface looks in action:


The intial page:

![Demo 6](figures/d0.png)

Some examples of search results:

| ![Demo 1](figures/d1.png) | ![Demo 2](figures/d2.png) | ![Demo 3](figures/d3.png) |
|--------------------|--------------------|--------------------|
| ![Demo 4](figures/d4.png) | ![Demo 5](figures/d5.png) | ![Demo 6](figures/d6.png) |


---

## Environment Variables

The project requires certain environment variables to be set up in a `.env` file. Below are the key variables and their purpose:

1. **Pinecone API Key**:
   - Used for connecting to the Pinecone vector database service.
   ```ini
   PINECONE_API_KEY=your-api-key-here
   ```

2. **Other Variables** (if applicable):
   - Add additional `.env` variables here, with a description of their usage.

> Ensure the `.env` file is located in the root directory or appropriately configured for each service.

---
