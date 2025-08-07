# WhatsApp Integration Guide

This guide covers the complete WhatsApp integration functionality for creating Zendesk tickets from WhatsApp messages.

## 🎯 Overview

The WhatsApp integration allows customers to create Zendesk support tickets directly through WhatsApp messages. The system automatically:

1. **Receives** WhatsApp messages via Twilio webhooks
2. **Validates** message content for sufficient detail
3. **Creates** Zendesk tickets for valid requests
4. **Responds** to customers with confirmation messages
5. **Handles** errors gracefully with appropriate responses

## 🏗️ Architecture

```
Customer WhatsApp → Twilio → Webhook → FastAPI → Zendesk API
                                    ↓
                              Validation & Processing
                                    ↓
                              Ticket Creation
                                    ↓
                              WhatsApp Response
```

## 📋 Prerequisites

### 1. Twilio Account Setup
- [ ] Twilio account with WhatsApp Business API access
- [ ] WhatsApp number configured
- [ ] Webhook endpoints configured
- [ ] Content templates (optional but recommended)

### 2. Zendesk Configuration
- [ ] Zendesk account with API access
- [ ] API token generated
- [ ] Domain configured
- [ ] Email configured

### 3. Environment Variables
```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=+1234567890
TWILIO_WEBHOOK_SECRET=your_webhook_secret
TWILIO_CONTENT_SID=your_content_sid

# Zendesk Configuration
ZENDESK_API_KEY=your_api_key
ZENDESK_DOMAIN=your-domain.zendesk.com
ZENDESK_EMAIL=your-email@domain.com
```

## 🚀 Quick Start

### 1. Start the Application
```bash
python main.py
```

### 2. Configure Twilio Webhooks
1. Go to Twilio Console → Messaging → Settings → WhatsApp
2. Set webhook URL: `https://your-domain.com/twilio/whatsapp`
3. Set HTTP method: `POST`

### 3. Test the Integration
```bash
python test_whatsapp_integration.py
```

## 📊 API Endpoints

### WhatsApp Webhook
- **URL**: `POST /twilio/whatsapp`
- **Purpose**: Receives WhatsApp messages from Twilio
- **Parameters**:
  - `From`: Sender's phone number (with whatsapp: prefix)
  - `Body`: WhatsApp message content
  - `MessageSid`: Twilio message SID
  - `To`: Recipient phone number

### Example Request
```bash
curl -X POST "https://your-domain.com/twilio/whatsapp" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+1234567890&Body=I can't log into my account&MessageSid=SM1234567890&To=whatsapp:+1234567890"
```

## 🔍 Content Validation

### Validation Rules
1. **Minimum Length**: 10 characters
2. **Meaningful Content**: Not just greetings or generic words
3. **Actionable Content**: Contains issue-related keywords

### Valid Keywords
- `problem`, `issue`, `error`, `bug`, `broken`
- `not working`, `can't`, `cannot`, `failed`
- `trouble`, `difficulty`, `question`, `inquiry`
- `request`, `need`, `want`, `looking for`

### Example Valid Messages
```
✅ "I can't log into my account, getting error 404"
✅ "Billing question about invoice #12345"
✅ "Need help with password reset"
✅ "System is down, urgent assistance needed"
```

### Example Invalid Messages
```
❌ "hi"
❌ "help"
❌ "hello"
❌ "thanks"
❌ "ok"
```

## 🎫 Ticket Creation

### Ticket Structure
```json
{
  "ticket": {
    "subject": "Generated from first sentence (max 50 chars)",
    "description": "Full WhatsApp message content",
    "requester": {
      "name": "WhatsApp User (+1234567890)",
      "email": "+1234567890@whatsapp.zendesk.com"
    },
    "tags": ["whatsapp", "auto-created"],
    "priority": "urgent|high|normal",
    "type": "incident"
  }
}
```

### Priority Determination
- **Urgent**: Contains `urgent`, `emergency`, `critical`, `broken`, `down`, `outage`
- **High**: Contains `important`, `issue`, `problem`, `error`, `failed`, `not working`
- **Normal**: Default priority

### Subject Generation
- Takes first sentence of the message
- Truncates to 50 characters if needed
- Adds "..." if truncated
- Falls back to "WhatsApp Support Request" if empty

## 💬 Response System

### Success Response
```
"Ticket #12345 created: 'I can't log into my account, getting error 404'. We'll get back to you soon."
```

### Validation Failure Response
```
"Please provide more details about your issue. For example: 'I can't log in' or 'Billing question about invoice #123'"
```

### Error Response
```
"Sorry, we couldn't create your ticket right now. Please try again later or contact support directly."
```

## 🎨 Content Templates

### Template Variables
- `{{1}}`: Truncated message content (first 50 characters)
- `{{2}}`: Ticket ID (if created successfully, otherwise "N/A")

### Example Template
```
Ticket {{2}} created: "{{1}}". We'll get back to you soon.
```

### Template Setup
1. Go to Twilio Console → Messaging → Content Editor
2. Create new template for WhatsApp
3. Add variables: `{{1}}` and `{{2}}`
4. Copy Content SID and add to environment variables

