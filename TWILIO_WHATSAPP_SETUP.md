# Twilio WhatsApp Integration Setup Guide

This guide will help you set up the Twilio WhatsApp integration for creating Zendesk tickets via WhatsApp messages using content templates.

## Prerequisites

1. **Twilio Account**: Sign up at [Twilio Console](https://console.twilio.com/)
2. **WhatsApp Business API Access**: Requires approval from Twilio (not available for trial accounts)
3. **Public URL**: Your application needs to be accessible via HTTPS (for webhooks)

## Step 1: Get Twilio Credentials

### 1.1 Account SID and Auth Token
1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Dashboard** → **Account Info**
3. Copy your **Account SID** and **Auth Token**
4. Add them to your `.env` file:
   ```env
   TWILIO_ACCOUNT_SID=your_account_sid_here
   TWILIO_AUTH_TOKEN=your_auth_token_here
   ```

### 1.2 WhatsApp Business API Setup
**Important**: WhatsApp Business API requires approval from Twilio and is not available for trial accounts.

1. Go to **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Follow the setup process to get WhatsApp Business API access
3. Once approved, you'll get a WhatsApp number (format: `+1234567890`)
4. Add the WhatsApp number to your `.env` file:
   ```env
   TWILIO_WHATSAPP_NUMBER=+1234567890
   ```

### 1.3 Content Template Setup (Optional but Recommended)
1. Go to **Messaging** → **Content Editor**
2. Click **Create new template**
3. Choose **WhatsApp** as the channel
4. Create a template with variables, for example:
   ```
   Ticket {{2}} created: "{{1}}". We'll get back to you soon.
   ```
5. Add variables:
   - `{{1}}`: Message content (truncated to 50 characters)
   - `{{2}}`: Ticket ID
6. Save the template and copy the **Content SID**
7. Add it to your `.env` file:
   ```env
   TWILIO_CONTENT_SID=HXb5b62575e6e4ff6129ad7c8efe1f983e
   ```

### 1.4 Webhook Secret (Optional)
1. Go to **Settings** → **API Keys & Tokens**
2. Create a new API key or use your existing one
3. Add the secret to your `.env` file (optional - for enhanced security):
   ```env
   TWILIO_WEBHOOK_SECRET=your_webhook_secret_here
   ```
   
   **Note**: The webhook secret is optional. If not provided, webhook signature validation will be skipped, but the integration will still work.

## Step 2: Configure Twilio Webhooks

### 2.1 WhatsApp Webhook
1. Go to **Messaging** → **Settings** → **WhatsApp Sandbox** (for testing)
2. Or **Messaging** → **Settings** → **WhatsApp Senders** (for production)
3. Set the webhook URL:
   ```
   https://your-domain.com/twilio/whatsapp
   ```
4. Set the HTTP method to **POST**

### 2.2 Status Webhook (Optional)
1. In the same WhatsApp configuration
2. Set the status callback URL:
   ```
   https://your-domain.com/twilio/status
   ```
3. Set the HTTP method to **POST**

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install the Twilio Python SDK along with other dependencies.

## Step 4: Test the Integration

### 4.1 Start the Application
```bash
python main.py
```

### 4.2 Test WhatsApp (Sandbox Mode)
1. **For Sandbox Testing**:
   - Go to **Messaging** → **Settings** → **WhatsApp Sandbox**
   - Follow the instructions to join your sandbox
   - Send a WhatsApp message to the sandbox number
   - Use a meaningful message like: "I can't log into my account, getting error 404"

2. **For Production**:
   - Send a WhatsApp message to your Twilio WhatsApp number
   - Use a meaningful message like: "I can't log into my account, getting error 404"
   - You should receive a confirmation WhatsApp message with the ticket number

### 4.3 Test Validation
1. Send a generic message like: "help"
2. You should receive a message asking for more details

## Step 5: Monitor Logs

Check the logs for WhatsApp processing:
```bash
tail -f logs/webhook_requests.log
```

Look for entries like:
```
Request abc123: Received WhatsApp message from +1234567890 to +0987654321
Request abc123: Message SID: SM1234567890abcdef
Request abc123: Message body: I can't log into my account
Request abc123: Successfully created ticket 12345 from WhatsApp
Request abc123: WhatsApp response sent successfully - Used template: True
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'twilio'**
   - Solution: Run `pip install -r requirements.txt`

2. **Invalid Twilio signature**
   - Solution: Check your `TWILIO_WEBHOOK_SECRET` in `.env` if you want to enable signature validation
   - For development, this warning can be ignored
   - **Note**: Webhook secret is optional - if not provided, signature validation will be skipped

3. **WhatsApp messages not being received**
   - Check if you have WhatsApp Business API access
   - Verify webhook URLs are correct and accessible
   - Check application logs for errors
   - Ensure you're using the correct WhatsApp number format

4. **Tickets not being created**
   - Verify Zendesk credentials in `.env`
   - Check Zendesk API permissions
   - Review application logs for Zendesk errors

5. **WhatsApp Business API not available**
   - WhatsApp Business API requires approval from Twilio
   - Not available for trial accounts
   - Contact Twilio support for approval

6. **Content template not working**
   - Verify `TWILIO_CONTENT_SID` is set correctly
   - Check template variables match the expected format
   - Ensure template is approved and active

### Debug Mode

To enable debug logging, add this to your `.env`:
```env
DEBUG=true
```

## Security Considerations

1. **Webhook Validation**: Always validate Twilio webhook signatures in production
2. **HTTPS**: Use HTTPS for all webhook URLs
3. **Rate Limiting**: Consider implementing rate limiting for WhatsApp endpoints
4. **Logging**: All WhatsApp interactions are logged for audit purposes

## API Endpoints

### WhatsApp Webhook
- **URL**: `POST /twilio/whatsapp`
- **Purpose**: Receives WhatsApp messages from Twilio
- **Parameters**:
  - `From`: Sender's phone number (with whatsapp: prefix)
  - `Body`: WhatsApp message content
  - `MessageSid`: Twilio message SID
  - `To`: Recipient phone number (your Twilio WhatsApp number)

### Status Webhook
- **URL**: `POST /twilio/status`
- **Purpose**: Receives message delivery status updates
- **Parameters**:
  - `MessageSid`: Twilio message SID
  - `MessageStatus`: Status of the message

## Example WhatsApp Workflows

### Successful Ticket Creation (with Content Template)
```
Customer: "I can't log into my account, getting error 404 when trying to access dashboard"
↓
System: Creates ticket #12345 with subject "I can't log into my account, getting error 404"
↓
System: Sends template message: "Ticket 12345 created: 'I can't log into my account, getting error 404...'. We'll get back to you soon."
```

### Successful Ticket Creation (without Content Template)
```
Customer: "I can't log into my account, getting error 404 when trying to access dashboard"
↓
System: Creates ticket #12345 with subject "I can't log into my account, getting error 404"
↓
System: "Ticket #12345 created: 'I can't log into my account, getting error 404'. We'll get back to you soon."
```

### Insufficient Content
```
Customer: "help"
↓
System: "Please provide more details about your issue. For example: 'I can't log in' or 'Billing question about invoice #123'"
```

### Error Handling
```
Customer: "I need assistance"
↓
System: "Sorry, we couldn't create your ticket right now. Please try again later or contact support directly."
```

## Content Templates

### Template Variables
The system supports the following template variables:
- `{{1}}`: Truncated message content (first 50 characters)
- `{{2}}`: Ticket ID (if created successfully, otherwise "N/A")

### Example Template
```
Ticket {{2}} created: "{{1}}". We'll get back to you soon.
```

### Template Setup Steps
1. Go to **Messaging** → **Content Editor**
2. Click **Create new template**
3. Select **WhatsApp** as the channel
4. Choose **Text** as the content type
5. Enter your template with variables
6. Add variables in the format `{{1}}`, `{{2}}`, etc.
7. Save and copy the Content SID

## WhatsApp Business API vs SMS

### Key Differences:
1. **Approval Required**: WhatsApp Business API requires approval from Twilio
2. **Number Format**: Uses `whatsapp:` prefix for phone numbers
3. **Message Format**: Supports rich media (images, documents, etc.)
4. **Delivery**: More reliable delivery than SMS
5. **Cost**: Generally more expensive than SMS
6. **User Experience**: Better user experience with read receipts, typing indicators
7. **Content Templates**: Support for structured message templates

### Advantages of WhatsApp:
- **Higher Engagement**: Users are more likely to respond
- **Rich Media**: Support for images, documents, and other media
- **Better UX**: Read receipts, typing indicators, and better formatting
- **Global Reach**: Popular worldwide, especially in emerging markets
- **Business Friendly**: Professional appearance and features
- **Content Templates**: Structured, consistent messaging

## Support

If you encounter issues:
1. Check the application logs
2. Verify all environment variables are set correctly
3. Test with a simple WhatsApp message first
4. Ensure your Twilio account has sufficient credits
5. Contact Twilio support for WhatsApp Business API issues
6. Verify content template is properly configured and approved 