# POC Script for XRay to Zephyr Scale Cloud-to-Cloud Migrations

The POC script is designed to highlight possibilities, it is not a production-ready script. The POC script is designed specifically for Cloud-to-Cloud migrations, on the same instance. However, it can also be adapted to support migrations from XRay to Zephyr Scale in Data Center-to-Data Center or Data Center-to-Cloud environments.

<!-- TOC -->

* [POC Script for Cloud-to-Cloud Migrations](#poc-script-for-cloud-to-cloud-migrations)
    * [Disclaimer](#disclaimer)
    * [Key Points](#key-points)
    * [High-Level Process](#high-level-process)
        * [Test Case Data](#test-case-data)
        * [Test Cycle Data](#test-cycle-data)
        * [Test Execution Data](#test-execution-data)
    * [Steps to Run the Script](#steps-to-run-the-script)
      
      
<!-- TOC -->

## Disclaimer
The POC script is designed to highlight possibilities and is not a production-ready script. This script is specifically for Cloud-to-Cloud migrations but can also be adapted for migrations from XRay to Zephyr Scale in Data Center-to-Data Center or Data Center-to-Cloud environments.

## Key Points
- **XRay APIs**: XRay has both REST and GraphQL endpoints.
  - Investigated Jira API (using JQL) but found it insufficient as it does not maintain associations between XRay entities.
  - XRay Cloud REST API has limitations.
- **GraphQL API**: We MUST use GraphQL API to GET data.
  - Documentation: [XRay GraphQL API](https://us.xray.cloud.getxray.app/doc/graphql/index.html)
  - Individual GraphQL calls cannot request more than 10,000 total items.
- **Attachments**: No attachments for the POC script. Users can query files from XRay using the GraphQL API.
- **Customization**: This script is not out-of-the-box and will require modifications by clients/partners to achieve an ideal migration.
- **Testing**: Call to test will be difficult unless all dependencies are already created.

## High-Level Process
There are three core test entities: **Test Case**, **Test Cycle**, and **Test Execution**.

### Test Case Data
- Combine XRay’s Test Cases and Preconditions into a Zephyr Scale test case (Precondition is a field in a Zephyr Scale test case).
- **Schema Endpoints**:
  - `getTests`
  - `getPreconditions`

### Test Cycle Data
- 1-to-1 correspondence between XRay Test Plan and Zephyr Scale Test Cycle.
- **Schema Endpoints**:
  - `getTestPlans`

### Test Execution Data
- 1-to-1 correspondence between XRay Test Run and Zephyr Scale Test Execution.
- The XRay Test Executions do not contain the pass/fail information; this information is obtained from TestRuns.
- **Schema Endpoints**:
  - `getTestExecutions`
  - `getTestRuns`

 
 ## Steps to Run the Script
 - **Replace information in app.prop file**
    - `Jira_api_token = <Jira_API_Token>`
    - `XRAY_Bearer_Token = <XRay_API_Token>`
    - `Scale_Bearer_Token = <Zephyr_Scale_API_Token>`
    - `project = <Jira_project>`
    - `projectKey = <Jira_project_Key>`
    - `projectID = <Jira_project_ID>`
    - `Jira_base_url = <host>/`
    - `email = <jira-User_email>` `
  
    - To get XRay Bearer Token, you must send a cURL based on XRay clientSecret and clientID
    - `curl -H "Content-Type: application/json" -X POST --data '{"client_id": "clientID from XRay","client_secret": "client Secret from XRay"}' https://xray.cloud.getxray.app/api/v1/authenticate`
  
    - After you have replaced all values in the app.properties file, run with the local python interpreter. IE python3 migrations.py
