#!/usr/bin/python
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'certified'}


DOCUMENTATION = '''
---
module: ec2_lc

short_description: Create or delete AWS Autoscaling Launch Configurations

description:
  - Can create or delete AWS Autoscaling Configurations
  - Works with the ec2_asg module to manage Autoscaling Groups

notes:
  - Amazon ASG Autoscaling Launch Configurations are immutable once created, so modifying the configuration after it is changed will not modify the
    launch configuration on AWS. You must create a new config and assign it to the ASG instead.
  - encrypted volumes are supported on versions >= 2.4

version_added: "1.6"

author:
  - "Gareth Rushgrove (@garethr)"
  - "Willem van Ketwich (@wilvk)"

options:
  state:
    description:
      - Register or deregister the instance
    default: present
    choices: ['present', 'absent']
  name:
    description:
      - Unique name for configuration
    required: true
  instance_type:
    description:
      - Instance type to use for the instance
    required: true
  image_id:
    description:
      - The AMI unique identifier to be used for the group
  key_name:
    description:
      - The SSH key name to be used for access to managed instances
  security_groups:
    description:
      - A list of security groups to apply to the instances. Since version 2.4 you can specify either security group names or IDs or a mix.  Previous
        to 2.4, for VPC instances, specify security group IDs and for EC2-Classic, specify either security group names or IDs.
  volumes:
    description:
      - A list of volume dicts, each containing device name and optionally ephemeral id or snapshot id. Size and type (and number of iops for io
        device type) must be specified for a new volume or a root volume, and may be passed for a snapshot volume. For any volume, a volume size less
        than 1 will be interpreted as a request not to create the volume.
  user_data:
    description:
      - Opaque blob of data which is made available to the ec2 instance. Mutually exclusive with I(user_data_path).
  user_data_path:
    description:
      - Path to the file that contains userdata for the ec2 instances. Mutually exclusive with I(user_data).
    version_added: "2.3"
  kernel_id:
    description:
      - Kernel id for the EC2 instance
  spot_price:
    description:
      - The spot price you are bidding. Only applies for an autoscaling group with spot instances.
  instance_monitoring:
    description:
      - Specifies whether instances are launched with detailed monitoring.
    type: bool
    default: 'no'
  assign_public_ip:
    description:
      - Used for Auto Scaling groups that launch instances into an Amazon Virtual Private Cloud. Specifies whether to assign a public IP address
        to each instance launched in a Amazon VPC.
    version_added: "1.8"
  ramdisk_id:
    description:
      - A RAM disk id for the instances.
    version_added: "1.8"
  instance_profile_name:
    description:
      - The name or the Amazon Resource Name (ARN) of the instance profile associated with the IAM role for the instances.
    version_added: "1.8"
  ebs_optimized:
    description:
      - Specifies whether the instance is optimized for EBS I/O (true) or not (false).
    default: false
    version_added: "1.8"
  classic_link_vpc_id:
    description:
      - Id of ClassicLink enabled VPC
    version_added: "2.0"
  classic_link_vpc_security_groups:
    description:
      - A list of security group IDs with which to associate the ClassicLink VPC instances.
    version_added: "2.0"
  vpc_id:
    description:
      - VPC ID, used when resolving security group names to IDs.
    version_added: "2.4"
  instance_id:
    description:
      - The Id of a running instance to use as a basis for a launch configuration. Can be used in place of image_id and instance_type.
    version_added: "2.4"
  placement_tenancy:
    description:
      - Determines whether the instance runs on single-tenant harware or not.
    default: 'default'
    version_added: "2.4"

extends_documentation_fragment:
    - aws
    - ec2

requirements:
    - boto3 >= 1.4.4

'''

