using './main.bicep'

param name = readEnvironmentVariable('AZURE_ENV_NAME') // The environment name, for example dev
param location = readEnvironmentVariable('AZURE_LOCATION') // Azure region to deploy resources to
param openai_key = readEnvironmentVariable('OPENAI_API_KEY') // OpenAI API key
param openai_endpoint = readEnvironmentVariable('OPENAI_API_ENDPOINT') // OpenAI API endpoint
