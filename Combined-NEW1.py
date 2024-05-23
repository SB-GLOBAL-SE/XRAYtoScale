import requests
from requests.auth import HTTPBasicAuth
import sys

####################################
#Must Authenticate first with XRAY clientID and clientSecret to get Bearer Token

#######
# curl -H "Content-Type: application/json" -X POST --data '{
#"client_id": "0805ACAC2C784561B89E1CC1B7F75E05","client_secret": "9565261606185b66b6e2bb76be6698101d1c9bff041c9bba7bf92a7b7a37328f" }'
# https://xray.cloud.getxray.app/api/v1/authenticate


################
###########Arguments 
if len(sys.argv) != 6:
    print("Usage: python3 combined.py <project> <project_key> <projectID> <jira_base_url> <email>")
    sys.exit(1)


Jira_api_token = ""
XRAY_Bearer_Token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiIwZWM0MjhhMS0yNDcxLTNlZWMtODhjOS1mNDMwMDQyODg4MjgiLCJhY2NvdW50SWQiOiI2M2Y1MTc4NmZiM2FjNDAwM2ZhMmNhYTUiLCJpc1hlYSI6ZmFsc2UsImlhdCI6MTcxNjQ4NjY5MSwiZXhwIjoxNzE2NTczMDkxLCJhdWQiOiIwODA1QUNBQzJDNzg0NTYxQjg5RTFDQzFCN0Y3NUUwNSIsImlzcyI6ImNvbS54cGFuZGl0LnBsdWdpbnMueHJheSIsInN1YiI6IjA4MDVBQ0FDMkM3ODQ1NjFCODlFMUNDMUI3Rjc1RTA1In0.jnliepxnHAZiowUsL9HZwWc8kbQcGHfnGmm-mpW8iLA"
Scale_Bearer_Token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb250ZXh0Ijp7ImJhc2VVcmwiOiJodHRwczovL21hdHRiNDcwMC5hdGxhc3NpYW4ubmV0IiwidXNlciI6eyJhY2NvdW50SWQiOiI2M2Y1MTc4NmZiM2FjNDAwM2ZhMmNhYTUifX0sImlzcyI6ImNvbS5rYW5vYWgudGVzdC1tYW5hZ2VyIiwic3ViIjoiMGVjNDI4YTEtMjQ3MS0zZWVjLTg4YzktZjQzMDA0Mjg4ODI4IiwiZXhwIjoxNzQ4MDIyMzQ2LCJpYXQiOjE3MTY0ODYzNDZ9.o_2-Q-1y_iVHmTBe61Uc8o125Z9XkAJ_pyBzXhVVu3U"
project = sys.argv[1]
projectKey = sys.argv[2]
projectID = sys.argv[3]
Jira_base_url = sys.argv[4]
email = sys.argv[5]



#####################################
########### Get total Test case count to determine iteration. 


jql = f'project={project} and issuetype=Test'
totalUrl = f'{Jira_base_url}/rest/api/3/search'
headers = {
    'Content-Type': 'application/json',
}
auth = HTTPBasicAuth(email, Jira_api_token)

# Parameters
params = {
    'jql': jql,
}
# Make the request
response = requests.get(totalUrl, headers=headers, auth=auth, params=params)
response=response.json()
total = response.get('total')
start = total
#####################################



# Default GraphQL XRAY endpoint
url = "https://xray.cloud.getxray.app/api/v2/graphql"  \

# Define the variables for the querys
variables = {
    "jql": f"project = {project}",  
    "projectId": f"{projectID}",  
    "testType": None,  
    "limit": 100,  
    "start": start,  
   # "folder": None  # determine if needed
}

#####################################
# Define the GraphQL query
#This query will retrieve tests, steps, and pre-conditions 
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

#####################################
###Send GraphQL request, by splitting the fetch of results into chunks of 100 test cases, per project
##
start_index = 0
all_results = []

# Fetch the results in chunks of 100
while start_index < total:
    variables['start'] = start_index
    response = requests.post(url, json={'query': query, 'variables': variables}, headers={
        "Authorization": f"Bearer {XRAY_Bearer_Token}",  # Replace with your actual token if needed
        "Content-Type": "application/json"
    })
    if response.status_code == 200:
        response_json = response.json()
        all_results.extend(response_json['data']['getTests']['results'])
        start_index += variables['limit']
    else:
        raise Exception(f"GraphQL query failed to run with status code {response.status_code} and response: {response.text}")
    
    #####################################
    #Log error message in textfile function
    def log_error_to_file(response, filename='error.txt'):
            print('Errors during execution - review error.txt')
            with open(filename, 'w') as file:
                if key:
                    file.write("Test Case Key:")
                    file.write(str(key))
                    file.write("\n if Test Case Key does NOT exists, the Test Case was not published.\n")
                if cycleKey:
                    file.write("\nTest Cycle Key:")
                    file.write(str(cycleKey))
                    file.write("\n if Test Cycle Key exists, the executions were NOT published for the associated Test Case and Cycle.\n")
                file.write("\nResponse Content:\n")
                file.write(response.content.decode('utf-8') + '\n')

    #####################################
    #Clear the error textfile at the beginning of the script run         
    with open('error.txt', 'w') as file:
        file.write('')

    if response.status_code == 200:
        data = response.json()

    else:
        print(f"Query failed to run by returning code of {response.status_code}. {response.text}")
        log_error_to_file(response)
    
