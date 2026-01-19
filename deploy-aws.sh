#!/bin/bash
set -euo pipefail

# AWS Deployment Script for AI OS
# Usage: ./deploy-aws.sh [environment] [action] [image-uri]
# Example: ./deploy-aws.sh prod deploy
# Example: ./deploy-aws.sh alpha deploy 123456789012.dkr.ecr.us-east-1.amazonaws.com/os-dashboard:v1.0.0-alpha.1

ENVIRONMENT=${1:-dev}
ACTION=${2:-deploy}
IMAGE_URI=${3:-}
AWS_REGION=${AWS_REGION:-us-east-1}
NON_INTERACTIVE=${NON_INTERACTIVE:-${CI:-false}}

# Try to get account ID, but allow script to continue if AWS CLI not configured (for CI)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")

echo "🚀 Deploying AI OS to AWS"
echo "Environment: $ENVIRONMENT"
echo "Action: $ACTION"
echo "Region: $AWS_REGION"
echo "Account ID: $ACCOUNT_ID"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check AWS CLI configuration
check_aws_config() {
    if [ "$NON_INTERACTIVE" != "true" ] && [ "$NON_INTERACTIVE" != "1" ]; then
        if ! aws sts get-caller-identity >/dev/null 2>&1; then
            print_error "AWS CLI not configured. Please run 'aws configure'"
            exit 1
        fi
        print_status "AWS CLI configured ✓"
    elif [ -z "$ACCOUNT_ID" ]; then
        print_warning "AWS CLI not configured (non-interactive mode). Some operations may fail."
    else
        print_status "AWS CLI configured ✓ (non-interactive mode)"
    fi
}

# Build Docker image
build_image() {
    # If IMAGE_URI is provided, skip build (image already built and pushed)
    if [ -n "$IMAGE_URI" ]; then
        print_status "Skipping build (using provided image: $IMAGE_URI)"
        return 0
    fi

    if [ -z "$ACCOUNT_ID" ]; then
        print_error "Cannot build image: AWS account ID not available"
        exit 1
    fi

    print_status "Building Docker image..."
    docker build -t os-dashboard:$ENVIRONMENT .

    print_status "Tagging image for ECR..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

    docker tag os-dashboard:$ENVIRONMENT $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/os-dashboard:$ENVIRONMENT
    docker tag os-dashboard:$ENVIRONMENT $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/os-dashboard:latest

    print_status "Pushing image to ECR..."
    docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/os-dashboard:$ENVIRONMENT
    docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/os-dashboard:latest

    IMAGE_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/os-dashboard:$ENVIRONMENT"
    print_status "Docker image built and pushed ✓"
}

# Deploy infrastructure
deploy_infrastructure() {
    print_status "Deploying infrastructure with CloudFormation..."

    STACK_NAME="os-dashboard-$ENVIRONMENT"

    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION >/dev/null 2>&1; then
        print_status "Updating existing CloudFormation stack..."
        aws cloudformation update-stack \
            --stack-name $STACK_NAME \
            --template-body file://aws-deployment.yml \
            --parameters ParameterKey=EnvironmentName,ParameterValue=$ENVIRONMENT \
            --capabilities CAPABILITY_IAM \
            --region $AWS_REGION

        aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $AWS_REGION
    else
        print_status "Creating new CloudFormation stack..."
        aws cloudformation create-stack \
            --stack-name $STACK_NAME \
            --template-body file://aws-deployment.yml \
            --parameters ParameterKey=EnvironmentName,ParameterValue=$ENVIRONMENT \
            --capabilities CAPABILITY_IAM \
            --region $AWS_REGION

        aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $AWS_REGION
    fi

    print_status "Infrastructure deployed ✓"
}

# Register task definition
register_task_definition() {
    print_status "Registering ECS task definition..."

    if [ -z "$ACCOUNT_ID" ]; then
        print_error "Cannot register task definition: AWS account ID not available"
        exit 1
    fi

    # Determine image URI to use
    local TASK_IMAGE_URI="$IMAGE_URI"
    if [ -z "$TASK_IMAGE_URI" ]; then
        TASK_IMAGE_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/os-dashboard:$ENVIRONMENT"
    fi

    print_status "Using image: $TASK_IMAGE_URI"

    # Replace placeholders in task definition
    sed -e "s|ACCOUNT_ID|$ACCOUNT_ID|g" \
        -e "s|REGION|$AWS_REGION|g" \
        -e "s|ENVIRONMENT|$ENVIRONMENT|g" \
        ecs-task-definition.json > ecs-task-definition-deploy.json

    # Replace image URI using jq if available, otherwise use sed
    if command -v jq >/dev/null 2>&1; then
        jq --arg img "$TASK_IMAGE_URI" '.containerDefinitions[0].image = $img' ecs-task-definition-deploy.json > ecs-task-definition-deploy.tmp.json
        mv ecs-task-definition-deploy.tmp.json ecs-task-definition-deploy.json
    else
        # Fallback: use sed with a pattern that matches the image field
        sed -i.bak "s|\"image\": \"[^\"]*\"|\"image\": \"$TASK_IMAGE_URI\"|g" ecs-task-definition-deploy.json
        rm -f ecs-task-definition-deploy.json.bak
    fi

    aws ecs register-task-definition \
        --cli-input-json file://ecs-task-definition-deploy.json \
        --region $AWS_REGION

    rm -f ecs-task-definition-deploy.json

    print_status "Task definition registered ✓"
}

