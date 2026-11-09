# Smartgarden-project
A Python-based IoT learning project that simulates garden sensor readings, sends telemetry to Microsoft Azure, processes events with Azure Functions, stores readings in Azure Blob Storage, and visualizes the data in a local Streamlit dashboard.
Project status: Learning / portfolio prototype. Sensor values are simulated; physical sensors are not required for the current implementation.

1. Project pipeline
Python sensor simulator
        |
        v
Azure IoT Hub
        |
        v
Azure Functions (event-driven processing)
        |
        v
Azure Blob Storage
        |
        v
Streamlit dashboard
        |
        v
Monitoring and low-moisture warning

Why each component is used
Component	Responsibility	Reason
Python simulator	Generates soil moisture, temperature and sunlight readings	Makes the system testable without physical hardware
Azure IoT Hub	Receives telemetry from the registered device	Provides a managed device-ingestion endpoint
Azure Functions	Processes incoming IoT events and validates required fields	Separates event processing from the device and dashboard
Azure Blob Storage	Stores processed readings as JSON blobs	Provides durable object storage for history and analysis
Streamlit	Displays latest readings, charts and reading history	Provides a lightweight way to inspect stored telemetry
Azure Monitor metrics / Function logs	Shows available execution activity and helps diagnose issues	Gives operational visibility into the cloud processing stage


2. Azure resources used
The project history identifies these resources:
Resource	Name
Resource group	smartmon--rg
IoT Hub	smartgarden-iothub
IoT Hub device identity	gardensensor1
Function App	smartgarden-function-2026
Storage account	smartgardenstore2026
Blob container	sensor-readings


3. Repository layout
SmartGardenMonitor/
├── sensor_simulator.py
├── dashboard.py
├── function_app/
│   ├── function_app.py
│   ├── host.json
│   ├── requirements.txt
│   └── .funcignore
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── docs/
    ├── Smart_Garden_Monitor_GitHub_Project_Documentation.docx
    └── screenshots/

4. Prerequisites
- Python installed on your computer.
- Visual Studio Code or another Python editor.
- An Azure subscription.
- An Azure IoT Hub with a device identity.
- An Azure Function App configured with the IoT Hub/Event Hubs-compatible trigger.
- An Azure Storage account and a blob container named sensor-readings.
- The project dependencies listed in the root and Function App requirements.txt files.
Exact package versions should be taken from the requirements files in this repository.

5. Local configuration
Create a local .env file in the project root. Do not commit it.

The simulator and dashboard use different credentials. Use the exact environment-variable names expected by the current Python source files.

Example template:
# Use the exact variable name read by sensor_simulator.py
IOTHUB_DEVICE_CONNECTION_STRING=

# Used by dashboard.py to read Blob Storage
AZURE_STORAGE_CONNECTION_STRING=
AZURE_STORAGE_CONTAINER=sensor-readings
The IoT Hub device connection string and the Storage connection string are different credentials. Never reuse one in place of the other.

If the Python files do not already load .env, install python-dotenv and call load_dotenv() before reading environment variables. Confirm the exact variable name in the source code before changing configuration.

6. Install and run
Open a terminal in the project root.
Create and activate a virtual environment
Windows PowerShell:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
Install root dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
If the project has a separate Function App dependency file, install those dependencies in the environment used to run or deploy the Function App:
python -m pip install -r .\function_app\requirements.txt
Start the simulator
In terminal 1:
python sensor_simulator.py
Confirm that the simulator connects and sends readings. Do not paste connection strings into GitHub, screenshots or public issue reports.
Start the dashboard
In terminal 2:
streamlit run dashboard.py
The dashboard should retrieve readings from the configured Blob Storage container and display the latest values and history. If the dashboard does not update automatically, check whether its refresh mechanism is configured and whether new blobs are arriving.

