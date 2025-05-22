#!/usr/bin/env bash



# Variables
# ------------------------------------------------------------------
# Expected environment variables (fail fast if any are missing)
#   SEARCH_NAME    - Azure AI Search service name
#   STORAGE_NAME   - Azure Storage account name
#   STORAGE_KEY    - Primary key for the storage account
#   CONTAINER_NAME - Blob container name
#   LOCATION       - Azure region (kept for completeness)
#   RESOURCE_GROUP - Resource-group name
# ------------------------------------------------------------------
set -o errexit -o nounset -o pipefail

: "${SEARCH_NAME?Environment variable SEARCH_NAME not set}"
: "${STORAGE_NAME?Environment variable STORAGE_NAME not set}"
: "${STORAGE_KEY?Environment variable STORAGE_KEY not set}"
: "${CONTAINER_NAME?Environment variable CONTAINER_NAME not set}"
: "${RESOURCE_GROUP?Environment variable RESOURCE_GROUP not set}"
: "${SEARCH_ADMIN_KEY?Environment variable SEARCH_ADMIN_KEY not set}"

# Derived variables used by the script
STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=${STORAGE_NAME};AccountKey=${STORAGE_KEY};EndpointSuffix=core.windows.net"
DATA_SOURCE_NAME="${STORAGE_NAME}-datasource"
INDEX_NAME="${STORAGE_NAME}-index"
INDEXER_NAME="${STORAGE_NAME}-indexer"
SKILLSET_NAME="${STORAGE_NAME}-skillset"
API_VERSION="2023-11-01"

# Create or update data source via REST API
curl -sS -X PUT "https://${SEARCH_NAME}.search.windows.net/datasources/${DATA_SOURCE_NAME}?api-version=${API_VERSION}" \
    -H "Content-Type: application/json" \
    -H "api-key: ${SEARCH_ADMIN_KEY}" \
    -d @- <<EOF
{
  "name": "${DATA_SOURCE_NAME}",
  "type": "azureblob",
  "credentials": {
    "connectionString": "${STORAGE_CONNECTION_STRING}"
  },
  "container": {
    "name": "${CONTAINER_NAME}"
  }
}
EOF


# Create or update index via REST API
curl -sS -X PUT "https://${SEARCH_NAME}.search.windows.net/indexes/${DATA_SOURCE_NAME}?api-version=${API_VERSION}" \
    -H "Content-Type: application/json" \
    -H "api-key: ${SEARCH_ADMIN_KEY}" \
    -d @- <<EOF
{
  "name": "${INDEX_NAME}",
  "fields": [
    { "name": "id", "type": "Edm.String", "key": true },
    { "name": "chunked_content", "type": "Edm.String", "searchable": true, "retrievable": true },
    { "name": "chunked_content_vectorized", "type": "Edm.Single", "dimensions": 1536, "vectorSearchProfile": "my-vector-profile", "searchable": true, "retrievable": false, "stored": false },
    { "name": "metadata", "type": "Edm.String", "retrievable": true, "searchable": true, "filterable": true }
  ],
  "vectorSearch": {
      "algorithms": [
          { "name": "my-algo-config", "kind": "hnsw", "hnswParameters": { }  }
      ],
      "profiles": [ 
        { "name": "my-vector-profile", "algorithm": "my-algo-config" }
      ]
  }
}
EOF

# Create or update indexer via REST API
curl -sS -X PUT "https://${SEARCH_NAME}.search.windows.net/indexers/${DATA_SOURCE_NAME}?api-version=${API_VERSION}" \
    -H "Content-Type: application/json" \
    -H "api-key: ${SEARCH_ADMIN_KEY}" \
    -d @- <<EOF
{
  "name": "${INDEXER_NAME}",
  "dataSourceName": "${DATA_SOURCE_NAME}",
  "targetIndexName": "${DATA_SOURCE_NAME}",
  "schedule": {
    "interval": "PT15M"
  },
  "parameters": {
    "configuration": {
      "dataToExtract": "contentAndMetadata",
      "imageAction": "generateNormalizedImages",
      "imageType": "all"
    }
  }
}
EOF

# Create or update skillset via REST API
curl -sS -X PUT "https://${SEARCH_NAME}.search.windows.net/skillsets/${DATA_SOURCE_NAME}?api-version=${API_VERSION}" \
    -H "Content-Type: application/json" \
    -H "api-key: ${SEARCH_ADMIN_KEY}" \
    -d @- <<EOF
{
  "name": "${SKILLSET_NAME}",
  "description": "Skillset for extracting content from blob storage",
  "skills": [
    {
      "@odata.type": "#Microsoft.Skills.Vision.ImageAnalysisSkill",
      "context": "/document/content",
      "imageType": "all",
      "defaultLanguageCode": "en",
      "modelVersion": "latest"
    }
  ]
}'

