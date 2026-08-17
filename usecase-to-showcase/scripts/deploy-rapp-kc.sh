#!/usr/bin/env bash
# Deploy the rapp_ai memory-agent platform (S/4HANA Knowledge Companion build)
# into a policy-constrained subscription.
#
# Adapted from infra/deploy-private.sh (the compliant shape: identity-based
# storage + VNet + private endpoints + reused AAD-only Azure OpenAI). Two
# rapp_ai-specific additions:
#   * an Azure Files share ("rappai") — the platform's memory + hot-deployable
#     agents/ live there, so a new *_agent.py lands without a code deploy
#   * "Storage File Data Privileged Contributor" for the function identity —
#     OAuth to the file data plane requires the *privileged* role
set -euo pipefail

SUB="${SUB:?set SUB to your subscription id}"   # never hardcode a tenant coordinate in a shareable script
RG="${RG:?set RG to your resource group name}"
LOC="${LOC:-westus2}"
APP="${APP:?set APP to your function app name}"
STG="${STG:?set STG to a globally-unique storage account name}"
SHARE="${SHARE:-rappai}"
VNET="${VNET:-vnet-$APP}"
SNET_FUNC="${SNET_FUNC:-snet-func}"
SNET_PE="${SNET_PE:-snet-pe}"

# Reused Azure OpenAI (AAD-only, public endpoint) — best deployed model.
AOAI_RG="${AOAI_RG:?set AOAI_RG}"
AOAI_NAME="${AOAI_NAME:?set AOAI_NAME}"
AOAI_ENDPOINT="${AOAI_ENDPOINT:?set AOAI_ENDPOINT}"
AOAI_DEPLOYMENT="${AOAI_DEPLOYMENT:-gpt-5.6-terra}"
AOAI_API_VERSION="${AOAI_API_VERSION:-2025-04-01-preview}"

# The rapp_ai checkout to publish.
SRC="${SRC:?set SRC to your rapp_ai checkout}"

say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
azs() { az "$@" --subscription "$SUB"; }

say "Resource group $RG ($LOC)"
azs group create -n "$RG" -l "$LOC" -o none

say "Storage account $STG (keyless + private — policy enforces both anyway)"
azs storage account create -n "$STG" -g "$RG" -l "$LOC" \
  --sku Standard_LRS --kind StorageV2 --min-tls-version TLS1_2 \
  --allow-blob-public-access false -o none 2>/dev/null || echo "    (exists)"

say "File share $SHARE (management plane — immune to shared-key policy)"
azs storage share-rm create --storage-account "$STG" -g "$RG" -n "$SHARE" -o none 2>/dev/null || echo "    (exists)"

say "Virtual network $VNET"
azs network vnet create -n "$VNET" -g "$RG" -l "$LOC" \
  --address-prefixes 10.30.0.0/16 \
  --subnet-name "$SNET_PE" --subnet-prefixes 10.30.2.0/24 -o none 2>/dev/null || echo "    (exists)"
azs network vnet subnet create -n "$SNET_FUNC" -g "$RG" --vnet-name "$VNET" \
  --address-prefixes 10.30.1.0/24 \
  --delegations Microsoft.App/environments -o none 2>/dev/null || echo "    ($SNET_FUNC exists)"

say "Private endpoints + DNS for storage (blob, file, queue, table)"
STG_ID=$(azs storage account show -n "$STG" -g "$RG" --query id -o tsv)
for SVC in blob file queue table; do
  ZONE="privatelink.${SVC}.core.windows.net"
  azs network private-dns zone create -g "$RG" -n "$ZONE" -o none 2>/dev/null || true
  azs network private-dns link vnet create -g "$RG" -n "link-$SVC" \
    -z "$ZONE" -v "$VNET" -e false -o none 2>/dev/null || true
  azs network private-endpoint create -n "pe-$STG-$SVC" -g "$RG" -l "$LOC" \
    --vnet-name "$VNET" --subnet "$SNET_PE" \
    --private-connection-resource-id "$STG_ID" \
    --group-id "$SVC" --connection-name "conn-$SVC" -o none 2>/dev/null \
    || echo "    (pe-$STG-$SVC exists)"
  azs network private-endpoint dns-zone-group create -g "$RG" \
    --endpoint-name "pe-$STG-$SVC" -n "zg-$SVC" \
    --private-dns-zone "$ZONE" --zone-name "$SVC" -o none 2>/dev/null || true
  echo "    $SVC ok"
