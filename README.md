# AUMS Assignment Maker

A Python-based automation system for the **Amrita University Academic Management System (AUMS)** that streamlines the discovery and collection of pending academic assignments. The system automatically scans available courses, identifies pending assignments, extracts assignment information and content, detects attachments, and downloads them into a structured local directory.

## Overview

Managing assignments across multiple courses in an academic portal can involve repetitive navigation and manual file collection. **AUMS Assignment Maker** automates this workflow through browser automation using Playwright.

The system is designed to:

1. Authenticate with AUMS using a persistent browser session.
2. Discover all available courses.
3. Navigate to the assignment section of each course.
4. Identify pending assignments.
5. Extract assignment metadata.
6. Open individual assignment pages.
7. Extract assignment page content.
8. Detect associated attachments.
9. Download assignment files.
10. Organize the collected material by course and assignment.

---

## Key Features

### Authentication & Session Management
- Persistent AUMS browser session.
- Reuses an existing authenticated session when available.
- Supports manual login when authentication is required.
- Stores session information locally.

### Course Discovery
- Automatically discovers available courses.
- Processes courses without requiring a manually specified course.
- Handles AUMS course and frame navigation.

### Assignment Detection
- Scans assignment sections across courses.
- Identifies assignments requiring attention.
- Extracts:
  - Course name
  - Assignment title
  - Assignment status
  - Opening date
  - Due date
  - Assignment URL

### Assignment Content Extraction
- Opens each pending assignment.
- Extracts the textual content of the assignment page.
- Stores the extracted content locally as `assignment.txt`.

### Attachment Management
- Detects assignment attachment links.
- Extracts attachment filenames and URLs.
- Downloads associated files automatically.
- Keeps files separated by assignment to prevent filename collisions.

### Organized Storage
Assignments are stored using a hierarchical directory structure:

```text
assignment_files/
└── <course>/
    └── <assignment>/
        ├── assignment.txt
        └── <attachment files>
```

Example:

```text
assignment_files/
└── Int M.Sc..2023.R.DS.1.22CSC402/
    ├── Assignment 21 - Using Pig/
    │   ├── assignment.txt
    │   └── employee.xlsx
    │
    └── Assignment 20 - Using Pig/
        ├── assignment.txt
        └── employee.xlsx
```

This structure ensures that attachments with identical filenames from different assignments do not overwrite one another.

---

## System Architecture

```text
                         ┌──────────────────┐
                         │      AUMS        │
                         │      Portal      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Authentication & │
                         │ Session Manager  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Course Discovery │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Assignment       │
                         │ Discovery        │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Pending          │
                         │ Assignment Filter│
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Assignment Page  │
                         │ Extraction       │
                         └───────┬───┬──────┘
                                 │   │
                    ┌────────────┘   └─────────────┐
                    ▼                              ▼
          ┌──────────────────┐          ┌──────────────────┐
          │ Assignment Text  │          │ Attachment       │
          │ Extraction       │          │ Detection        │
          └────────┬─────────┘          └────────┬─────────┘
                   │                             │
                   │                             ▼
                   │                    ┌──────────────────┐
                   │                    │ File Download    │
                   │                    └────────┬─────────┘
                   │                             │
                   └──────────────┬──────────────┘
                                  ▼
                         ┌──────────────────┐
                         │ Organized Local  │
                         │ Assignment Data  │
                         └──────────────────┘
```

---

## Project Structure

```text
AUMS/
│
├── main.py
├── config.py
├── requirements.txt
├── README.md
│
├── aums/
│   ├── courses.py
│   ├── assignments.py
│   └── attachments.py
│
├── storage/
│   └── aums_session.json
│
└── assignment_files/
    └── <course>/
        └── <assignment>/
```

### `main.py`

The primary application entry point and workflow controller.

Responsibilities include:

- Browser initialization
- AUMS session management
- Authentication handling
- Portal discovery
- Course scanning
- Pending assignment collection
- Assignment processing
- Content extraction
- Attachment downloading

### `aums/courses.py`

Responsible for course-level navigation and discovery.

Core responsibilities:

- Discover course links
- Locate course frames
- Locate the assignment section within courses

### `aums/assignments.py`

Responsible for assignment discovery and extraction.

Core responsibilities:

- Extract assignment listings
- Extract assignment metadata
- Identify pending assignments
- Open individual assignment pages
- Extract assignment text
- Detect attachment links

### `aums/attachments.py`

Responsible for downloading assignment files.

Core responsibilities:

- Process attachment URLs
- Download files
- Store files in assignment-specific directories
- Handle duplicate file references

