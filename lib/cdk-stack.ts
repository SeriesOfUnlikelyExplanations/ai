import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import {ServicePrincipal, Role} from 'aws-cdk-lib/aws-iam';
import {readFileSync} from 'fs';

export class AIStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    const defaultVpc = ec2.Vpc.fromLookup(this, 'VPC', { isDefault: true })
    const role = new Role(this, 'ai-role',
      { assumedBy: new ServicePrincipal('ec2.amazonaws.com') }
    )

    // A security group acts as a virtual firewall for your instance to control inbound and outbound traffic.
    const securityGroup = new ec2.SecurityGroup(this, 'ai-sg',
      {
        vpc: defaultVpc,
        allowAllOutbound: true, // will let your instance send outboud traffic
        securityGroupName: 'ai-sg',
      }
    )

    // lets use the security group to allow inbound traffic on specific ports
    securityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(22),
      'Allows SSH access from Internet'
    )

    // Finally lets provision our ec2 instance
    const instance = new ec2.Instance(this, 'ai-instance', {
      vpc: defaultVpc,
      role: role,
      securityGroup: securityGroup,
      instanceName: 'ai-instance',
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.G4DN,
        ec2.InstanceSize.XLARGE2
      ),
      machineImage: ec2.MachineImage.latestAmazonLinux({
        generation: ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
      }),

      keyName: 'ai-key', // we will create this in the console before we deploy
    })
    
    const userDataScript = readFileSync('./lib/startup.sh', 'utf8');
    // add user data to the EC2 instance
    instance.addUserData(userDataScript);

    // cdk lets us output prperties of the resources we create after they are created
    // we want the ip address of this new instance so we can ssh into it later
    new cdk.CfnOutput(this, 'ai-ip', {
      value: instance.instancePublicIp
    })
  }
}
