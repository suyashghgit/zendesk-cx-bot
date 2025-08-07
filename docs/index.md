# Zendesk CX Bot Documentation

Welcome to the documentation for the **Zendesk CX Bot** - an intelligent FastAPI application that automates ticket categorization and analysis for Zendesk customer support systems.

## 🚀 Quick Start

The Zendesk CX Bot leverages Azure OpenAI's advanced language models to provide real-time ticket processing, automatic categorization, and quality analysis, significantly improving customer support efficiency and decision-making.

### Key Features

- **🤖 AI-Powered Ticket Categorization**: Automatic categorization using Azure OpenAI
- **📊 Support Quality Analysis**: Comprehensive analysis of support interactions
- **📱 WhatsApp Integration**: Create tickets directly through WhatsApp messages
- **🔄 Real-time Processing**: Webhook-based automation for instant responses
- **📈 Scalable Architecture**: Handles any volume of tickets efficiently

## 📚 Documentation Sections

### [Overview](APPLICATION_WRITEUP.md)
Comprehensive technical documentation covering:
- Problem statement and solution approach
- Architecture overview and key components
- Core functionality details
- Technical implementation and configuration
- Business and technical value

### [Architecture](architecture-diagram.md)
System architecture visualization showing:
- WhatsApp ticket creation flow
- Regular Zendesk ticket creation flow
- Common categorization flow
- Ticket solved analysis process

### [Development Setup](LOCAL_DEVELOPMENT_SETUP.md)
Local development guide including:
- ngrok setup for local development
- Twilio webhook configuration
- Testing and troubleshooting steps
- Production deployment considerations

## 🛠 Technology Stack

- **Backend Framework**: FastAPI (Python)
- **AI Engine**: Azure OpenAI GPT models
- **API Integration**: Zendesk REST API
- **Messaging Platform**: Twilio WhatsApp Business API
- **Configuration**: Pydantic Settings
- **Logging**: Python logging with file and console output
- **Deployment**: Uvicorn server

## 🎯 Use Cases

1. **Automatic Ticket Categorization**: When a new ticket is created, the system automatically categorizes it into predefined categories using AI analysis.

2. **Support Quality Analysis**: When a ticket is marked as "SOLVED", the system analyzes the entire conversation for sentiment, empathy, clarity, and provides actionable insights.

3. **WhatsApp Integration**: Customers can create support tickets directly through WhatsApp messages, with automatic validation and ticket creation.

## 🔧 Getting Started

1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Configure Environment**: Copy `env_example.txt` to `.env` and fill in your credentials
3. **Run Application**: `python main.py`
4. **Access Documentation**: Visit the sections above for detailed guides

## 📖 Additional Resources

- **GitHub Repository**: [zendesk-cx-bot](https://github.com/your-username/zendesk-cx-bot)
- **Environment Setup**: See `env_example.txt` for required configuration
- **Requirements**: See `requirements.txt` for Python dependencies

---

*This documentation is built with [MkDocs](https://www.mkdocs.org/) and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme.*
