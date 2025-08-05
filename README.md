# Zendesk CX Bot

A FastAPI application that processes Zendesk webhook events and categorizes tickets using Hugging Face's inference API.

## Features

- Receives Zendesk webhook events for ticket creation
- Extracts subject and description from ticket data
- Uses Hugging Face's BART-large-MNLI model for ticket categorization
- Logs all requests with detailed information
- Provides REST API endpoints for health checks

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory with your Hugging Face API key:

```env
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

### 3. Get Hugging Face API Key

1. Go to [Hugging Face](https://huggingface.co/)
2. Create an account or sign in
3. Go to your profile settings
4. Navigate to "Access Tokens"
5. Create a new token with "read" permissions
6. Copy the token and add it to your `.env` file

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
- Hugging Face API response
- Categorization results

## Model Information

This application uses the `facebook/bart-large-mnli` model from Hugging Face, which is:
- Free to use (with API rate limits)
- Optimized for text classification tasks
- Provides confidence scores for predictions
- Supports zero-shot classification

## Configuration

The application uses the following Hugging Face model:
- **Model**: `facebook/bart-large-mnli`
- **Task**: Zero-shot text classification
- **API Endpoint**: `https://api-inference.huggingface.co/models/facebook/bart-large-mnli`

## Development

To run in development mode with auto-reload:

```bash
python main.py
```

The application will automatically reload when you make changes to the code.
