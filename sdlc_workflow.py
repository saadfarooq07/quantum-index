from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict
import json

class SDLCPhase(Enum):
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"

class RoleType(Enum):
    PRODUCT_MANAGER = "product_manager"
    ARCHITECT = "architect"
    ENGINEER = "engineer"
    QA_ENGINEER = "qa_engineer"

@dataclass
class Role:
    role_type: RoleType
    name: str
    goal: str
    constraints: str
    actions: List[str]

@dataclass
class Action:
    name: str
    description: str
    input_schema: Dict
    output_schema: Dict
    role: RoleType
    phase: SDLCPhase

@dataclass
class WorkflowState:
    current_phase: SDLCPhase
    active_role: RoleType
    completed_actions: List[str]
    pending_actions: List[str]
    artifacts: Dict[str, str]

class SDLCWorkflow:
    def __init__(self):
        self.roles = {
            RoleType.PRODUCT_MANAGER: Role(
                role_type=RoleType.PRODUCT_MANAGER,
                name="Alice",
                goal="Create successful products meeting market demands",
                constraints="Use same language as requirements",
                actions=["WritePRD", "PrepareDocuments"]
            ),
            RoleType.ARCHITECT: Role(
                role_type=RoleType.ARCHITECT,
                name="Bob", 
                goal="Design concise, usable, complete systems",
                constraints="Keep architecture simple, use appropriate open source",
                actions=["WriteDesign"]
            ),
            RoleType.ENGINEER: Role(
                role_type=RoleType.ENGINEER,
                name="Alex",
                goal="Write elegant, readable, extensible code",
                constraints="Follow standards, be modular and maintainable",
                actions=["WriteCode", "WriteCodeReview", "FixBug"]
            ),
            RoleType.QA_ENGINEER: Role(
                role_type=RoleType.QA_ENGINEER,
                name="Charlie",
                goal="Ensure high quality and reliability",
                constraints="Comprehensive test coverage",
                actions=["WriteTest", "RunTest"]
            )
        }
        
        self.actions = {
            "WritePRD": Action(
                name="WritePRD",
                description="Create product requirements document",
                input_schema={"requirements": "str"},
                output_schema={"prd": "str"},
                role=RoleType.PRODUCT_MANAGER,
                phase=SDLCPhase.REQUIREMENTS
            ),
            "WriteDesign": Action(
                name="WriteDesign", 
                description="Create system design document",
                input_schema={"prd": "str"},
                output_schema={"design": "str"},
                role=RoleType.ARCHITECT,
                phase=SDLCPhase.DESIGN
            ),
            "WriteCode": Action(
                name="WriteCode",
                description="Implement features",
                input_schema={"design": "str"},
                output_schema={"code": "str"},
                role=RoleType.ENGINEER,
                phase=SDLCPhase.IMPLEMENTATION
            ),
            "WriteTest": Action(
                name="WriteTest",
                description="Create test cases",
                input_schema={"code": "str"},
                output_schema={"tests": "str"},
                role=RoleType.QA_ENGINEER,
                phase=SDLCPhase.TESTING
            )
        }
        
        self.state = WorkflowState(
            current_phase=SDLCPhase.REQUIREMENTS,
            active_role=RoleType.PRODUCT_MANAGER,
            completed_actions=[],
            pending_actions=["WritePRD"],
            artifacts={}
        )
    
    def to_gguf(self) -> Dict:
        """Convert workflow to GGUF format"""
        return {
            "roles": {role.name: {
                "type": role.role_type.value,
                "goal": role.goal,
                "constraints": role.constraints,
                "actions": role.actions
            } for role in self.roles.values()},
            
            "actions": {action.name: {
                "description": action.description,
                "input_schema": action.input_schema,
                "output_schema": action.output_schema,
                "role": action.role.value,
                "phase": action.phase.value
            } for action in self.actions.values()},
            
            "workflow": {
                "phases": [phase.value for phase in SDLCPhase],
                "transitions": {
                    SDLCPhase.REQUIREMENTS.value: SDLCPhase.DESIGN.value,
                    SDLCPhase.DESIGN.value: SDLCPhase.IMPLEMENTATION.value,
                    SDLCPhase.IMPLEMENTATION.value: SDLCPhase.TESTING.value,
                    SDLCPhase.TESTING.value: SDLCPhase.DEPLOYMENT.value
                }
            }
        }
    
    def save_gguf(self, filename: str):
        """Save workflow as GGUF file"""
        gguf_data = self.to_gguf()
        with open(filename, 'w') as f:
            json.dump(gguf_data, f, indent=2)
            
    @classmethod
    def from_gguf(cls, filename: str) -> 'SDLCWorkflow':
        """Load workflow from GGUF file"""
        with open(filename) as f:
            data = json.load(f)
            
        workflow = cls()
        
        # Restore roles
        for name, role_data in data["roles"].items():
            role_type = RoleType(role_data["type"])
            workflow.roles[role_type] = Role(
                role_type=role_type,
                name=name,
                goal=role_data["goal"],
                constraints=role_data["constraints"],
                actions=role_data["actions"]
            )
            
        # Restore actions
        for name, action_data in data["actions"].items():
            workflow.actions[name] = Action(
                name=name,
                description=action_data["description"],
                input_schema=action_data["input_schema"],
                output_schema=action_data["output_schema"],
                role=RoleType(action_data["role"]),
                phase=SDLCPhase(action_data["phase"])
            )
            
        return workflow

if __name__ == "__main__":
    # Create workflow
    workflow = SDLCWorkflow()
    
    # Save as GGUF
    workflow.save_gguf("sdlc_workflow.gguf")
    
    # Load from GGUF
    loaded = SDLCWorkflow.from_gguf("sdlc_workflow.gguf")
    
    # Verify
    assert workflow.to_gguf() == loaded.to_gguf()
    print("SDLC Workflow GGUF conversion successful!")
