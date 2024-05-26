## HOSPITAL MANAGEMENT SYSTEM (HMS)
This system is strictly for employees of a hospital network.

# HMS Database
The database system should be able to query basic information about the hospital employees such as staff ID number, name, address, and phone number. 
The system should be able to query information about room and patient assignments for each employee of a department. 
The database should be able to store patient information for use by employees such as patient ID, name, location, room number, assigned staff, prescriptions, and invoices to generate reports. 
The database to be developed will consist of the following tables:
* Hospital
* Department
* Doctor
* Staff
* Patient
* Room
* Prescription
* Invoice
* Appointment
* Pharmacy

## Specific User’s Requirements

User requirements refers to the needs of the user and the activities that the user will be able to perform once the database is made. It basically entails the things that users will be able to do with the database management system. For our hospital database, the staff are the users and below are some of the tasks that will be performed by the staff of the hospital:

* Patient registration
* Patient check out
* Generation of patient information reports
* Availability of beds
* Storage of mandatory patient information
* Updating patient information

## Non-functional requirements help in understanding how the database system should behave. 
Below are some of the most important non-functional requirements for the hospital database:

* Security: 
    Security is very important in a hospital database as we do not want the people working in the hospital to alter the information in the database. Thus, administrative rights or appropriate permission should be set such that the staff or any other person working in the hospital only is able to add data and not change it.

* Performance: 
    The response time of the system being able to create/change records should be less, and the database system should work without slowing down.

* Maintainability: 
    Having some kind of backup is extremely important in a hospital database as patients are actively visiting the hospital and it is most likely to be busy.

* Reliability: 
    The hospital database system should be available all the time.


## Business Rules
Business rules depict the business arrangements that apply to the information stored on an organization’s database. They reflect how a business sees the utilization of the data it has. The business rules assigned for the hospitable database are:

* Hospital table should be the main table in the hospital management schema, and the Department table should be the next important table, so the Department table contains the Hospital Id foreign key which is the primary key in the Hospital table.
* The date columns in the appointment table and the room table must flow the same data pattern such as (YYYY/MM/DD).
* The cost in the invoice table and prescription must be in Dollar.
* The date columns cannot contain null values.
* Each hospital must have its own unique identification number.
* Each hospital has several departments which must be identified with a unique identification number.
* Each doctor or staff member will be given their own unique identification number.
* A hospital has departments according to medical needs.
* A doctor or staff member will be assigned to only one department.
* A doctor may be assigned to multiple patients.
* A patient may schedule an appointment to be seen by a doctor.
* A patient may be admitted to the hospital when necessary.
* If a patient is admitted, a staff member will be assigned to the patient’s room.
* If admitted, a patient will be assigned to only one room.
* Each room will be assigned to only one patient.
* A patient will be given an invoice for any services received at the providing hospital.
* If necessary, a patient may be prescribed medication.
* Prescription requests will be sent to a pharmacy specified by the patient.

Entity-Relationship Diagram (ERD)

An entity relationship diagram is a graphical representation of the entities and relationships in the database structure. Its purpose is to provide a conceptually simplistic picture to the complex design of the database itself. Data is collected and stored for each entity while relationships describe the associations between the data. The ERD of the Hospital Network begins with the main table Hospital, then Department, where it branches off into Doctor and Staff, before leading into Patient through connections of Room and Appointment. The Patient Table makes additional connections by branching into Invoice, Pharmacy, and Prescription.
![DataBase Schema](https://miro.medium.com/v2/resize:fit:828/format:webp/1*-CFps3Yl_t-HQFlrOoTtGQ.png)


## Creating Database with postgres

1. Type `psql --username <username>` in your terminal to create a user in postgres. Where <username> should a or the username. Try psql -U postgres and enter your password in your terminal

2. Type the followinfg commands in the psql console.
```sql
CREATE DATABASE hms;
CREATE USER nelso WITH PASSWORD 'nelso';
ALTER ROLE nelso SET client_encoding TO 'utf8';
ALTER ROLE nelso SET default_transaction_isolation TO 'read committed';
ALTER ROLE nelso SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE hms TO nelso;

ALTER DATABASE hms OWNER TO nelso;
GRANT ALL ON SCHEMA public TO nelso;
GRANT ALL ON SCHEMA public TO public;
```


### Monitoring Tasks
We will be using celery to distribute the task to brokers such as redis and flower to monitor the tasks

* Install celery by using `pip install celery[redis]` in the terminal

* Add  'celery' to INSTALLED_APPS in settings.py of your project

* Create a celery.py file in the directory which settings.py can be found

* Paste the following code in celery.py file
    ```python
    from __future__ import absolute_import, unicode_literals
    import os
    from celery import Celery
    from django.conf import settings

    # Set the default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

    app = Celery('backend')  # Replace 'your_project' with your project's name.

    # Configure Celery using settings from Django settings.py.
    app.config_from_object('django.conf:settings', namespace='CELERY')

    # Load tasks from all registered Django app configs.
    app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

    @app.task(bind=True)
    def debug_task(self):
        print(f"Request: {self.request!r}")

    ``` 
Replace the text 'backend' with the name of your project

* Paste the following code in the __init__.py file which is in the same directory as settigs.py
    ```python
    from .celery import app as celery_app

    __all__ = ("celery_app",)
    ```
* Download redis and click on redis.cli to start redis

* Add these lines of code in your settings.py
    ```python
    # set the celery broker url 
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    
    # set the celery result backend 
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    
    # set the celery timezone 
    CELERY_TIMEZONE = 'UTC'
    ```

* Run the django server `python manage.py runserver` in your terminal and also in your root directory of the project

* Run `celery -A backend.celery worker --pool=solo -l info` in your terminal and also in the root directory of the project 

* Install flower by using `pip install flower`

* Run `celery -A backend flower  worker --loglevel=info` in your terminal and also in the root directory of the project 
