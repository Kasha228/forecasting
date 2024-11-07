from forecasting import create_app
import json

app = create_app()
app.config['SERVER_NAME'] = 'localhost:5002'

with app.app_context():
    # Ensure all blueprints and namespaces are registered 
    _ = app.url_map 

    from forecasting.blueprints.api import api

    swagger_dict = api.__schema__

    with open('swagger.json', 'w') as f:
        json.dump(swagger_dict, f, indent=4)

    print('Swagger JSON saved successfully!')
    
del app.config['SERVER_NAME']
