# AE Knowledge Hub 🚀

A comprehensive knowledge management and collaboration platform built with Streamlit and PostgreSQL. This application serves as a centralized hub for sharing materials, best practices, use cases, and team knowledge.

## Features

- **👥 User Management** - Admin panel for user administration and role-based access control
- **📚 Materials** - Centralized repository for learning materials and resources
- **💡 Knowledge Pills** - Bite-sized learning content for quick knowledge consumption
- **📋 Best Practices** - Documented best practices and guidelines
- **📖 Use Cases** - Real-world use case documentation and examples
- **🗺️ Roadmap** - Project roadmap and upcoming initiatives
- **🛠️ Stack & Tools** - Technology stack documentation and tool recommendations
- **📊 Dashboard** - Analytics and insights overview
- **⭐ AE of the Month** - Recognition and highlights of team achievements
- **🔐 Authentication** - Secure email-based authentication system with role-based access

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **Database:** PostgreSQL / SQLite
- **Authentication:** Streamlit Authenticator + Bcrypt
- **Data Processing:** Pandas
- **Environment Management:** Python-dotenv

## Prerequisites

- Python 3.8+
- PostgreSQL (optional - SQLite is supported as default)
- pip or conda

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AE-rtfact
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```
   # Database Configuration
   DB_TYPE=postgresql  # or sqlite
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=ae_knowledge
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_PATH=ae_knowledge.db  # For SQLite
   ```

5. **Initialize the database**
   ```bash
   python test_db_connection.py
   ```

## Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Access the application**
   
   Open your browser and navigate to `http://localhost:8501`

3. **Login**
   
   Use your authorized email to access the platform. User roles determine what features and content you can access.

## Project Structure

```
AE-rtfact/
├── app.py                      # Main Streamlit application
├── database.py                 # Database connection and queries
├── allowed_emails.py           # Email authorization and user roles
├── requirements.txt            # Python dependencies
├── test_db_connection.py       # Database connection testing
├── importar_materiais.py       # Utility for importing materials
├── pages/
│   ├── admin_usuarios.py       # User management panel
│   ├── dashboard.py            # Analytics dashboard
│   ├── materiais.py            # Materials repository
│   ├── pilulas_conhecimento.py # Knowledge pills page
│   ├── boas_praticas.py        # Best practices documentation
│   ├── casos_de_uso.py         # Use cases documentation
│   ├── roadmap.py              # Roadmap and planning
│   ├── stack_tools.py          # Technology stack documentation
│   └── ae_do_mes.py            # Monthly achievements
├── utils/
│   └── menu.py                 # Navigation menu utilities
└── assets/
    └── avatars/                # User avatar images
```

## Database Schema

The application supports both SQLite and PostgreSQL databases with the following main tables:

- **allowed_emails** - Authorized users and their roles
- **Users** - User profiles and authentication
- **Materials** - Content repository
- **Knowledge Pills** - Short-form learning content
- **Best Practices** - Guidelines and recommendations
- **Use Cases** - Documentation and examples
- **Roadmap Items** - Project planning
- **Stack Items** - Technology recommendations

## Authentication & Authorization

- Email-based authentication using Streamlit Authenticator
- Password hashing with bcrypt
- Role-based access control (RBAC)
- User approval workflow through admin panel

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_TYPE` | Database type (postgresql/sqlite) | sqlite |
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | ae_knowledge |
| `DB_USER` | Database user | - |
| `DB_PASSWORD` | Database password | - |
| `DB_PATH` | SQLite database path | ae_knowledge.db |

## Development

### Running Tests
```bash
python test_db_connection.py
```

### Importing Materials
```bash
python importar_materiais.py
```

### Code Style
The project follows PEP 8 guidelines. Use appropriate naming conventions and include docstrings for functions.

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## Troubleshooting

### Database Connection Issues
- Verify your `.env` file configuration
- Ensure PostgreSQL is running (if using PostgreSQL)
- Check database credentials

### Authentication Issues
- Verify your email is in the `allowed_emails` table
- Clear browser cache and re-login
- Check bcrypt password hashing

## Support & Documentation

For more information or support, contact the development team.

## License

Analytics Engineer Team @ ARTEFACT

---

**Last Updated:** March 2026
**Status:** Active Development
