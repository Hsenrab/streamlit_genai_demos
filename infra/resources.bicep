param location string
param resourceToken string
param tags object

param openai_key string
param openai_endpoint string 

 
resource web 'Microsoft.Web/sites@2022-03-01' = {
  name: 'web-${resourceToken}'
  location: location
  tags: union(tags, { 'azd-service-name': 'web' })
  kind: 'app,linux'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      ftpsState: 'Disabled'
      appCommandLine: 'startup.sh'
    }
    httpsOnly: true
  }
  identity: {
    type: 'SystemAssigned'
  }

  resource appSettings 'config' = {
    name: 'appsettings'
    properties: {
      SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
      ENABLE_ORYX_BUILD: 'true'
      OPENAI_API_KEY: openai_key
      OPENAI_API_ENDPOINT: openai_endpoint
    }
  }

  resource logs 'config' = {
    name: 'logs'
    properties: {
      applicationLogs: {
        fileSystem: {
          level: 'Verbose'
        }
      }
      detailedErrorMessages: {
        enabled: true
      }
      failedRequestsTracing: {
        enabled: true
      }
      httpLogs: {
        fileSystem: {
          enabled: true
          retentionInDays: 1
          retentionInMb: 35
        }
      }
    }
  }
}
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: 'app-${resourceToken}'
  location: location
  sku: {
    name: 'F1'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource search 'Microsoft.Search/searchServices@2023-11-01' = {
  name: 'search-${resourceToken}'
  location: location
  sku: {
    name: 'basic'
  }
  properties: {
    partitionCount: 1
    replicaCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
  }
  tags: tags
}

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'st${uniqueString(resourceToken, location)}'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    allowBlobPublicAccess: false
  }
  tags: tags
}

resource container 'Microsoft.Storage/storageAccounts/blobServices/containers@2022-09-01' = {
  name: '${storage.name}/default/searchdocuments'
  properties: {
    publicAccess: 'None'
  }
}

resource configureSearch 'Microsoft.Resources/deploymentScripts@2020-10-01' = {
  name: 'configure-search-${resourceToken}'
  location: location
  kind: 'AzureCLI'
  properties: {
    azCliVersion: '2.53.0'
    timeout: 'PT15M'
    retentionInterval: 'P1D'
    scriptContent: loadTextContent('scripts/configure-search.sh')
    supportingScriptUris: []
    environmentVariables: [
      {
        name: 'SEARCH_NAME'
        value: search.name
      }
      {
        name: 'STORAGE_NAME'
        value: storage.name
      }
      {
        name: 'STORAGE_KEY'
        value: storage.listKeys().keys[0].value
      }
      {
        name: 'CONTAINER_NAME'
        value: container.name
      }
      {
        name: 'LOCATION'
        value: location
      }
      {
        name: 'RESOURCE_GROUP'
        value: resourceGroup().name
      }
    ]
    forceUpdateTag: uniqueString(resourceToken)
    cleanupPreference: 'OnSuccess'
  }
}

output WEB_URI string = 'https://${web.properties.defaultHostName}'
