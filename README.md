# Outreach Agent System

An automated outreach agent that orchestrates multi-platform lead generation and follow-up processes using AI, error handling, and best practices. This agent automatically generates personalized outreach messages, manages lead data, sends emails, and creates follow-up tasks across multiple project management platforms.

## Features

- **AI-Powered Message Generation**: Claude AI integration with prompt engineering and temperature control
- **Lead Management**: Airtable integration with data validation and error handling
- **Email Automation**: Secure SMTP handling with TLS encryption, bulk email capabilities, and reporting
- **Task Management**: ClickUp integration with priority management and due date handling
- **Logging & Monitoring**: Detailed logging with file and console output for debugging
- **Type Safety & Validation**: Type hints, input validation, and error handling throughout the codebase
- **Configuration Management**: Environment-based configuration with validation and secure credential handling
- **Multi-Service Integration**: Orchestrated workflow across multiple platforms with fault tolerance
- **Performance Monitoring**: Real-time performance metrics and analytics tracking
- **Retry Mechanisms**: Retry logic with exponential backoff for API rate limits

## Architecture

```
outreach-agent/
├── main.py                 # Orchestration agent with error handling
├── anthropic_client.py     # AI client with prompt engineering
├── airtable_client.py      # Lead management with CRUD operations
├── email_sender.py         # Email automation with bulk capabilities
├── clickup_client.py       # Task management with API coverage
├── requirements.txt        # Version-pinned dependencies
└── README.md              # Documentation
```

## Core Components

### Outreach Agent (`main.py`)
- **Orchestration**: Workflow management with error handling
- **Configuration Management**: Environment-based configuration with validation
- **Campaign Analytics**: Reporting and statistics for campaign performance
- **Fault Tolerance**: Error handling and recovery mechanisms
- **Type Safety**: Type hints and validation throughout
- **Performance Monitoring**: Real-time metrics tracking and optimization

### AI Message Generator (`anthropic_client.py`)
- **Prompt Engineering**: Prompt construction with context awareness
- **Temperature Control**: Configurable creativity levels for message generation
- **Error Handling**: API error handling with specific exception types
- **Connection Testing**: Built-in API connectivity validation
- **Rate Limit Management**: Retry logic with exponential backoff
- **Retry Mechanisms**: Automatic retry with exponential backoff for rate limit errors

### Lead Management System (`airtable_client.py`)
- **CRUD Operations**: Create, Read, Update, Delete functionality
- **Data Validation**: Input validation and error checking
- **Connection Pooling**: API connection management
- **Error Recovery**: Error handling with specific HTTP status code handling
- **Bulk Operations**: Support for batch processing of lead data

### Email Automation Engine (`email_sender.py`)
- **Secure SMTP**: TLS encryption and authentication
- **Bulk Email Support**: High-volume email sending with reporting
- **Input Validation**: Email address and content validation
- **Connection Testing**: Built-in SMTP connectivity validation
- **Formatting**: Proper email headers and formatting

### Task Management Agent (`clickup_client.py`)
- **API Coverage**: ClickUp API integration
- **Priority Management**: Task prioritization and due date handling
- **List Management**: List and space management capabilities
- **Error Recovery**: Error handling with specific API error types
- **Connection Validation**: Built-in API connectivity testing

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Set the following environment variables with proper values:

```bash
# Anthropic AI Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key

# Airtable Lead Management
AIRTABLE_API_KEY=your-airtable-api-key
AIRTABLE_BASE_ID=your-base-id
AIRTABLE_TABLE_NAME=Leads

# ClickUp Task Management
CLICKUP_API_KEY=your-clickup-api-key
CLICKUP_LIST_ID=your-list-id

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@example.com
```

### 3. Lead Data Structure
Ensure your Airtable base contains a table with the following fields:
- `Name`: Lead's full name
- `Company`: Company name
- `Email`: Contact email address

## Usage

### Running the Outreach Campaign
```bash
python main.py
```

