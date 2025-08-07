# Zendesk CX Bot - Application Write-up

## Overview

The **Zendesk CX Bot** is an intelligent FastAPI application that automates ticket categorization and analysis for Zendesk customer support systems. It leverages Azure OpenAI's advanced language models to provide real-time ticket processing, automatic categorization, and quality analysis, significantly improving customer support efficiency and decision-making. **Additionally, the application includes a comprehensive Twilio WhatsApp integration that allows customers to create support tickets directly through WhatsApp messages.**

## Problem Statement

Customer support teams face several critical challenges:

1. **Manual Ticket Categorization**: Support agents spend significant time manually categorizing tickets, leading to delays and inconsistencies
2. **Quality Assessment**: Lack of systematic analysis of support interactions to identify areas for improvement
3. **Scalability Issues**: As ticket volume grows, manual processes become unsustainable
4. **Inconsistent Responses**: Human categorization can be subjective and inconsistent across different agents
5. **Missing Insights**: Valuable data from support interactions often goes unanalyzed

## Solution Approach

### Architecture Overview

The application follows a **microservices architecture** with clear separation of concerns:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Zendesk       │    │   FastAPI App    │◄───│   Azure OpenAI  │
│   Webhooks      │───▶│   (Main Logic)   │───▶│   (AI Engine)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Zendesk API    │
                       │   (Updates)      │
                       └──────────────────┘
```

### Key Components

1. **FastAPI Application** (`main.py`)
   - RESTful API server with webhook endpoints
   - CORS middleware for cross-origin requests
   - Comprehensive logging and error handling

2. **Webhook Router** (`app/routers/webhook.py`)
   - Handles ticket creation events (`/ticketCreatedWebhook`)
   - Processes status change events (`/ticketStatusChangedWebhook`)
   - Extracts and validates ticket data

3. **Twilio Router** (`app/routers/twilio.py`)
   - Handles WhatsApp webhooks (`/twilio/whatsapp`)
   - Processes message status callbacks (`/twilio/status`)
   - Validates Twilio webhook signatures for security
   - Manages WhatsApp message processing and ticket creation

4. **Azure OpenAI Service** (`services/azure_openai.py`)
   - Intelligent ticket categorization using GPT models
   - Support quality analysis and insights generation
   - Structured JSON responses for easy integration

5. **Zendesk Service** (`services/zendesk.py`)
   - API integration for ticket updates
   - Comment extraction and analysis
   - Automated tagging and categorization

6. **Twilio Service** (`services/twilio.py`)
   - WhatsApp message processing and validation
   - Automatic ticket creation from WhatsApp messages
   - Phone number formatting and validation
   - Webhook signature validation for security

7. **Utility Functions** (`app/utils.py`)
   - Request ID generation for tracking
   - Data parsing and validation
   - Standardized response formatting

### Core Functionality

#### 1. Automatic Ticket Categorization

When a new ticket is created, the system:

1. **Receives webhook** from Zendesk with ticket details
2. **Extracts data** (subject, description, ticket ID)
3. **Analyzes content** using Azure OpenAI's GPT model
4. **Categorizes ticket** into predefined categories:
   - `human_resources`, `engineering`, `it_support`, `product`, `design`
   - `sales`, `marketing`, `finance`, `legal`, `customer_support`
   - `operations`, `executive`
5. **Updates ticket** with automatic tags and categorization comments
6. **Logs results** for audit and monitoring

#### 2. Support Quality Analysis

When a ticket is marked as "SOLVED", the system:

1. **Triggers analysis** based on status change
2. **Extracts comments** from the entire conversation (public comments only)
3. **Analyzes interaction** using AI for:
   - Sentiment analysis (Positive, Neutral, Negative)
   - Satisfaction likelihood (High, Medium, Low)
   - Agent empathy score (1-5 scale)
   - Clarity score (1-5 scale)
   - Pain points identification
   - Frustration signals detection
   - Action recommendations
4. **Updates ticket** with comprehensive analysis report (as private comment for internal use only)
5. **Provides insights** for continuous improvement

#### 3. WhatsApp Integration

The application includes a comprehensive WhatsApp integration that allows customers to create support tickets directly through WhatsApp messages:

**WhatsApp Ticket Creation Workflow:**
1. **Customer sends WhatsApp message** to the configured Twilio WhatsApp number
2. **Twilio webhook** sends message to `/twilio/whatsapp` endpoint
3. **System validates content** (minimum 10 characters, meaningful content)
4. **If valid** → Creates Zendesk ticket automatically with:
   - Subject generated from first sentence (max 50 characters)
   - Full message as description
   - Requester info (WhatsApp User + phone number)
   - Priority determined by content analysis
5. **If insufficient** → Sends WhatsApp message asking for more details
6. **Customer receives confirmation** WhatsApp message with ticket number

**WhatsApp Validation Rules:**
- **Minimum length**: 10 characters
- **Must contain actionable content**: Not just "hi", "help", "hello"
- **Should describe an issue or request**: Contains problem-related keywords

**Security Features:**
- **Webhook signature validation** for enhanced security
- **Phone number formatting** and validation
- **Error handling** with graceful fallbacks
- **Comprehensive logging** for audit and debugging

## Technical Implementation

### Technology Stack

- **Backend Framework**: FastAPI (Python)
- **AI Engine**: Azure OpenAI GPT models
- **API Integration**: Zendesk REST API
- **Messaging Platform**: Twilio WhatsApp Business API
- **Configuration**: Pydantic Settings
- **Logging**: Python logging with file and console output
- **Deployment**: Uvicorn server

### Key Features

1. **Asynchronous Processing**: All operations are async for better performance
2. **Error Handling**: Comprehensive error handling with detailed logging
3. **Request Tracking**: Unique request IDs for all operations
4. **Data Validation**: Robust data parsing and validation
5. **Scalable Architecture**: Modular design for easy extension
6. **Multi-Channel Support**: Webhooks and WhatsApp integration
7. **Security**: Webhook signature validation and secure API key management

### Configuration Management

The application uses environment variables for configuration:

```env
# Azure OpenAI Configuration
azure_openai_api_key=your_azure_openai_api_key_here
azure_openai_endpoint=https://your-resource.cognitiveservices.azure.com/
azure_openai_deployment=your-deployment-name
azure_openai_model=your-model-name
azure_openai_api_version=2024-12-01-preview

