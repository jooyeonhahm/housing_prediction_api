#!/bin/sh

# This script sets up a local system to work with an Azure account, builds a Docker image, pushes it to Azure Container Registry (ACR),
# and deploys an API in Azure Kubernetes Service (AKS). It also demonstrates how to update Kubernetes deployments with a new image version
# and how to get a prediction from the deployed API.

# Login to Azure with a specific tenant
az login --tenant [TENANT_NAME].onmicrosoft.com # Replace [TENANT_NAME] with your tenant name
# Set the Azure account subscription to use
az account set --subscription=[SUBSCRIPTION_ID] # Replace [SUBSCRIPTION_ID] with your subscription ID
# Get credentials for a specific AKS cluster and resource group, overwriting any existing credentials
az aks get-credentials --name [CLUSTER_NAME] --resource-group [RESOURCE_GROUP] --overwrite-existing # Replace [CLUSTER_NAME] and [RESOURCE_GROUP] with appropriate values
# Set the current kubectl context to the specified cluster
kubectl config use-context [CLUSTER_NAME] # Replace [CLUSTER_NAME] with your cluster name
# Convert kubeconfig to use Azure AD for authentication
kubelogin convert-kubeconfig

# Login to Azure Container Registry
az acr login --name [ACR_NAME] # Replace [ACR_NAME] with your Azure Container Registry name
# Get credentials again for the AKS cluster, if necessary
az aks get-credentials --name [CLUSTER_NAME] --resource-group [RESOURCE_GROUP] --overwrite-existing # No changes needed here if already set

# Define variables for image prefix, name, and the Azure Container Registry domain
IMAGE_PREFIX=[YOUR_IMAGE_PREFIX] # Replace [YOUR_IMAGE_PREFIX] with your image prefix
IMAGE_NAME=[YOUR_IMAGE_NAME] # Replace [YOUR_IMAGE_NAME] with your image name
ACR_DOMAIN=[ACR_DOMAIN].azurecr.io # Replace [ACR_DOMAIN] with your ACR domain

# Get the short hash of the last git commit to use as a tag for the Docker image
TAG=$(git rev-parse --short HEAD)
# Replace the placeholder [TAG] in the Kubernetes deployment patch file with the actual git commit hash
sed "s/\[TAG\]/${TAG}/g" .k8s/overlays/prod/patch-deployment-[YOUR_DEPLOYMENT_NAME].yaml > .k8s/overlays/prod/patch-deployment-[YOUR_DEPLOYMENT_NAME].yaml # Replace [YOUR_DEPLOYMENT_NAME] with your deployment name
# Construct the Fully Qualified Domain Name (FQDN) for the Docker image
IMAGE_FQDN="${ACR_DOMAIN}/${IMAGE_PREFIX}/${IMAGE_NAME}:${TAG}"

# Build, tag, and push the Docker image to ACR
docker build -t ${IMAGE_NAME}:${TAG} .
docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_FQDN}
docker push ${IMAGE_FQDN}
# Optionally, pull and run the image locally to verify
docker pull ${IMAGE_FQDN}
docker run --publish 8000:8000 --rm ${IMAGE_NAME}:${TAG}

# Deploy the API in AKS using kubectl and kustomize
NAMESPACE=[YOUR_NAMESPACE] # Replace [YOUR_NAMESPACE] with your namespace
# Example commands to interact with the namespace, e.g., checking logs, certificates, and gateways
kubectl --namespace externaldns logs -l "app.kubernetes.io/name=external-dns,app.kubernetes.io/instance=external-dns"
kubectl --namespace istio-ingress get certificates ${NAMESPACE}-cert
kubectl --namespace istio-ingress get certificaterequests
kubectl --namespace istio-ingress get gateways ${NAMESPACE}-gateway

# Set the current kubectl context to use the specified namespace
kubectl config set-context --current --namespace=[YOUR_NAMESPACE] # Replace [YOUR_NAMESPACE] with your namespace

# Apply Kubernetes configurations from the .k8s directory
kubectl kustomize .k8s/bases
kubectl apply -k .k8s/bases
kubectl kustomize .k8s/overlays/dev
kubectl apply -k .k8s/overlays/dev

# Ensure the kubectl context is set to the AKS cluster and convert kubeconfig for Azure AD authentication
kubectl config use-context [CLUSTER_NAME] # Replace [CLUSTER_NAME] with your cluster name
kubelogin convert-kubeconfig

# Apply production overlays from the .k8s directory
kubectl kustomize .k8s/overlays/prod
kubectl apply -k .k8s/overlays/prod
# Set the current namespace in the kubectl context again, if necessary
kubectl config set-context --current --namespace=[YOUR_NAMESPACE] # Replace [YOUR_NAMESPACE] with


# Get a prediction from API in AKS
curl -X 'POST' 'https://[NAMESPACE].[API_ADDRESS]/predict' -L -H 'Content-Type: application/json' -d '{"houses": [{ "MedInc": 8.3252, "HouseAge": 42, "AveRooms": 6.98, "AveBedrms": 1.02, "Population": 322, "AveOccup": 2.55, "Latitude": 37.88, "Longitude": -122.23 }]}' 