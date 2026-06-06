# AMRx Hub: A Curated Web Platform for Discovery of Antimicrobial Resistance Resources

A comprehensive Django-based web application tailored to support antimicrobial resistance (AMR) research. AMRx Hub provides scientists and clinicians with unified collaborative tools, secure data analysis pipelines, and centralized resource sharing.

## 🎯 Technical Features

* **Advanced Authentication & Security:** Custom user model with secure session management, built-in email verification, and Google OAuth integration via `django-allauth`.
* **Flexible Database Architecture:** Dynamic environment-based toggling between SQLite for rapid local development and Postgresql for high-performance production.
* **Storage & Static Management:** Robust file upload handling with WhiteNoise integration for serving static assets effectively in production environments.
* **Platform-Agnostic Deployment:** Out-of-the-box support for multiple PaaS providers including Render (via `render.yaml`), Railway (via `nixpacks.toml` and Docker), and Heroku-like environments (via `procfile`).

## 🛠 Tech Stack

* **Backend:** Django 5.2.3, Python 3.11+
* **Database:** Postgresql (Production), SQLite (Development)
* **Authentication:** Django Allauth + Google OAuth
* **Infrastructure:** Docker, Render, Nixpacks
* **Static Files:** WhiteNoise

## 📁 Project Structure

Below is an overview of the project's structure, focusing heavily on the configuration and infrastructure files used outside of the standard Django boilerplate:

```text
ATH/
├── authentication/          # Django app: User management, custom models, and auth views
├── history/                 # Django app: Audit models and mixins for activity tracking
├── main/                    # Django app: Core project settings and URL routing
├── notifications/           # Django app: Notification triggers
├── profil/                  # Django app: Extended user profiles
├── resources/               # Django app: Resource library and document management
├── tools/                   # Django app: Research tools and analysis instruments
│
# --- Non-Django Default / Infrastructure Files ---
├── app.py                   # ASGI/WSGI entry point wrapper or custom server script
├── build.sh                 # Custom build script for PaaS platforms (e.g., Render)
├── Dockerfile               # Containerization configuration for Docker deployments
├── nixpacks.toml            # Build environment instructions for Railway/Nixpacks
├── procfile                 # Process definitions for web and worker dynos
├── render.yaml              # Infrastructure-as-code configuration for Render deployment
├── tidb-ca.pem              # SSL certificate for secure connections to TiDB databases
├── robot.txt                # Search engine crawler instructions for SEO
├── sitemap.xml              # XML sitemap mapping out public routes for search indexing
└── requirements.txt         # Python dependency lockfile