# Zendesk Configuration
zendesk_domain=your-zendesk-domain
zendesk_email=your-zendesk-email
zendesk_api_key=your-zendesk-api-key

# Twilio Configuration
twilio_account_sid=your_twilio_account_sid
twilio_auth_token=your_twilio_auth_token
twilio_whatsapp_number=+1234567890
twilio_content_sid=your_content_sid
```

## How to Run the Code

### Prerequisites

1. **Python 3.8+** installed
2. **Azure OpenAI** account and API key
3. **Zendesk** account with API access
4. **Twilio** account with WhatsApp Business API access
5. **Git** for cloning the repository

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd zendesk-cx-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env_example.txt .env
   # Edit .env with your actual credentials
   ```

4. **Configure Twilio WhatsApp** (NEW):
   - Set up WhatsApp Business API in Twilio Console
   - Configure webhook endpoints:
     - WhatsApp webhook: `https://your-domain.com/twilio/whatsapp`
   - Add all Twilio credentials to `.env` file

5. **Run the application**:
   ```bash
   python main.py
   ```

6. **Verify the application**:
   - Health check: `http://localhost:8080/health`
   - Root endpoint: `http://localhost:8080/`

### Development Mode

For development with auto-reload:
```bash
python main.py
```

The application will automatically reload when code changes are detected.

## Why This Solution Works

### 1. **Intelligent Automation**

The application replaces manual categorization with AI-powered analysis, ensuring:
- **Consistency**: AI provides uniform categorization across all tickets
- **Accuracy**: Advanced language models understand context and nuances
- **Speed**: Real-time processing eliminates manual delays
- **Scalability**: Handles any volume of tickets without additional resources

### 2. **Comprehensive Analysis**

The support quality analysis provides:
- **Actionable Insights**: Identifies specific areas for improvement
- **Customer Experience**: Tracks sentiment and satisfaction metrics
- **Agent Performance**: Evaluates empathy and clarity scores
- **Process Optimization**: Recommends actions for better support

### 3. **Seamless Integration**

The solution integrates seamlessly with existing Zendesk workflows:
- **Non-disruptive**: Works alongside existing processes
- **Automatic Updates**: Updates tickets with AI insights automatically
- **Audit Trail**: Comprehensive logging for compliance and debugging
- **Backward Compatible**: Doesn't require changes to existing Zendesk setup

### 4. **Business Value**

The application delivers significant business value:

- **Reduced Response Times**: Automatic categorization speeds up ticket routing
- **Improved Customer Satisfaction**: Better categorization leads to faster resolution
- **Operational Efficiency**: Reduces manual workload for support teams
- **Data-Driven Insights**: Provides analytics for continuous improvement
- **Cost Savings**: Reduces manual processing costs and improves resource allocation

### 5. **Technical Value**

The solution demonstrates technical best practices:

- **Modular Design**: Easy to maintain and extend
- **Error Handling**: Robust error handling and logging
- **Performance**: Asynchronous processing for optimal performance
- **Security**: Secure API key management and validation
- **Monitoring**: Comprehensive logging and request tracking

## Conclusion

The Zendesk CX Bot represents a modern, intelligent solution to customer support automation challenges. By leveraging Azure OpenAI's advanced language models, it provides accurate, consistent, and scalable ticket processing that significantly improves support team efficiency and customer experience.

The application's modular architecture, comprehensive error handling, and seamless integration make it a robust solution for organizations looking to modernize their customer support operations. The combination of automatic categorization and quality analysis provides both immediate operational benefits and long-term strategic insights for continuous improvement. 