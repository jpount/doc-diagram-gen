# Target Technology Stack Configuration Template

## Overview
This is a template file for configuring target technology stacks. Copy this to your project root as TARGET_TECH_STACK.md and customize for your specific modernization project.

## Quick Configuration Options

### Common Enterprise Stacks

#### Option 1: Modern Cloud-Native Stack
- **Frontend**: Angular 17+ with TypeScript
- **Backend**: Spring Boot 3.x (Java 17+)
- **Database**: PostgreSQL 15+
- **Cache**: Redis
- **Messaging**: Apache Kafka
- **Cloud**: AWS/Azure with Kubernetes
- **API**: REST + GraphQL

#### Option 2: Microsoft Enterprise Stack
- **Frontend**: Blazor or React
- **Backend**: .NET 8 with ASP.NET Core
- **Database**: SQL Server 2022
- **Cache**: Redis
- **Messaging**: Azure Service Bus
- **Cloud**: Azure with AKS
- **API**: REST with OData

#### Option 3: Lightweight Microservices Stack
- **Frontend**: React 18+ or Vue 3
- **Backend**: Node.js with Express/Fastify
- **Database**: MongoDB + PostgreSQL
- **Cache**: Redis
- **Messaging**: RabbitMQ
- **Cloud**: AWS with ECS/Fargate
- **API**: REST + GraphQL

---

## Detailed Configuration

### Target Architecture Pattern
**Pattern:** {{ARCHITECTURE_PATTERN}}
<!-- Options: Microservices | Modular Monolith | Serverless | Event-Driven -->
**Justification:** {{PATTERN_JUSTIFICATION}}

## Frontend Technologies

### Primary Framework
- **Framework:** {{FRONTEND_FRAMEWORK}}
<!-- Options: Angular 17+ | React 18+ | Vue 3+ | Blazor | Next.js -->
- **TypeScript Version:** {{TS_VERSION}}
- **State Management:** {{STATE_MANAGEMENT}}
<!-- Options: NgRx | Redux | MobX | Zustand | Signals | Pinia -->
- **UI Component Library:** {{UI_LIBRARY}}
<!-- Options: Angular Material | MUI | Ant Design | Tailwind UI | Custom -->
- **Build Tool:** {{BUILD_TOOL}}
<!-- Options: Webpack | Vite | esbuild | Turbopack -->
- **Testing:** {{FRONTEND_TESTING}}
<!-- Options: Jest | Vitest | Cypress | Playwright -->

### Mobile Strategy
- **Approach:** {{MOBILE_APPROACH}}
<!-- Options: Progressive Web App | React Native | Flutter | Native | None -->

## Backend Technologies

### Primary Language & Framework
- **Language:** {{BACKEND_LANGUAGE}}
<!-- Options: Java 17+ | C# (.NET 8) | Node.js | Python | Go -->
- **Framework:** {{BACKEND_FRAMEWORK}}
<!-- Options: Spring Boot 3.x | ASP.NET Core | Express | FastAPI | Gin -->
- **API Style:** {{API_STYLE}}
<!-- Options: REST | GraphQL | gRPC | Mixed -->
- **API Gateway:** {{API_GATEWAY}}
<!-- Options: Spring Cloud Gateway | Kong | AWS API Gateway | Azure API Management | None -->

## Data Technologies

### Primary Database
- **Type:** {{PRIMARY_DATABASE}}
<!-- Options: PostgreSQL | MySQL | SQL Server | Oracle | MongoDB -->
- **Version:** {{DB_VERSION}}
- **Hosting:** {{DB_HOSTING}}
<!-- Options: Self-managed | RDS | Azure SQL | Cloud SQL -->

### NoSQL/Document Store
- **Type:** {{NOSQL_DATABASE}}
<!-- Options: MongoDB | DynamoDB | Cosmos DB | Cassandra | None -->

### Caching
- **Solution:** {{CACHE_SOLUTION}}
<!-- Options: Redis | Memcached | Hazelcast | Apache Ignite | None -->

### Search
- **Engine:** {{SEARCH_ENGINE}}
<!-- Options: Elasticsearch | OpenSearch | Solr | Azure Cognitive Search | None -->