# Update ECS service
update_service() {
    print_status "Updating ECS service..."

    CLUSTER_NAME="$ENVIRONMENT-cluster"
    SERVICE_NAME="os-dashboard-service"

    # Check if service exists
    if aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION | grep -q "ACTIVE"; then
        print_status "Updating existing service..."
        aws ecs update-service \
            --cluster $CLUSTER_NAME \
            --service $SERVICE_NAME \
            --task-definition os-dashboard-task \
            --region $AWS_REGION
    else
        print_status "Creating new service..."
        aws ecs create-service \
            --cluster $CLUSTER_NAME \
            --service-name $SERVICE_NAME \
            --task-definition os-dashboard-task \
            --desired-count 1 \
            --launch-type FARGATE \
            --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345]}" \
            --region $AWS_REGION
    fi

    print_status "Service updated ✓"
}

# Setup secrets in SSM Parameter Store
setup_secrets() {
    print_status "Setting up secrets in SSM Parameter Store..."

    # Database credentials
    aws ssm put-parameter \
        --name "/$ENVIRONMENT/db/username" \
        --value "osdashboard" \
        --type "SecureString" \
        --region $AWS_REGION \
        --overwrite

    aws ssm put-parameter \
        --name "/$ENVIRONMENT/db/password" \
        --value "$(openssl rand -base64 32)" \
        --type "SecureString" \
        --region $AWS_REGION \
        --overwrite

    # Generate database URL (will be constructed from CloudFormation outputs)
    DB_ENDPOINT=$(aws cloudformation describe-stacks --stack-name os-dashboard-$ENVIRONMENT --query 'Stacks[0].Outputs[?OutputKey==`DBEndpoint`].OutputValue' --output text --region $AWS_REGION)

    aws ssm put-parameter \
        --name "/$ENVIRONMENT/db/url" \
        --value "postgresql://osdashboard:$(aws ssm get-parameter --name "/$ENVIRONMENT/db/password" --with-decryption --query Parameter.Value --output text --region $AWS_REGION)@$DB_ENDPOINT:5432/osdashboard" \
        --type "SecureString" \
        --region $AWS_REGION \
        --overwrite

    # Redis URL
    REDIS_ENDPOINT=$(aws cloudformation describe-stacks --stack-name os-dashboard-$ENVIRONMENT --query 'Stacks[0].Outputs[?OutputKey==`RedisEndpoint`].OutputValue' --output text --region $AWS_REGION)

    aws ssm put-parameter \
        --name "/$ENVIRONMENT/redis/url" \
        --value "redis://$REDIS_ENDPOINT:6379/0" \
        --type "SecureString" \
        --region $AWS_REGION \
        --overwrite

    print_warning "Please set the following secrets manually:"
    echo "  - /$ENVIRONMENT/openai/key"
    echo "  - /$ENVIRONMENT/secret/key"
    print_status "Secrets setup ✓"
}

# Get service status
get_status() {
    print_status "Getting deployment status..."

    CLUSTER_NAME="$ENVIRONMENT-cluster"
    SERVICE_NAME="os-dashboard-service"

    aws ecs describe-services \
        --cluster $CLUSTER_NAME \
        --services $SERVICE_NAME \
        --region $AWS_REGION \
        --query 'services[0].{status:status,runningCount:runningCount,desiredCount:desiredCount}' \
        --output table
}

# Main deployment flow
main() {
    check_aws_config

    # Update ACCOUNT_ID if it wasn't set initially but AWS is now available
    if [ -z "$ACCOUNT_ID" ] && [ "$NON_INTERACTIVE" != "true" ] && [ "$NON_INTERACTIVE" != "1" ]; then
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")
    fi

    case $ACTION in
        "build")
            build_image
            ;;
        "infra")
            deploy_infrastructure
            ;;
        "secrets")
            setup_secrets
            ;;
        "task")
            register_task_definition
            ;;
        "service")
            update_service
            ;;
        "deploy")
            build_image
            deploy_infrastructure
            sleep 30  # Wait for infrastructure
            setup_secrets
            register_task_definition
            update_service
            ;;
        "status")
            get_status
            ;;
        *)
            print_error "Invalid action. Use: build|infra|secrets|task|service|deploy|status"
            exit 1
            ;;
    esac

    print_status "Operation completed successfully! 🎉"
    if [ -n "$IMAGE_URI" ]; then
        print_status "Deployed image: $IMAGE_URI"
    fi
}

main "$@"
