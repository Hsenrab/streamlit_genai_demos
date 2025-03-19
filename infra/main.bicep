targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('OpenAI API key')
param openai_key string

@description('OpenAI API endpoint')
param openai_endpoint string

@description('Doc Intel API key')
param doc_intel_key string

@description('Doc Intel API endpoint')
param doc_intel_endpoint string

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var tags = { 'azd-env-name': name }

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
  location: location
  tags: tags
}

module resources 'resources.bicep' = {
  name: 'resources'
  scope: resourceGroup
  params: {
    location: location
    resourceToken: resourceToken
    tags: tags
    openai_key: openai_key
    openai_endpoint: openai_endpoint
  }
}

output AZURE_LOCATION string = location
