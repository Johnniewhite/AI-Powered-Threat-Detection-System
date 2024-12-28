# AI-Powered Threat Detection System

An advanced threat detection platform that uses AI to analyze and identify potential security threats in both images and text content. The system provides real-time analysis with detailed threat assessments.

## 🌟 Key Features

### Image Analysis
- Real-time threat detection in images
- File signature and content analysis
- Size and extension-based risk assessment
- Detailed threat scoring and reporting

### Text Analysis
- Advanced phishing detection
- Malware and spam identification
- Context-aware threat assessment
- Pattern-based analysis

### Smart Dashboard
- Real-time threat monitoring
- Interactive threat visualizations
- Historical analysis
- Comprehensive threat statistics

## 🔍 How It Works

### Image Analysis Process
1. When an image is uploaded, the system:
   - Calculates file hash for unique identification
   - Analyzes file size and extension
   - Checks for malicious patterns
   - Generates a threat score based on multiple factors
   - Provides detailed recommendations

### Text Analysis Process
1. For text input, the system:
   - Scans for known phishing patterns
   - Identifies potential malware indicators
   - Detects spam patterns
   - Uses contextual analysis for threat assessment
   - Provides categorized results with confidence scores

### Threat Scoring System
- Scores range from 0.0 to 1.0
- Critical threats: >= 0.8
- High risk: >= 0.6
- Moderate: >= 0.4
- Low risk: < 0.4

## 📁 Project Structure

### Backend Structure
```
backend/
├── app/
│   ├── api/                    # API endpoints
│   │   └── api_v1/
│   │       ├── endpoints/      # Route handlers
│   │       │   ├── detection.py    # Threat detection logic
│   │       │   ├── dashboard.py    # Dashboard statistics
│   │       │   └── history.py      # Historical data
│   ├── core/                   # Core functionality
│   │   ├── auth.py            # Authentication
│   │   ├── config.py          # Configuration
│   │   └── database.py        # Database setup
│   ├── models/                # Database models
│   │   ├── detection.py       # Detection records
│   │   └── user.py           # User management
│   └── services/              # Business logic
│       ├── image_analysis.py  # Image processing
│       └── text_analysis.py   # Text processing
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/            # Reusable components
│   │   ├── Layout.tsx        # Main layout
│   │   └── common/           # Shared components
│   ├── pages/                # Main pages
│   │   ├── Dashboard.tsx     # Statistics dashboard
│   │   ├── ImageAnalysis.tsx # Image upload & analysis
│   │   ├── TextAnalysis.tsx  # Text input & analysis
│   │   └── History.tsx       # Detection history
│   ├── services/             # API services
│   │   └── api.ts           # API client
│   └── contexts/             # React contexts
│       └── AuthContext.tsx   # Authentication state
```

## 🧮 Core Components

### Detection Engine
- `detection.py`: Handles both image and text analysis
  - Uses pattern matching for text analysis
  - Implements file analysis for images
  - Calculates threat scores
  - Generates detailed reports

### Dashboard Analytics
- `dashboard.py`: Manages statistics and visualization data
  - Tracks detection patterns
  - Generates threat distributions
  - Calculates risk metrics
  - Provides historical analysis

### Frontend Components
- `ImageAnalysis.tsx`: Handles image uploads and displays results
- `TextAnalysis.tsx`: Manages text input and analysis display
- `Dashboard.tsx`: Shows interactive charts and statistics
- `History.tsx`: Displays past detection records

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 13+

### Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd threat-detection-system

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

## 🎯 How to Use

### 1. Dashboard
- View real-time threat statistics
- Monitor detection patterns
- Access historical data
- Track security metrics

### 2. Image Analysis
- Upload any image file
- Get instant threat assessment
- View detailed analysis results
- Receive security recommendations

### 3. Text Analysis
- Input any text content
- Get real-time threat detection
- View threat categories and scores
- Access detailed analysis report

### 4. History
- Browse past detections
- Filter by date and type
- Export detection reports
- Track threat patterns

## 🔒 Security Features
- Advanced threat detection algorithms
- Real-time analysis
- Multi-factor threat assessment
- Comprehensive reporting

## 🛠 Technology Stack

### Backend
- FastAPI for high-performance API
- SQLAlchemy for database operations
- Advanced AI models for threat detection
- PostgreSQL for data storage

### Frontend
- React with TypeScript
- Material-UI components
- Interactive charts and visualizations
- Responsive design

## 📊 API Access

Access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

---

Built with ❤️ for a more secure digital world