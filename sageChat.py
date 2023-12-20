from sagemaker.huggingface.model import HuggingFaceModel, HuggingFacePredictor
from sagemaker.huggingface import get_huggingface_llm_image_uri
import boto3, sys, sagemaker, json, requests

iam_client = boto3.client('iam')
role = iam_client.get_role(RoleName='AmazonSageMaker-ExecutionRole-20231214T132659')['Role']['Arn']
sess = sagemaker.Session()

sagemaker_client = boto3.client('sagemaker');

# ~ https://huggingface.co/blog/sagemaker-huggingface-llm

def main(cmd):
  match cmd:
    case "create":
      print("Creating the predictor...")
      predictor = createPredictor();
      print(predictor)
      print(predictor.endpoint_name)
    case "predict":
      print("Running the prediction...")
      response = runPredictor()
      print(response)
    case "cleanup":
      print("Deleting the endpoints..")
      response = deleteEndpoint('all')
      print(response)
      print("Deleting the endpoint configs..")
      response = deleteEndpointConfig('all')
      print(response)
      print("Deleting the models..")
      response =  deleteModel('all')
      print(response)
      delete_log_streams(prefix='/aws/sagemaker/Endpoints')
    case _:
      print("unsupported command given")
      
def createPredictor():
  # Hub model configuration <https://huggingface.co/models>
  hub = {
    'HF_MODEL_ID':'TheBloke/Wizard-Vicuna-13B-Uncensored-HF',
    'SM_NUM_GPUS': json.dumps(1)
  }
  # create Hugging Face Model Class
  huggingface_model = HuggingFaceModel(
    transformers_version="4.28",                            # Transformers version used
    pytorch_version="2.0.0",                                 # PyTorch version used
    py_version='py310',
    env=hub,
    role=role, 
  )

  # deploy model to SageMaker Inference
  predictor = huggingface_model.deploy(
    initial_instance_count=1,
    instance_type="ml.g5.2xlarge",
    container_startup_health_check_timeout=450,
  )
  return predictor
   
def runPredictor():
  # example request: you always need to define "inputs"
  response = sagemaker_client.list_endpoints();
  name = response['Endpoints'][0]['EndpointName']
  predictor = HuggingFacePredictor(endpoint_name=name, sagemaker_session=sess)
  
  data = {
    "inputs": "My name is Julien and I like to"
  }

  # request
  return predictor.predict(data)

def deleteEndpoint(endpointName):
  if endpointName == 'all':
    response = sagemaker_client.list_endpoints();
    endpointNames = [d['EndpointName'] for d in response['Endpoints']]
  else:
    endpointNames = [endpointName]
  deletedEndpoints = []
  for endpointName in endpointNames:
    response = sagemaker_client.delete_endpoint(EndpointName=endpointName)
    deletedEndpoints.append(response) 
  return deletedEndpoints
    
def deleteEndpointConfig(endpointConfigName):
  if endpointConfigName == 'all':
    response = sagemaker_client.list_endpoint_configs();
    endpointConfigNames = [d['EndpointConfigName'] for d in response['EndpointConfigs']]
  else:
    endpointConfigNames = [endpointConfigName]
  deletedEndpointConfigs = []
  for endpointConfigName in endpointConfigNames:
    response = sagemaker_client.delete_endpoint_config(EndpointConfigName=endpointConfigName)
    deletedEndpointConfigs.append(response) 
  return deletedEndpointConfigs

def deleteModel(modelName):
  if modelName == 'all':
    response = sagemaker_client.list_models();
    modelNames = [d['ModelName'] for d in response['Models']]
  else:
    modelNames = [modelName]
  deletedModels = []
  for modelName in modelNames:
    response = sagemaker_client.delete_model(ModelName=modelName)
    deletedModels.append(response) 
  return deletedModels

def delete_log_streams(prefix=None):
  """Delete CloudWatch Logs log streams with given prefix or all."""
  next_token = None
  logs = boto3.client('logs')

  if prefix:
    log_groups = logs.describe_log_groups(logGroupNamePrefix=prefix)
  else:
    log_groups = logs.describe_log_groups()

  for log_group in log_groups['logGroups']: 
    print("Delete log group:", log_group['logGroupName'])    
    logs.delete_log_group(logGroupName=log_group['logGroupName'])
    
if __name__ == '__main__':
  main(sys.argv[1])






