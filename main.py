from app import create_app
from app.config import Config

app = create_app(Config)
Config.init_app(app)

if __name__ == '__main__':
    app.run(debug=True) 