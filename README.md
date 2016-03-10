# phil
## Opinionated Web Phramework for Python


### [Project is still under construction]


This project contains bolierplate, structure, and integrations for python web projects that use the following stack:

- WSGI (via nginx + gunicorn)
- Werkzeug
- Mustache templates
- MySQL
- Redis
- Memcache

*The goal of this project is not to make a flexible web framework that works for most people, but rather, to create a framework that saves a lot of time for people who agree that this exact technology stack is reasonable for their needs.*

### Features:
- Encourages use of DAOs instead of an ORM (I like to write my own queries thank you)
- Borrows concepts from DDD and splits the model layer into 3 sub-layers: Domain, Data Access, and Services
- Uses logic-less Mustache templates. This provides 2 advantages: 
  1. All data must be computed before reaching the view (ensures sanity)
  2. All templates can be rendered client-side via the Mustache Javascript library
- Built-in MySQL federation based on Instagram-like id -> shard mappings

### Usage Guidlines and Definitions:
- Controllers should focus on HTTP details. They handle web requests, preform operations via model services, and construct an HTTP response. Controllers should be stateless.
- Model Services perform high-level tasks by requesting appropriate Domain Objects from a DAO and calling operations on them.  Requests into your application that aren't from the web (like offline tasks or command line scripts) should call Model Services directly. Model Services should be stateless.
- Domain Objects encapsulate business logic and state (the meat and potatoes)
- DAOs provide an application-level interface to the database and factory methods for creating new Domain Objects. They also act as a repository for domain object.
- Views are simply mustache templates