The agent will:
1. **Validate Configuration**: Check all environment variables and API connections
2. **Retrieve Leads**: Fetch lead data from Airtable with error handling
3. **Generate Messages**: Create personalized messages using Claude AI
4. **Send Emails**: Deliver outreach emails with logging
5. **Create Tasks**: Generate follow-up tasks in ClickUp
6. **Report Results**: Provide campaign statistics
7. **Performance Metrics**: Display performance analytics

### Campaign Output Example
```
2024-01-15 10:30:15 - __main__ - INFO - Initializing outreach agent system
2024-01-15 10:30:16 - __main__ - INFO - All clients initialized successfully
2024-01-15 10:30:17 - __main__ - INFO - Starting outreach campaign
2024-01-15 10:30:18 - airtable_client - INFO - Successfully retrieved 25 leads from Airtable
2024-01-15 10:30:20 - anthropic_client - INFO - Generated personalized message for John Doe at TechCorp in 2.34s
2024-01-15 10:30:21 - email_sender - INFO - Successfully sent email to john@techcorp.com in 1.12s
2024-01-15 10:30:22 - clickup_client - INFO - Created ClickUp task for John Doe at TechCorp in 0.89s

Campaign Summary:
Total Leads: 25
Validated: 23
Messages Generated: 23
Emails Sent: 23
Tasks Created: 23
Failed: 2

Performance Metrics:
Total Processing Time: 45.67s
Average Message Generation: 2.34s
Average Email Sending: 1.12s
Average Task Creation: 0.89s
```

## Customization

### Modifying the AI Agent Behavior
Edit the prompt engineering in `anthropic_client.py`:
```python
def _build_prompt(self, lead, client_info, offer):
    # Customize prompt engineering for your specific use case
    return f"Your custom prompt template..."
```

### Extending the Outreach Agent
Add new functionality to the `OutreachAgent` class in `main.py`:
```python
def custom_lead_processing(self, lead):
    # Add custom lead processing logic
    pass
```

### Configuration Management
Modify the `OutreachConfig` dataclass in `main.py`:
```python
@dataclass
class OutreachConfig:
    # Add new configuration parameters
    custom_setting: str = "default_value"
```

## Security & Best Practices

### API Key Management
- Store all API keys as environment variables
- Use app passwords for email accounts with 2FA
- Regularly rotate API keys and monitor usage
- Implement proper error handling for authentication failures

### Error Handling
- Exception handling throughout the codebase
- Specific error types for different failure scenarios
- Degradation and recovery mechanisms
- Logging for debugging and monitoring

### Performance Optimization
- Connection pooling for API clients
- Timeout management for all external calls
- Data processing and validation
- Memory-conscious operations for large datasets
- Real-time performance monitoring and optimization

## Monitoring & Analytics

### Logging
- Logging with multiple handlers
- File-based logging for production environments
- Console output for debugging
- Structured log messages with context

### Campaign Analytics
- Success/failure tracking
- Performance metrics and reporting
- Error categorization and analysis
- Real-time campaign monitoring
- Processing time analytics for each operation

### Performance Monitoring
- Real-time performance metrics tracking
- Average processing times for each operation
- Bottleneck identification and optimization
- Performance reporting

## Testing & Validation

### Connection Testing
Each client includes built-in connection testing:
```python
# Test API connections
anthropic_client.test_connection()
airtable_client.test_connection()
email_sender.test_connection()
clickup_client.test_connection()
```

### Data Validation
Input validation throughout:
- Email address format validation
- Lead data completeness checking
- API response validation
- Configuration parameter validation

## Dependencies

- `anthropic>=0.18.0`: AI API client with rate limiting
- `requests>=2.31.0`: HTTP library with connection pooling
- `python-docx>=1.2.0`: Document generation capabilities

## Features

- **Scalability**: Designed for high-volume outreach campaigns
- **Reliability**: Error handling and recovery
- **Security**: Secure credential management and data handling
- **Monitoring**: Logging and analytics
- **Maintainability**: Clean, documented code following best practices
- **Performance**: Real-time monitoring and optimization capabilities

## License

This project is designed for use with proper compliance to all integrated platform terms of service. Ensure adherence to email marketing regulations and API usage policies.
