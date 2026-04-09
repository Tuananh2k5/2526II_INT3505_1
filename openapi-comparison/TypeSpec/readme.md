# TypeSpec Implementation

This directory demonstrates **TypeSpec**, a modern API definition language by Microsoft. 

TypeSpec is designed to be highly reusable and compiles directly down to OpenAPI 3.0 (or other formats). To utilize it within Python (Flask), we compile the TypeSpec into OpenAPI, and then use `connexion` to execute it (just like we did in the OpenAPI folder!).

## Requirements and Compilation

TypeSpec requires Node.js.

1. **Install TypeSpec tools locally** via npm:
   ```bash
   npm install
   ```

2. **Compile the specification**:
   ```bash
   npm run build
   ```
   *This command runs the compiler, converting `main.tsp` to `openapi.yaml` located at `tsp-output/@typespec/openapi3/openapi.yaml`.*

## Python Server Installation

1. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

Start the application:
```bash
python app.py
```
The server will start on `http://127.0.0.1:5004`.

## Testing the API (Swagger UI)

Because our output is an OpenAPI specification, we get Swagger UI inherently.
Navigate to `http://127.0.0.1:5004/api/ui/` in your browser. This will open the automatically generated Swagger UI where you can perform Create, Read, Update, and Delete (CRUD) operations on Users.
