#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { AIStack } from '../lib/cdk-stack';

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: 'us-west-2'
}

const app = new cdk.App();
new AIStack(app, 'AIStack', {
  stackName: 'AIStack',
  description: 'This is the EC2 startup app for ml stuff',
  env: env
});
