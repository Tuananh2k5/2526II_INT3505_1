# OpenAPI Implementation

This directory contains a Flask application driven by an OpenAPI 3.0 specification (`openapi.yaml`). We use the `connexion` Python library, which natively routes HTTP requests mapped in the OpenAPI file directly to Python functions, and automatically hosts a Swagger UI dashboard.

## Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

Start the application:
```bash
python app.py
```
The server will start on `http://127.0.0.1:5001`.

## Testing the API (Swagger UI)

Navigate to `http://127.0.0.1:5001/api/ui/` in your browser. This will open the automatically generated Swagger UI where you can perform Create, Read, Update, and Delete (CRUD) operations on Users.

## Editing the API Requirements

- **Modify Endpoints**: Open `openapi.yaml` and update the routes or schemas. Be sure to link operations via `operationId: api.<function_name>`.
- **Implement Logic**: Open `api.py` and modify the dictionary logic or connect a real database (like SQLAlchemy).
