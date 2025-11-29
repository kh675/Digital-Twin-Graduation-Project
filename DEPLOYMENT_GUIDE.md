# Step 9: Cloud Deployment Guide

## 🚀 Digital Twin AI Platform - Deployment Guide

Complete guide for deploying the full system (API + Dashboard + PDF Generator) to the cloud.

---

## 📋 Pre-Deployment Checklist

- [x] All 8 steps completed locally
- [x] API endpoints tested locally
- [x] Dashboard tested locally
- [x] PDF generation working
- [x] All data files present
- [ ] Requirements.txt created
- [ ] Environment variables configured
- [ ] Deployment platform selected

---

## 🎯 Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLOUD DEPLOYMENT                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │   FastAPI API    │◄────────┤  Streamlit       │     │
│  │   (Render.com)   │         │  Dashboard       │     │
│  │                  │         │  (Streamlit      │     │
│  │  Port: 8000      │         │   Cloud)         │     │
│  └──────────────────┘         └──────────────────┘     │
│         │                              │                │
│         │                              │                │
│         ▼                              ▼                │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Data Files      │         │  User Browser    │     │
│  │  (JSON/CSV)      │         │                  │     │
│  └──────────────────┘         └──────────────────┘     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Option 1: Deploy to Render.com (Recommended)

### Step 1: Prepare Repository

1. **Create GitHub Repository**
   ```bash
   cd "c:/Users/marwa/OneDrive/Desktop/digital twin ai"
   git init
   git add .
   git commit -m "Initial commit: Digital Twin AI Platform"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/digital-twin-ai.git
   git push -u origin main
   ```

2. **Verify Files**
   - ✅ `requirements.txt`
   - ✅ `start.sh`
   - ✅ `.env.example`
   - ✅ `api/main.py`
   - ✅ `dashboard/app.py`
   - ✅ All data files (JSON, CSV, PKL)

### Step 2: Deploy API to Render

1. **Create Render Account**: https://render.com

2. **New Web Service**:
   - Connect GitHub repository
   - Name: `digital-twin-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `bash start.sh`

3. **Environment Variables**:
   ```
   DATA_DIR=./
   PDF_OUTPUT_DIR=./pdf_reports
   DEBUG=False
   ```

4. **Deploy**: Click "Create Web Service"

5. **Get API URL**: `https://digital-twin-api.onrender.com`

### Step 3: Deploy Dashboard to Streamlit Cloud

1. **Create Streamlit Account**: https://streamlit.io/cloud

2. **New App**:
   - Repository: Your GitHub repo
   - Branch: `main`
   - Main file path: `dashboard/app.py`

3. **Advanced Settings** → Secrets:
   ```toml
   API_BASE_URL = "https://digital-twin-api.onrender.com"
   ```

4. **Deploy**: Click "Deploy!"

5. **Get Dashboard URL**: `https://your-app.streamlit.app`

---

## 📦 Option 2: Deploy to Railway.app

### Step 1: Deploy API

1. **Create Railway Account**: https://railway.app

2. **New Project** → Deploy from GitHub

3. **Configure**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables**:
   ```
   PORT=8000
   DATA_DIR=./
   ```

5. **Deploy** and get URL

### Step 2: Deploy Dashboard

Same as Streamlit Cloud option above.

---

## 🔧 API Configuration for Production

### Update CORS Settings

Edit `api/main.py`:

```python
# For production, specify allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.streamlit.app",  # Your dashboard URL
        "http://localhost:8501"  # For local testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Add PDF Generation Endpoint

Already included in `api/main.py`, but verify:

```python
@app.get("/generate-pdf/{student_id}")
def generate_pdf_endpoint(student_id: str):
    # Generate PDF on-demand
    pdf_path = generate_student_pdf(student_id)
    return FileResponse(pdf_path, media_type='application/pdf')
```

---

## 🎨 Dashboard Configuration for Production

### Update API URL

Edit `dashboard/app.py`:

```python
import os

# Use environment variable for API URL
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
```

### Streamlit Secrets

Create `.streamlit/secrets.toml`:

```toml
API_BASE_URL = "https://your-api.onrender.com"
```

Then in code:

```python
import streamlit as st
API_BASE = st.secrets.get("API_BASE_URL", "http://localhost:8000")
```

---

## 📊 Data Files Deployment

### Required Files

Ensure these are in your repository:

```
data/
├── digital_twin_students_1500_cleaned.csv
├── egypt_jobs_full_1500_cleaned.csv
├── digital_twin_courses_1500_cleaned.csv

skill_gap_profiles/
└── student_profiles.json

