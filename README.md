# AMRx Hub
https://doi.org/10.5281/zenodo.22180074

AMRx Hub is an open-access web platform for centralized discovery of antimicrobial resistance (AMR) resources across the scientific ecosystem. It brings together databases, analytical tools, publications, protocols, surveillance systems, educational content, and policy references into a single searchable repository.

The platform is designed to reduce fragmentation in AMR research and practice by improving access for researchers, clinicians, educators, students, policymakers, and public health professionals.

## Problem Statement

AMR resources are distributed across many websites, databases, repositories, publications, and institutional platforms. This fragmentation makes it time-intensive to identify relevant tools, datasets, educational materials, and surveillance resources.

AMRx Hub addresses this challenge by organizing AMR-related resources into a centralized, searchable platform.

## Resource Discovery Model

AMRx Hub primarily functions as a discovery and access platform rather than attempting to replace the individual tools, databases, repositories, or resources it catalogues.

Where appropriate, the Hub provides users with information about a resource and directs them to the original platform or source. This allows AMRx Hub to bring distributed AMR resources together while preserving links to their original providers.

## Open-Source Development

AMRx Hub is developed using an open-source approach to encourage transparency, reproducibility, community participation, and continued development.

The project source code and development information are maintained through its public repository.

## Project Status

AMRx Hub is under active development. Resource coverage, metadata, search capabilities, platform functionality, and technical infrastructure will continue to evolve as the Hub grows and as new AMR resources become available.

### Current Development Status

AMRx Hub is under active development.

- The current production stack is Django with server-rendered HTML templates.
- Existing functionality is powered by Django-rendered pages.
- A Next.js frontend is currently being developed.
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

- Web-Based Access
- Curated AMR Resources
- Structured Resource Categories
- Search and Discovery
- One Health Coverage
- Centralized Access
- Metadata-Driven Resource Management
- External Resource Integration
- Open Source and Community-Driven

## Tool Categories

### Organism-Specific Tools Categories 
(This categories features majorly the ESKAPE organisms)

- Enterococcus faecium
- Staphylococcus aureus
- Klebsiella pneumoniae
- Acinetobacter baumannii
- Pseudomonas aeruginosa
- Enterobacter species
- Mycobacterium tuberculosis
(Note: These categories are subject to chnage and updates)

### General Use Tools Categories

- AMR Gene Detection
- Pathogen Identification
- Strain & Sequence Typing
- Virulence Factor Detection
- Genomic Epidemiology
- AMR Phenotype Prediction
(Note: These categories are subject to chnage and updates)

## Resource Categories

- AMR Knowledge & Publications
- Surveillance & AMR Data
- One Health & Sector Resources
- Guidelines, Policies & Stewardship
- Laboratory, Protocols & Training
- Environmental AMR & Antimicrobial Pollution
(Note: These categories are subject to chnage and updates)

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

> Note: Next.js frontend integration is currently under development in a private repository.

## Installation

```bash
# Clone the repository
git clone https://github.com/ender-ma/AMRxHub.git
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

Please follow project standards and maintain scientific integrity when submitting changes. Change and ideas can be submitted to 

## Roadmap (Future Goals)

- Next.js frontend integration
- Enhanced search functionality
- Expanded resource coverage
- Community contribution workflows
- Resource quality assessment
- API development
- Increased educational content
- Backend Ai integration

## Citation

Formal citation information will be added after manuscript publication.

## License

License information can be found in the license file.

## Contact

- **Project Lead:** Akinloluwa Isaac Adeolu-Shittu
- **Email:** isaacodes25@gmail.com
- **Website:** https://www.amrxhub.com/
- **GitHub Repository:** https://github.com/ender-ma/AMRxHub
