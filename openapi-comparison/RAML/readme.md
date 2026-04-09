# RAML Implementation

This directory contains a Flask application representing our **RAML** API specification (`raml.raml`).

Much like API Blueprint, RAML parsing in Python servers to do automatic routing isn't natively as standardized as OpenAPI (`connexion`). So here, the API is defined cleanly in RAML, and the Flask app implements the CRUD.

## Requirements

The RAML file structure uses YAML to specify resources, types, and methods clearly.

## Installation

1. Prepare your Python environment:
   ```bash
   pip install -r requirements.txt
   ```

2. (Optional) To render the official documentation from the RAML file using API Console GUI:
   ```bash
   npm install -g api-console-cli
   api-console build raml.raml -o docs
   ```

## Running the Server

Start the application:
```bash
python app.py
```
The server will start on `http://127.0.0.1:5003`.

## Testing the API (Custom Test UI)

Navigate to `http://127.0.0.1:5003/`. Unlike OpenAPI which ships with Swagger out of the box, we provide an elegantly styled HTML Test UI to perform the Users CRUD operations.

## Managing the Setup

- **Design**: Open `raml.raml` to design endpoints mapping to resources.
- **Implement**: Create the matching routes on `app.py`.
