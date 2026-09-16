from app.classifier import classify_ticket  # Imports the AI classifier
test_cases = [
    ("The invoice automation is unable to connect to SAP. Today's invoices are blocked, but the finance team confirmed they can wait until tomorrow.", "HIGH"),

    ("A user requested a new search option in the automation dashboard.", "LOW"),

    ("The monthly compliance report automation failed. The report must be submitted to the regulator within 25 minutes.", "CRITICAL"),

    ("One purchase order failed because an attachment had an unsupported format. The remaining purchase orders processed successfully, but the failed item needs manual correction.", "MEDIUM"),

    ("The bot encountered a database timeout, automatically retried, and completed the transaction successfully. No manual action is required.", "LOW"),

    ("The claims bot cannot access the claims application. Today's processing is stopped and an operator must investigate, but there is no SLA deadline today.", "HIGH"),

    ("A password will expire in 10 days. The automation is currently running normally.", "LOW"),

    ("The payroll bot cannot connect to the payroll system. Payroll must be submitted within 15 minutes and employees may not be paid on time.", "CRITICAL"),

    ("One customer record failed because a required field was missing. The bot processed all other records, but someone must correct and reprocess the failed record.", "MEDIUM"),

    ("The operations team requested that the bot email a weekly performance summary.", "LOW"),

    ("The order-processing bot stopped because the ERP application is unavailable. Hundreds of orders are accumulating and must be processed within the next 30 minutes.", "CRITICAL"),

    ("The reporting bot failed while generating a weekly report. An analyst generated the report manually, but the automation issue still needs investigation before next week's run.", "MEDIUM"),

    ("The Salesforce automation cannot authenticate because its production credential expired. Customer onboarding is currently blocked and requires intervention, but there is no immediate deadline.", "HIGH"),

    ("The bot detected a temporary API error and successfully recovered after its configured retry. All records were processed.", "LOW"),

    ("A regulatory submission bot is failing authentication. The filing deadline is in 20 minutes and the submission cannot currently be completed manually.", "CRITICAL"),

    ("One invoice was routed to the exception queue because its invoice number could not be extracted. A user needs to review the document, but normal invoice processing continues.", "MEDIUM"),

    ("The inventory automation has stopped because the warehouse API is unavailable. Inventory updates are currently blocked, but the business confirmed the issue can be resolved later today.", "HIGH"),

    ("The bot completed its run, but one output file contains incorrect formatting. A support analyst needs to fix the file before tomorrow.", "MEDIUM"),

    ("The payment automation cannot access the banking portal. Payments are blocked and require technical intervention, but the payment deadline is two days away.", "HIGH"),

    ("The production billing automation failed across all business units. Thousands of bills are blocked and today's billing deadline is in 10 minutes.", "CRITICAL"),
]
correct_by_severity = {
    "LOW": 0,
    "MEDIUM": 0,
    "HIGH": 0,
    "CRITICAL": 0
}

passed = 0
failed = 0
total = len(test_cases)

for ticket_text, expected_severity in test_cases:

    result = classify_ticket(ticket_text)

    actual_severity = result.severity.value

    print(f"Expected: {expected_severity}")
    print(f"Actual:   {actual_severity}")

    if actual_severity == expected_severity:
        passed += 1
        correct_by_severity[expected_severity] += 1
    else:
        failed += 1

    print(f"Passed:   {actual_severity == expected_severity}")
    print("-" * 40)

accuracy = (passed / total) * 100

print("Evaluation Results")
print("------------------")
print(f"Total:    {total}")
print(f"Passed:   {passed}")
print(f"Failed:   {failed}")
print(f"Accuracy: {accuracy}%")

print(f"LOW COUNT: {correct_by_severity['LOW']}")
print(f"MEDIUM COUNT: {correct_by_severity['MEDIUM']}")
print(f"HIGH COUNT: {correct_by_severity['HIGH']}")
print(f"CRITICAL COUNT: {correct_by_severity['CRITICAL']}")