EXAMPLES = '''

# create a launch configuration using an AMI image and instance type as a basis

- name: note that encrypted volumes are only supported in >= Ansible 2.4
  ec2_lc:
    name: special
    image_id: ami-XXX
    key_name: default
    security_groups: ['group', 'group2' ]
    instance_type: t1.micro
    volumes:
    - device_name: /dev/sda1
      volume_size: 100
      volume_type: io1
      iops: 3000
      delete_on_termination: true
      encrypted: true
    - device_name: /dev/sdb
      ephemeral: ephemeral0

# create a launch configuration using a running instance id as a basis

- ec2_lc:
    name: special
    instance_id: i-00a48b207ec59e948
    key_name: default
    security_groups: ['launch-wizard-2' ]
    volumes:
    - device_name: /dev/sda1
      volume_size: 120
      volume_type: io1
      iops: 3000
      delete_on_termination: true

# create a launch configuration to omit the /dev/sdf EBS device that is included in the AMI image

- ec2_lc:
    name: special
    image_id: ami-XXX
    key_name: default
    security_groups: ['group', 'group2' ]
    instance_type: t1.micro
    volumes:
    - device_name: /dev/sdf
      no_device: true
'''

RETURN = '''
arn:
  description: The Amazon Resource Name of the launch configuration.
  returned: when I(state=present)
  type: string
  sample: arn:aws:autoscaling:us-east-1:148830907657:launchConfiguration:888d9b58-d93a-40c4-90cf-759197a2621a:launchConfigurationName/launch_config_name
changed:
  description: Whether the state of the launch configuration has changed.
  returned: always
  type: bool
  sample: false
created_time:
  description: The creation date and time for the launch configuration.
  returned: when I(state=present)
  type: string
  sample: '2017-11-03 23:46:44.841000'
image_id:
  description: The ID of the Amazon Machine Image used by the launch configuration.
  returned: when I(state=present)
  type: string
  sample: ami-9be6f38c
instance_type:
  description: The instance type for the instances.
  returned: when I(state=present)
  type: string
  sample: t1.micro
name:
  description: The name of the launch configuration.
  returned: when I(state=present)
  type: string
  sample: launch_config_name
result:
  description: The specification details for the launch configuration.
  returned: when I(state=present)
  type: complex
  contains:
    PlacementTenancy:
      description: The tenancy of the instances, either default or dedicated.
      returned: when I(state=present)
      type: string
      sample: default
    associate_public_ip_address:
      description: (EC2-VPC) Indicates whether to assign a public IP address to each instance.
      returned: when I(state=present)
      type: NoneType
      sample: null
    block_device_mappings:
      description: A block device mapping, which specifies the block devices.
      returned: when I(state=present)
      type: complex
      contains:
        device_name:
          description: The device name exposed to the EC2 instance (for example, /dev/sdh or xvdh).
          returned: when I(state=present)
          type: string
          sample: /dev/sda1
        ebs:
          description: The information about the Amazon EBS volume.
          returned: when I(state=present)
          type: complex
          contains:
            snapshot_id:
              description: The ID of the snapshot.
              returned: when I(state=present)
              type: NoneType
              sample: null
            volume_size:
              description: The volume size, in GiB.
              returned: when I(state=present)
              type: string
              sample: '100'
        virtual_name:
          description: The name of the virtual device (for example, ephemeral0).
          returned: when I(state=present)
          type: NoneType
          sample: null
    classic_link_vpc_id:
      description: The ID of a ClassicLink-enabled VPC to link your EC2-Classic instances to.
      returned: when I(state=present)
      type: NoneType
      sample: null
    classic_link_vpc_security_groups:
      description: The IDs of one or more security groups for the VPC specified in ClassicLinkVPCId.
      returned: when I(state=present)
      type: list
      sample: []
    created_time:
      description: The creation date and time for the launch configuration.
      returned: when I(state=present)
      type: string
      sample: '2017-11-03 23:46:44.841000'
    delete_on_termination:
      description: Indicates whether the volume is deleted on instance termination.
      returned: when I(state=present)
      type: bool
      sample: true
    ebs_optimized:
      description: Indicates whether the instance is optimized for EBS I/O (true) or not (false).
      returned: when I(state=present)
      type: bool
      sample: false
    image_id:
      description: The ID of the Amazon Machine Image used by the launch configuration.
      returned: when I(state=present)
      type: string
      sample: ami-9be6f38c
    instance_monitoring:
      description: Indicates whether instances in this group are launched with detailed (true) or basic (false) monitoring.
      returned: when I(state=present)
      type: bool
      sample: true
    instance_profile_name:
      description: The name or Amazon Resource Name (ARN) of the instance profile associated with the IAM role for the instance.
      returned: when I(state=present)
      type: string
      sample: null
    instance_type:
      description: The instance type for the instances.
      returned: when I(state=present)
      type: string
      sample: t1.micro
    iops:
      description: The number of I/O operations per second (IOPS) to provision for the volume.
      returned: when I(state=present)
      type: NoneType
      sample: null
    kernel_id:
      description: The ID of the kernel associated with the AMI.
      returned: when I(state=present)
      type: string
      sample: ''
    key_name:
      description: The name of the key pair.
      returned: when I(state=present)
      type: string
      sample: testkey
    launch_configuration_arn:
      description: The Amazon Resource Name (ARN) of the launch configuration.
      returned: when I(state=present)
      type: string
      sample: arn:aws:autoscaling:us-east-1:148830907657:launchConfiguration:888d9b58-d93a-40c4-90cf-759197a2621a:launchConfigurationName/launch_config_name
    member:
      description: ""
      returned: when I(state=present)
      type: string
      sample: "\n      "
    name:
      description: The name of the launch configuration.
      returned: when I(state=present)
      type: string
      sample: launch_config_name
    ramdisk_id:
      description: The ID of the RAM disk associated with the AMI.
      returned: when I(state=present)
      type: string
      sample: ''
    security_groups:
      description: The security groups to associate with the instances.
      returned: when I(state=present)
      type: list
      sample:
      - sg-5e27db2f
    spot_price:
      description: The price to bid when launching Spot Instances.
      returned: when I(state=present)
      type: NoneType
      sample: null
    use_block_device_types:
      description: Indicates whether to suppress a device mapping.
      returned: when I(state=present)
      type: bool
      sample: false
    user_data:
      description: The user data available to the instances.
      returned: when I(state=present)
      type: string
      sample: ''
    volume_type:
      description: The volume type (one of standard, io1, gp2).
      returned: when I(state=present)
      type: NoneType
      sample: null
security_groups:
  description: The security groups to associate with the instances.
  returned: when I(state=present)
  type: list
  sample:
  - sg-5e27db2f

'''


