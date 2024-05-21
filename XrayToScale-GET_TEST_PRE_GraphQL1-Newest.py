import requests

# Define the GraphQL endpoint
url = "https://xray.cloud.getxray.app/api/v2/graphql"  # Replace with your actual endpoint

project = "XRAY"
# Define the variables for the querys
variables = {
    "jql": "project = XRAY",  # Replace with your JQL
    "projectId": "10002",  # Replace with your project ID
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
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiIwZWM0MjhhMS0yNDcxLTNlZWMtODhjOS1mNDMwMDQyODg4MjgiLCJhY2NvdW50SWQiOiI2M2Y1MTc4NmZiM2FjNDAwM2ZhMmNhYTUiLCJpc1hlYSI6ZmFsc2UsImlhdCI6MTcxNjIwNzg3NywiZXhwIjoxNzE2Mjk0Mjc3LCJhdWQiOiIwODA1QUNBQzJDNzg0NTYxQjg5RTFDQzFCN0Y3NUUwNSIsImlzcyI6ImNvbS54cGFuZGl0LnBsdWdpbnMueHJheSIsInN1YiI6IjA4MDVBQ0FDMkM3ODQ1NjFCODlFMUNDMUI3Rjc1RTA1In0.bueS1OlOxRiqdWumLJnBtmOuJeeJu2TZbgmyYvRPt3o"
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
#print(TestCaseData)

   
    XRAYtransformed_data = []

for item in TestCaseData:
    
    transformed_item = {
        'Name': item['jira_summary'].replace('(', '').replace(')', '').strip(),
        'projectKey': 'XRAY',  # Replace with your actual project key if different
        'objective': item['jira_description'].replace('(', '').replace(')', '').strip(),
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
    default_headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb250ZXh0Ijp7ImJhc2VVcmwiOiJodHRwczovL21hdHRiNDcwMC5hdGxhc3NpYW4ubmV0IiwidXNlciI6eyJhY2NvdW50SWQiOiI2M2Y1MTc4NmZiM2FjNDAwM2ZhMmNhYTUifX0sImlzcyI6ImNvbS5rYW5vYWgudGVzdC1tYW5hZ2VyIiwic3ViIjoiMGVjNDI4YTEtMjQ3MS0zZWVjLTg4YzktZjQzMDA0Mjg4ODI4IiwiZXhwIjoxNzQ3NzUzMjkwLCJpYXQiOjE3MTYyMTcyOTB9.ohRcxiCS0lxVgIznaifxb9U8qIOBInzfwTd6TVcI9UU'

    }
    testcase_url = "https://api.zephyrscale.smartbear.com/v2/testcases"
    # Send POST request
    response = requests.post(testcase_url, json=payload, headers=default_headers)
    
    # Print the response status code and JSON response
    if response.status_code == 201:
        response_data = response.json()  # Parse JSON response
        key = response_data.get("key")
        new_item = item.copy()
        new_item["key"] = key
        updated_XRAYtransformed_data.append(new_item)
        #print({"Key": key})
        # Add the test case ID to the set of processed test cases
        processed_test_case_ids.add(issue_id)
    else:
        print("Error")
        print(response.content)

# Print updated XRAYtransformed_data with keys
#print(updated_XRAYtransformed_data)
        
    
#Send Request to POST test Steps:
ScaleSteps = {}

for item in updated_XRAYtransformed_data:
    default_headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb250ZXh0Ijp7ImJhc2VVcmwiOiJodHRwczovL21hdHRiNDcwMC5hdGxhc3NpYW4ubmV0IiwidXNlciI6eyJhY2NvdW50SWQiOiI2M2Y1MTc4NmZiM2FjNDAwM2ZhMmNhYTUifX0sImlzcyI6ImNvbS5rYW5vYWgudGVzdC1tYW5hZ2VyIiwic3ViIjoiMGVjNDI4YTEtMjQ3MS0zZWVjLTg4YzktZjQzMDA0Mjg4ODI4IiwiZXhwIjoxNzQ3NzUzMjkwLCJpYXQiOjE3MTYyMTcyOTB9.ohRcxiCS0lxVgIznaifxb9U8qIOBInzfwTd6TVcI9UU'}
    key = item.get('key')
    testCaseKey=key
    steps = item.get('steps')
    formatted_steps = [
        {
            'inline': {
                'testData': step.get('data') or '',
                'description': step.get('action') or '',
                'expectedResult': step.get('result') or ''
            }
        }
        for step in steps
    ]
    ScaleSteps[key] = formatted_steps
    
    stepsPayload = {
        "mode": "OVERWRITE",
        "items": ScaleSteps[testCaseKey]

    }
    
    testcase_url = f"https://api.zephyrscale.smartbear.com/v2/testcases/{testCaseKey}/teststeps"
 
    response = requests.post(testcase_url, json=stepsPayload, headers=default_headers)
    if response.status_code == 201:
        print(f"Steps posted successfully for {key}")
    else:
        error_data = response.json()
        if "Test Data, Description and Expected Result are empty" in error_data.get("message", ""):
            print(f"No data in test steps, but successfyl")
        else:
            print(f"Unexpected error for {key}: {response.status_code}")
            print(response.content)