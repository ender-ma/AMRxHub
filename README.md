# AMRx Hub

AMRx Hub is an open-access web platform for centralized discovery of antimicrobial resistance (AMR) resources across the scientific ecosystem. It brings together databases, analytical tools, publications, protocols, surveillance systems, educational content, and policy references into a single searchable repository.

The platform is designed to reduce fragmentation in AMR research and practice by improving access for researchers, clinicians, educators, students, policymakers, and public health professionals.

## Problem Statement

AMR resources are distributed across many websites, databases, repositories, publications, and institutional platforms. This fragmentation makes it time-intensive to identify relevant tools, datasets, educational materials, and surveillance resources.

AMRx Hub addresses this challenge by organizing AMR-related resources into a centralized, searchable platform.

## Current Development Status

AMRx Hub is under active development.

- The current production stack is Django with server-rendered HTML templates.
- Existing functionality is powered by Django-rendered pages.
- A Next.js frontend is currently being developed and integrated.
- A REST API has not yet been implemented.
- The project is transitioning toward a decoupled architecture.

## Target Audience

AMRx Hub is intended for:

- Researchers
- Microbiologists
- Bioinformaticians
- Clinicians
- Public health professionals
- Educators
- Students
- Policymakers

## Core Features (Current Platform)

The current platform focuses on:

- Centralized resource discovery
- Curated antimicrobial resistance resources
- Search and filtering capabilities
- Resource categorization
- Community resource submission
- Educational resource access
- Open access resource sharing
- One Health resource organization

## Resource Categories

### General Categories

- Databases
- Genomic Data Repositories
- Publications & Manuscripts
- Software Repositories
- Protocols & SOPs
- Training & Educational Resources
- Surveillance Resources
- Guidelines & Policy Documents

### Organism-Specific Categories

- Mycobacterium tuberculosis Tools
- Staphylococcus aureus Tools
- Salmonella Tools
- Neisseria Tools
- Other Organism Tools

## Mission

AMRx Hub aims to democratize access to antimicrobial resistance resources by improving discoverability, supporting evidence-based research, and enabling cross-disciplinary collaboration. The project follows a One Health framework to strengthen integration across human, animal, and environmental health domains while supporting global AMR awareness and scientific progress.

## Technology Stack

### Backend

- Django

### Frontend

- HTML
- CSS
- JavaScript

### Database

- PostgreSQL

### Version Control

- Git
- GitHub

> Note: Next.js frontend integration is currently under development.

## Installation

```bash
# Clone the repository
git clone https://github.com/<owner>/AMRxHub.git
cd AMRxHub

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Run development server
python manage.py runserver
```

## Contributing

Contributions are welcome. Areas for contribution include:

- Resource submissions
- Documentation improvements
- Bug reports
- Feature suggestions
- Development contributions

Please follow project standards and maintain scientific integrity when submitting changes.

## Roadmap (Future Goals)

- Next.js frontend integration
- Enhanced search functionality
- Expanded resource coverage
- Community contribution workflows
- Resource quality assessment
- API development
- Increased educational content

## Citation

Formal citation information will be added after manuscript publication.

## License

License information will be added once the project license is finalized.

## Contact

- **Project Lead:** _To be added_
- **Email:** _To be added_
- **Website:** _To be added_
- **GitHub Repository:** https://github.com/<owner>/AMRxHub