## Messaging & Event Streaming

### Message Broker
- **Primary:** {{MESSAGE_BROKER}}
<!-- Options: Apache Kafka | RabbitMQ | AWS SQS/SNS | Azure Service Bus | None -->
- **Pattern:** {{MESSAGING_PATTERN}}
<!-- Options: Pub/Sub | Queue | Event Streaming | Mixed -->

## Cloud & Infrastructure

### Cloud Platform
- **Provider:** {{CLOUD_PROVIDER}}
<!-- Options: AWS | Azure | GCP | Multi-cloud | On-premise | Hybrid -->

### Container Orchestration
- **Platform:** {{CONTAINER_PLATFORM}}
<!-- Options: Kubernetes | AWS ECS | Azure Container Instances | Docker Swarm | None -->
- **Distribution:** {{K8S_DISTRIBUTION}}
<!-- Options: AKS | EKS | GKE | OpenShift | Rancher | Self-managed -->

### Infrastructure as Code
- **Tool:** {{IAC_TOOL}}
<!-- Options: Terraform | CloudFormation | ARM Templates | Pulumi | Ansible -->

### CI/CD
- **Pipeline:** {{CICD_PIPELINE}}
<!-- Options: GitHub Actions | GitLab CI | Jenkins | Azure DevOps | CircleCI -->
- **Deployment Strategy:** {{DEPLOYMENT_STRATEGY}}
<!-- Options: Blue-Green | Canary | Rolling | Feature Flags -->

## Security & Compliance

### Authentication & Authorization
- **Identity Provider:** {{IDENTITY_PROVIDER}}
<!-- Options: Okta | Auth0 | Azure AD | Keycloak | AWS Cognito | Custom -->
- **Protocol:** {{AUTH_PROTOCOL}}
<!-- Options: OAuth 2.0 | OIDC | SAML | JWT -->

### Secrets Management
- **Solution:** {{SECRETS_MANAGEMENT}}
<!-- Options: HashiCorp Vault | AWS Secrets Manager | Azure Key Vault | Kubernetes Secrets -->

### Compliance Requirements
- **Standards:** {{COMPLIANCE_STANDARDS}}
<!-- Options: PCI DSS | HIPAA | GDPR | SOC 2 | ISO 27001 | None -->

## Observability & Monitoring

### Application Performance Monitoring
- **APM:** {{APM_SOLUTION}}
<!-- Options: Datadog | New Relic | Dynatrace | AppDynamics | OpenTelemetry -->

### Logging
- **Aggregation:** {{LOGGING_SOLUTION}}
<!-- Options: ELK Stack | Splunk | CloudWatch | Azure Monitor -->

### Metrics
- **Solution:** {{METRICS_SOLUTION}}
<!-- Options: Prometheus + Grafana | CloudWatch | Azure Monitor | Datadog -->

## Migration Constraints

### Technical Constraints
- **Legacy System Compatibility:** {{LEGACY_COMPATIBILITY}}
- **Data Migration Window:** {{MIGRATION_WINDOW}}
- **Performance Requirements:** {{PERFORMANCE_REQUIREMENTS}}

### Organizational Constraints
- **Team Skills:** {{TEAM_SKILLS}}
- **Budget:** {{BUDGET_CONSTRAINTS}}
- **Timeline:** {{TIMELINE}}

---

## Template Usage Instructions

### Method 1: Manual Configuration
1. Copy this file to project root as `TARGET_TECH_STACK.md`
2. Replace all `{{PLACEHOLDER}}` values with your choices
3. Remove template instructions and comments

### Method 2: Use Setup Script
Run the interactive setup script:
```bash
./setup-tech-stack.sh
```

### Method 3: Quick Presets
Use a preset configuration:
```bash
./setup-tech-stack.sh --preset cloud-native
./setup-tech-stack.sh --preset microsoft
./setup-tech-stack.sh --preset lightweight
```

### Method 4: Environment Variables
Set environment variables and run:
```bash
export TECH_STACK_PRESET="cloud-native"
export FRONTEND_FRAMEWORK="Angular 17+"
export BACKEND_FRAMEWORK="Spring Boot 3.x"
./setup-tech-stack.sh --from-env
```