# RAML Implementation

This directory contains a Flask application representing our **RAML** API specification (`raml.raml`). 

RAML (RESTful API Modeling Language) is a YAML-based language for describing RESTful APIs.

## Project Structure

- `raml.raml`: The API specification.
- `app.py`: The Flask backend implementing the API logic.
- `index.html`: A custom, elegantly styled Test UI for CRUD operations.
- `docs.html`: Professional documentation generated via `raml2html`.
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

3. **(Optional) Generate Professional Documentation**:
   We use `raml2html` to generate a high-quality static documentation page:
   ```bash
   # Install raml2html globally
   npm install -g raml2html

   # Generate documentation
   raml2html raml.raml > docs.html
   ```

## Running the Server

Start the application by running:
```bash
python app.py
```
The server will start on **`http://127.0.0.1:5003`**.

## Testing the API

We provide two ways to interact with the API:

1. **Custom Test UI**: Navigate to **`http://127.0.0.1:5003/`**. This is a functional UI for CRUD operations.
2. **Professional Docs**: Navigate to **`http://127.0.0.1:5003/docs`** (after generating `docs.html`). This provides a beautifully rendered view of the RAML specification.

## Implementation Details

- **RAML**: Defines resources, methods, and data types in `raml.raml`.
- **Flask**: Implements manual routing in `app.py`.
- **CORS**: Enabled to allow seamless UI interaction.