### `config.py`

Contains application-level configuration, including:

- AUMS URL
- Session location
- Download directory
- Browser configuration
- Other runtime settings

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Playwright | Browser automation and AUMS interaction |
| HTML / DOM APIs | Portal content extraction |
| File System APIs | Local file organization and storage |

---

## Requirements

- Python 3.x
- A valid AUMS account
- Internet connection
- Playwright-compatible browser
- Required Python dependencies listed in `requirements.txt`

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Dhyan007/AUMS.git
cd AUMS
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

#### macOS / Linux

```bash
source venv/bin/activate
```

#### Windows

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Install Playwright browsers

```bash
playwright install
```

---

## Usage

Start the application with:

```bash
python main.py
```

The application then follows the automated workflow:

```text
Launch Application
        │
        ▼
Open AUMS
        │
        ▼
Check Saved Session
        │
        ├── Session Valid ───────► Continue
        │
        └── Session Invalid
                    │
                    ▼
              Manual Login
                    │
                    ▼
              Save Session
                    │
                    ▼
              Open Portal
                    │
                    ▼
             Scan All Courses
                    │
                    ▼
          Find Pending Assignments
                    │
                    ▼
          Process Each Assignment
                    │
                    ├── Extract Metadata
                    ├── Extract Content
                    ├── Detect Attachments
                    └── Download Files
                    │
                    ▼
             Organize Results
```

---

## Session Management

The application uses a persistent browser session:

```text
storage/aums_session.json
```

When a valid session exists, the application can reuse it instead of requiring authentication every time.

### Security

The session file may contain authentication-related browser state and **must not be committed to a public repository**.

Add the following entries to `.gitignore`:

```gitignore
storage/
assignment_files/
```

Downloaded assignments should also remain outside version control.

---

## Example Execution

A typical scan may produce output similar to:

```text
======================================================================
COURSE SCAN COMPLETE
======================================================================
Courses scanned: 15
Pending assignments found: 2
======================================================================

ALL PENDING ASSIGNMENTS
======================================================================

1. Int M.Sc..2023.R.DS.1.22CSC402
   Assignment: Assignment 21: Using Pig
   Status: Not Started
   Open: Sep 23, 2026 11:05 AM
   Due: Oct 10, 2026 11:55 PM

2. Int M.Sc..2023.R.DS.1.22CSC402
   Assignment: Assignment 20: Using Pig
   Status: Not Started
   Open: Sep 23, 2026 11:00 AM
   Due: Oct 10, 2026 11:55 PM
```

After discovery, each assignment is processed individually and its content and attachments are stored in its corresponding directory.

---

## Data Collected

For each pending assignment, the system can collect:

```text
Course
 ├── Assignment Title
 ├── Status
 ├── Opening Date
 ├── Due Date
 ├── Assignment URL
 ├── Assignment Text
 └── Attachments
      ├── Filename
      └── Downloaded File
```

---

## Design Principles

The project follows several design principles:

### Automation First

Repetitive portal navigation and file collection are handled programmatically rather than manually.

### Modular Architecture

Course discovery, assignment extraction, and attachment downloading are separated into dedicated modules.

### Assignment Isolation

Every assignment receives its own directory, preventing data collisions between assignments.

### Persistent Authentication

A saved browser session minimizes unnecessary authentication steps.

### Extensibility

The modular structure allows additional functionality to be introduced without rewriting the complete application.

---

## Future Development

Potential extensions include:

- Assignment deadline prioritization
- Course-wise assignment dashboards
- Deadline notifications
- Automatic periodic assignment scanning
- Assignment search and filtering
- Course-wise statistics
- Assignment content summarization
- AI-assisted assignment analysis
- Integration with notification services
- Automated submission workflows where permitted

---

## Limitations

- The system depends on the current structure and behavior of the AUMS portal.
- Changes to AUMS page structure, URLs, frames, or authentication mechanisms may require updates to the scraper.
- A valid authenticated AUMS session is required to access course and assignment information.
- Downloaded content is dependent on the availability and permissions of individual assignment attachments.

---

## Responsible Use

This project is intended for **educational and personal automation purposes**.

Users should ensure that their use of the application complies with:

- AUMS usage policies
- Institutional policies
- Assignment submission rules
- Applicable terms of service
- Academic integrity requirements

The application should not be used to bypass access controls or submit academic work in violation of institutional policies.

---

## Author

**Dhyan Sudheer**

GitHub: `Dhyan007`

---

## License

This project is intended as an educational software project. Licensing terms can be added according to the author's intended distribution model.