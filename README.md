# GenAI Demos with streamlit

As someone familar with python a way to create quick demos with a functional UI

![system diagram](diagram.png)

## Pre-req

- Azure subscription with contributor rights
- Previously deployed OpenAI / Foundry resource with gpt4o deployed.

## Usage

### Locally

1. Create a virtual environment - [Learn more about creating virtual environments with Conda.](https://nhsdigital.github.io/rap-community-of-practice/training_resources/python/virtual-environments/conda/)
2. Activate environment and install dependencies in requirements.txt

    ```bash
    pip install -r src\requirements.txt
    ```

3. Create a `.env` file in the root directory to configure model access. A `sample.env` file is provided as a template.

    Example `.env` file:

    ```text
    # OpenAI Configuration
    OPENAI_API_ENDPOINT=https://<your-endpoint>.openai.azure.com
    OPENAI_API_KEY=<your-api-key>
    
    # AI Foundry Configuration (for WebSearch feature)
    AI_FOUNDRY_ENDPOINT=https://<your-foundry-project>.services.ai.azure.com/api/projects/<your-project-name>
    AI_FOUNDRY_AGENT_ID=asst_<your-agent-id>
    ```

4. Run the command below to run strealit on localhost.

```bash
python -m streamlit run src/Home.py
```

### Deploy to cloud

1. Install AZD and clone the repo.

2. Create a main.bicepparam file from template

3. Add openai api key and endpoint from existing resource into param file.

   - `Environment Name`: This will be used as a prefix for the resource group that will be created to hold all Azure resources. This name should be unique within your Azure subscription.

4. Login to azd cli

    ```bash
    azd auth login
    ```

5. Run the following command to build a deployable copy of your application, provision the template's infrastructure to Azure and also deploy the application code to those newly provisioned resources.

    ```bash
    azd up
    ```

    This command will prompt you for the following information:
   - `Azure Location`: The Azure location where your resources will be deployed.
   - `Azure Subscription`: The Azure Subscription where your resources will be deployed.

    > NOTE: This may take a while to complete as it executes three commands: `azd package` (builds a deployable copy of your application), `azd provision` (provisions Azure resources), and `azd deploy` (deploys application code). You will see a progress indicator as it packages, provisions and deploys your application.

6. If you want to change things make changes to python files and run `azd deploy` again to update your changes.

## Notes

This uses the F1 (free) SKU for app service, which has limited CPU and RAM resources.

See the [pricing calculator](https://azure.microsoft.com/en-au/pricing/calculator/) for details on paid SKUs replace the SKU option with a suitable choice.

Based on the this [great template:](MiguelElGallo/simple-streamlit-azd)

Added support for `azd pipeline config`, enabling creation of CI/CD pipeline for GitHub Actions. Note this is still a [beta](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/configure-devops-pipeline?tabs=GitHub) feature in AZD. 