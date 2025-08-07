# Local Development Setup with ngrok

This guide will help you set up local development for the Twilio WhatsApp integration using ngrok.

## Prerequisites

1. **ngrok account**: Sign up at [ngrok.com](https://ngrok.com/)
2. **ngrok installed**: Download and install ngrok
3. **Local application running**: Your FastAPI app should be running on localhost

## Step 1: Install ngrok

### Option 1: Using Homebrew (macOS)
```bash
brew install ngrok
```

### Option 2: Manual Installation
1. Go to [ngrok.com](https://ngrok.com/download)
2. Download for your platform
3. Extract and add to your PATH

## Step 2: Authenticate ngrok

1. Get your authtoken from [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
2. Run:
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

## Step 3: Start Your Application

1. Start your FastAPI application:
```bash
python main.py
```

2. Your app should be running on `http://localhost:8080`

## Step 4: Expose Your Local Server

1. Open a new terminal window
2. Run ngrok to expose your local server:
```bash
ngrok http 8080
```

3. You'll see output like:
```
Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       51ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:8080
```

4. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

## Step 5: Configure Twilio Webhooks

1. **Go to Twilio Console** → **Messaging** → **Settings** → **WhatsApp Sandbox**
2. **Set the webhook URL** to your ngrok URL:
   ```
   https://abc123.ngrok.io/twilio/whatsapp
   ```
3. **Set HTTP method** to **POST**
4. **Save the configuration**

## Step 6: Test the Integration

1. **Join your WhatsApp sandbox** (follow Twilio instructions)
2. **Send a WhatsApp message** to the sandbox number
3. **Check your application logs** for incoming webhooks
4. **Verify ticket creation** in your Zendesk account

## Step 7: Monitor Webhooks

1. **ngrok web interface**: Visit `http://127.0.0.1:4040` to see all incoming requests
2. **Application logs**: Check your application logs for webhook processing
3. **Twilio logs**: Check Twilio console for webhook delivery status

## Troubleshooting

### Common Issues

1. **ngrok URL changes on restart**
   - Solution: Update your Twilio webhook URL each time you restart ngrok
   - Alternative: Use ngrok with custom domains (requires paid plan)

2. **Webhook not reaching your app**
   - Check if your app is running on port 8080
   - Verify ngrok is forwarding to the correct port
   - Check ngrok web interface for errors

3. **HTTPS certificate issues**
   - ngrok provides HTTPS automatically
   - Make sure you're using the HTTPS URL from ngrok

4. **Twilio webhook validation fails**
   - This is expected in development
   - Check logs for "Skipping webhook signature validation" messages

## Production Deployment

When you're ready for production:

1. **Deploy your application** to a cloud service (AWS, Google Cloud, etc.)
2. **Get a public HTTPS URL** for your application
3. **Update Twilio webhooks** to use your production URL
4. **Remove ngrok** - it's only for local development

## Example ngrok Configuration

### Start ngrok with custom subdomain (paid plan):
```bash
ngrok http 8080 --subdomain=myapp
```

### Start ngrok with custom region:
```bash
ngrok http 8080 --region=us
```

### View ngrok logs:
```bash
ngrok http 8080 --log=stdout
```

## Security Considerations

1. **ngrok exposes your local server** - only use for development
2. **Anyone with the ngrok URL** can access your app
3. **Don't use ngrok in production**
4. **Keep ngrok sessions private** - don't share URLs publicly 