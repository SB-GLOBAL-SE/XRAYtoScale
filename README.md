Disclaimer:


The POC script is designed to highlight possibilities, it is not a production ready script.

The POC script is designed specifically for Cloud-to-Cloud migrations. However, it can also be adapted to support migrations from XRay to Zephyr Scale in Data Center-to-Data Center or Data Center-to-Cloud environments

XRay has both REST and GraphQL endpoint

Investigated Jira API (Using JQL), not sufficient, does not keep associating between XRay entities.

XRay Cloud REST API is limited

We MUST use GraphQL API https://us.xray.cloud.getxray.app/doc/graphql/index.html to GET data

Individual GraphQL calls cannot request more than 10,000 total item

No attachments for POC Script, though users can query the file from XRay using GraphQL API.

This script is not out of the box, it will require modifications by clients/partners to promote an ideal migration.

Call to test will be difficult unless we can guarantee all dependencies were already created.





High Level Process: 


There are three core test entities: Test Case, Test Cycle and Test Execution

We receive the following information from the XRay API:

Test Case Data: Combine XRay’s Test Cases + Precondition to Zephyr Scale test case (Precondition is a field in a Zephyr Scale test case)

Schema

getTests

getPreconditions

Test Cycle Data: 1 to 1 correspondence between XRay Test Plan ant Zephyr Scale Test Cycle

Schema

getTestPlans

Test Execution Data: 1 to 1 correspondence between XRay Test Run and Zephyr Scale Test Execution. The XRay Test Executions do not contain the pass/fail information, and you get that information from TestRuns.

Schema

getTestExecutions

getTestRuns

