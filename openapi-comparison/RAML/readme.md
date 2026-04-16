# RAML Implementation

This directory contains a Flask application representing our **RAML** API specification (`raml.raml`). 

RAML (RESTful API Modeling Language) is a YAML-based language for describing RESTful APIs.

## Project Structure

- `raml.raml`: The API specification.
- `app.py`: The Flask backend implementing the API logic.
- `index.html`: A custom, elegantly styled Test UI for CRUD operations.
- `openapi.json`: OpenAPI specification converted from RAML.
- `swagger-ui.html`: Interactive Swagger UI for professional testing.
- `requirements.txt`: Python dependencies.

## Installation & Setup

1. **Prepare the environment**:
   It is recommended to use a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Generate Interactive Documentation**:
   Since native RAML interactive tools can be problematic, we convert the specification to OpenAPI to leverage the powerful **Swagger UI**:
   ```bash
   # Install the converter
   npm install -g oas-raml-converter

   # Convert RAML to OpenAPI 3.0
   oas-raml-converter --from RAML --to OAS30 raml.raml > openapi.json
   ```

## Running the Server

Start the application by running:
```bash
python app.py
```
The server will start on **`http://127.0.0.1:5003`**.

## Testing the API

We provide two ways to interact with the API:

1. **Custom Test UI**: Navigate to **`http://127.0.0.1:5003/`**. This is a functional UI for basic CRUD operations.
2. **Professional Interactive Docs**: Navigate to **`http://127.0.0.1:5003/docs`**. This uses **Swagger UI** to provide a professional, interactive experience (with "Try it Out" support) based on your RAML definition.

## Implementation Details

- **RAML**: Defines resources, methods, and data types in `raml.raml`.
- **Conversion**: The `openapi.json` is proof that RAML can be easily integrated into the broader OpenAPI ecosystem.
- **Flask**: Implements manual routing in `app.py`.
- **CORS**: Enabled to allow seamless UI interaction.
