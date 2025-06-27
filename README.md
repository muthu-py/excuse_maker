# 🤖 ExcuseGenie - Intelligent Excuse Generator

A comprehensive web application that generates believable excuses with AI-powered proof documents and SMS/call integration.

## ✨ Features

### 🎯 Core Functionality
- **Smart Excuse Generation**: AI-powered excuse creation for various scenarios
- **User Authentication**: Secure login/registration system
- **Excuse History**: Save and manage your generated excuses
- **Multiple Categories**: Work, school, family, health, social, transportation

### 📄 Proof Generation System
The app can generate multiple types of supporting documents for your excuses:

1. **📄 Official Documents**: Professional PDF documents (medical certificates, work notes, etc.)
2. **💬 Chat Screenshots**: WhatsApp-style conversation screenshots
3. **🎵 Audio Recordings**: Voice recordings of your excuse
4. **📍 Location Data**: GPS location history for the excuse period

### 📱 Communication Features
- **SMS Integration**: Send excuses via SMS using Twilio
- **Call Integration**: Make automated calls with excuse messages
- **Communication Logs**: Track all SMS and call activities

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd excuse_generator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file with:
   ```
   db_pass=your_mysql_password
   SECRET_KEY=your_secret_key
   TWILIO_SID=your_twilio_sid
   TWILIO_TOKEN=your_twilio_token
   TWILIO_FROM_NUMBER=your_twilio_number
   GOOGLE_API_KEY=your_google_api_key
   ```

4. **Initialize the database**:
   ```bash
   python init_db.py
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

## 🎮 Usage

### Generating Excuses with Proof
1. **Login** to your account
2. **Select a category** (work, school, family, etc.)
3. **Enter context** describing your situation
4. **Choose tone** (professional, casual, formal, etc.)
5. **Select proof types** you want generated:
   - 📄 Official Document
   - 💬 Chat Screenshot
   - 🎵 Audio Recording
   - 📍 Location Data
6. **Generate** your excuse
7. **Download** the generated proof documents

### Managing Excuses
- **Save** excuses to your history
- **Copy** excuses to clipboard
- **Generate proof** for saved excuses
- **Delete** excuses from history
- **Search and filter** through your excuse history

### Communication Features
- **Send SMS** with your excuse
- **Make calls** with automated excuse messages
- **View logs** of all communications

## 🛠️ Technical Details

### Backend Modules
- `user_auth.py`: User authentication and management
- `generate_exucuse.py`: AI-powered excuse generation
- `generate_proof.py`: Proof document generation
- `excuse_history.py`: Excuse storage and retrieval
- `call_sms.py`: SMS and call integration
- `db.py`: Database connection management

### Frontend
- **Responsive Design**: Works on desktop and mobile
- **Modern UI**: Clean, intuitive interface
- **Real-time Updates**: Dynamic content loading
- **File Downloads**: Direct download of generated documents

### API Endpoints
- `POST /api/generate_excuse`: Generate new excuses
- `POST /api/save_excuse`: Save excuses to history
- `GET /api/get_excuses`: Retrieve user's excuse history
- `POST /api/generate_proof`: Generate proof documents
- `POST /api/send_sms`: Send SMS messages
- `POST /api/make_call`: Make automated calls
- `GET /api/get_sms_logs`: Get communication logs

## 📁 File Structure
```
excuse_generator/
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization
├── requirements.txt      # Python dependencies
├── modules/              # Backend modules
│   ├── user_auth.py
│   ├── generate_exucuse.py
│   ├── generate_proof.py
│   ├── excuse_history.py
│   ├── call_sms.py
│   └── db.py
├── templates/            # HTML templates
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
├── static/              # Static files
│   ├── dashboard.css
│   ├── dashboard.js
│   └── proofs/          # Generated proof files
└── README.md
```

## 🔧 Configuration

### Database Setup
The application uses MySQL. Create a database named `excusegen` and run `init_db.py` to create the necessary tables.

### Twilio Setup (Optional)
For SMS/call features, you'll need a Twilio account:
1. Sign up at [twilio.com](https://twilio.com)
2. Get your Account SID and Auth Token
3. Get a phone number for sending SMS/calls
4. Add credentials to your `.env` file

### Google API Setup
For AI-powered excuse generation:
1. Get a Google API key from [Google Cloud Console](https://console.cloud.google.com)
2. Enable the Generative AI API
3. Add the API key to your `.env` file

## 🎨 Customization

### Adding New Proof Types
To add new proof generation types:
1. Add the generation function to `modules/generate_proof.py`
2. Update the API endpoint in `app.py`
3. Add UI elements in `templates/dashboard.html`
4. Update JavaScript in `static/dashboard.js`

### Styling
The application uses custom CSS in `static/dashboard.css`. You can modify colors, layouts, and animations to match your brand.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This application is for educational and entertainment purposes only. Please use responsibly and ethically. The generated excuses and proof documents are fictional and should not be used to deceive or mislead others. 