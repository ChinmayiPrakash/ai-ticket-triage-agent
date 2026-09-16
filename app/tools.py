def check_application_status(application: str):
    """Checks whether an application is currently available."""

    application_status = {
        "SAP": "DOWN",
        "Salesforce": "UP",
        "Payroll": "UP"
    }

    status = application_status.get(application, "UNKNOWN")

    return {
        "application": application,
        "status": status
    }