import traceback
from ansible.module_utils.ec2 import (get_aws_connection_info, ec2_argument_spec, camel_dict_to_snake_dict, get_ec2_security_group_ids_from_names,
                                      boto3_conn, snake_dict_to_camel_dict, HAS_BOTO3, AWSRetry)
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule

try:
    import botocore
except ImportError:
    pass

backoff_params = dict(tries=10, delay=3, backoff=1.5)


@AWSRetry.backoff(**backoff_params)
def create_lt(connection, **params):
    """ Creates a launch template """
    try:
        connection.create_launch_template(**params)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json(msg="Failed to create launch template", exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))


@AWSRetry.backoff(**backoff_params)
def create_lt_version(connection, **params):
    """ Creates a new version of an existing launch template """
    try:
        connection.create_launch_template_version(**params)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json(msg="Failed to create launch template version", exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))


@AWSRetry.backoff(**backoff_params)
def describe_lt(connection, launch_template):
    """ Checks for existing launch templates matching the name or id and returns a dict object if found """
    try:
        if launch_template['LaunchTemplateName'] is not None:
            lt = connection.describe_launch_templates(LaunchTemplateNames=[launch_template['LaunchTemplateName']])
            return lt['LaunchTemplates'][0]
        elif launch_template['LaunchTemplateId'] is not None:
            lt = connection.describe_launch_templates(LaunchTemplateIds=[launch_template['LaunchTemplateId']])
            return lt['LaunchTemplates'][0]
    except botocore.exceptions.ClientError:
        return None
    except botocore.exceptions.BotoCoreError as e:
        module.fail_json(msg="Failed to describe the launch template", exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))


