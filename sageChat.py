import boto3, sys, torch, json, requests
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer
from llama_cpp import Llama
      
iam_client = boto3.client('iam')
role = iam_client.get_role(RoleName='AmazonSageMaker-ExecutionRole-20231214T132659')['Role']['Arn']
# ~ sess = sagemaker.Session()

sagemaker_client = boto3.client('sagemaker');

model = 'TheBloke/Chronos-Hermes-13b-v2-GGUF'
# Austism/chronos-hermes-13b-v2
# mindrage/Manticore-13B-Chat-Pyg-Guanaco-GGML
# mistralai/Mistral-7B-Instruct-v0.2
# mistralai/Mixtral-8x7B-v0.1
# TheBloke/Mixtral-8x7B-v0.1-GGUF

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
    case "download":
      snapshot_download(repo_id=model, local_dir="models/"+model,
        local_dir_use_symlinks=False, revision="main")
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
    case 'chat':
      llm = Llama(model_path="models/"+model+"/chronos-hermes-13b-v2.Q4_K_M.gguf", chat_format="llama-2")
      response = llm.create_chat_completion(
        messages = [
          {"role": "system", "content": "You are an assistant who perfectly describes penises."},
          {
            "role": "user",
            "content": "Describe my penis in detail please."
          }
        ]
      )
      print(response)
      # ~ model_load = AutoModelForCausalLM.from_pretrained("./models/"+model+'/', 
        # ~ torch_dtype=torch.bfloat16, 
        # ~ low_cpu_mem_usage=True)
      
      # ~ tokenizer = AutoTokenizer.from_pretrained("./models/"+model+'/')
      # ~ model_load.to('cpu').eval();

      # ~ # Let's chat for 10 lines
      # ~ for step in range(10):
          # ~ # encode the new user input, add the eos_token and return a tensor in Pytorch
          # ~ new_user_input_ids = tokenizer.encode(tokenizer.eos_token + input(">> User:"), return_tensors='pt')

          # ~ # append the new user input tokens to the chat history
          # ~ bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

          # ~ # generated a response while limiting the total chat history to 1000 tokens, 
          # ~ chat_history_ids = model_load.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
          # ~ # pretty print last ouput tokens from bot
          # ~ print("Bot: {}".format(tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)))

    case _:
      print("unsupported command given")
      
def createPredictor():
  # Hub model configuration <https://huggingface.co/models>
  hub = {
    'HF_MODEL_ID':model,
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






