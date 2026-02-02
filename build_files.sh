#!/bin/bash

# Build script for Vercel deployment
echo "Installing dependencies..."
uv pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Copying static files to build directory..."
mkdir -p staticfiles_build
cp -r staticfiles/* staticfiles_build/

echo "Build completed successfully!"
