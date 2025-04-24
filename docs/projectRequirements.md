
# **Cyber Challenge**

**Authors:** @roberthartman, @cmandich

---

## **Overview: Docker, URLs, and APIs—Oh My!**
The Cyber Challenge is a collaborative exercise for the team to design and build a REST API packaged as a Docker application.

---

## **Challenge Objective**

Rivian's cybersecurity team requires a system to manage malicious URLs to block them effectively. Your task is to develop an application that fetches, filters, and presents a list of malicious URLs in a programmatically ingestible format.

---

## **API Requirements**

Develop a REST API with the following endpoints:

### **1. GET /denylist**
- [x] Returns URLs from the external source: `https://urlhaus.abuse.ch/downloads/text/`.
- [x] Filters out URLs added via `POST /allowlist`.
- [x] Persists all retrieved URLs locally to avoid overwhelming the upstream data source.
- [x] Provides fresh data, even in times of change.

---

### **2. POST /allowlist**
- [x] Accepts a list of URLs to be excluded from the `/denylist` output.
- [?] Saves the received URLs to persistent storage and **_retains historical data_**.
- [x] Responds with the added URLs in the JSON field:
  ```json
  {
      "urls_added": ["url1", "url2", ...]
  }
  ```

---

### **3. GET /allowlist**
- [x] Returns all URLs added to the allowlist without duplicates.

---

### **Additional API Requirements**
- [x] Persistent storage must retain data across application restarts.
- [x] Programming language and storage method (e.g., local files, database, or memory cache) are developer's choice.

---

## **Application Infrastructure Requirements**

- [x] The application must be containerized using **Docker**.
- [x] Include both a `Dockerfile` and a `docker-compose.yml` file for deployment.
- [x] The `Dockerfile` should define the application's environment, dependencies, and entry point.
- [x] The `docker-compose.yml` file should configure the services, networks, and volumes required for the application.
- [x] Ensure the application can be built and run using a single `docker-compose up` command.
- [x] The application should be able to run in a local development environment as well as in a production environment.
- [x] Provide clear instructions on how to build and run the Docker containers.
- [x] Include health checks in the Docker configuration to ensure the application is running correctly.
- [x] Ensure the application logs are accessible and can be monitored.
- [x] The application should be scalable, allowing multiple instances to run concurrently if needed.
- [x] Include any necessary environment variables and configuration files required for the application to run.

---
## **Table view of requirements**
This section outlines the comprehensive requirements for the application to ensure it meets the objectives and functions as expected. The tasks listed below are essential for the successful completion of the Cyber Challenge:

| Task                                                                                                    |
|---------------------------------------------------------------------------------------------------------|
| Docker Compose setup to display the current user and directory                                          |
| Implement Endpoint 1: **GET /denylist**                                                                 |
| Implement Endpoint 2: **POST /allowlist**                                                               |
| Implement Endpoint 3: **GET /allowlist**                                                                |
| Implement persistent storage using a database                                                           |
| API provides fresh data, even in times of change                                                        |
| Add an Application Load Balancer (e.g., Traefik, Nginx) to enable access on port 80                     |
| Add HTTPS (port 443) with a certificate and redirect traffic from port 80 to 443                        |
| API documentation (endpoint, request, and response details)                                             |
| Code documentation (file descriptions and instructions to run the project)                              |
| Containerize the application using Docker                                                               |
| Include a `Dockerfile` defining the application's environment, dependencies, and entry point            |
| Include a `docker-compose.yml` file configuring services, networks, and volumes                         |
| Ensure the application can be built and run using a single `docker-compose up` command                  |
| Ensure the application runs in both local development and production environments                       |
| Provide clear instructions on how to build and run the Docker containers                                |
| Include health checks in the Docker configuration to ensure the application is running correctly        |
| Ensure application logs are accessible and can be monitored                                             |
| Ensure the application is scalable, allowing multiple instances to run concurrently if needed           |
| Include any necessary environment variables and configuration files required for the application to run |

---
## **Deliverables**

At the end of the challenge, teams must submit:

1. [x] A **working REST API** that meets all outlined requirements.
2. [x] A **Dockerfile** and **docker-compose.yml** file for deployment.
3. [x] Successfully passing tests in `tests/<tests_file>`.
4. [x] API documentation detailing endpoints, requests, and responses.
5. [x] Code documentation including file descriptions and instructions to run the project.
6. [x] Clear instructions on how to build and run the Docker containers.
7. [x] Configuration files and environment variables required for the application to run.
8. [x] Evidence of health checks in the Docker configuration to ensure the application is running correctly.
9. [x] Logs demonstrating the application is accessible and can be monitored.
10. [x] Proof of scalability, showing multiple instances can run concurrently if needed.

---
