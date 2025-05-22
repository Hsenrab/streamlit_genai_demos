#!/usr/bin/env bash
# filepath: infra/scripts/test-configure-search.sh
set -euo pipefail

SUFFIX="test4"

# --- parameters ---------------------------------------------------
LOCATION="westeurope"
RG="test-search-rg-$SUFFIX"
SEARCH_NAME="testsearch$SUFFIX"
STORAGE_NAME="teststor$SUFFIX"
CONTAINER_NAME="searchdocuments"
# ------------------------------------------------------------------

echo "Creating sandbox resources..."
az group create -g "$RG" -l "$LOCATION"                 >/dev/null
az search service create -g "$RG" -n "$SEARCH_NAME" \
    --sku basic                                          >/dev/null
az storage account create -g "$RG" -n "$STORAGE_NAME" \
    -l "$LOCATION" --sku Standard_LRS                   >/dev/null
STORAGE_KEY=$(az storage account keys list \
                --resource-group "$RG" \
                --account-name "$STORAGE_NAME" \
                --query '[0].value' -o tsv)
# Create the container using the freshly obtained storage account key
az storage container create --account-name "$STORAGE_NAME" \
    --account-key "$STORAGE_KEY" \
    --name "$CONTAINER_NAME"                            >/dev/null

echo "Environment variables just defined:"
for VAR in LOCATION RG SEARCH_NAME STORAGE_NAME STORAGE_KEY CONTAINER_NAME; do
    printf '%s=%s\n' "$VAR" "${!VAR}"
done

# Export variables expected by configure-search.sh
export SEARCH_NAME STORAGE_NAME STORAGE_KEY CONTAINER_NAME
export RESOURCE_GROUP="$RG" LOCATION

# Fetch and export the Search service admin key for subsequent commands
SEARCH_ADMIN_KEY=$(az search admin-key show \
    --resource-group "$RG" \
    --service-name "$SEARCH_NAME" \
    --query 'primaryKey' -o tsv)

export SEARCH_ADMIN_KEY

# Run the script under test (bash -x to echo commands)
echo "Running configure-search.sh..."
bash -x "$(dirname "$0")/configure-search.sh"




echo "SEARCH_ADMIN_KEY has been set."

# Uncomment to clean up automatically
# az group delete -g "$RG" --yes --no-wait