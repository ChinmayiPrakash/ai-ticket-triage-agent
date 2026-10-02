def check_application_status(application: str):
    """Checks whether an application is currently available."""
    # This dictionary is pretending to be an external monitoring system:
    #Later this could be replaced by calling monitoring API to SAP, Salesforce and Payroll
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