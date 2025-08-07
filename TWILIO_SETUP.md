# Twilio SMS Integration Setup Guide

This guide will help you set up the Twilio SMS integration for creating Zendesk tickets via text messages.

## Prerequisites

1. **Twilio Account**: Sign up at [Twilio Console](https://console.twilio.com/)
2. **Twilio Phone Number**: Purchase a phone number for SMS
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

### 1.2 Phone Number
1. Go to **Phone Numbers** → **Manage** → **Active numbers**
2. Click **Buy a number** or use an existing number
3. Make sure the number supports **SMS** capabilities
4. Copy the phone number and add it to your `.env` file:
   ```env
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### 1.3 Webhook Secret (Optional but Recommended)
1. Go to **Settings** → **API Keys & Tokens**
2. Create a new API key or use your existing one
3. Add the secret to your `.env` file:
   ```env
   TWILIO_WEBHOOK_SECRET=your_webhook_secret_here
   ```

## Step 2: Configure Twilio Webhooks

### 2.1 SMS Webhook
1. Go to **Phone Numbers** → **Manage** → **Active numbers**
2. Click on your phone number
3. Under **Messaging**, set the webhook URL:
   ```
   https://your-domain.com/twilio/sms
   ```
4. Set the HTTP method to **POST**

### 2.2 Status Webhook (Optional)
1. In the same phone number configuration
2. Under **Messaging**, set the status callback URL:
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

### 4.2 Test SMS
1. Send an SMS to your Twilio phone number
2. Use a meaningful message like: "I can't log into my account, getting error 404"
3. You should receive a confirmation SMS with the ticket number

### 4.2 Test Validation
1. Send a generic message like: "help"
2. You should receive a message asking for more details

## Step 5: Monitor Logs

Check the logs for SMS processing:
```bash
tail -f logs/webhook_requests.log
```

Look for entries like:
```
Request abc123: Received SMS from +1234567890 to +0987654321
Request abc123: Message SID: SM1234567890abcdef
Request abc123: Message body: I can't log into my account
Request abc123: Successfully created ticket 12345 from SMS
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'twilio'**
   - Solution: Run `pip install -r requirements.txt`

2. **Invalid Twilio signature**
   - Solution: Check your `TWILIO_WEBHOOK_SECRET` in `.env`
   - For development, this warning can be ignored

3. **SMS not being received**
   - Check if your phone number supports SMS
   - Verify webhook URLs are correct and accessible
   - Check application logs for errors

4. **Tickets not being created**
   - Verify Zendesk credentials in `.env`
   - Check Zendesk API permissions
   - Review application logs for Zendesk errors

### Debug Mode

To enable debug logging, add this to your `.env`:
```env
DEBUG=true
```

## Security Considerations

1. **Webhook Validation**: Always validate Twilio webhook signatures in production
2. **HTTPS**: Use HTTPS for all webhook URLs
3. **Rate Limiting**: Consider implementing rate limiting for SMS endpoints
4. **Logging**: All SMS interactions are logged for audit purposes

## API Endpoints

### SMS Webhook
- **URL**: `POST /twilio/sms`
- **Purpose**: Receives SMS messages from Twilio
- **Parameters**:
  - `From`: Sender's phone number
  - `Body`: SMS message content
  - `MessageSid`: Twilio message SID
  - `To`: Recipient phone number

### Status Webhook
- **URL**: `POST /twilio/status`
- **Purpose**: Receives message delivery status updates
- **Parameters**:
  - `MessageSid`: Twilio message SID
  - `MessageStatus`: Status of the message

## Example SMS Workflows

### Successful Ticket Creation
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

## Support

If you encounter issues:
1. Check the application logs
2. Verify all environment variables are set correctly
3. Test with a simple SMS message first
4. Ensure your Twilio account has sufficient credits 