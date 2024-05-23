import requests

####################################
#Must Authenticate first with XRAY clientID and clientSecret to get Bearer Token
# curl -H "Content-Type: application/json" -X POST --data '{
#"client_id": "0805ACAC2C784561B89E1CC1B7F75E05","client_secret": "9565261606185b66b6e2bb76be6698101d1c9bff041c9bba7bf92a7b7a37328f" }'
# https://xray.cloud.getxray.app/api/v1/authenticate

XRAY_Bearer_Token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiIwZWM0MjhhMS0yNDcxLTNlZWMtODhjOS1mNDMwMDQyODg4MjgiLCJhY2NvdW50SWQiOiI2M2Y1MTc4NmZiM2FjNDAwM2ZhMmNhYTUiLCJpc1hlYSI6ZmFsc2UsImlhdCI6MTcxNjM5OTMzMSwiZXhwIjoxNzE2NDg1NzMxLCJhdWQiOiIwODA1QUNBQzJDNzg0NTYxQjg5RTFDQzFCN0Y3NUUwNSIsImlzcyI6ImNvbS54cGFuZGl0LnBsdWdpbnMueHJheSIsInN1YiI6IjA4MDVBQ0FDMkM3ODQ1NjFCODlFMUNDMUI3Rjc1RTA1In0.5qx0sFGCnWanOo7O6eMmFjCk9y9hW6aDfJv20OzlWHw"

Scale_Bearer_Token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb250ZXh0Ijp7ImJhc2VVcmwiOiJodHRwczovL21hdHRiNDcwMC5hdGxhc3NpYW4ubmV0IiwidXNlciI6eyJhY2NvdW50SWQiOiI2M2Y1MTc4NmZiM2FjNDAwM2ZhMmNhYTUifX0sImlzcyI6ImNvbS5rYW5vYWgudGVzdC1tYW5hZ2VyIiwic3ViIjoiMGVjNDI4YTEtMjQ3MS0zZWVjLTg4YzktZjQzMDA0Mjg4ODI4IiwiZXhwIjoxNzQ3NzUzMjkwLCJpYXQiOjE3MTYyMTcyOTB9.ohRcxiCS0lxVgIznaifxb9U8qIOBInzfwTd6TVcI9UU"
project = "2Xray"
projectKey = "XRRR"
projectId = "10003"

# Define the GraphQL endpoint
url = "https://xray.cloud.getxray.app/api/v2/graphql"  # Replace with your actual endpoint

# Define the variables for the querys
variables = {
    "jql": f"project = {project}",  # Replace with your JQL
    "projectId": f"{projectId}",  # Replace with your project ID
    "testType": None,  # Replace with test type if needed
    "limit": 10,  # Replace with desired limit (max 100)
    "start": 0,  # Replace with desired start index
    "folder": None  # Replace with folder information if needed
}

# Define the query
query = """
query GetTests($limit: Int!, $start: Int, $jql: String, $projectId: String, $testType: TestTypeInput, $folder: FolderSearchInput) {
    getTests(limit: $limit, start: $start, jql: $jql, projectId: $projectId, testType: $testType, folder: $folder) {
        total
        start
        limit
        results {
            jira(fields: ["summary", "description"])
            issueId
            testType {
                name
                kind
            }
            steps {
                data
                action
                result
            }
            preconditions(limit: 100) {
                total
                start
                results {
                    jira(fields: ["summary", "description"])
                    issueId
                    definition

                }
            }
        }
    }
}
"""

# Set headers, including authentication if required
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {XRAY_Bearer_Token}"
}

# Make the request
response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)




# Parse the response
if response.status_code == 200:
    data = response.json()
    
else:
    print(f"Query failed to run by returning code of {response.status_code}. {response.text}")

TestCaseData = []

# Iterate over the test results
for test in data['data']['getTests']['results']:
    test_data = {
        'jira_summary': test['jira']['summary'],
        'jira_description': test['jira']['description'],
        'issue_id': test['issueId'],
        'steps': test['steps'],
        'preconditions': []
    }
    
    # Iterate over the preconditions in each test result
    for precondition in test['preconditions']['results']:
        precondition_data = {
            'precondition_issue_id': precondition['issueId'],
            'precondition_summary': precondition['jira']['summary'],
            'precondition_description': precondition['jira']['description']
        }
        test_data['preconditions'].append(precondition_data)
    
    TestCaseData.append(test_data)
    

   
    XRAYtransformed_data = []
print(TestCaseData)
for item in TestCaseData:
    
    transformed_item = {
        'Name': item['jira_summary'].replace('(', '').replace(')', '').strip(),
        'projectKey': projectKey,  # Replace with your actual project key if different
        'objective' : item['jira_description'].replace('(', '').replace(')', '').strip() if item['jira_description'] else '',
        'XrayTestID': item['issue_id'],
        'steps': item['steps'],
        'preconditions': item['preconditions']
    }
    
    XRAYtransformed_data.append(transformed_item)
    
# New list to store updated data with keys
updated_XRAYtransformed_data = []

# Track processed test case IDs to avoid duplicates
processed_test_case_ids = set()

for item in XRAYtransformed_data:
    projectKey = item.get("projectKey")
    name = item.get("Name")
    objective = item.get("objective")
    issue_id = item.get("XrayTestID")  # Ensure this is the unique identifier
    
    # Check if the test case ID has been processed
    if issue_id in processed_test_case_ids:
        continue  # Skip duplicate test cases
    
    # Combine preconditions into a single string for payload
    preconditions = item.get("preconditions", [])
    precondition_text = ""
    if preconditions:
        precondition_text = '; '.join(
            f"{precondition['precondition_summary']}: {precondition['precondition_description']}"
            for precondition in preconditions
        )

    payload = {
        "projectKey": projectKey,
        "name": name,
        "objective": objective,
        "precondition": precondition_text
    }

    