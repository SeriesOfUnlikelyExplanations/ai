# Generative AI toolkit
I wanted to create this toolkit/workspace to allow me to take a model from huggingface, deploy it to sagemaker, and then run it both through a script and through an API. It's a work in progress and I'm not sure where it will eventually end up.

## Models from Huggingface
I was playing around with huggingface AI models and I found that most of them didn't run on sagemaker (despite having the little deploy script prepared). Most of the models are using a version of transformers that's newer than what's available on Sagemaker and they don't include the little script that allows sagemaker to use that higher version. I'm starting off with a sample model (Wizard 13B uncensored) and see if I can get it to run on sagemaker. If I can, then I'm going to get Google's RT-1 robotics transformer loaded into huggingface and then working when I deploy it to sagemaker.


