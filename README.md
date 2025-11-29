# Digital Twin AI Platform 🎓

AI-powered student success platform providing personalized learning roadmaps, career predictions, and skill gap analysis for 1500 students.

## 🌟 Features

- **Career Prediction**: ML-powered career path recommendations
- **Personalized Roadmaps**: 3-stage learning paths (Beginner → Intermediate → Advanced)
- **Skill Gap Analysis**: Identify missing skills with visual charts
- **Student Clustering**: Group students by skills and career goals
- **Peer Discovery**: Find similar students for collaboration
- **PDF Reports**: Professional reports with charts and QR codes
- **Interactive Dashboard**: 6-tab Streamlit interface

## 🚀 Live Demo

- **Dashboard**: [https://your-app.streamlit.app](https://your-app.streamlit.app)
- **API Docs**: [https://your-api.onrender.com/docs](https://your-api.onrender.com/docs)

## 📊 Tech Stack

- **Backend**: FastAPI, Python 3.10+
- **Frontend**: Streamlit
- **ML**: XGBoost, Scikit-learn, Sentence Transformers
- **Visualization**: Plotly, Matplotlib, Seaborn
- **PDF Generation**: ReportLab
- **Deployment**: Render.com, Streamlit Cloud

## 🏗️ Project Structure

```
digital-twin-ai/
├── api/                    # FastAPI backend
│   └── main.py
├── dashboard/              # Streamlit frontend
│   ├── app.py
│   └── utils.py
├── models/                 # ML models
├── roadmaps/              # Generated roadmaps (1500 files)
├── pdf_reports/           # Generated PDFs
├── embeddings/            # Skill embeddings
├── skill_gap_profiles/    # Student profiles
├── recommendations/       # Course/job recommendations
├── clustering_engine.py   # Student clustering
├── generate_pdf_report.py # PDF generation
├── requirements.txt       # Dependencies
└── DEPLOYMENT_GUIDE.md    # Deployment instructions
```

## 🛠️ Local Setup

### Prerequisites
- Python 3.10+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/digital-twin-ai-platform.git
cd digital-twin-ai-platform
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API:
```bash
uvicorn api.main:app --reload --port 8000
```

4. Run the Dashboard (in another terminal):
```bash
streamlit run dashboard/app.py
```

5. Access:
- API: http://localhost:8000
- Dashboard: http://localhost:8501
- API Docs: http://localhost:8000/docs

## 📡 API Endpoints

### Student Data
- `GET /predict-career/{student_id}` - Career prediction
- `GET /get-roadmap/{student_id}` - Personalized roadmap
- `GET /get-recommendations/{student_id}` - Course/job recommendations
- `GET /get-profile/{student_id}` - Skill gap profile

### Clustering
- `GET /cluster-student/{student_id}` - Student's cluster info
- `GET /cluster-profile/{cluster_label}` - Cluster analytics
- `GET /similar-students/{student_id}` - Find similar students
- `GET /all-clusters` - All clusters overview

### Utilities
- `GET /health` - Health check
- `GET /list-students` - List all students

## 🎨 Dashboard Features

### 6 Interactive Tabs:
1. **📋 Roadmap** - 3-stage learning path with courses and projects
2. **📊 Skills Analysis** - Bar charts and radar charts
3. **🎯 Recommendations** - Personalized course and job matches
4. **📈 Career Insights** - Prediction confidence and timeline
5. **🔮 Cluster Insights** - Cluster membership and analytics
6. **👥 Similar Students** - Peer discovery and networking

## 🚀 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) and [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for detailed instructions.

### Quick Deploy

**API (Render.com)**:
```bash
# Build: pip install -r requirements.txt
# Start: bash start.sh
```

**Dashboard (Streamlit Cloud)**:
- Main file: `dashboard/app.py`
- Secrets: `API_BASE_URL = "https://your-api.onrender.com"`

## 📊 Data Pipeline

```
Step 1: Skill Embeddings → Step 2: Skill Gap Analysis
         ↓                            ↓
Step 3: Recommendations ← Step 4: Career Prediction
         ↓                            ↓
Step 5: Roadmap Generation → Step 6: Dashboard
         ↓                            ↓
Step 7: Clustering → Step 8: PDF Reports → Step 9: Deployment
```

## 🧪 Testing

```bash
# Test API
pytest test_api.py

# Test specific student
curl http://localhost:8000/cluster-student/S0001
```

## 📄 Documentation

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Complete deployment guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Quick deployment steps
- [DASHBOARD_README.md](DASHBOARD_README.md) - Dashboard documentation
- [STEP1_SUCCESS.txt](STEP1_SUCCESS.txt) through [STEP9_SUCCESS.txt](STEP9_SUCCESS.txt) - Implementation summaries

## 🤝 Contributing

This is a graduation project. For questions or suggestions, please open an issue.

## 📝 License

This project is created for educational purposes.

## 👥 Authors

- **Marwa** - Digital Twin AI Platform

## 🙏 Acknowledgments

- Sentence Transformers for embeddings
- FastAPI for the amazing framework
- Streamlit for the beautiful dashboard
- Render and Streamlit Cloud for free hosting

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-11-30
