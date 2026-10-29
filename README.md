# AMRx Hub
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22180074.svg)](https://doi.org/10.5281/zenodo.22180074)
[![MRA](https://img.shields.io/badge/MRA-10.1128%2Fmra.00997--26-1f6feb)](https://doi.org/10.1128/mra.00997-26)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django 5.2](https://img.shields.io/badge/django-5.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![Project Status: WIP](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Famrxhub.helixbiogeninstitute.org)](https://amrxhub.helixbiogeninstitute.org)
[![Last commit](https://img.shields.io/github/last-commit/ender-ma/AMRxHub)](https://github.com/ender-ma/AMRxHub/commits/main)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](#contributing)


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

Please follow project standards and maintain scientific integrity when submitting changes. Changes and ideas can be submitted to amrtool344@gmail.com

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

If AMRx Hub supports your work, please cite the publication and the software release you used.

**Publication (Microbiology Resource Announcements)**

> Oladipo EK, Adeolu-Shittu AI, Fatuyi-Adene AD, Emmanuel JO. 2026. AMRx Hub: a curated web platform for discovery of antimicrobial resistance resources. Microbiol Resour Announc e00997-26. https://doi.org/10.1128/mra.00997-26

**Software (Zenodo)**

> Oladipo, E. K., Adeolu-Shittu, A. I., Fatuyi-Adene, A. D., & Emmanuel, J. O. (2026). *AMRx Hub: A Curated Web Platform for Discovery of Antimicrobial Resistance Resources* (Version 0.9.5) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.22180074

<details>
<summary>BibTeX</summary>

```bibtex
@article{oladipo2026amrxhub,
  author  = {Oladipo, Elijah Kolawole and Adeolu-Shittu, Akinloluwa Isaac and Fatuyi-Adene, Adeniyi Daniel and Emmanuel, Joy Olamiposi},
  title   = {{AMRx Hub}: a curated web platform for discovery of antimicrobial resistance resources},
  journal = {Microbiology Resource Announcements},
  year    = {2026},
  pages   = {e00997-26},
  doi     = {10.1128/mra.00997-26}
}

@software{oladipo2026amrxhub_software,
  author    = {Oladipo, Elijah Kolawole and Adeolu-Shittu, Akinloluwa Isaac and Fatuyi-Adene, Adeniyi Daniel and Emmanuel, Joy Olamiposi},
  title     = {{AMRx Hub}: A Curated Web Platform for Discovery of Antimicrobial Resistance Resources},
  version   = {0.9.5},
  publisher = {Zenodo},
  year      = {2026},
  doi       = {10.5281/zenodo.22180074},
  url       = {https://doi.org/10.5281/zenodo.22180074}
}
```

</details>

## License

License information can be found in the license file.

## Contact

- **Technical Lead:** Akinloluwa Isaac Adeolu-Shittu
- **Email:** isaacodes25@gmail.com
- **Website:** https://amrxhub.helixbiogeninstitute.org
- **GitHub Repository:** https://github.com/ender-ma/AMRxHub
