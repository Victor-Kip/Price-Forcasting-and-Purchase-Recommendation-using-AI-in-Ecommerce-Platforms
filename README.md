# GenEcomm – AI-Powered Price Forecasting and Purchase Recommendation

GenEcomm is a web application that helps users make smarter shopping decisions by providing **future price forecasts** and **personalized product recommendations** for e-commerce platforms.

## Features

- 🔐 **User Authentication**

  - Register, log in, and log out with secure password hashing
  - Google OAuth login option
  - Email verification and password reset (in progress)

- 🛍️ **Core Functionality**

  - Search for products
  - View price forecasts using AI models
  - Receive personalized recommendations

- 📊 **Dashboard**
  - Displays last viewed product and predictions
  - Search bar for quick access
  - Recent activity section

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Jinja2 Templates
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login, OAuth (Google)
- **Email Service**: Flask-Mail (Gmail SMTP)
