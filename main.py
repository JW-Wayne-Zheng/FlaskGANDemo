import os
from app import create_app
from app.config import Config

app = create_app(Config)
Config.init_app(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, port=port) 