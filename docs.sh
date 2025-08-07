#!/bin/bash

# MkDocs Documentation Management Script
# Usage: ./docs.sh [serve|build|deploy|gh-deploy]

case "$1" in
    "serve")
        echo "Starting MkDocs development server..."
        echo "Documentation will be available at: http://localhost:8000"
        echo "Press Ctrl+C to stop the server"
        mkdocs serve
        ;;
    "build")
        echo "Building static documentation site..."
        mkdocs build
        echo "Static site built in 'site/' directory"
        ;;
    "deploy")
        echo "Building and deploying to GitHub Pages..."
        mkdocs gh-deploy
        echo "Documentation deployed to GitHub Pages"
        ;;
esac 