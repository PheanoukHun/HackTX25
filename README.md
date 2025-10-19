# OptiLife - Personalized Financial Planning

OptiLife is a full-stack web application designed to help users with personalized financial planning. It provides a secure platform for users to manage their financial information, set goals, and receive tailored insights. The application features a modern React frontend, a robust Flask backend, and an encrypted SQLite database for secure data storage.

## Features

*   **User Authentication**: Secure registration, login, and logout functionalities.
*   **Personalized Financial Profiles**: Users can input and manage various financial details, including income, expenses, debts, and financial goals.
*   **Encrypted Data Storage**: All sensitive user data is stored securely in an encrypted SQLite database using AES-GCM encryption.
*   **Intuitive User Interface**: A responsive and user-friendly frontend built with React and TypeScript.
*   **API-driven Backend**: A RESTful API developed with Flask handles all data interactions and business logic.

## Technologies Used

### Frontend
*   **React**: A JavaScript library for building user interfaces.
*   **TypeScript**: A typed superset of JavaScript that compiles to plain JavaScript.
*   **Vite**: A fast build tool that provides a quicker development experience for web projects.
*   **React Router DOM**: For declarative routing in React applications.
*   **@google/genai**: Potentially for AI-driven financial insights or conversational features.
*   **Marked**: A markdown parser and compiler.

### Backend
*   **Flask**: A lightweight Python web framework.
*   **Python**: The programming language for the backend logic.
*   **Flask-CORS**: A Flask extension for handling Cross-Origin Resource Sharing (CORS).

### Database
*   **SQLite**: A C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.
*   **PyCryptodome**: A comprehensive collection of cryptographic primitives for Python, used here for AES-GCM encryption of user data.

## Project Structure

The repository is organized into the following main directories:

*   `frontend/`: Contains the React.js application, including components, pages, and styling.
*   `flask-backend/`: Houses the Flask API, responsible for handling requests, business logic, and interacting with the database.
*   `db/`: Contains the database management logic and schema definition.
    *   `dbManager.py`: Python script for managing the encrypted SQLite database.
    *   `schema.json`: Defines the structure of the user data.

## Setup and Installation

To get OptiLife up and running on your local machine, follow these steps:

### Prerequisites

*   **Python 3.x**: Make sure Python is installed and added to your PATH.
*   **Node.js & npm (or yarn)**: Required for the frontend development.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/HackTX25.git
cd HackTX25
```

### 2. Backend Setup

Navigate to the `flask-backend` directory and set up the Python environment:

```bash
cd flask-backend
python -m venv venv
.\venv\Scripts\activate   # On Windows
source venv/bin/activate # On macOS/Linux
pip install Flask Flask-Cors pycryptodome
```

**Environment Variables**:
Before running the backend, you need to set the following environment variables:

*   `FLASK_SECRET_KEY`: A strong, random key for Flask session management.
*   `DB_PASSWORD`: A strong password for encrypting and decrypting the SQLite database.

Example (for Windows Command Prompt):
```bash
set FLASK_SECRET_KEY=your_flask_secret_key_here
set DB_PASSWORD=your_database_encryption_password_here
```
Example (for macOS/Linux Bash):
```bash
export FLASK_SECRET_KEY=your_flask_secret_key_here
export DB_PASSWORD=your_database_encryption_password_here
```

**Run the Backend**:
```bash
python app.py
```
The Flask backend will typically run on `http://127.0.0.1:5000`.

### 3. Frontend Setup

Open a new terminal, navigate to the `frontend` directory, and install dependencies:

```bash
cd ../frontend
npm install
```

**Run the Frontend**:
```bash
npm run dev
```
The React development server will usually start on `http://localhost:5173`.

## Usage

1.  **Register**: Access the application through your browser (e.g., `http://localhost:5173`), navigate to the registration page, and create a new user account.
2.  **Login**: Use your registered credentials to log in.
3.  **Financial Planning**: Once logged in, you can fill out forms with your financial details, set goals, and explore personalized planning options.
4.  **Profile Management**: Update your user information and financial data as needed.

## Database Management (CLI)

The `db/dbManager.py` script can be used for command-line database operations (for development/debugging purposes).

**Usage**:
```bash
python db/dbManager.py <json_file> <action_number>
```

**Actions**:
*   `1`: Add new user (JSON file should contain user data including `name` and `password`).
*   `2`: Pull user data (JSON file should contain `{"name": "username"}`).
*   `3`: Update user (JSON file should contain `{"name": "username", ...updated_fields}`).
*   `4`: Get specific field(s) (JSON file should contain `{"name": "username", "fields": ["income", "city"]}`).

**Example**:
```bash
# To add a new user (assuming user_data.json exists with user details)
python db/dbManager.py user_data.json 1

# To pull user data for 'JohnDoe'
echo '{"name": "JohnDoe"}' > temp_user.json
python db/dbManager.py temp_user.json 2