####################################
#### Take XRAY Test Case and Precondition data and parse it

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

        
####################################
#### Combine XRAY Test Case and Precondition data
    
        XRAYtransformed_data = []

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

###############################
###### Transform the Test Case data so it is Zephyr Scale API acceptable 

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
############################
##### Create Test Cases in Zephyr Scale         
        default_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {Scale_Bearer_Token}'
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
            processed_test_case_ids.add(issue_id)

        else:
            log_error_to_file(response)
            
    #Send Request to POST test Steps:
    ScaleSteps = {}

###############################
###### Transform the Test Step data so it is Zephyr Scale API acceptable 

    for item in updated_XRAYtransformed_data:
        default_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {Scale_Bearer_Token}'
        }
        
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
        
############################
##### Update Test Cases with associated Test Steps in Zephyr Scale    

        testcase_url = f"https://api.zephyrscale.smartbear.com/v2/testcases/{testCaseKey}/teststeps"
    
        response = requests.post(testcase_url, json=stepsPayload, headers=default_headers)
        if response.status_code == 201:
            pass
        else:
            error_data = response.json()
            error_message = error_data.get("message", "").strip()
            
            # Debug statements to understand the content of error_message
            #print(f"Error message received: '{error_message}'")
            
            if ("Test Data, Description and Expected Result are empty" in error_message or 
                "Should contain at least 1 step and no more than 100" in error_message):
                pass
            else:
                print(f"Unexpected error for {key}: {response.status_code}")
                log_error_to_file(response)

    url = "https://xray.cloud.getxray.app/api/v2/graphql"  

#####################################
# Define the GraphQL query
#This query will retrieve Test Cycles, associated Test Executions and Runs from XRAY

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



    variables = {
        "jql": f"project = {project}",  
        "projectId": f"{projectID}", 
        "testType": "Test", 
        "limit": 100, 
        "start": 0,  
        "folder": None  
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {XRAY_Bearer_Token}"
    }

#####################################
###Send GraphQL request, to get Test Cycle and Execution information

    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

    if response.status_code == 200:
        response = response.json()
        
    else:
        print(f"Query failed to run by returning code of {response.status_code}. {response.text}")
        log_error_to_file(response)

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

    #Get Key from updated_XRAYtransformed_data, so we have test case key to update results to when submitting POST exeuctions

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
            "projectKey" : projectKey,
            "name" : summary,
        }

#####################################
###Create Test Cycle in Zephyr Scale

        cycleUrl = "https://api.zephyrscale.smartbear.com/v2/testcycles"
        default_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {Scale_Bearer_Token}'
        }
        
        
        response = requests.post(cycleUrl, json=cyclePayload, headers=default_headers)
        if response.status_code == 201:
            response_data = response.json()  # Parse JSON response
            cycleKey = response_data.get("key")
            
            #####POST executions for that cycle (iterate down formatted_response)

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
            def create_payloads(summary_executions, projectKey, cycle_key):
                payloads = []
                for execution in summary_executions:
                    if 'key' in execution:  # Ensure 'key' exists to avoid KeyError
                        payload = {
                            "projectKey": projectKey,
                            "testCaseKey": execution['key'],
                            "testCycleKey": cycle_key,
                            "statusName": execution['name'],
                            "comment" : execution['description'],
                        }

                        payloads.append(payload)

                        
                return payloads


            target_summary = summary  

            cycle_key = cycleKey  

            summary_executions = store_executions_for_summary(formatted_response, target_summary)
            payloads = create_payloads(summary_executions, projectKey, cycle_key)

#####################################
###Create Test Executions in associated Test Cyclels in Zephyr Scale

            executions_url = "https://api.zephyrscale.smartbear.com/v2/testexecutions"
            default_headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {Scale_Bearer_Token}'
                }

            # Sending the payloads to the API
            for cycle_payload in payloads:
                response = requests.post(executions_url, json=cycle_payload, headers=default_headers)
                if response.status_code == 201:
                    print("Executions were successful")
                else:
                    log_error_to_file(response)
        else:
            log_error_to_file(response)
