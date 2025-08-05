# Zendesk CX Bot

A FastAPI application that processes Zendesk webhook events and categorizes tickets using Hugging Face's inference API.

## Features

- Receives Zendesk webhook events for ticket creation
- Extracts subject and description from ticket data
- Uses Azure OpenAI for ticket categorization and analysis
- Logs all requests with detailed information
- Provides REST API endpoints for health checks

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory with your Azure OpenAI API key:

```env
# Azure OpenAI Configuration
azure_openai_api_key=your_azure_openai_api_key_here
azure_openai_endpoint=https://your-resource.cognitiveservices.azure.com/
azure_openai_deployment=your-deployment-name
azure_openai_model=your-model-name
azure_openai_api_version=2024-12-01-preview

# Zendesk Configuration (optional)
zendesk_domain=your-zendesk-domain
zendesk_email=your-zendesk-email
zendesk_api_key=your-zendesk-api-key
```

### 3. Get Azure OpenAI API Key

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to your Azure OpenAI resource
3. Go to "Keys and Endpoint" section
4. Copy the API key and endpoint URL
5. Add them to your `.env` file

### 4. Run the Application

```bash
python main.py
```

The application will start on `http://localhost:8080`

## API Endpoints

### Health Check
- **GET** `/health` - Check if the service is running

### Webhook Endpoint
- **POST** `/ticketCreatedWebhook` - Receives Zendesk webhook events

## Ticket Categories

The application categorizes tickets into the following categories:

- `human_resources`
- `engineering`
- `it_support`
- `product`
- `design`
- `sales`
- `marketing`
- `finance`
- `legal`
- `customer_support`
- `operations`
- `executive`

## Logging

All webhook requests are logged to:
- Console output for immediate visibility
- `logs/webhook_requests.log` for persistent storage

Each request gets a unique UUID for tracking and includes:
- Request headers and body
- Extracted ticket data
- Rendered template
- Azure OpenAI API response
- Categorization results

## Model Information

This application uses Azure OpenAI for:
- Ticket categorization with confidence scores
- Support quality analysis and insights
- Structured JSON responses for easy integration
- Customizable prompts for different use cases

## Configuration

The application uses Azure OpenAI with the following configuration:
- **Service**: Azure OpenAI
- **Tasks**: Text categorization and analysis
- **Response Format**: Structured JSON
- **Customizable**: Prompts and parameters can be adjusted

## Development

To run in development mode with auto-reload:

```bash
python main.py
```

The application will automatically reload when you make changes to the code.