done

say "Function app $APP (Flex Consumption, VNet-injected, identity-based storage)"
azs functionapp create -n "$APP" -g "$RG" \
  --storage-account "$STG" \
  --flexconsumption-location "$LOC" \
  --runtime python --runtime-version 3.11 \
  --assign-identity '[system]' \
  --deployment-storage-auth-type SystemAssignedIdentity \
  --vnet "$VNET" --subnet "$SNET_FUNC" -o none 2>/dev/null || echo "    (exists)"

MI=$(azs functionapp show -n "$APP" -g "$RG" --query identity.principalId -o tsv)
echo "    managed identity: $MI"

say "Role assignments for the function identity"
for ROLE in "Storage Blob Data Owner" "Storage Queue Data Contributor" \
            "Storage Table Data Contributor" "Storage Account Contributor" \
            "Storage File Data Privileged Contributor"; do
  azs role assignment create --assignee-object-id "$MI" \
    --assignee-principal-type ServicePrincipal \
    --role "$ROLE" --scope "$STG_ID" -o none 2>/dev/null \
    && echo "    granted: $ROLE" || echo "    already: $ROLE"
done
AOAI_ID=$(azs cognitiveservices account show -n "$AOAI_NAME" -g "$AOAI_RG" --query id -o tsv)
for ROLE in "Cognitive Services OpenAI User"; do
  azs role assignment create --assignee-object-id "$MI" \
    --assignee-principal-type ServicePrincipal \
    --role "$ROLE" --scope "$AOAI_ID" -o none 2>/dev/null \
    && echo "    granted: $ROLE" || echo "    already: $ROLE"
done

say "App settings (no keys anywhere — AAD all the way down)"
azs functionapp config appsettings set -n "$APP" -g "$RG" --settings \
  "AzureWebJobsStorage__accountName=$STG" \
  "AZURE_OPENAI_ENDPOINT=$AOAI_ENDPOINT" \
  "AZURE_OPENAI_DEPLOYMENT_NAME=$AOAI_DEPLOYMENT" \
  "AZURE_OPENAI_API_VERSION=$AOAI_API_VERSION" \
  "ASSISTANT_NAME=S4HANA Knowledge Companion" \
  "CHARACTERISTIC_DESCRIPTION=grounded, citation-first knowledge companion for an S/4HANA transformation program" \
  "USE_CLOUD_STORAGE=true" \
  "USE_IDENTITY_BASED_STORAGE=true" \
  "AZURE_STORAGE_ACCOUNT_NAME=$STG" \
  "AZURE_FILES_SHARE_NAME=$SHARE" \
  "AzureFunctionsJobHost__functionTimeout=00:10:00" -o none
azs functionapp config appsettings delete -n "$APP" -g "$RG" \
  --setting-names AZURE_OPENAI_API_KEY AzureWebJobsStorage \
                  SCM_DO_BUILD_DURING_DEPLOYMENT ENABLE_ORYX_BUILD \
  -o none 2>/dev/null || true

say "Waiting 90s for role propagation before publish"
sleep 90

say "Publishing function code (remote Oryx build)"
( cd "$SRC" && func azure functionapp publish "$APP" --build remote --python )

HOST=$(azs functionapp show -n "$APP" -g "$RG" --query defaultHostName -o tsv)
say "Done — https://$HOST"
echo "    health: https://$HOST/api/health"
