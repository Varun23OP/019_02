# Farmer Financial Infrastructure API

A farmer-governed financial infrastructure that democratizes agricultural credit through transparent data-driven assessment, enabling marginal farmers to escape informal lending cycles and build portable financial identities.

## Product Vision

To become India's farmer-governed financial infrastructure that democratizes agricultural credit through transparent data-driven assessment, enabling 86 million marginal farmers to escape informal lending cycles and build portable financial identities.

## Target Audience

- **Marginal Farmers**: Farmers with less than 2.5 acres lacking land titles
- **FPO Coordinators**: Managing 3-peer guarantee groups
- **Rural Banks/NBFCs**: Seeking data-driven agricultural lending with reduced risk

## Core Features

- **Farmer Management**: Complete CRUD operations for farmer profiles
- **Credit Assessment**: Data-driven credit scoring and loan eligibility calculation
- **Financial Identity**: Portable financial profiles for farmers
- **Risk Categorization**: Transparent risk assessment for lenders

## Technology Stack

- **Backend Framework**: FastAPI (Python)
- **Database**: SQLAlchemy ORM with SQLite (development) / PostgreSQL (production)
- **Data Validation**: Pydantic
- **Architecture**: Modular Monolith

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd /path/to/project
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

5. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file and update the configuration values as needed.

## Running the Application

### Development Mode

Run the application with auto-reload enabled:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### Production Mode

For production deployment:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Farmers

- `POST /api/v1/farmers` - Create a new farmer
- `GET /api/v1/farmers` - Get all farmers (with pagination)
- `GET /api/v1/farmers/{farmer_id}` - Get a specific farmer
- `PUT /api/v1/farmers/{farmer_id}` - Update a farmer
- `DELETE /api/v1/farmers/{farmer_id}` - Delete a farmer

### Credit Assessments

- `POST /api/v1/farmers/{farmer_id}/assessments` - Create credit assessment for a farmer
- `GET /api/v1/farmers/{farmer_id}/assessments` - Get all assessments for a farmer

### Health Check

- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with API information

## Database Schema

### Farmer Model
- `id`: Primary key
- `name`: Farmer's full name
- `phone`: Unique phone number
- `village`: Village name
- `district`: District name
- `state`: State name
- `land_size_acres`: Land size (max 2.5 acres for marginal farmers)
- `status`: Account status (active/inactive/pending)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Credit Assessment Model
- `id`: Primary key
- `farmer_id`: Foreign key to Farmer
- `assessment_date`: Assessment date
- `credit_score`: Credit score (0-1000)
- `loan_eligibility_amount`: Eligible loan amount
- `risk_category`: Risk classification
- `notes`: Additional notes
- `created_at`: Creation timestamp

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for security operations
- `ALLOWED_ORIGINS`: CORS allowed origins
- `DEBUG`: Debug mode flag

## Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   └── routers/
│       ├── __init__.py
│       └── farmers.py       # Farmer endpoints
├── .env.example             # Environment variables template
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

## Development Guidelines

1. **Code Quality**: Follow PEP 8 style guidelines
2. **Error Handling**: All endpoints include proper error handling and logging
3. **Validation**: Input validation using Pydantic schemas
4. **Security**: Never commit `.env` file with real credentials
5. **Database**: Use migrations for schema changes in production

## Security Considerations

- Change `SECRET_KEY` in production to a strong random string
- Use PostgreSQL instead of SQLite for production
- Enable HTTPS in production
- Implement rate limiting for API endpoints
- Add authentication/authorization as needed
- Regularly update dependencies for security patches

## Future Enhancements

- Authentication and authorization (JWT)
- Role-based access control (RBAC)
- FPO coordinator management
- Peer guarantee group management
- Integration with banking systems
- Mobile application support
- Advanced analytics and reporting
- Document upload and verification

## Support

For issues, questions, or contributions, please contact the development team.

## License

[Specify your license here]
