# FoodCam Project Structure

## Recommended Organization

```
foodcam/                          # Root project directory
├── backend/                      # Django backend
│   ├── config/                   # Project configuration (renamed from posefit_project)
│   │   ├── __init__.py
│   │   ├── settings/             # Split settings
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # Base settings
│   │   │   ├── development.py    # Development settings
│   │   │   ├── production.py     # Production settings
│   │   │   └── testing.py        # Testing settings
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/                     # Django applications
│   │   ├── __init__.py
│   │   ├── accounts/             # User management
│   │   ├── classification/       # Food classification (renamed from classify)
│   │   ├── history/              # User history
│   │   ├── core/                 # Core utilities (renamed from index)
│   │   └── common/               # Shared utilities
│   │       ├── __init__.py
│   │       ├── models.py         # Abstract base models
│   │       ├── permissions.py    # Custom permissions
│   │       ├── serializers.py    # Base serializers
│   │       ├── utils.py          # Utility functions
│   │       └── validators.py     # Custom validators
│   ├── ml_models/                # Machine learning models
│   │   ├── __init__.py
│   │   ├── food_classifier.py    # Food classification logic
│   │   ├── calorie_estimator.py  # Calorie estimation logic
│   │   └── models/               # Model files
│   │       ├── TW_Food101_MobileNetV2.pt
│   │       └── class_names.json
│   ├── static/                   # Static files
│   ├── media/                    # User uploads
│   ├── templates/                # Django templates
│   ├── requirements/             # Requirements files
│   │   ├── base.txt              # Base requirements
│   │   ├── development.txt       # Development requirements
│   │   └── production.txt        # Production requirements
│   ├── manage.py
│   └── .env.example              # Environment variables template
├── frontend/                     # Vue.js frontend
│   ├── src/
│   │   ├── components/           # Reusable components
│   │   ├── pages/                # Page components
│   │   ├── services/             # API services
│   │   ├── stores/               # State management
│   │   ├── utils/                # Utility functions
│   │   ├── assets/               # Static assets
│   │   └── styles/               # Global styles
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── docs/                         # Documentation
│   ├── api.md                    # API documentation
│   ├── deployment.md             # Deployment guide
│   └── development.md            # Development setup
├── scripts/                      # Utility scripts
│   ├── setup.sh                  # Setup script
│   ├── deploy.sh                 # Deployment script
│   └── backup.sh                 # Backup script
├── docker/                       # Docker configuration
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── .gitignore
├── README.md
└── LICENSE
```

## Key Improvements

1. **Clear separation** between backend and frontend
2. **Modular Django apps** with clear responsibilities
3. **Split settings** for different environments
4. **Organized ML models** in dedicated directory
5. **Proper documentation** structure
6. **Docker support** for containerization
7. **Utility scripts** for common tasks
8. **Environment-specific requirements**

## Benefits

- **Maintainability**: Clear structure makes code easier to maintain
- **Scalability**: Modular design supports growth
- **Deployment**: Environment-specific configurations
- **Collaboration**: Clear organization helps team development
- **Testing**: Separated concerns make testing easier 