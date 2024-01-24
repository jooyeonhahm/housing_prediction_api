# Lab Description
This project builds a FastAPI application with specified endpoints, trains a model with `sci-kit learn`, managing dependencies with `poetry`, validates data inputs and outputs with `pydantic` models, tests the application using `pytest`, creates a `Dockerfile` for containerization, and deploys the application via `kubernetes`.

## How To Deploy the API on Azure

### Requirements
You need the following installed with your bash command line: `Azure CLI`, `minikube`, `kubectl`, `kubelogin`, and `Docker`, and `Python`.

### Setting up Local System to work with Azure

The api is hosted through authenticating into Azure with the following commands:

```shell
az login --tenant berkeleydatasciw255.onmicrosoft.com
az account set --subscription=0257ef73-2cbf-424a-af32-f3d41524e705
az aks get-credentials --name w255-aks --resource-group w255 --overwrite-existing
kubectl config use-context w255-aks
kubelogin convert-kubeconfig

az acr login --name w255mids
az aks get-credentials --name w255-aks --resource-group w255 --overwrite-existing
```

### Containerizing  

The API is packaged as a docker container and portably deployed via hosting in Azure Kubernetes Service (AKS). The container was built and then pushed to Azure Container Repository (ACR) with the following commands. 

```shell
IMAGE_PREFIX=jooyeonhahm
IMAGE_NAME=project
ACR_DOMAIN=w255mids.azurecr.io
TAG=$(git rev-parse --short HEAD) ### latest git commit short hash
IMAGE_FQDN="${ACR_DOMAIN}/${IMAGE_PREFIX}/${IMAGE_NAME}:${TAG}"

docker build --platform linux/amd64 --no-cache -t ${IMAGE_NAME}:${TAG} .
docker tag "${IMAGE_NAME}" ${IMAGE_FQDN}
docker push "${IMAGE_FQDN}"
docker pull "${IMAGE_FQDN}"
```

### Deploying on AKS
The API image pushed to ACR enables deploying the application in a secure way to a production cluster. By applying the following commands, you may deploy the api online.

```shell
kubectl config set-context --current --namespace=jooyeonhahm
kubectl kustomize .k8s/overlays/prod
kubectl apply -k .k8s/overlays/prod
```

By curling the following command, you can check whether the deployment is successful.

```
curl -X 'POST' 'https://${NAMESPACE}.mids255.com/predict' -L -H 'Content-Type: application/json' -d '{"houses": [{ "MedInc": 8.3252, "HouseAge": 42, "AveRooms": 6.98, "AveBedrms": 1.02, "Population": 322, "AveOccup": 2.55, "Latitude": 37.88, "Longitude": -122.23 }]}'
```

### Build-Push Script

You may refer to the build-push script in the home directory for more detailed dsecription of procedure and automating the process.

## 1. What API Does

This project builds a FastAPI application, utilizing the functionalities of poetry, pytest, and docker. The Fast API has the following endpoints:

- `/predict` endpoint

    takes a `POST` request in the following format (a list of json dictionaries):  
        
      {houses:
        [
            {
                "MedInc": float,
                "HouseAge": float,
                "AveRooms": float,
                "AveBedrms": float,
                "Population": float,
                "AveOccup": float,
                "Latitude": float,
                "Longitude": float
            }
            ,
            ...
        ]  
      }

    and returns a list of housing price predictions in the following format:
        
      [
        {
        "prediction": [float]
        }
      ]  

- `/health` endpoint

    returns the current time in the ISO8601 format.

- `/` endpoint

    returns `not implemented` to the requester.
- `/docs` endpoint

    serves the corresponding OpenAPI documentation, utilizing fastAPI's innate functions
- `/openapi.json` endpoint

    returns a `json` object that meets the OpenAPI specification, utilizing fastAPI's innate functions


## 2. How to build the API

* You can build this application by building the docker image provided in the home directory. You may use the following command in your shell: 
        
        docker build -t [image_name] .
        

## 3. How to run the API

* You can run this application by running the build container with the following bash command:
        
        docker run -d -p 8000:8000 --name [container_name] [image_name]
        

## 4. How to test the API

* You can test your application's endpoints by running the pytest in your shell:
        
        poetry run pytest
        
    The pytest will run `test.py` to collect multiple items to test your application's endpoints and inform you whether each test has succeeded.
