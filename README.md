# Zendesk CX Bot

An intelligent FastAPI application that automates ticket categorization and analysis for Zendesk customer support systems. Leverages Azure OpenAI's advanced language models to provide real-time ticket processing, automatic categorization, and quality analysis.

## 🚀 Features

- **🤖 AI-Powered Ticket Categorization**: Automatic categorization using Azure OpenAI
- **📊 Support Quality Analysis**: Comprehensive analysis of support interactions
- **📱 WhatsApp Integration**: Create tickets directly through WhatsApp messages
- **🔄 Real-time Processing**: Webhook-based automation for instant responses
- **📈 Scalable Architecture**: Handles any volume of tickets efficiently

## 📚 Documentation

This project includes comprehensive documentation built with **MkDocs** and the **Material for MkDocs** theme.

### Viewing Documentation

1. **Local Development Server**:
   ```bash
   ./docs.sh serve
   ```
   Then visit: http://localhost:8000

2. **Build Static Site**:
   ```bash
   ./docs.sh build
   ```
   Static files will be generated in the `site/` directory.

3. **Deploy to GitHub Pages**:
   ```bash
   ./docs.sh deploy
   ```

### Documentation Structure

- **Home**: Project overview and quick start guide
- **Overview**: Comprehensive technical documentation (`APPLICATION_WRITEUP.md`)
- **Architecture**: System architecture visualization (`architecture-diagram.md`)
- **Development Setup**: Local development guide (`LOCAL_DEVELOPMENT_SETUP.md`)

## 🛠 Quick Start

### Prerequisites

- Python 3.8+
- Azure OpenAI account and API key
- Zendesk account with API access
- Twilio account with WhatsApp Business API access

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd zendesk-cx-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp env_example.txt .env
   # Edit .env with your actual credentials
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **View documentation**:
   ```bash
   ./docs.sh serve
   ```

## 🏗 Architecture

The application follows a microservices architecture with clear separation of concerns:

- **FastAPI Application**: Main server with webhook endpoints
- **Azure OpenAI Service**: AI-powered categorization and analysis
- **Zendesk Service**: API integration for ticket management
- **Twilio Service**: WhatsApp integration for ticket creation
- **Webhook Routers**: Handle incoming webhooks from Zendesk and Twilio

## 📖 Documentation Features

The MkDocs documentation includes:

- **Responsive Design**: Works great on mobile and desktop
- **Search Functionality**: Built-in search with keyboard navigation
- **Dark/Light Mode**: Toggle between themes
- **Code Highlighting**: Syntax highlighting for code blocks
- **Navigation**: Easy navigation with table of contents
- **Git Integration**: Shows last modified dates (when in git repository)

## 🔧 Development

### Running Tests
```bash
pytest
```

### Documentation Development
```bash
# Start development server with auto-reload
./docs.sh serve

# Build static site
./docs.sh build

# Deploy to GitHub Pages
./docs.sh deploy
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Update documentation if needed
5. Submit a pull request

---

*Documentation built with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)* 