import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Railway!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))  # Используйте порт из переменной среды или 8080 по умолчанию
    app.run(host='0.0.0.0', port=port)  # Убедитесь, что указали хост 0.0.0.0
