import importlib.machinery
import importlib.util
import pkgutil
import connexion

if not hasattr(pkgutil, 'get_loader'):
    def get_loader(name):
        if name == '__main__':
            return importlib.machinery.SourceFileLoader(name, __file__)
        spec = importlib.util.find_spec(name)
        return spec.loader if spec is not None else None
    pkgutil.get_loader = get_loader

app = connexion.App(__name__, specification_dir='./')
app.add_api('openapi.yaml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
