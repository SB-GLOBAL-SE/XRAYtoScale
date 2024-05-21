import requests

# Define the GraphQL endpoint
url = "https://xray.cloud.getxray.app/api/v2/graphql"  # Replace with your actual endpoint

project = "XRAY"
# Define the variables for the querys
variables = {
    "jql": f"project = {project}",  # Replace with your JQL
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
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiIwZWM0MjhhMS0yNDcxLTNlZWMtODhjOS1mNDMwMDQyODg4MjgiLCJhY2NvdW50SWQiOiI2M2Y1MTc4NmZiM2FjNDAwM2ZhMmNhYTUiLCJpc1hlYSI6ZmFsc2UsImlhdCI6MTcxNjMwNTAwMCwiZXhwIjoxNzE2MzkxNDAwLCJhdWQiOiIwODA1QUNBQzJDNzg0NTYxQjg5RTFDQzFCN0Y3NUUwNSIsImlzcyI6ImNvbS54cGFuZGl0LnBsdWdpbnMueHJheSIsInN1YiI6IjA4MDVBQ0FDMkM3ODQ1NjFCODlFMUNDMUI3Rjc1RTA1In0.ZHf5zNWz9BfHhYGbTboEIH4GmftQddLWR7oSx_KmUDk"}


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

url = "https://xray.cloud.getxray.app/api/v2/graphql"  # Replace with your actual endpoint

# Define the query
query = """
{
    getTestPlans(limit: 100) {
        total
        start
        limit
        results {
            jira(fields: ["summary", "description"])
            issueId
            testExecutions(limit: 100) {
                total
                start
                limit
    
                results {
                    issueId
                    testRuns(limit: 100 ) {
                        total
                        limit
                        start
                        results {
                            id
                            status {
                                name
                                color
                                description
                            }
                            test {
                                issueId
                                jira(fields: ["summary", "description"])
                            }
                            
                        }
                    
                }
                    
                }         
            }
        }
    }
}
"""


# Define the variables for the query
variables = {
    "jql": f"project = {project}",  # Replace with your JQL
    #"issueIds": None,  # Replace with issue IDs if needed
    "projectId": "10002",  # Replace with your project ID
    "testType": "Test",  # Replace with test type if needed
    #"modifiedSince": None,  # Replace with modified date if needed
    "limit": 10,  # Replace with desired limit (max 100)
    "start": 0,  # Replace with desired start index
    "folder": None  # Replace with folder information if needed
}

# Set headers, including authentication if required
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiIwZWM0MjhhMS0yNDcxLTNlZWMtODhjOS1mNDMwMDQyODg4MjgiLCJhY2NvdW50SWQiOiI2M2Y1MTc4NmZiM2FjNDAwM2ZhMmNhYTUiLCJpc1hlYSI6ZmFsc2UsImlhdCI6MTcxNjMwNTAwMCwiZXhwIjoxNzE2MzkxNDAwLCJhdWQiOiIwODA1QUNBQzJDNzg0NTYxQjg5RTFDQzFCN0Y3NUUwNSIsImlzcyI6ImNvbS54cGFuZGl0LnBsdWdpbnMueHJheSIsInN1YiI6IjA4MDVBQ0FDMkM3ODQ1NjFCODlFMUNDMUI3Rjc1RTA1In0.ZHf5zNWz9BfHhYGbTboEIH4GmftQddLWR7oSx_KmUDk"}
# Make the request
response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)



# Parse the response
if response.status_code == 200:
    response = response.json()
    #print(response)
else:
    print(f"Query failed to run by returning code of {response.status_code}. {response.text}")

formatted_response = []
plan_executions = {}

for plan in response['data']['getTestPlans']['results']:
    plan_name = plan['jira']['summary']
    if plan_name not in plan_executions:
        plan_executions[plan_name] = {
            'summary': plan_name,
            'testExecutions': {
                'testRuns': {
                    'status': []
                }
            }
        }

    for execution in plan['testExecutions']['results']:
        for run in execution['testRuns']['results']:
            status_entry = {
                'name': run['status']['name'],
                'description': run['status']['description'],
                'issueId': run['test']['issueId']
            }
            if plan_name == 'Multiplan':
                plan_executions[plan_name]['testExecutions']['testRuns']['status'] = status_entry
            else:
                plan_executions[plan_name]['testExecutions']['testRuns']['status'].append(status_entry)

formatted_response = list(plan_executions.values())


#print(formatted_response)
#Get Key from updated Xray transformed data, so we have test case key to update results to when submitting POST exeuctions