recommendations/
└── recommendations.json

roadmaps/
├── S0001_roadmap.json
├── S0002_roadmap.json
└── ... (1500 files)

models/
├── career_model_xgb.pkl
├── label_encoder.pkl
├── feature_list.pkl
└── features_all.csv

embeddings/
└── embeddings_students.pkl

clusters.json
similar_students.json
cluster_profiles.json
cluster_assignments.json
```

### File Size Considerations

If repository is too large (>500MB):

1. **Use Git LFS** for large files:
   ```bash
   git lfs install
   git lfs track "*.pkl"
   git lfs track "*.csv"
   ```

2. **Or use cloud storage**:
   - Upload to AWS S3 / Google Cloud Storage
   - Update paths in code to download on startup

---

## 🧪 Testing Deployed System

### Test API Endpoints

```bash
# Health check
curl https://your-api.onrender.com/health

# Get student cluster
curl https://your-api.onrender.com/cluster-student/S0001

# Get all clusters
curl https://your-api.onrender.com/all-clusters

# Generate PDF
curl https://your-api.onrender.com/generate-pdf/S0001 --output S0001.pdf
```

### Test Dashboard

1. Visit: `https://your-app.streamlit.app`
2. Enter student ID: `S0001`
3. Click "Load Student Data"
4. Verify all tabs load correctly
5. Test cluster insights and similar students

---

## 🔐 Security Best Practices

### 1. API Key Authentication (Optional)

Add to `api/main.py`:

```python
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.get("/protected-endpoint")
def protected_route(api_key: str = Depends(verify_api_key)):
    return {"message": "Access granted"}
```

### 2. Rate Limiting

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/cluster-student/{student_id}")
@limiter.limit("10/minute")
def get_cluster(request: Request, student_id: str):
    # Your code here
```

### 3. HTTPS Only

Both Render and Streamlit Cloud provide HTTPS automatically.

---

## 📈 Monitoring & Logging

### Render Logs

View logs in Render dashboard:
- Deployment logs
- Runtime logs
- Error tracking

### Add Logging to Code

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/endpoint")
def my_endpoint():
    logger.info("Endpoint called")
    # Your code
```

---

## 🚨 Troubleshooting

### Common Issues

**Issue**: API returns 500 error
- **Solution**: Check Render logs for Python errors
- Verify all data files are present
- Check file paths are correct

**Issue**: Dashboard can't connect to API
- **Solution**: Verify API_BASE_URL is correct
- Check CORS settings in API
- Ensure API is deployed and running

**Issue**: PDF generation fails
- **Solution**: Check writable permissions for `pdf_reports/`
- Verify matplotlib backend is set to 'Agg'
- Check memory limits on platform

**Issue**: Large files not deploying
- **Solution**: Use Git LFS
- Or exclude from repo and download on startup

---

## 💰 Cost Estimates

### Free Tier Options

**Render.com**:
- Free tier: 750 hours/month
- Spins down after 15 min inactivity
- Good for demos

**Streamlit Cloud**:
- Free tier: 1 app
- Always on
- Perfect for dashboards

**Total Cost**: $0/month for demo purposes

### Paid Options (if needed)

**Render**:
- Starter: $7/month (always on)
- Standard: $25/month (more resources)

**Railway**:
- $5/month base + usage

---

## ✅ Deployment Verification Checklist

- [ ] API deployed and accessible
- [ ] All endpoints return correct data
- [ ] Dashboard deployed and loads
- [ ] Dashboard connects to API successfully
- [ ] Student data displays correctly
- [ ] Cluster insights work
- [ ] Similar students feature works
- [ ] PDF generation works (if enabled)
- [ ] QR codes link correctly
- [ ] No console errors
- [ ] Performance acceptable
- [ ] HTTPS enabled
- [ ] Logs accessible

---

## 🎉 Post-Deployment

### Share Your Demo

**API Documentation**: `https://your-api.onrender.com/docs`

**Dashboard**: `https://your-app.streamlit.app`

**Sample API Calls**:
```bash
# Get student S0001's cluster
https://your-api.onrender.com/cluster-student/S0001

# View all clusters
https://your-api.onrender.com/all-clusters
```

### Demo Script

1. Show dashboard homepage
2. Load student S0001
3. Navigate through tabs:
   - Roadmap
   - Skills Analysis
   - Recommendations
   - Career Insights
   - Cluster Insights
   - Similar Students
4. Generate PDF report
5. Show API documentation

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Railway Docs](https://docs.railway.app/)

---

**Deployment Status**: Ready for cloud deployment! 🚀
