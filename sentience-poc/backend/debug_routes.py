from app import app
import sys

print("Routes:")
for route in app.routes:
    print(route.path)
