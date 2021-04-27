from app import create_app
from waitress import serve

serve(create_app(), host='0.0.0.0', port=8080)