@AWSRetry.backoff(**backoff_params)
def describe_lt_version(connection, launch_template, version_number):
    """ Describes a specific version of a launch template """
    try:
        # import pdb; pdb.set_trace();
        if launch_template['LaunchTemplateName'] is not None:
            lt = connection.describe_launch_template_versions(LaunchTemplateName=launch_template['LaunchTemplateName'], Versions=[str(version_number)])
            return lt['LaunchTemplateVersions'][0]
        elif launch_template['LaunchTemplateId'] is not None:
            lt = connection.describe_launch_template_versions(LaunchTemplateId=launch_template['LaunchTemplateId'], Versions=[str(version_number)])
            return lt['LaunchTemplateVersions'][0]
        else:
            module.fail_json(msg="Missing launch template name or id")
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json(msg="Failed to describe launch template version number: %s" % version_number)


@AWSRetry.backoff(**backoff_params)
def delete_lt(connection, launch_template):
    """ Deletes a launch template and all versions """
    try:
        if launch_template['LaunchTemplateName'] is not None:
            lt = connection.delete_launch_template(LaunchTemplateName=launch_template['LaunchTemplateName'])
            return lt
        elif launch_template['LaunchTemplateId'] is not None:
            lt = connection.delete_launch_template(LaunchTemplateId=launch_template['LaunchTemplateId'])
            return lt
        else:
            module.fail_json(msg="Missing launch template name or id")
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json(msg="Failed to delete the launch template", exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))


@AWSRetry.backoff(**backoff_params)
def delete_lt_version(connection, launch_template, ):
    """ Deletes a specific launch template version """
    try:
        if launch_template['LaunchTemplateName'] is not None:
            lt = connection.delete_launch_template_versions(LaunchTemplateName=launch_template['LaunchTemplateName'], Versions=[launch_template['Version']])
            return lt
        elif launch_template['LaunchTemplateId'] is not None:
            lt = connection.delete_launch_template_versions(LaunchTemplateId=launch_template['LaunchTemplateId'], Versions=[launch_template['Version']])
            return lt
        else:
            module.fail_json(msg="Missing launch template name or id")
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json(msg="Failed to delete the launch template version", exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))


def create_launch_template_or_version(connection):
    launch_template = dict()
    results = dict(
        changed=False,
        results=dict()
    )
    name = module.params.get('name')
    version_description = module.params.get('version_description')
    ami_id = module.params.get('ami_id')
    instance_type = module.params.get('instance_type')
    key_name = module.params.get('key_name')
    security_group_ids = module.params.get('security_group_ids')
    security_groups = module.params.get('security_groups')
    cpu_credits = module.params.get('cpu_credits')

    launch_template['LaunchTemplateName'] = name
    launch_template['LaunchTemplateData'] = dict()
    if version_description:
        launch_template['VersionDescription'] = version_description
    if ami_id:
        launch_template['LaunchTemplateData']['ImageId'] = ami_id
    if instance_type:
        launch_template['LaunchTemplateData']['InstanceType'] = instance_type
    if key_name:
        launch_template['LaunchTemplateData']['KeyName'] = key_name
    if security_group_ids:
        launch_template['LaunchTemplateData']['SecurityGroupIds'] = security_group_ids
    if security_groups:
        launch_template['LaunchTemplateData']['SecurityGroups'] = security_groups
    if cpu_credits:
        launch_template['LaunchTemplateData']['CreditSpecification'] = {"CpuCredits": cpu_credits}

    # import pdb; pdb.set_trace();

    lt = describe_lt(connection, launch_template)
    if lt is None:  # Create New Launch Template
        if launch_template['LaunchTemplateData'] is not None:
            create_lt(connection, **launch_template)
            lt = describe_lt(connection, launch_template)
            results['changed'] = True
        else:
            module.fail_json(msg="Launch template data missing.")
    else:   # Create new Version for existing Launch Template
        if (launch_template['LaunchTemplateData'] and launch_template['LaunchTemplateData'] is not None):
        # Diff the existing latest version and our args to ensure idempotence
            lt_latest_version = describe_lt_version(connection, launch_template, lt['LatestVersionNumber'])

            if lt_latest_version['LaunchTemplateData'] != launch_template['LaunchTemplateData']:
                create_lt_version(connection, **launch_template)
                lt = describe_lt(connection, launch_template)
                results['changed'] = True

    lt = describe_lt(connection, launch_template)
    lt_latest_version = describe_lt_version(connection, launch_template, lt['LatestVersionNumber'])

    results['results']['id'] = lt['LaunchTemplateId']
    results['results']['name'] = lt['LaunchTemplateName']
    results['results']['create_time'] = to_text(lt['CreateTime'])
    results['results']['default_version_number'] = lt['DefaultVersionNumber']
    results['results']['latest_version_number'] = lt['LatestVersionNumber']
    results['results']['latest_version'] = dict(
        launch_template_data = lt_latest_version['LaunchTemplateData'],
        create_time = to_text(lt_latest_version['CreateTime'])
    )

    return results


