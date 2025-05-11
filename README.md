# Online Survey System

A comprehensive web application for creating and managing online surveys. This system allows administrators to create surveys, and users to participate in them.

## Features

- **User Authentication**: Register, login, and manage user accounts
- **Admin Panel**: Admin users can create and manage surveys
- **Survey Creation**: Create surveys with multiple question types
  - Multiple Choice (single selection)
  - Checkbox (multiple selections)
  - Text Input
- **Survey Management**: Edit, activate/deactivate, and delete surveys
- **Survey Taking**: Users can participate in active surveys
- **Results Visualization**: View and analyze survey responses with charts and statistics

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript
  - Bootstrap 5 for responsive design
  - Chart.js for data visualization
  - Flatpickr for date selection
- **Backend**: Python with Flask framework
- **Database**: MongoDB for data storage
- **Authentication**: Flask-Login for user session management

## Installation and Setup

### Prerequisites

- Python 3.7 or higher
- MongoDB installed and running
- Git (optional, for cloning the repository)

### Setup Instructions

1. Clone or download the repository

2. Set up a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - **Windows**:
     ```
     venv\Scripts\activate
     ```
   - **Unix/MacOS**:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the root directory with the following variables:
   ```
   SECRET_KEY=your_secret_key
   MONGO_URI=mongodb://localhost:27017/survey_app
   FLASK_ENV=development
   ```

6. Run the application:
   ```
   python app.py
   ```

7. Access the application at `http://localhost:5000`

## Usage

### Admin User

1. The first user who registers will automatically become an admin
2. Log in with your admin credentials
3. Create surveys by navigating to the "Create Survey" page
4. Add various types of questions to your survey
5. Manage your surveys from the dashboard
6. View survey results and analytics

### Regular User

1. Register a new account
2. Browse available surveys from your dashboard
3. Take surveys by selecting a survey and submitting your responses
4. View your survey participation history

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Bootstrap](https://getbootstrap.com/)
- [Chart.js](https://www.chartjs.org/)
- [Flatpickr](https://flatpickr.js.org/)
- [Font Awesome](https://fontawesome.com/)
- [Flask](https://flask.palletsprojects.com/)
- [PyMongo](https://pymongo.readthedocs.io/)
