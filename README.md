# Zendesk CX Bot

A FastAPI application that processes Zendesk webhook events and categorizes tickets using Hugging Face's inference API. **Now with Twilio WhatsApp support for creating tickets via WhatsApp messages using content templates.**

## Features

- Receives Zendesk webhook events for ticket creation
- Extracts subject and description from ticket data
- Uses Azure OpenAI for ticket categorization and analysis
- **NEW: WhatsApp ticket creation via Twilio with content templates**
- Logs all requests with detailed information
- Provides REST API endpoints for health checks

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory with your API keys:

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

# Twilio Configuration (NEW)
twilio_account_sid=your_twilio_account_sid
twilio_auth_token=your_twilio_auth_token
twilio_whatsapp_number=your_twilio_whatsapp_number
twilio_webhook_secret=your_twilio_webhook_secret  # Optional - for webhook signature validation
twilio_content_sid=your_twilio_content_sid
```

### 3. Get Azure OpenAI API Key

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to your Azure OpenAI resource
3. Go to "Keys and Endpoint" section
4. Copy the API key and endpoint URL
5. Add them to your `.env` file

### 4. Get Twilio Credentials (NEW)

1. Go to [Twilio Console](https://console.twilio.com/)
2. Get your Account SID and Auth Token
3. Set up WhatsApp Business API (requires approval from Twilio)
4. Get your WhatsApp number from Twilio
5. **Optional**: Create a content template for WhatsApp messages
   - Go to **Messaging** → **Content Editor**
   - Create a template with variables (e.g., `{{1}}` for message, `{{2}}` for ticket ID)
   - Copy the Content SID and add it to your `.env` file
6. Set up webhook endpoints in Twilio console:
   - WhatsApp webhook: `https://your-domain.com/twilio/whatsapp`
   - Status webhook: `https://your-domain.com/twilio/status` (optional)
7. Add credentials to your `.env` file

### 5. Run the Application

```bash
python main.py
```

The application will start on `http://localhost:8080`

## API Endpoints

### Health Check
- **GET** `/health` - Check if the service is running

### Webhook Endpoints
- **POST** `/ticketCreatedWebhook` - Receives Zendesk webhook events
- **POST** `/ticketStatusChangedWebhook` - Receives Zendesk status change events

### Twilio WhatsApp Endpoints (NEW)
- **POST** `/twilio/whatsapp` - Receives WhatsApp webhooks from Twilio
- **POST** `/twilio/status` - Receives message status callbacks from Twilio

## WhatsApp Ticket Creation Workflow (NEW)

### How it works:
1. Customer sends WhatsApp message to your Twilio WhatsApp number
2. Twilio webhook sends message to `/twilio/whatsapp` endpoint
3. System validates WhatsApp content (minimum 10 characters, meaningful content)
4. If valid → Creates Zendesk ticket automatically
5. If insufficient → Sends WhatsApp message asking for more details
6. Customer receives confirmation WhatsApp message with ticket number (using content template if configured)

### WhatsApp Validation Rules:
- **Minimum length**: 10 characters
- **Must contain actionable content**: Not just "hi", "help", "hello"
- **Should describe an issue or request**: Contains problem-related keywords

### Content Templates (Optional):
If you configure a `twilio_content_sid`, the system will use Twilio's content templates for responses:
- **Variable 1**: Truncated message content (first 50 characters)
- **Variable 2**: Ticket ID (if created successfully)

### Example WhatsApp Interactions:

**✅ Successful ticket creation:**
```
Customer: "I can't log into my account, getting error 404 when trying to access dashboard"
↓
System: Creates ticket #12345 with subject "I can't log into my account, getting error 404"
↓
System: "Ticket #12345 created: 'I can't log into my account, getting error 404'. We'll get back to you soon."
```

**❌ Insufficient content:**
```
Customer: "help"
↓
System: "Please provide more details about your issue. For example: 'I can't log in' or 'Billing question about invoice #123'"
```

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
- **NEW: WhatsApp content and validation results**
- **NEW: Content template usage status**

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

## Security Considerations

- **Twilio webhook validation**: All WhatsApp webhooks are validated using Twilio's signature verification
- **Content validation**: WhatsApp content is validated before ticket creation to prevent spam
- **Rate limiting**: Consider implementing rate limiting for WhatsApp endpoints in production
- **Logging**: All WhatsApp interactions are logged for audit purposes
