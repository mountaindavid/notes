# Notes App

A web application for creating and managing notes, built with Django.

## Description

Notes App is a full-featured web application that allows users to:
- Create, edit, and delete notes
- Organize notes by categories
- Manage user accounts
- Use a modern and intuitive interface

## Technologies

- **Backend**: Django 4.x
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (for development)
- **Deployment**: Docker

## Project Structure

```
Notes/
├── backend/                 # Django application
│   ├── apps/
│   │   ├── notes/          # Notes application
│   │   └── users/          # Users application
│   ├── core/               # Core settings
│   ├── notes_project/      # Django project settings
│   ├── static/             # Static files
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Docker configuration
│   └── docker-compose.yml  # Docker Compose configuration
└── docs/                   # Documentation
```

## Installation and Setup

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/mountaindavid/Notes.git
cd Notes
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Start the development server:
```bash
python manage.py runserver
```

### Using Docker

1. Clone the repository and navigate to the backend folder:
```bash
git clone https://github.com/mountaindavid/Notes.git
cd Notes/backend
```

2. Run with Docker Compose:
```bash
docker-compose up --build
```

## Usage

After starting the application:

1. Open your browser and go to: `http://localhost:8000`
2. Register or log in to your account
3. Start creating and managing your notes

## API Endpoints

- `/api/notes/` - CRUD operations for notes
- `/api/users/` - User management
- `/admin/` - Django admin panel

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is distributed under the MIT License. See the `LICENSE` file for more information.

## Contact

- GitHub: [@mountaindavid](https://github.com/mountaindavid)
- Project: [https://github.com/mountaindavid/Notes](https://github.com/mountaindavid/Notes)
