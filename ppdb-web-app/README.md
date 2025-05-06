# PPDB Web Application

## Overview
This project is a simple web application for Penerimaan Peserta Didik Baru (PPDB), which includes functionalities for user registration, login, and a dashboard to display submitted form information.

## Project Structure
```
ppdb-web-app
├── src
│   ├── static
│   │   ├── css
│   │   │   └── styles.css
│   │   └── js
│   │       └── main.js
│   └── templates
│       ├── auth
│       │   ├── login.html
│       │   └── register.html
│       ├── dashboard
│       │   └── index.html
│       ├── layout
│       │   └── base.html
│       └── index.html
├── app.py
├── config.py
├── requirements.txt
└── README.md
```

## Features
- User registration and login forms
- Homepage with registration instructions
- User dashboard displaying submitted form information

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd ppdb-web-app
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python app.py
   ```

## Usage
- Access the homepage to view registration instructions.
- Register a new account or log in with existing credentials.
- After logging in, users can view their dashboard with submitted information.

## License
This project is licensed under the MIT License.