## 🔧 Configuration Options

### Environment Variables
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | Yes | - |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | Yes | - |
| `TWILIO_WHATSAPP_NUMBER` | WhatsApp number | Yes | - |
| `TWILIO_WEBHOOK_SECRET` | Webhook signature secret | No | - |
| `TWILIO_CONTENT_SID` | Content template SID | No | - |
| `ZENDESK_API_KEY` | Zendesk API key | Yes | - |
| `ZENDESK_DOMAIN` | Zendesk domain | Yes | - |
| `ZENDESK_EMAIL` | Zendesk email | Yes | - |

### Validation Settings
```python
# Minimum message length
MIN_MESSAGE_LENGTH = 10

# Generic patterns to reject
GENERIC_PATTERNS = [
    r'^hi\b', r'^hello\b', r'^hey\b',
    r'^good\s*(morning|afternoon|evening)\b',
    r'^thanks?\b', r'^thank\s*you\b',
    r'^ok\b', r'^okay\b', r'^yes\b', r'^no\b',
    r'^help\b', r'^support\b'
]

# Issue-related keywords
ISSUE_KEYWORDS = [
    'problem', 'issue', 'error', 'bug', 'broken',
    'not working', 'can\'t', 'cannot', 'failed',
    'failure', 'trouble', 'difficulty', 'question',
    'inquiry', 'request', 'need', 'want',
    'looking for', 'searching for', 'trying to'
]
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Webhook Not Receiving Messages
- [ ] Check Twilio webhook URL configuration
- [ ] Verify server is accessible via HTTPS
- [ ] Check server logs for incoming requests

#### 2. Ticket Creation Fails
- [ ] Verify Zendesk credentials
- [ ] Check Zendesk API permissions
- [ ] Review error logs for specific issues

#### 3. WhatsApp Response Not Sent
- [ ] Verify Twilio credentials
- [ ] Check WhatsApp number configuration
- [ ] Review Twilio logs for message status

#### 4. Content Validation Issues
- [ ] Check validation rules in code
- [ ] Review message content requirements
- [ ] Test with different message types

### Debugging Steps
1. **Check Logs**: Review `logs/webhook_requests.log`
2. **Test Endpoint**: Use test script `test_whatsapp_integration.py`
3. **Verify Configuration**: Check environment variables
4. **Monitor Twilio**: Check Twilio console for message status
5. **Check Zendesk**: Verify tickets in Zendesk dashboard

## 📈 Monitoring

### Key Metrics
- **Message Volume**: Number of WhatsApp messages received
- **Validation Rate**: Percentage of messages that pass validation
- **Ticket Creation Rate**: Percentage of valid messages that create tickets
- **Response Time**: Time to process and respond to messages
- **Error Rate**: Percentage of failed requests

### Log Analysis
```bash
# View recent logs
tail -f logs/webhook_requests.log

# Search for specific patterns
grep "WhatsApp message" logs/webhook_requests.log
grep "ticket created" logs/webhook_requests.log
grep "validation failed" logs/webhook_requests.log
```

## 🔄 Workflow Examples

### Successful Ticket Creation
```
Customer: "I can't log into my account, getting error 404 when trying to access dashboard"
↓
System: Validates content (✓ 10+ chars, ✓ meaningful content)
↓
System: Creates ticket #12345 with subject "I can't log into my account, getting error 404"
↓
System: Sends "Ticket #12345 created: 'I can't log into my account, getting error 404'. We'll get back to you soon."
```

### Validation Failure
```
Customer: "help"
↓
System: Validates content (✗ insufficient detail)
↓
System: Sends "Please provide more details about your issue. For example: 'I can't log in' or 'Billing question about invoice #123'"
```

### Error Handling
```
Customer: "I need assistance"
↓
System: Attempts to create ticket
↓
System: Zendesk API error occurs
↓
System: Sends "Sorry, we couldn't create your ticket right now. Please try again later or contact support directly."
```

## 🚀 Future Enhancements

### Potential Improvements
1. **AI-Powered Categorization**: Auto-categorize tickets using AI
2. **Multi-language Support**: Support for multiple languages
3. **Rich Media Support**: Handle images, documents, voice messages
4. **Conversation History**: Track conversation context
5. **Automated Responses**: AI-powered initial responses
6. **Integration with CRM**: Connect with other customer systems
7. **Analytics Dashboard**: Real-time analytics and insights
8. **Custom Workflows**: Configurable business rules

### Implementation Ideas
- **Smart Routing**: Route tickets based on content analysis
- **Priority Prediction**: AI-powered priority determination
- **Customer Segmentation**: Identify VIP customers
- **Response Templates**: Dynamic response generation
- **Escalation Rules**: Automatic escalation for urgent issues

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the logs for error details
3. Test with the provided test script
4. Verify all configuration settings
5. Contact support with specific error messages

## 📚 Additional Resources

- [Twilio WhatsApp API Documentation](https://www.twilio.com/docs/whatsapp)
- [Zendesk API Documentation](https://developer.zendesk.com/api-reference)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Requests Library](https://requests.readthedocs.io/) 