using './main.bicep'

param name = readEnvironmentVariable('AZURE_ENV_NAME') // The environment name, for example dev
param location = readEnvironmentVariable('AZURE_LOCATION') // Azure region to deploy resources to
param openai_key = '<api_key>'
param openai_endpoint = '<endpoint>'
param doc_intel_key = '<api_key>'
param doc_intel_endpoint = '<endpoint>'
