# Project Description
This project builds a FastAPI application with specified endpoints, trains a model with `sci-kit learn`, managing dependencies with `poetry`, validates data inputs and outputs with `pydantic` models, tests the application using `pytest`, creates a `Dockerfile` for containerization, and deploys the application via `kubernetes`.

## How To Deploy the API on Azure

### Requirements
You need the following installed with your bash command line: `Azure CLI`, `minikube`, `kubectl`, `kubelogin`, `Docker`, and `Python`.

### Configuration for Azure
Authenticate and set up your local system for Azure deployment with the following steps:

```shell
az login --tenant [TENANT_NAME].onmicrosoft.com
az account set --subscription=[SUBSCRIPTION_ID]
az aks get-credentials --name [CLUSTER_NAME] --resource-group [RESOURCE_GROUP] --overwrite-existing
kubectl config use-context [CLUSTER_NAME]
kubelogin convert-kubeconfig

az acr login --name [ACR_NAME]
az aks get-credentials --name [CLUSTER_NAME] --resource-group [RESOURCE_GROUP] --overwrite-existing

### Containerization 

Containerize and deploy the API using the following commands:

```shell
IMAGE_PREFIX=[YOUR_IMAGE_PREFIX]
IMAGE_NAME=[YOUR_IMAGE_NAME]
ACR_DOMAIN=[ACR_DOMAIN].azurecr.io
TAG=$(git rev-parse --short HEAD) # latest git commit short hash
IMAGE_FQDN="${ACR_DOMAIN}/${IMAGE_PREFIX}/${IMAGE_NAME}:${TAG}"

docker build --platform linux/amd64 --no-cache -t ${IMAGE_NAME}:${TAG} .
docker tag "${IMAGE_NAME}" ${IMAGE_FQDN}
docker push "${IMAGE_FQDN}"
docker pull "${IMAGE_FQDN}"
```

### Deploying on AKS
Deploy the API to AKS with the following commands:

```shell
kubectl config set-context --current --namespace=[NAMESPACE] # Replace [NAMESPACE] with your namespace
kubectl kustomize .k8s/overlays/prod
kubectl apply -k .k8s/overlays/prod
```

Test the deployment:
```shell
curl -X 'POST' 'https://$[NAMESPACE].[API_ADDRESS]/predict' -L -H 'Content-Type: application/json' -d '{"houses": [{ "MedInc": 8.3252, "HouseAge": 42, "AveRooms": 6.98, "AveBedrms": 1.02, "Population": 322, "AveOccup": 2.55, "Latitude": 37.88, "Longitude": -122.23 }]}'
```

### Automation Script

Refer to the build-push script in the home directory for an automated deployment process.

## API

### API Features
- `/predict` endpoint: Accepts POST requests with housing data and returns price predictions.
- `/health` endpoint: Returns the current server time in ISO8601 format.
- `/docs` endpoint: Serves the OpenAPI documentation.
- `/openapi.json` endpoint: Returns the OpenAPI specification as JSON.


### Building the API
* Build the Docker container using the provided Dockerfile:
        
        docker build -t [image_name] .
        

### Running the API
* Run the Docker container:
        
        docker run -d -p 8000:8000 --name [container_name] [image_name]
        

### Testing the API

* Test the application using pytest:
        
        poetry run pytest
        
    This runs tests defined in test.py, checking the application's endpoints.
