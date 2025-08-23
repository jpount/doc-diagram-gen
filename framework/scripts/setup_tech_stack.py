#!/usr/bin/env python3
"""
Interactive Target Technology Stack Configuration Script
Generates TARGET_TECH_STACK.md based on user selections or presets
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Try to import yaml, but make it optional
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

class Colors:
    """Terminal colors (cross-platform)"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    @staticmethod
    def enable_windows():
        """Enable ANSI colors on Windows 10+"""
        if sys.platform == 'win32':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                Colors.disable()
    
    @staticmethod
    def disable():
        """Disable colors"""
        for attr in dir(Colors):
            if not attr.startswith('_') and attr.isupper():
                setattr(Colors, attr, '')


class TechStackConfigurator:
    """Interactive technology stack configuration"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.resolve()
        self.framework_dir = self.script_dir.parent
        self.project_root = self.framework_dir.parent
        
        # Configuration files
        self.template_file = self.framework_dir / "templates" / "TARGET_TECH_STACK.template.md"
        self.presets_file = self.framework_dir / "templates" / "tech-stack-presets.yaml"
        self.output_file = self.project_root / "TARGET_TECH_STACK.md"
        
        # Technology stack configuration
        self.tech_stack = {}
        self.presets = {}
        
        # Enable colors
        Colors.enable_windows()
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if sys.platform == 'win32' else 'clear')
    
    def show_header(self):
        """Display configuration header"""
        self.clear_screen()
        print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BLUE}║     Target Technology Stack Configuration Wizard          ║{Colors.RESET}")
        print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
        print()
    
    def load_presets(self):
        """Load technology stack presets"""
        if YAML_AVAILABLE and self.presets_file.exists():
            try:
                with open(self.presets_file) as f:
                    self.presets = yaml.safe_load(f) or {}
                print(f"{Colors.GREEN}✅ Loaded {len(self.presets)} presets{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️  Could not load presets: {e}{Colors.RESET}")
                self.create_default_presets()
        else:
            if not YAML_AVAILABLE:
                print(f"{Colors.YELLOW}ℹ️  YAML support not available, using default presets{Colors.RESET}")
            self.create_default_presets()
    
    def create_default_presets(self):
        """Create default technology stack presets"""
        self.presets = {
            "cloud-native": {
                "name": "Modern Cloud-Native Stack",
                "description": "Microservices architecture with Kubernetes",
                "frontend_framework": "Angular 17+",
                "backend_framework": "Spring Boot 3.x",
                "backend_language": "Java 17+",
                "primary_database": "PostgreSQL 15+",
                "cache_solution": "Redis",
                "message_broker": "Apache Kafka",
                "cloud_provider": "AWS",
                "container_platform": "Kubernetes",
                "api_style": "REST + GraphQL"
            },
            "microsoft": {
                "name": "Microsoft Enterprise Stack",
                "description": "Full Microsoft technology stack",
                "frontend_framework": "Blazor",
                "backend_framework": "ASP.NET Core",
                "backend_language": ".NET 8",
                "primary_database": "SQL Server 2022",
                "cache_solution": "Redis",
                "message_broker": "Azure Service Bus",
                "cloud_provider": "Azure",
                "container_platform": "Azure Container Instances",
                "api_style": "REST with OData"
            },
            "lightweight": {
                "name": "Lightweight Microservices",
                "description": "Node.js based microservices",
                "frontend_framework": "React 18+",
                "backend_framework": "Express/Fastify",
                "backend_language": "Node.js",
                "primary_database": "MongoDB",
                "cache_solution": "Redis",
                "message_broker": "RabbitMQ",
                "cloud_provider": "AWS",
                "container_platform": "AWS ECS",
                "api_style": "REST + GraphQL"
            }
        }
    
    def prompt_selection(self, prompt: str, options: List[str]) -> str:
        """Prompt user for selection from options"""
        print(f"\n{Colors.GREEN}{prompt}{Colors.RESET}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        while True:
            try:
                choice = input(f"Select (1-{len(options)}): ").strip()
                index = int(choice) - 1
                if 0 <= index < len(options):
                    return options[index]
                else:
                    print(f"{Colors.RED}Invalid selection. Please try again.{Colors.RESET}")
            except (ValueError, KeyError):
                print(f"{Colors.RED}Invalid input. Please enter a number.{Colors.RESET}")
    
    def prompt_input(self, prompt: str, default: str = "") -> str:
        """Prompt user for text input"""
        if default:
            user_input = input(f"{Colors.GREEN}{prompt} [{default}]: {Colors.RESET}").strip()
            return user_input if user_input else default
        else:
            return input(f"{Colors.GREEN}{prompt}: {Colors.RESET}").strip()
    
    def select_preset(self) -> Optional[Dict]:
        """Select a technology stack preset"""
        if not self.presets:
            return None
        
        print(f"\n{Colors.CYAN}Available Presets:{Colors.RESET}")
        preset_names = list(self.presets.keys())
        preset_names.append("Custom (Manual Configuration)")
        
        for i, name in enumerate(preset_names, 1):
            if name != "Custom (Manual Configuration)":
                preset = self.presets[name]
                print(f"  {i}. {preset['name']} - {preset['description']}")
            else:
                print(f"  {i}. {name}")
        
        choice = self.prompt_selection("Select a preset", preset_names)
        
        if choice == "Custom (Manual Configuration)":
            return None
        
        return self.presets.get(choice.lower().replace(" ", "-"))
    
    def configure_frontend(self):
        """Configure frontend technologies"""
        print(f"\n{Colors.BLUE}Frontend Configuration{Colors.RESET}")
        print("-" * 40)
        
        frameworks = [
            "Angular 17+",
            "React 18+",
            "Vue 3+",
            "Blazor",
            "Next.js 14+",
            "Svelte",
            "Other"
        ]
        
        self.tech_stack["frontend_framework"] = self.prompt_selection(
            "Select frontend framework", frameworks
        )
        
        if self.tech_stack["frontend_framework"] == "Other":
            self.tech_stack["frontend_framework"] = self.prompt_input("Enter framework name")
        
        # State management
        state_options = {
            "Angular 17+": ["NgRx", "Signals", "Akita", "None"],
            "React 18+": ["Redux", "MobX", "Zustand", "Context API", "None"],
            "Vue 3+": ["Pinia", "Vuex", "None"],
        }
        
        if self.tech_stack["frontend_framework"] in state_options:
            self.tech_stack["state_management"] = self.prompt_selection(
                "Select state management",
                state_options[self.tech_stack["frontend_framework"]]
            )
        else:
            self.tech_stack["state_management"] = self.prompt_input(
                "Enter state management solution", "None"
            )
        
        # UI Library
        ui_libraries = [
            "Material UI",
            "Ant Design",
            "Tailwind CSS",
            "Bootstrap",
            "Custom",
            "None"
        ]
        
        self.tech_stack["ui_library"] = self.prompt_selection(
            "Select UI component library", ui_libraries
        )
    
    def configure_backend(self):
        """Configure backend technologies"""
        print(f"\n{Colors.BLUE}Backend Configuration{Colors.RESET}")
        print("-" * 40)
        
        languages = [
            "Java 17+",
            "C# (.NET 8)",
            "Node.js",
            "Python",
            "Go",
            "Rust",
            "Other"
        ]
        
        self.tech_stack["backend_language"] = self.prompt_selection(
            "Select backend language", languages
        )
        
        # Framework based on language
        framework_options = {
            "Java 17+": ["Spring Boot 3.x", "Quarkus", "Micronaut", "Jakarta EE"],
            "C# (.NET 8)": ["ASP.NET Core", "Minimal APIs", "Orleans"],
            "Node.js": ["Express", "Fastify", "NestJS", "Koa"],
            "Python": ["FastAPI", "Django", "Flask", "Starlette"],
            "Go": ["Gin", "Echo", "Fiber", "Chi"],
            "Rust": ["Actix", "Rocket", "Axum", "Warp"]
        }
        
        if self.tech_stack["backend_language"] in framework_options:
            self.tech_stack["backend_framework"] = self.prompt_selection(
                "Select backend framework",
                framework_options[self.tech_stack["backend_language"]]
            )
        else:
            self.tech_stack["backend_framework"] = self.prompt_input("Enter framework name")
        
        # API Style
        api_styles = ["REST", "GraphQL", "gRPC", "REST + GraphQL", "All"]
        self.tech_stack["api_style"] = self.prompt_selection("Select API style", api_styles)
    
    def configure_database(self):
        """Configure database technologies"""
        print(f"\n{Colors.BLUE}Database Configuration{Colors.RESET}")
        print("-" * 40)
        
        databases = [
            "PostgreSQL",
            "MySQL",
            "SQL Server",
            "Oracle",
            "MongoDB",
            "DynamoDB",
            "Cassandra",
            "Other"
        ]
        
        self.tech_stack["primary_database"] = self.prompt_selection(
            "Select primary database", databases
        )
        
        # NoSQL option
        use_nosql = self.prompt_input("Use additional NoSQL database? (y/n)", "n").lower()
        if use_nosql == 'y':
            nosql_options = ["MongoDB", "DynamoDB", "Redis", "Elasticsearch", "None"]
            self.tech_stack["nosql_database"] = self.prompt_selection(
                "Select NoSQL database", nosql_options
            )
        else:
            self.tech_stack["nosql_database"] = "None"
        
        # Caching
        cache_options = ["Redis", "Memcached", "Hazelcast", "Apache Ignite", "None"]
        self.tech_stack["cache_solution"] = self.prompt_selection(
            "Select caching solution", cache_options
        )
    
    def configure_cloud(self):
        """Configure cloud and infrastructure"""
        print(f"\n{Colors.BLUE}Cloud & Infrastructure Configuration{Colors.RESET}")
        print("-" * 40)
        
        providers = ["AWS", "Azure", "GCP", "Multi-cloud", "On-premise", "Hybrid"]
        self.tech_stack["cloud_provider"] = self.prompt_selection(
            "Select cloud provider", providers
        )
        
        # Container orchestration
        container_platforms = [
            "Kubernetes",
            "AWS ECS",
            "Azure Container Instances",
            "Docker Swarm",
            "OpenShift",
            "None"
        ]
        
        self.tech_stack["container_platform"] = self.prompt_selection(
            "Select container platform", container_platforms
        )
        
        # CI/CD
        cicd_options = [
            "GitHub Actions",
            "GitLab CI",
            "Jenkins",
            "Azure DevOps",
            "CircleCI",
            "ArgoCD"
        ]
        
        self.tech_stack["cicd_pipeline"] = self.prompt_selection(
            "Select CI/CD pipeline", cicd_options
        )
    
    def configure_messaging(self):
        """Configure messaging and event streaming"""
        print(f"\n{Colors.BLUE}Messaging Configuration{Colors.RESET}")
        print("-" * 40)
        
        brokers = [
            "Apache Kafka",
            "RabbitMQ",
            "AWS SQS/SNS",
            "Azure Service Bus",
            "Redis Pub/Sub",
            "None"
        ]
        
        self.tech_stack["message_broker"] = self.prompt_selection(
            "Select message broker", brokers
        )
    
    def generate_tech_stack_file(self):
        """Generate TARGET_TECH_STACK.md file"""
        print(f"\n{Colors.YELLOW}Generating TARGET_TECH_STACK.md...{Colors.RESET}")
        
        # Load template
        if self.template_file.exists():
            template = self.template_file.read_text()
        else:
            template = self.get_default_template()
        
        # Replace placeholders
        output = template
        for key, value in self.tech_stack.items():
            placeholder = f"{{{{{key.upper()}}}}}"
            output = output.replace(placeholder, value)
        
        # Replace remaining placeholders with defaults
        remaining_placeholders = {
            "{{ARCHITECTURE_PATTERN}}": "Microservices",
            "{{PATTERN_JUSTIFICATION}}": "Scalability and maintainability",
            "{{TS_VERSION}}": "5.0+",
            "{{BUILD_TOOL}}": "Webpack",
            "{{FRONTEND_TESTING}}": "Jest + Cypress",
            "{{MOBILE_APPROACH}}": "Progressive Web App",
            "{{API_GATEWAY}}": "Kong",
            "{{DB_VERSION}}": "Latest",
            "{{DB_HOSTING}}": "Cloud-managed",
            "{{SEARCH_ENGINE}}": "Elasticsearch",
            "{{MESSAGING_PATTERN}}": "Event Streaming",
            "{{K8S_DISTRIBUTION}}": "EKS",
            "{{IAC_TOOL}}": "Terraform",
            "{{DEPLOYMENT_STRATEGY}}": "Blue-Green",
            "{{IDENTITY_PROVIDER}}": "Okta",
            "{{AUTH_PROTOCOL}}": "OAuth 2.0 + OIDC",
            "{{SECRETS_MANAGEMENT}}": "HashiCorp Vault",
            "{{COMPLIANCE_STANDARDS}}": "SOC 2",
            "{{APM_SOLUTION}}": "Datadog",
            "{{LOGGING_SOLUTION}}": "ELK Stack",
            "{{METRICS_SOLUTION}}": "Prometheus + Grafana",
            "{{LEGACY_COMPATIBILITY}}": "API Gateway for legacy integration",
            "{{MIGRATION_WINDOW}}": "6-12 months",
            "{{PERFORMANCE_REQUIREMENTS}}": "< 200ms response time",
            "{{TEAM_SKILLS}}": "Full-stack development",
            "{{BUDGET_CONSTRAINTS}}": "Optimize for cloud costs",
            "{{TIMELINE}}": "12-18 months"
        }
        
        for placeholder, default in remaining_placeholders.items():
            output = output.replace(placeholder, default)
        
        # Add generation timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"<!-- Generated by Tech Stack Configurator on {timestamp} -->\n\n"
        output = header + output
        
        # Write file
        self.output_file.write_text(output)
        print(f"{Colors.GREEN}✅ Generated TARGET_TECH_STACK.md{Colors.RESET}")
    
    def get_default_template(self) -> str:
        """Get default template if file not found"""
        return """# Target Technology Stack Configuration

