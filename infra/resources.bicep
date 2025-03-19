param location string
param resourceToken string
param tags object

param openai_key string
param openai_endpoint string 
param doc_intel_key string
param doc_intel_endpoint string
 
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
      DOC_INTEL_API_KEY: doc_intel_key
      DOC_INTEL_ENDPOINT: doc_intel_endpoint
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


output WEB_URI string = 'https://${web.properties.defaultHostName}'
