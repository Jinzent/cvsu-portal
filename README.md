# CVSU Bacoor Online Academic Services & Transaction System

A web-based system developed using Django that streamlines academic transactions for students and staff of CVSU Bacoor Campus.  
The system reduces manual processing by allowing students to request documents, schedule appointments, submit fee payments, and send inquiries online, while staff can manage and process these transactions.

---

## Features

### Authentication
- Student registration and login
- Staff login with role-based access
- Secure logout (POST-based)

### CRUD Modules (6 Tables)
1. Student Profile  
2. Document Types (Staff-managed)  
3. Document Requests  
4. Appointments  
5. Fee Payments  
6. Inquiries  

Each module supports Create, Read, Update, and Delete operations with proper permission checks.

### Staff Functions
- Approve or reject document requests
- Confirm or cancel appointments
- Verify fee payments
- Respond to student inquiries
- View dashboard summaries

### Querying
- Search by keyword
- Filter by status (Pending, Approved, Verified, etc.)
- Dynamic result updates using Django ORM

### Front-end
- Responsive UI using Bootstrap
- Separate dashboards for students and staff
- User-friendly forms and navigation

---

## Technologies Used
- Python 3
- Django
- SQLite (development database)
- HTML, CSS, Bootstrap