7. How to verify the pipeline
Check each boundary in order:
1. Simulator: Is it generating and sending telemetry?
2. IoT Hub: Is the device connected and is message ingestion increasing?
3. Azure Function: Is the event-triggered function being invoked? Review available metrics and logs.
4. Blob Storage: Are new JSON blobs appearing in sensor-readings?
5. Dashboard: Does Streamlit retrieve the new readings and update the charts/table?
A Function execution count indicates invocation activity; it does not by itself prove that every reading was validated and successfully written to Blob Storage.

8. Monitoring and known limitations
The available Azure Metrics screenshot showed On Demand Function Execution Count. The Always Ready metrics shown in the portal had zero values and are not needed to demonstrate this consumption-based prototype.

The supplied Function App screenshots showed an Application Insights configuration prompt and a Log stream prompt to configure Application Insights. Therefore, this repository does not claim that Application Insights dependency tracing, detailed failure analytics or alert rules are already configured.

The Storage lifecycle-management screenshot showed No rules. No lifecycle retention/tiering policy should be claimed until one is created and verified.

Application Insights, Log Analytics and diagnostic ingestion can incur costs. Review pricing and retention before enabling them.

9. Security checklist
- Keep .env out of Git.
- Keep secret-bearing local.settings.json out of Git.
- Never publish IoT Hub device keys, Storage connection strings, SAS tokens, passwords or certificates.
- Use .env.example only for blank placeholders.
- Review screenshots for subscription IDs, tenant IDs, account details and unmasked keys.
- If a secret was committed, rotate/revoke it in Azure. Removing it in a later commit does not make the exposed credential safe.
- Use least-privilege access for Azure resources.

10. Troubleshooting
Symptom	First checks
Simulator says IoT connection string is missing	Check the variable name used by sensor_simulator.py; confirm .env is loaded before os.getenv()
UnauthorizedError or invalid key	Confirm the IoT Hub connection string belongs to device gardensensor1; do not use the Storage credential
ModuleNotFoundError: No module named azure	Activate the correct virtual environment and install the requirements using python -m pip
Function does not trigger	Check simulator output, IoT Hub ingestion, Function App status, trigger settings and consumer group
Function runs but no blob appears	Review Function logs, storage configuration, container name and write permissions
Dashboard shows old readings	Check whether the simulator is running and whether new blobs are being created; then check dashboard refresh/caching
Log stream asks for Application Insights	This is a configuration prompt; it does not alone mean the Function is broken
Only Function Execution Count is available	Record the metric that exists; do not claim unavailable dependency or failure metrics
Lifecycle management says “No rules”	No lifecycle policy exists yet; define retention requirements before creating one


For detailed troubleshooting history and the project evidence, see the documentation in docs/.

11. What is implemented versus future enterprise work
Demonstrated in this prototype
- Simulated sensor readings.
- An IoT Hub device identity.
- Event-driven Azure Function processing.
- JSON persistence in Azure Blob Storage.
- A local Streamlit dashboard with latest readings, history and a low-moisture threshold warning.
- Azure Function execution-count metric evidence.
Not yet demonstrated as production controls
- Physical sensor deployment and fleet provisioning.
- Managed identity replacing connection-string authentication end to end.
- Key Vault integration.
- Private endpoints and network isolation.
- Application Insights dependency tracing and tested alert rules.
- Formal retention/lifecycle rules.
- CI/CD, infrastructure as code, staging approvals and rollback.
- Production incident acknowledgement, escalation and audit workflows.

12. Portfolio summary
Built a Python-based Smart Garden Monitor prototype using Microsoft Azure IoT Hub, Azure Functions, Azure Blob Storage and Streamlit. Simulated soil-moisture, temperature and sunlight telemetry; sent device messages to IoT Hub; processed events with an Azure Function; stored JSON readings in Blob Storage; and built a local dashboard with current readings, historical charts and a low-moisture warning. Documented the end-to-end pipeline, Azure monitoring evidence, security considerations and troubleshooting.
Important: This project uses simulated sensor data and is intended for learning and portfolio demonstration.
