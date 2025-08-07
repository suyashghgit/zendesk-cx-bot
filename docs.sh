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
    "gh-deploy")
        echo "Deploying to GitHub Pages (manual method)..."
        echo "This will push the built site to the 'gh-pages' branch"
        mkdocs gh-deploy --force
        echo "Documentation deployed to GitHub Pages"
        echo "Visit: https://suyashghgit.github.io/zendesk-cx-bot/"
        ;;
    *)
        echo "Usage: ./docs.sh [serve|build|deploy|gh-deploy]"
        echo ""
        echo "Commands:"
        echo "  serve      - Start development server (http://localhost:8000)"
        echo "  build      - Build static site in 'site/' directory"
        echo "  deploy     - Build and deploy to GitHub Pages (manual)"
        echo "  gh-deploy  - Deploy to GitHub Pages (manual, with force)"
        echo ""
        echo "Examples:"
        echo "  ./docs.sh serve      # Start development server"
        echo "  ./docs.sh build      # Build static site"
        echo "  ./docs.sh deploy     # Deploy to GitHub Pages"
        echo "  ./docs.sh gh-deploy  # Force deploy to GitHub Pages"
        echo ""
        echo "GitHub Pages URL: https://suyashghgit.github.io/zendesk-cx-bot/"
        ;;
esac 