import connexion

# Initialize Connexion app, pointing to the default folder TypeSpec outputs to
app = connexion.App(__name__, specification_dir='./tsp-output/@typespec/openapi3')
app.add_api('openapi.yaml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
