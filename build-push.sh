#!/bin/sh

# Setting up local system to work with Azure account
az login --tenant berkeleydatasciw255.onmicrosoft.com
az account set --subscription=0257ef73-2cbf-424a-af32-f3d41524e705
az aks get-credentials --name w255-aks --resource-group w255 --overwrite-existing
kubectl config use-context w255-aks
kubelogin convert-kubeconfig

az acr login --name w255mids
az aks get-credentials --name w255-aks --resource-group w255 --overwrite-existing

IMAGE_PREFIX=jooyeonhahm
IMAGE_NAME=lab4
ACR_DOMAIN=w255mids.azurecr.io

# Get short hast of the last git commit
TAG=$(git rev-parse --short HEAD)
# Stream edit find and replace [TAG] with latest git hash
sed "s/\[TAG\]/${TAG}/g" .k8s/overlays/prod/patch-deployment-lab4_copy.yaml > .k8s/overlays/prod/patch-deployment-lab4.yaml
# Generate the updated image FQDN
IMAGE_FQDN="${ACR_DOMAIN}/${IMAGE_PREFIX}/${IMAGE_NAME}:${TAG}"

# Push image to a namespaced location in ACR
docker build -t ${IMAGE_NAME}:${TAG} .
docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_FQDN}
docker push ${IMAGE_FQDN}
docker pull ${IMAGE_FQDN}
docker run --publish 8000:8000 --rm ${IMAGE_NAME}:${TAG}

# Deploy API in AKS
NAMESPACE=jooyeonhahm
kubectl --namespace externaldns logs -l "app.kubernetes.io/name=external-dns,app.kubernetes.io/instance=external-dns"
kubectl --namespace istio-ingress get certificates ${NAMESPACE}-cert
kubectl --namespace istio-ingress get certificaterequests
kubectl --namespace istio-ingress get gateways ${NAMESPACE}-gateway

kubectl config set-context --current --namespace=jooyeonhahm

kubectl kustomize .k8s/bases
kubectl apply -k .k8s/bases
kubectl kustomize .k8s/overlays/dev
kubectl apply -k .k8s/overlays/dev

kubectl config use-context w255-aks
kubelogin convert-kubeconfig

kubectl kustomize .k8s/overlays/prod
kubectl apply -k .k8s/overlays/prod
kubectl config set-context --current --namespace=jooyeonhahm
kubelogin convert-kubeconfig

# Get a prediction from API in AKS
curl -X 'POST' 'https://${NAMESPACE}.mids255.com/predict' -L -H 'Content-Type: application/json' -d '{"houses": [{ "MedInc": 8.3252, "HouseAge": 42, "AveRooms": 6.98, "AveBedrms": 1.02, "Population": 322, "AveOccup": 2.55, "Latitude": 37.88, "Longitude": -122.23 }]}'