def delete_launch_template_or_version(connection):
    launch_template = dict()
    results = dict(
        changed=False,
        results=dict()
    )
    launch_template['LaunchTemplateName'] = module.params.get('name')
    launch_template['LaunchTemplateId'] = module.params.get('id')
    launch_template['Version'] = module.params.get('version')
    # import pdb; pdb.set_trace();

    if launch_template['Version'] is not None:
        lt_version_to_delete = describe_lt_version(connection, launch_template, launch_template['Version'])
        lt = delete_lt_version(connection, launch_template)
        results['changed'] = True
    else:
        lt = delete_lt(connection, launch_template)
        results['changed'] = True

    return results

def delete_launch_template_version(connection):
    launch_template = dict()
    results = dict(
        changed=False,
        results=dict()
    )

    return results

# def delete_launch_config(connection, module):
#     try:
#         name = module.params.get('name')
#         launch_configs = connection.describe_launch_configurations(LaunchConfigurationNames=[name]).get('LaunchConfigurations')
#         if launch_configs:
#             connection.delete_launch_configuration(LaunchConfigurationName=launch_configs[0].get('LaunchConfigurationName'))
#             module.exit_json(changed=True)
#         else:
#             module.exit_json(changed=False)
#     except botocore.exceptions.ClientError as e:
#         module.fail_json(msg="Failed to delete launch configuration", exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))


def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            name=dict(type='str', required=True),
            id = dict(type='str'),
            state=dict(type='str', default='present'),
            version_description=dict(type='str'),
            ami_id=dict(type='str'),
            instance_type=dict(type='str'),
            key_name=dict(type='str'),
            security_group_ids=dict(type='list'),
            security_groups=dict(type='list'),
            cpu_credits=dict(type='str', allowed_values=['standard', 'unlimited']),
            version=dict(type='str')

            # #TODO: ebs_optimized=dict(type='bool', default=False),
            # #TODO:  iam_instance_profile=dict(
            # #     default=None
            # #     options=dict(
            # #         arn=dict(type='str'),
            # #         name=dict(type='str'),
            # #     ),
            # # ),
            # # TODO: block_device_mapping,
            # # TODO: network_interfaces,
            # ami_id=dict(type='str'),
            # instance_type=dict(type='str'),
            # key_name=dict(type='str'),
            # # TODO: monitoring,
            # # TODO: Placement,
            # # TODO: DisableApiTermination,
            # # TODO: InstanceInitiatedShutdownBehaviour,
            # # TODO: user_data=dict(type='str'),
            # # TODO: TagSpecifications,
            # security_group_ids=dict(type='list'),
            # # TODO: security_group_names=dict(type='list'),
            # # TODO: InstanceMarketOptions,
            # # TODO: CreditSpecification
            # # TODO: CPU Options
        ),
    )

    global module
    module = AnsibleModule(
        argument_spec=argument_spec#,
        # mutually_exclusive=[['user_data', 'user_data_path']]
    )

    if not HAS_BOTO3:
        module.fail_json(msg='boto3 required for this module')

    region, ec2_url, aws_connect_params = get_aws_connection_info(module, boto3=True)
    connection = boto3_conn(module,
                            conn_type='client',
                            resource='ec2',
                            region=region,
                            endpoint=ec2_url,
                            **aws_connect_params)

    state = module.params.get('state')

    if state == 'present':
        results = create_launch_template_or_version(connection)
    elif state == 'absent':
        results = delete_launch_template_or_version(connection)
    #TODO: elif state == 'absent':
    #     delete_launch_config(connection, module)


    module.exit_json(changed=results['changed'], results=results['results'])

if __name__ == '__main__':
    main()
