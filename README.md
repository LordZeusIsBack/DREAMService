<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

# DREAMSERVICE

<em></em>

<!-- BADGES -->

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/Redis-FF4438.svg?style=default&logo=Redis&logoColor=white" alt="Redis">
<img src="https://img.shields.io/badge/GNU%20Bash-4EAA25.svg?style=default&logo=GNU-Bash&logoColor=white" alt="GNU%20Bash">
<img src="https://img.shields.io/badge/Gunicorn-499848.svg?style=default&logo=Gunicorn&logoColor=white" alt="Gunicorn">
<img src="https://img.shields.io/badge/Celery-37814A.svg?style=default&logo=Celery&logoColor=white" alt="Celery">
<img src="https://img.shields.io/badge/Django-092E20.svg?style=default&logo=Django&logoColor=white" alt="Django">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?style=default&logo=GitHub-Actions&logoColor=white" alt="GitHub%20Actions">

<!-- default option, no dependency badges. -->

<!-- default option, no dependency badges. -->

</div>
<br>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
  - [Project Index](#project-index)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

DREAMService is a Django-based backend for real estate platforms that centralizes buyer, seller, and property data in a clean, modular architecture. It serves engineering teams and product builders who need a scalable, production-ready foundation to ship property workflows faster and more reliably. Core functionality includes web APIs for domain entities, background task orchestration with Celery and Redis, and production-ready operations using Gunicorn with CI automation via GitHub Actions.

## Features

- API: Exposes RESTful endpoints for authentication, user profiles, and property workflows, wired via Django apps, URLs, and views.​
- buyer_data: Ingests and validates buyer profiles, contact info, and preferences with serializers, signals, and loan calculation utilities.​
- estate_data: Models and stores property listings with CRUD, geospatial helpers, and calculator utilities for search-ready data.​
- seller_data: Manages seller accounts, subscriptions, and verification flows with serializers, admin integration, and utility decorators.​
- common: Provides shared models, background tasks, OTP handling, storage backends, and structured logging for cross-module consistency.​
- Operations: Runs background jobs with Celery + Redis, serves via Gunicorn, and automates CI with GitHub Actions.

---

## Project Structure

```sh
└── DREAMService/
    ├── .github
    │   └── workflows
    ├── api
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── migrations
    │   ├── models.py
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── build.sh
    ├── buyer_data
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── migrations
    │   ├── models.py
    │   ├── serializer.py
    │   ├── tests.py
    │   ├── urls.py
    │   ├── utils
    │   └── views.py
    ├── common
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── migrations
    │   ├── models.py
    │   ├── serializer.py
    │   ├── tasks.py
    │   ├── tests.py
    │   ├── urls.py
    │   ├── utils
    │   └── views.py
    ├── dream_service
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── celery.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── estate_data
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── migrations
    │   ├── models.py
    │   ├── serializer.py
    │   ├── tests.py
    │   ├── urls.py
    │   ├── utils
    │   └── views.py
    ├── manage.py
    ├── requirements.txt
    └── seller_data
        ├── __init__.py
        ├── admin.py
        ├── apps.py
        ├── migrations
        ├── models.py
        ├── serializer.py
        ├── tests.py
        ├── urls.py
        ├── utils
        └── views.py
```

### Project Index

<details open>
	<summary><b><code>DREAMSERVICE/</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/build.sh'>build.sh</a></b></td>
					<td style='padding: 8px;'>Deployment script for building and configuring the application server.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/manage.py'>manage.py</a></b></td>
					<td style='padding: 8px;'>Django CLI for running management commands and project tasks.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/requirements.txt'>requirements.txt</a></b></td>
					<td style='padding: 8px;'>Python package dependencies list for project installation and setup.</code></td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- .github Submodule -->
	<details>
		<summary><b>.github</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ .github</b></code>
			<!-- workflows Submodule -->
			<details>
				<summary><b>workflows</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ .github.workflows</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/.github/workflows/django.yml'>django.yml</a></b></td>
							<td style='padding: 8px;'>CI/CD workflow for automated testing and deployment automation.</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<!-- api Submodule -->
	<details>
		<summary><b>api</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ api</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/api/admin.py'>admin.py</a></b></td>
					<td style='padding: 8px;'>Django admin panel configurations for API model management.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/api/apps.py'>apps.py</a></b></td>
					<td style='padding: 8px;'>Application configuration defining API app metadata and settings.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/api/models.py'>models.py</a></b></td>
					<td style='padding: 8px;'>Database models defining API data structures and relationships.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/api/tests.py'>tests.py</a></b></td>
					<td style='padding: 8px;'>Unit tests for validating API functionality and endpoints.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/api/urls.py'>urls.py</a></b></td>
					<td style='padding: 8px;'>URL routing patterns mapping endpoints to API views.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/api/views.py'>views.py</a></b></td>
					<td style='padding: 8px;'>Request handlers implementing API business logic and responses.</code></td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- buyer_data Submodule -->
	<details>
		<summary><b>buyer_data</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ buyer_data</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/buyer_data/admin.py'>admin.py</a></b></td>
					<td style='padding: 8px;'>Admin interface configurations for buyer profile and data management.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/buyer_data/apps.py'>apps.py</a></b></td>
					<td style='padding: 8px;'>App configuration defining buyer_data module metadata and signals.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/buyer_data/models.py'>models.py</a></b></td>
					<td style='padding: 8px;'>Buyer profile, preferences, and contact information database models.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/buyer_data/serializer.py'>serializer.py</a></b></td>
					<td style='padding: 8px;'>JSON serializers for buyer data validation and API responses.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/buyer_data/tests.py'>tests.py</a></b></td>
					<td style='padding: 8px;'>Test suite for buyer registration, validation, and profile workflows.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/buyer_data/urls.py'>urls.py</a></b></td>
					<td style='padding: 8px;'>URL patterns routing buyer profile and preference endpoints.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/buyer_data/views.py'>views.py</a></b></td>
					<td style='padding: 8px;'>View handlers for buyer registration, authentication, and CRUD operations.</code></td>
				</tr>
			</table>
			<!-- migrations Submodule -->
			<details>
				<summary><b>migrations</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ buyer_data.migrations</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/buyer_data/migrations/0001_initial.py'>0001_initial.py</a></b></td>
							<td style='padding: 8px;'>Initial database schema migration creating buyer data tables.</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/buyer_data/migrations/0002_initial.py'>0002_initial.py</a></b></td>
							<td style='padding: 8px;'>Secondary migration adding buyer relationships and foreign key constraints.</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/buyer_data/migrations/0003_alter_buyer_phone_number.py'>0003_alter_buyer_phone_number.py</a></b></td>
							<td style='padding: 8px;'>Schema update modifying buyer phone number field validation rules.</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- utils Submodule -->
			<details>
				<summary><b>utils</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ buyer_data.utils</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/buyer_data/utils/loan_math.py'>loan_math.py</a></b></td>
							<td style='padding: 8px;'>Mathematical utilities for calculating EMI, interest, and loan eligibility.</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/buyer_data/utils/signals.py'>signals.py</a></b></td>
							<td style='padding: 8px;'>Django signals for buyer profile creation and update events.</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<!-- common Submodule -->
	<details>
		<summary><b>common</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ common</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/common/admin.py'>admin.py</a></b></td>
					<td style='padding: 8px;'>Admin configurations for shared models and cross-module utilities.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/common/apps.py'>apps.py</a></b></td>
					<td style='padding: 8px;'>Application configuration for common shared resources and middleware.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/common/models.py'>models.py</a></b></td>
					<td style='padding: 8px;'>Shared database models for OTP, logs, and base classes.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/common/serializer.py'>serializer.py</a></b></td>
					<td style='padding: 8px;'>Common serializers for standardized API responses and data validation.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/common/tasks.py'>tasks.py</a></b></td>
					<td style='padding: 8px;'>Celery background tasks for email, OTP, and async processing.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/common/tests.py'>tests.py</a></b></td>
					<td style='padding: 8px;'>Test cases for common utilities, tasks, and shared functionality.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/common/urls.py'>urls.py</a></b></td>
					<td style='padding: 8px;'>URL routing for OTP verification and shared endpoint patterns.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/common/views.py'>views.py</a></b></td>
					<td style='padding: 8px;'>View handlers for OTP generation, validation, and common operations.</code></td>
				</tr>
			</table>
			<!-- migrations Submodule -->
			<details>
				<summary><b>migrations</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ common.migrations</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/common/migrations/0001_initial.py'>0001_initial.py</a></b></td>
							<td style='padding: 8px;'>Initial migration creating OTP, logging, and shared utility tables.</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- utils Submodule -->
			<details>
				<summary><b>utils</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ common.utils</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/common/utils/otp_handler.py'>otp_handler.py</a></b></td>
							<td style='padding: 8px;'>OTP generation, validation, and expiration logic for authentication.</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/common/utils/signals.py'>signals.py</a></b></td>
							<td style='padding: 8px;'>Django signals for logging, notifications, and cross-module event handling.</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/common/utils/storage_backends.py'>storage_backends.py</a></b></td>
							<td style='padding: 8px;'>Custom storage backends for AWS S3 and media file management.</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/common/utils/upload_logs.py'>upload_logs.py</a></b></td>
							<td style='padding: 8px;'>Logging utilities for tracking file uploads and storage operations.</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<!-- dream_service Submodule -->
	<details>
		<summary><b>dream_service</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ dream_service</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/dream_service/asgi.py'>asgi.py</a></b></td>
					<td style='padding: 8px;'>ASGI application configuration for async server and websocket support.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/dream_service/celery.py'>celery.py</a></b></td>
					<td style='padding: 8px;'>Celery configuration defining broker, tasks, and background job settings.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/dream_service/settings.py'>settings.py</a></b></td>
					<td style='padding: 8px;'>Django settings for database, middleware, apps, and environment variables.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/dream_service/urls.py'>urls.py</a></b></td>
					<td style='padding: 8px;'>Root URL configuration routing all app endpoints and admin.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/dream_service/wsgi.py'>wsgi.py</a></b></td>
					<td style='padding: 8px;'>WSGI application entry point for Gunicorn and production deployment.</code></td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- estate_data Submodule -->
	<details>
		<summary><b>estate_data</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ estate_data</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/estate_data/admin.py'>admin.py</a></b></td>
					<td style='padding: 8px;'>Admin interface for property listings, images, and estate management.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/estate_data/apps.py'>apps.py</a></b></td>
					<td style='padding: 8px;'>App configuration defining estate_data module metadata and ready hooks.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/estate_data/models.py'>models.py</a></b></td>
					<td style='padding: 8px;'>Property listing models with fields for location, price, and amenities.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/estate_data/serializer.py'>serializer.py</a></b></td>
					<td style='padding: 8px;'>Serializers for property data validation, search, and API responses.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/estate_data/tests.py'>tests.py</a></b></td>
					<td style='padding: 8px;'>Test suite for property CRUD operations and search functionality.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/estate_data/urls.py'>urls.py</a></b></td>
					<td style='padding: 8px;'>URL patterns for property listing, search, and detail endpoints.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/estate_data/views.py'>views.py</a></b></td>
					<td style='padding: 8px;'>View handlers for property creation, retrieval, filtering, and pagination.</code></td>
				</tr>
			</table>
			<!-- migrations Submodule -->
			<details>
				<summary><b>migrations</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ estate_data.migrations</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/estate_data/migrations/0001_initial.py'>0001_initial.py</a></b></td>
							<td style='padding: 8px;'>Initial migration creating property listing and related data tables.</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- utils Submodule -->
			<details>
				<summary><b>utils</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ estate_data.utils</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/estate_data/utils/geo_utils.py'>geo_utils.py</a></b></td>
							<td style='padding: 8px;'>Geospatial utilities for distance calculation and location-based property search.</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/estate_data/utils/signals.py'>signals.py</a></b></td>
							<td style='padding: 8px;'>Django signals for property updates, indexing, and notification triggers.</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/estate_data/utils/views_calculator.py'>views_calculator.py</a></b></td>
							<td style='padding: 8px;'>Calculator utilities for property views, popularity scoring, and analytics.</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<!-- seller_data Submodule -->
	<details>
		<summary><b>seller_data</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ seller_data</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/seller_data/admin.py'>admin.py</a></b></td>
					<td style='padding: 8px;'>Admin interface for seller accounts, verification, and subscription management.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/seller_data/apps.py'>apps.py</a></b></td>
					<td style='padding: 8px;'>App configuration defining seller_data module metadata and initialization logic.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/seller_data/models.py'>models.py</a></b></td>
					<td style='padding: 8px;'>Seller profile, verification status, and subscription tier database models.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/seller_data/serializer.py'>serializer.py</a></b></td>
					<td style='padding: 8px;'>Serializers for seller registration, verification, and profile data validation.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/seller_data/tests.py'>tests.py</a></b></td>
					<td style='padding: 8px;'>Test suite for seller onboarding, verification workflows, and subscriptions.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/seller_data/urls.py'>urls.py</a></b></td>
					<td style='padding: 8px;'>URL routing for seller registration, verification, and profile endpoints.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/seller_data/views.py'>views.py</a></b></td>
					<td style='padding: 8px;'>View handlers for seller authentication, profile updates, and subscription management.</code></td>
				</tr>
			</table>
			<!-- migrations Submodule -->
			<details>
				<summary><b>migrations</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ seller_data.migrations</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/seller_data/migrations/0001_initial.py'>0001_initial.py</a></b></td>
							<td style='padding: 8px;'>Initial migration creating seller account and verification tables.</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/seller_data/migrations/0002_remove_sellerverification_aadhaar_card_and_more.py'>0002_remove_sellerverification_aadhaar_card_and_more.py</a></b></td>
							<td style='padding: 8px;'>Migration removing Aadhaar fields and updating verification document structure.</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/seller_data/migrations/0003_alter_seller_phone_number.py'>0003_alter_seller_phone_number.py</a></b></td>
							<td style='padding: 8px;'>Schema update modifying seller phone number field with validation.</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- utils Submodule -->
			<details>
				<summary><b>utils</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ seller_data.utils</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/LordZeusIsBack/DREAMService/blob/main/seller_data/utils/subscription_decorator.py'>subscription_decorator.py</a></b></td>
							<td style='padding: 8px;'>Decorator utilities for enforcing subscription-based access control and feature gating.</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---

## Getting Started

### Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python
- **Package Manager:** Pip

### Installation

Build DREAMService from the source and install dependencies:

1. **Clone the repository:**

   ```sh
   ❯ git clone https://github.com/LordZeusIsBack/DREAMService
   ```

2. **Navigate to the project directory:**

   ```sh
   ❯ cd DREAMService
   ```

3. **Install the dependencies:**

<!-- SHIELDS BADGE CURRENTLY DISABLED -->

    <!-- [![pip][pip-shield]][pip-link] -->
    <!-- REFERENCE LINKS -->
    <!-- [pip-shield]: https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white -->
    <!-- [pip-link]: https://pypi.org/project/pip/ -->

    **Using [pip](https://pypi.org/project/pip/):**

    ```sh
    ❯ pip install -r requirements.txt
    ```

### Usage

Run the project with:

**Using [pip](https://pypi.org/project/pip/):**

```sh
python manage.py runserver
```

### Testing

Dreamservice uses the pytest test framework. Run the test suite with:

**Using [pip](https://pypi.org/project/pip/):**

```sh
pytest
```

---

## Contributing

- **💬 [Join the Discussions](https://github.com/LordZeusIsBack/DREAMService/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/LordZeusIsBack/DREAMService/issues)**: Submit bugs found or log feature requests for the `DREAMService` project.
- **💡 [Submit Pull Requests](https://github.com/LordZeusIsBack/DREAMService/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your GitHub account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/LordZeusIsBack/DREAMService
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to GitHub**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/LordZeusIsBack/DREAMService/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=LordZeusIsBack/DREAMService">
   </a>
</p>
</details>

---

## License

Dreamservice is protected under the [LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

## Acknowledgments

- Credit `contributors`, `inspiration`, `references`, etc.

<div align="right">

[![][back-to-top]](#top)

</div>

[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square

---
