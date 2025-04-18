using './main.bicep'

param name = readEnvironmentVariable('AZURE_ENV_NAME') // The environment name, for example dev
param location = readEnvironmentVariable('AZURE_LOCATION') // Azure region to deploy resources to
param openai_key = readEnvironmentVariable('AZURE_OPENAI_KEY') // Azure OpenAI key
param openai_endpoint = readEnvironmentVariable('AZURE_OPENAI_ENDPOINT') // Azure OpenAI endpoint
