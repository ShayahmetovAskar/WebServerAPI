from app import create_app
from waitress import serve

serve(create_app(), port=5000)
