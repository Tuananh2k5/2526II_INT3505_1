# API Blueprint Implementation

This directory contains a Flask application and an API Blueprint configuration (`apiBlueprint.apib`). 

 Unlike OpenAPI, API Blueprint lacks a native Python extension like `connexion` to magically link routes and provide a server-rendered Swagger UI. Instead, we manually implemented the Flask routes mirroring the Blueprint document, and provide an HTML-based testing UI.

## Requirements

The API Blueprint file (`.apib`) is written in Markdown format. To render the documentation professionally, you would typically use an external CLI tool like **Aglio** or **Snowboard** (NodeJS based).

## Installation

1. Prepare your Python environment:
   ```bash
   pip install -r requirements.txt
   ```

2. (Optional) To render the official documentation from the API Blueprint file using Aglio:
   ```bash
   npm install -g aglio
   aglio -i apiBlueprint.apib -o docs.html
   ```

## Running the Server

Start the application:
```bash
python app.py
```
The server will start on `http://127.0.0.1:5002`.

## Testing the API (Custom Test UI)

Navigate to `http://127.0.0.1:5002/` directly to access the custom API Testing UI plugin to interact with the endpoints. This replaces Swagger UI since we don't have native compilation.

## Adding Features

- Open `apiBlueprint.apib` and use Markdown formatting to add new resources or actions.
- Modify `app.py` to add new Flask `@app.route` handlers for those endpoints.
