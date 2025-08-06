# Zendesk CX Bot - Mermaid Charts

## 1. System Architecture Overview

```mermaid
graph TB
    subgraph "External Systems"
        ZD[Zendesk Platform]
        AO[Azure OpenAI]
    end
    
    subgraph "Zendesk CX Bot"
        subgraph "API Layer"
            API[FastAPI Application]
            WH[Webhook Router]
        end
        
        subgraph "Services Layer"
            ZS[Zendesk Service]
            AOS[Azure OpenAI Service]
        end
        
        subgraph "Utils Layer"
            UT[Utility Functions]
            CFG[Configuration]
        end
        
        subgraph "Data Layer"
            LOG[Logging System]
        end
    end
    
    ZD -->|Webhook Events| WH
    WH -->|Ticket Data| ZS
    WH -->|Analysis Requests| AOS
    AOS -->|AI Responses| WH
    ZS -->|Ticket Updates| ZD
    AOS -->|API Calls| AO
    
    WH --> UT
    WH --> LOG
    ZS --> UT
    AOS --> UT
    UT --> CFG
```

## 2. Ticket Creation Flow

```mermaid
sequenceDiagram
    participant Z as Zendesk
    participant W as Webhook Router
    participant U as Utils
    participant AO as Azure OpenAI
    participant ZS as Zendesk Service
    participant L as Logger
    
    Z->>W: POST /ticketCreatedWebhook
    W->>U: generate_request_id()
    W->>L: log_request_start()
    W->>U: parse_request_body()
    W->>U: extract_ticket_data()
    
    alt JSON Data
        W->>AO: process_ticket_categorization()
        AO->>AO: categorize_ticket()
        AO-->>W: categorization_response
        
        W->>ZS: update_ticket_tags()
        ZS->>Z: PUT /api/v2/tickets/{id}
        Z-->>ZS: success_response
        ZS-->>W: update_result
    else Text Data
        W->>L: log_warning()
    end
    
    W->>L: log_success()
    W-->>Z: success_response
```

## 3. Ticket Status Change Flow

```mermaid
sequenceDiagram
    participant Z as Zendesk
    participant W as Webhook Router
    participant U as Utils
    participant ZS as Zendesk Service
    participant AO as Azure OpenAI
    participant L as Logger
    
    Z->>W: POST /ticketStatusChangedWebhook
    W->>U: generate_request_id()
    W->>L: log_request_start()
    W->>U: parse_request_body()
    
    alt Status is SOLVED
        W->>ZS: extract_ticket_comments()
        ZS->>Z: GET /api/v2/tickets/{id}/comments
        Z-->>ZS: comments_data
        ZS-->>W: public_comments
        
        W->>AO: process_ticket_analysis()
        AO->>AO: analyze_ticket_comments()
        AO-->>W: llm_response
        
        W->>ZS: update_ticket_with_analysis()
        ZS->>Z: PUT /api/v2/tickets/{id}
        Z-->>ZS: success_response
        ZS-->>W: analysis_update_result
    else Status not SOLVED
        W->>L: log_info()
    end
    
    W->>L: log_success()
    W-->>Z: success_response
```

## 4. Data Flow Diagram

```mermaid
flowchart TD
    A[Zendesk Webhook] --> B{Data Type?}
    B -->|JSON| C[Extract Ticket Data]
    B -->|Text| D[Log Warning]
    
    C --> E{Event Type?}
    E -->|Ticket Created| F[Process Categorization]
    E -->|Status Changed| G{Status = SOLVED?}
    
    F --> H[Azure OpenAI Categorization]
    H --> I[Update Ticket Tags]
    I --> J[Log Results]
    
    G -->|Yes| K[Extract Comments]
    G -->|No| L[Log Status Change]
    
    K --> M[Azure OpenAI Analysis]
    M --> N[Update Ticket Analysis]
    N --> O[Log Results]
    
    J --> P[Return Success Response]
    L --> P
    O --> P
    D --> P
```

## 5. Component Relationships

```mermaid
graph LR
    subgraph "Core Application"
        MAIN[main.py]
        CONFIG[config.py]
    end
    
    subgraph "Routers"
        WEBHOOK[webhook.py]
    end
    
    subgraph "Services"
        ZENDESK[zendesk.py]
        AZURE[azure_openai.py]
    end
    
    subgraph "Utils"
        UTILS[utils.py]
    end
    
    MAIN --> CONFIG
    MAIN --> WEBHOOK
    WEBHOOK --> ZENDESK
    WEBHOOK --> AZURE
    WEBHOOK --> UTILS
    ZENDESK --> CONFIG
    AZURE --> CONFIG
```

## 6. Error Handling Flow

```mermaid
flowchart TD
    A[Request Received] --> B{Valid Request?}
    B -->|No| C[Log Error]
    B -->|Yes| D[Process Request]
    
    D --> E{Processing Success?}
    E -->|No| F[Exception Handler]
    E -->|Yes| G[Log Success]
    
    F --> H[Create Error Response]
    G --> I[Create Success Response]
    
    H --> J[Return Error Response]
    I --> K[Return Success Response]
    
    C --> L[Return Error Response]
```

## 7. Configuration Management

```mermaid
graph TD
    A[Environment Variables] --> B[Pydantic Settings]
    B --> C[Application Config]
    
    C --> D[Azure OpenAI Config]
    C --> E[Zendesk Config]
    C --> F[Server Config]
    C --> G[CORS Config]
    
    D --> H[API Key]
    D --> I[Endpoint]
    D --> J[Deployment]
    D --> K[Model]
    
    E --> L[Domain]
    E --> M[Email]
    E --> N[API Key]
    
    F --> O[Host]
    F --> P[Port]
    
    G --> Q[Origins]
    G --> R[Methods]
    G --> S[Headers]
```

## 8. Logging Architecture

```mermaid
graph TB
    A[Application Events] --> B[Logging System]
    B --> C[Console Output]
    B --> D[File Handler]
    
    D --> E[logs/webhook_requests.log]
    
    subgraph "Log Types"
        F[Request Start]
        G[Request Body]
        H[Processing Steps]
        I[API Responses]
        J[Error Messages]
        K[Success Messages]
    end
    
    F --> B
    G --> B
    H --> B
    I --> B
    J --> B
    K --> B
```

## 9. API Endpoints Structure

```mermaid
graph LR
    A[FastAPI App] --> B[Root Endpoint /]
    A --> C[Health Check /health]
    A --> D[Webhook Router]
    
    D --> E[POST /ticketCreatedWebhook]
    D --> F[POST /ticketStatusChangedWebhook]
    
    E --> G[Process Ticket Creation]
    F --> H[Process Status Change]
    
    G --> I[Azure OpenAI Categorization]
    H --> J[Azure OpenAI Analysis]
    
    I --> K[Update Zendesk Tags]
    J --> L[Update Zendesk Analysis]
```

## 10. Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        LB[Load Balancer]
        subgraph "Application Servers"
            APP1[App Instance 1]
            APP2[App Instance 2]
            APP3[App Instance N]
        end
        DB[Database/Logs]
        MON[Monitoring]
    end
    
    subgraph "External Services"
        ZD[Zendesk]
        AO[Azure OpenAI]
    end
    
    ZD --> LB
    LB --> APP1
    LB --> APP2
    LB --> APP3
    
    APP1 --> AO
    APP2 --> AO
    APP3 --> AO
    
    APP1 --> DB
    APP2 --> DB
    APP3 --> DB
    
    APP1 --> MON
    APP2 --> MON
    APP3 --> MON
``` 