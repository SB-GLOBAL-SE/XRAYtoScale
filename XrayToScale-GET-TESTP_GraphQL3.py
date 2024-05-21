import requests

# Define the GraphQL endpoint
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
    "jql": "project = XRAY",  # Replace with your JQL
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

for plan in response['data']['getTestPlans']['results']:
    executions = []
    for execution in plan['testExecutions']['results']:
        for run in execution['testRuns']['results']:
            executions.append({
                'name': run['status']['name'],
                'description': run['status']['description'],
                'issueId': run['test']['issueId']
            })
    
    formatted_response.append({
        'summary': plan['jira']['summary'],
        'testExecutions': {
            'testRuns': {
                'status': executions if plan['jira']['summary'] == 'TP' else executions[0]  # Group all for TP, single for others
            }
        }
    })

print(formatted_response)
