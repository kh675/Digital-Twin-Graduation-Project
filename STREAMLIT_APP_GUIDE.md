# Streamlit App Testing Guide

## 🚀 Quick Start

Once Streamlit installation completes, run:

```powershell
streamlit run dashboard/app.py
```

The app will open at: `http://localhost:8501`

## 📱 App Structure

### **Navigation Flow:**
```
Home → Student Input Form → Results → Dashboard
```

### **Pages:**

1. **Home** (`dashboard/app.py`)
   - Welcome page
   - Feature overview
   - Getting started guide
   - Platform statistics

2. **Student Input Form** (`dashboard/pages/1_Student_Input_Form.py`)
   - 7-step wizard
   - Collects 45+ student fields
   - Validates input (e.g., grades must match courses)
   - **Redirects to Results page** after submission

3. **Results** (`dashboard/pages/2_Results.py`)
   - **Your old dashboard content** (preserved)
   - Shows immediately after form submission
   - 4 tabs:
     - 📋 Roadmap - Learning path
     - 📊 Skills Analysis - Current vs missing skills
     - 🎯 Recommendations - Courses, roles, companies
     - 📈 Career Insights - Career probabilities
   - PDF download button
   - Personalized with ML data from API

4. **Dashboard** (`dashboard/pages/3_Dashboard.py`)
   - Analytics view
   - Skill Radar Chart
   - Career Probability Bar Chart
   - Query parameter support: `?student=S1503`

## 🧪 Testing Checklist

### Test 1: Home Page
- [ ] App opens successfully
- [ ] Welcome message displays
- [ ] Sidebar shows all pages
- [ ] Statistics show correctly

### Test 2: Student Input Form
- [ ] All 7 steps load
- [ ] Navigation works (Next/Back buttons)
- [ ] Form validation works (try mismatched grades)
- [ ] Submit button works
- [ ] Redirects to Results page after submission

### Test 3: Results Page
- [ ] Loads with query parameter `?student=S1503`
- [ ] Shows student name and ID
- [ ] All 4 tabs display correctly
- [ ] Skills analysis shows current vs missing
- [ ] Recommendations appear
- [ ] Career insights chart displays
- [ ] PDF download button works

### Test 4: Dashboard Page
- [ ] Loads with query parameter `?student=S1503`
- [ ] Skill Radar Chart displays
- [ ] Career Probability Bar Chart displays
- [ ] Data loads from API correctly

## 🔧 Troubleshooting

### API Not Running
If you see "Could not load Digital Twin":
```powershell
# Terminal 1: Start API
uvicorn api.main:app --reload --port 8000
```

### Port Already in Use
```powershell
streamlit run dashboard/app.py --server.port 8502
```

### Clear Cache
If data doesn't update:
- Press `C` in the terminal running Streamlit
- Or add `?nocache=1` to the URL

## 📊 Expected User Flow

**New Student:**
1. Opens app → sees Home
2. Clicks "Student Input Form" in sidebar
3. Fills 7 steps → submits
4. **Auto-redirected to Results page**
5. Views personalized recommendations
6. Can click Dashboard in sidebar for analytics

**Returning Student:**
1. Goes to Results or Dashboard page
2. Enters Student ID (e.g., S1503)
3. Views saved digital twin

## ✅ Success Criteria

- ✅ All pages load without errors
- ✅ Form submission creates new student
- ✅ Results page shows ML-generated recommendations
- ✅ Dashboard charts display correctly
- ✅ PDF download works
- ✅ Navigation flow is intuitive

## 🎯 Next Steps

After verifying the app works:
1. Test with real student data
2. Verify ML recommendations are accurate
3. Check PDF generation
4. Test on different browsers
5. Deploy to production (if ready)
