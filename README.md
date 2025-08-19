# ProtCyber - Vulnerability Assessment Report Generator

A professional Python application that generates comprehensive PDF vulnerability assessment reports from security scan data. This tool transforms raw vulnerability data into polished, branded reports suitable for client delivery.

## 🚀 Features

- **Professional PDF Generation**: Creates branded PDF reports with company logos and custom styling
- **Vulnerability Analysis**: Processes and categorizes vulnerabilities by severity levels
- **Visual Elements**: Includes pie charts and color-coded severity indicators
- **Customizable Templates**: Configurable report sections and company branding
- **Database Integration**: Connects to MySQL databases to retrieve vulnerability data
- **AI-Powered Analysis**: Uses OpenAI integration for enhanced vulnerability descriptions
- **Multi-Severity Support**: Handles Critical, High, Medium, Low, and Informative vulnerabilities

## 📋 Prerequisites

- Python 3.7+
- MySQL database with vulnerability data
- OpenAI API key (optional, for enhanced analysis)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/codarkle/ProtCyber.git
   cd ProtCyber
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the application**
   - Update `report_config.py` with your company information
   - Add your company logo to the `assets/` directory
   - Configure database connection settings

## 📁 Project Structure

```
ProtCyber/
├── main.py                 # Main application entry point
├── report_config.py        # Configuration and templates
├── utils.py               # Utility functions and database operations
├── pie_chart.py           # Chart generation utilities
├── beautify_response.py   # Response formatting utilities
├── openai_func.py         # OpenAI integration
├── requirements.txt       # Python dependencies
├── assets/               # Images and branding assets
│   ├── ProtCyber_logo.png
│   ├── company_logo.png
│   └── icons/
└── rapport_artci_ci_30062025.json  # Sample vulnerability data
```

## ⚙️ Configuration

### Company Branding
Edit `report_config.py` to customize:
- Company name
- Logo path
- Front page image
- Report templates and content

### Database Configuration
Configure your MySQL database connection in the utility functions to retrieve vulnerability data.

## 🚀 Usage

### Basic Usage
```python
from main import PDFReport

# Create a new report
report = PDFReport(
    title="Vulnerability Assessment Report",
    domain="example.com",
    logo_path="assets/company_logo.png"
)

# Generate the report
report.generate_report(vulnerability_data)
```

### Command Line Usage
```bash
python main.py --domain example.com --title "Security Assessment"
```

## 📊 Report Sections

The generated PDF includes:
1. **Front Page** - Company branding and report title
2. **Statement of Confidentiality** - Legal disclaimers
3. **Scope** - Assessment boundaries and limitations
4. **Executive Summary** - High-level findings overview
5. **Recommendations** - Strategic security advice
6. **Detailed Analysis** - Comprehensive vulnerability breakdown
7. **Vulnerabilities** - Individual vulnerability details
8. **Conclusion** - Summary and next steps

## 🎨 Customization

### Severity Color Coding
The application uses color-coded severity indicators:
- **Critical (1)**: Red gradient
- **High (2)**: Orange gradient  
- **Medium (3)**: Green gradient
- **Low (4)**: Blue gradient

### Adding Custom Sections
Modify `report_config.py` to add or modify report sections and content templates.

## 🔧 Dependencies

- **fpdf2**: PDF generation
- **mysql-connector-python**: Database connectivity
- **beautify_response**: Response formatting
- **matplotlib**: Chart generation (for pie charts)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the configuration documentation

## 🔒 Security

- Ensure vulnerability data is handled securely
- Use encrypted database connections
- Protect API keys and sensitive configuration
- Follow your organization's security policies

---

**ProtCyber** - Professional vulnerability assessment reporting made simple. 