## Architecture Pattern
**Pattern:** {{ARCHITECTURE_PATTERN}}
**Justification:** {{PATTERN_JUSTIFICATION}}

## Frontend Technologies
- **Framework:** {{FRONTEND_FRAMEWORK}}
- **State Management:** {{STATE_MANAGEMENT}}
- **UI Library:** {{UI_LIBRARY}}

## Backend Technologies
- **Language:** {{BACKEND_LANGUAGE}}
- **Framework:** {{BACKEND_FRAMEWORK}}
- **API Style:** {{API_STYLE}}

## Data Technologies
- **Primary Database:** {{PRIMARY_DATABASE}}
- **NoSQL Database:** {{NOSQL_DATABASE}}
- **Cache:** {{CACHE_SOLUTION}}

## Messaging
- **Message Broker:** {{MESSAGE_BROKER}}

## Cloud & Infrastructure
- **Cloud Provider:** {{CLOUD_PROVIDER}}
- **Container Platform:** {{CONTAINER_PLATFORM}}
- **CI/CD:** {{CICD_PIPELINE}}
"""
    
    def show_summary(self):
        """Show configuration summary"""
        print(f"\n{Colors.CYAN}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.CYAN}Technology Stack Summary{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")
        
        categories = [
            ("Frontend", ["frontend_framework", "state_management", "ui_library"]),
            ("Backend", ["backend_language", "backend_framework", "api_style"]),
            ("Data", ["primary_database", "nosql_database", "cache_solution"]),
            ("Infrastructure", ["cloud_provider", "container_platform", "cicd_pipeline"]),
            ("Messaging", ["message_broker"])
        ]
        
        for category, keys in categories:
            print(f"{Colors.BLUE}{category}:{Colors.RESET}")
            for key in keys:
                if key in self.tech_stack:
                    display_key = key.replace("_", " ").title()
                    print(f"  • {display_key}: {self.tech_stack[key]}")
            print()
        
        print(f"{Colors.GREEN}✅ Configuration saved to: TARGET_TECH_STACK.md{Colors.RESET}")
    
    def run(self, preset_name: Optional[str] = None):
        """Main configuration flow"""
        self.show_header()
        self.load_presets()
        
        if preset_name:
            # Use specified preset
            if preset_name in self.presets:
                self.tech_stack = self.presets[preset_name].copy()
                print(f"{Colors.GREEN}Using preset: {preset_name}{Colors.RESET}")
            else:
                print(f"{Colors.RED}Preset '{preset_name}' not found{Colors.RESET}")
                return
        else:
            # Interactive selection
            preset = self.select_preset()
            
            if preset:
                self.tech_stack = preset.copy()
                print(f"\n{Colors.GREEN}Using preset configuration{Colors.RESET}")
                
                # Option to customize
                customize = self.prompt_input("Customize this preset? (y/n)", "n").lower()
                if customize == 'y':
                    self.configure_frontend()
                    self.configure_backend()
                    self.configure_database()
                    self.configure_cloud()
                    self.configure_messaging()
            else:
                # Manual configuration
                self.configure_frontend()
                self.configure_backend()
                self.configure_database()
                self.configure_cloud()
                self.configure_messaging()
        
        # Generate file
        self.generate_tech_stack_file()
        self.show_summary()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Interactive Target Technology Stack Configuration"
    )
    parser.add_argument(
        "--preset",
        choices=["cloud-native", "microsoft", "lightweight"],
        help="Use a preset configuration"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    
    args = parser.parse_args()
    
    if args.no_color:
        Colors.disable()
    
    configurator = TechStackConfigurator()
    configurator.run(preset_name=args.preset)


if __name__ == "__main__":
    main()