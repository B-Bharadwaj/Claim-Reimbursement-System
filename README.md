# Claim Reimbursement System

## Project Summary

The **Claim Reimbursement System** is a full-stack web application designed to automate and streamline the employee expense reimbursement process within an organization. It implements a complete, real-world approval workflow with clearly defined roles, secure authentication, and audit-friendly state transitions.

The system enables **Employees** to submit expense claims, **Managers** to review and approve or reject them, and **Finance** users to perform final approval and mark claims as paid. Built with a clean separation of concerns across frontend, backend, and a dedicated OCR microservice, this project demonstrates production-grade architecture, role-based access control, and scalable backend design suitable for enterprise environments.

---

## System Architecture Overview

The application follows a **clean, service-oriented architecture** composed of four primary components, each with a clearly defined responsibility.

### Frontend (React)
- Provides role-based dashboards for Employees, Managers, and Finance users
- Handles authentication, protected routing, and secure API communication
- Integrates OCR results into claim forms with editable auto-fill
- Automatically refreshes expired access tokens for a seamless user experience

### Backend (Django + Django REST Framework)
- Exposes RESTful APIs for authentication, claims, approvals, and payments
- Enforces claim lifecycle transitions and role-based permissions
- Manages receipt uploads and associates OCR results with claims
- Acts as the orchestration layer between the frontend, database, and OCR service

### Database (PostgreSQL)
- Serves as the primary persistent data store
- Stores users, roles, claims, receipts, OCR metadata, and workflow states
- Ensures data integrity through relational modeling and constraints
- Supports transactional operations required for financial approval workflows

### OCR Microservice (FastAPI)
- Dedicated microservice for receipt text extraction
- Processes receipt images and PDFs using Tesseract OCR
- Extracts structured data including vendor, date, amount, confidence score, and raw text
- Designed to be independently deployable and replaceable

Each component runs independently and communicates over HTTP, enabling scalability, maintainability, and a clear separation of concerns.


---

## High-Level Workflow

1. **Employee**
   - Creates a claim in `DRAFT` state
   - Uploads receipt documents
   - Submits the claim for review

2. **Manager**
   - Views submitted claims
   - Approves or rejects claims
   - Approved claims move to finance review

3. **Finance**
   - Reviews manager-approved claims
   - Performs final approval
   - Marks claims as `PAID`

4. **Employee**
   - Can track claim status end-to-end
   - Sees final payment confirmation

**Claim Lifecycle States:**
- DRAFT → SUBMITTED → MANAGER_APPROVED / REJECTED → FINANCE_APPROVED → PAID


---

## Role-Based Feature Breakdown

### Employee
- Create and edit claims (draft mode)
- Upload receipts and supporting documents
- Submit claims for approval
- View claim status and history
- See payment confirmation once processed

### Manager
- View submitted claims from reporting employees
- Review claim details and receipts
- Approve or reject claims with comments

### Finance
- View manager-approved claims
- Perform final validation
- Mark claims as paid
- Ensure financial audit readiness

---
## 5. OCR Workflow

1. Employee uploads a receipt while creating a claim
2. Django backend forwards the receipt to the OCR microservice
3. OCR service extracts:
   - Vendor name
   - Receipt date
   - Total amount
   - Confidence score
   - Raw extracted text
4. OCR response is stored against the receipt
5. Frontend auto-fills claim fields using OCR results
6. Employee reviews and edits extracted values if needed
7. Final submitted values are always user-authoritative

OCR acts as an assistive feature, not a mandatory or blocking dependency.

---
## Folder Structure

```bash
claim-reimbursement-system/
│
├── backend/
│ ├── accounts/ # Authentication & user roles
│ ├── claims/ # Claim models, workflow logic
│ ├── receipts/ # Document uploads & OCR metadata
│ ├── config/ # Django settings & URLs
│ └── manage.py
│
├── frontend/
│ ├── src/
│ │ ├── auth/ # Login & JWT handling
│ │ ├── layouts/ # Role-based layouts
│ │ ├── pages/ # Dashboards per role
│ │ └── services/ # API layer
│ └── package.json
│
├── ocr-service/
│ ├── app/
│ │ ├── main.py # FastAPI entry point
│ │ └── ocr.py # OCR extraction logic
│ └── requirements.txt
│
└── README.md
```
---
## Tech Stack

### Backend
- Django
- Django REST Framework
- JWT Authentication
- PostgreSQL
- Role-based permissions

### Frontend
- React
- Role-based routing
- Secure JWT handling
- Modular dashboard layouts

### OCR Service
- FastAPI
- Receipt text extraction
- Vendor, date, and amount parsing (MVP)

---
## Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL
- Git

---
### Backend Setup (Django)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
---
### Frontend Setup (React)
```bash
cd frontend
npm install
npm start
```
---
### OCR Service Setup (FastAPI)
```bash
cd ocr-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```
---
## Environment Variables & Configuration

### Backend (.env)
```bash
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/claims_db
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=1
OCR_SERVICE_URL=http://localhost:8001/ocr
```
---
### Frontend (.env)
```bash
REACT_APP_API_BASE_URL=http://localhost:8000/api
```
---
## 7. API Overview (High-Level)

### Authentication
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`

### Claims
- `POST /api/claims/`
- `GET /api/claims/my/`
- `PUT /api/claims/{id}/submit/`

### Manager Actions
- `PUT /api/claims/{id}/manager-approve/`
- `PUT /api/claims/{id}/manager-reject/`

### Finance Actions
- `PUT /api/claims/{id}/finance-approve/`
- `PUT /api/claims/{id}/mark-paid/`

### OCR Service
- `POST /ocr`

---