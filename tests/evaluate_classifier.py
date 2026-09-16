from app.classifier import classify_ticket  # Imports the AI classifier

test_cases = [
    ("A reporting bot failed overnight, but the report is only needed next week.", "MEDIUM"),

    ("The payroll bot failed, but the payroll team completed the process manually before the deadline.", "MEDIUM"),

    ("SAP is intermittently slow and one bot required a manual restart. No business deadline is impacted.", "MEDIUM"),

    ("A bot failed to upload a regulatory filing that must be submitted within 20 minutes.", "CRITICAL"),

    ("Users requested an option to export dashboard results to Excel.", "LOW"),

    ("The invoice bot failed for one invoice because the PDF was corrupted. All other invoices processed successfully.", "MEDIUM"),

    ("The claims automation cannot connect to the API. Claims are accumulating, but the SLA deadline is tomorrow.", "HIGH"),

    ("The claims automation cannot connect to the API. The SLA deadline is in 15 minutes and hundreds of claims are blocked.", "CRITICAL"),

    ("A Salesforce credential will expire in 5 days, but the bot is currently running successfully.", "LOW"),

    ("The bot encountered a temporary network error, automatically retried, and completed successfully without intervention.", "LOW"),
]

passed = 0
failed = 0
total = len(test_cases)

for ticket_text, expected_severity in test_cases:

    result = classify_ticket(ticket_text)

    actual_severity = result.severity.value

    print(f"Expected: {expected_severity}")
    print(f"Actual:   {actual_severity}")

    if actual_severity == expected_severity:
        passed = passed + 1
    else:
        failed = failed + 1

    print(f"Passed:   {actual_severity == expected_severity}")
    print("-" * 40)

accuracy = (passed / total) * 100

print("Evaluation Results")
print("------------------")
print(f"Total:    {total}")
print(f"Passed:   {passed}")
print(f"Failed:   {failed}")
print(f"Accuracy: {accuracy}%")