key_lookup = {item['XrayTestID']: item['key'] for item in updated_XRAYtransformed_data}

# Update formatted_response with the corresponding key values
for plan in formatted_response:
    if isinstance(plan['testExecutions']['testRuns']['status'], dict):
        issue_id = plan['testExecutions']['testRuns']['status']['issueId']
        if issue_id in key_lookup:
            plan['testExecutions']['testRuns']['status']['key'] = key_lookup[issue_id]
    elif isinstance(plan['testExecutions']['testRuns']['status'], list):
        for status in plan['testExecutions']['testRuns']['status']:
            issue_id = status['issueId']
            if issue_id in key_lookup:
                status['key'] = key_lookup[issue_id]


for item in formatted_response:
    summary = item['summary']
    
    cyclePayload = {
        "projectKey" : project,
        "name" : summary,
    }

    cycleUrl = "https://api.zephyrscale.smartbear.com/v2/testcycles"
    default_headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb250ZXh0Ijp7ImJhc2VVcmwiOiJodHRwczovL21hdHRiNDcwMC5hdGxhc3NpYW4ubmV0IiwidXNlciI6eyJhY2NvdW50SWQiOiI2M2Y1MTc4NmZiM2FjNDAwM2ZhMmNhYTUifX0sImlzcyI6ImNvbS5rYW5vYWgudGVzdC1tYW5hZ2VyIiwic3ViIjoiMGVjNDI4YTEtMjQ3MS0zZWVjLTg4YzktZjQzMDA0Mjg4ODI4IiwiZXhwIjoxNzQ3NzUzMjkwLCJpYXQiOjE3MTYyMTcyOTB9.ohRcxiCS0lxVgIznaifxb9U8qIOBInzfwTd6TVcI9UU'}
    response = requests.post(cycleUrl, json=cyclePayload, headers=default_headers)
    if response.status_code == 201:
        response_data = response.json()  # Parse JSON response
        cycleKey = response_data.get("key")
        print({"Key": cycleKey})
        #####POST executions for that cycle (iterate down formatted_response)
        #print(formatted_response)
        def store_executions_for_summary(formatted_response, target_summary):
            executions_for_summary = []
            for entry in formatted_response:
                if entry['summary'] == target_summary:
                    test_executions = entry['testExecutions']['testRuns']['status']
                    if isinstance(test_executions, list):
                        executions_for_summary.extend(test_executions)
                    else:
                        executions_for_summary.append(test_executions)
            return executions_for_summary

        # Function to create payloads from summary executions
        def create_payloads(summary_executions, project_key, cycle_key):
            payloads = []
            for execution in summary_executions:
                if 'key' in execution:  # Ensure 'key' exists to avoid KeyError
                    payload = {
                        "projectKey": project_key,
                        "testCaseKey": execution['key'],
                        "testCycleKey": cycle_key,
                        "statusName": execution['name'],
                        "comment" : execution['description'],
                    }
                    payloads.append(payload)

                    
            return payloads

        # Example usage
        target_summary = summary  
        project_key = project
        cycle_key = cycleKey  # Replace with actual cycle key

        summary_executions = store_executions_for_summary(formatted_response, target_summary)
        payloads = create_payloads(summary_executions, project_key, cycle_key)

        # API URL and headers
        executions_url = "https://api.zephyrscale.smartbear.com/v2/testexecutions"
        default_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb250ZXh0Ijp7ImJhc2VVcmwiOiJodHRwczovL21hdHRiNDcwMC5hdGxhc3NpYW4ubmV0IiwidXNlciI6eyJhY2NvdW50SWQiOiI2M2Y1MTc4NmZiM2FjNDAwM2ZhMmNhYTUifX0sImlzcyI6ImNvbS5rYW5vYWgudGVzdC1tYW5hZ2VyIiwic3ViIjoiMGVjNDI4YTEtMjQ3MS0zZWVjLTg4YzktZjQzMDA0Mjg4ODI4IiwiZXhwIjoxNzQ3NzUzMjkwLCJpYXQiOjE3MTYyMTcyOTB9.ohRcxiCS0lxVgIznaifxb9U8qIOBInzfwTd6TVcI9UU'
        }

        # Sending the payloads to the API
        for cycle_payload in payloads:
            response = requests.post(executions_url, json=cycle_payload, headers=default_headers)
            if response.status_code == 201:
                print("Executions were successful")
            else:
                print(response.content)
    else:
        print("Error")
        print(response.text)
