from IPython.core.magic import Magics, magics_class, line_magic, cell_magic
from IPython.core.interactiveshell import InteractiveShell
from typing import Any, Dict, Optional
import ast
import json
from ..quantum.state_manager import EntanglementManager, SuperpositionGenerator
from ..models.nemotron import NemotronModel
from ..core.config import IDEConfig
from ..quantum.advanced_operations import AdvancedQuantumOps

@magics_class
class QuantumMagics(Magics):
    """Custom magic commands for quantum-enhanced IPython"""
    
    def __init__(self, shell: InteractiveShell, config: IDEConfig):
        super().__init__(shell)
        self.config = config
        self.entanglement = EntanglementManager(config.quantum)
        self.superposition = SuperpositionGenerator(config.quantum)
        self.nemotron = NemotronModel(config.model)
        self.context_stack: List[int] = []
        self.quantum_ops = AdvancedQuantumOps(config.quantum_config)
        self.active_context = None

    @line_magic
    def quantum_context(self, line: str) -> None:
        """Create or switch quantum context
        
        Usage: %quantum_context [name]
        """
        if not line:
            self._print_contexts()
            return
            
        # Create new context
        context_id = self.entanglement.create_state(line)
        self.context_stack.append(context_id)
        print(f"Created quantum context {context_id}: {line}")
        
    @line_magic
    def quantum_context_adv(self, line: str) -> None:
        """Create or switch to a quantum context"""
        context_name = line.strip()
        self.active_context = self.quantum_ops.create_memory_state(context_name, {})
        return f"Created quantum context: {context_name}"

    @line_magic
    def quantum_entangle(self, line: str) -> None:
        """Entangle two quantum contexts
        
        Usage: %quantum_entangle context1 context2
        """
        try:
            ctx1, ctx2 = map(int, line.split())
            self.entanglement.entangle_states(ctx1, ctx2)
            print(f"Entangled contexts {ctx1} and {ctx2}")
        except ValueError:
            print("Usage: %quantum_entangle context1 context2")
            
    @line_magic
    def quantum_entangle_adv(self, line: str) -> None:
        """Entangle two quantum states"""
        state1, state2 = line.split()
        entanglement = self.quantum_ops.measure_entanglement(state1.strip(), state2.strip())
        return f"Entanglement measure: {entanglement:.3f}"

    @cell_magic
    def quantum_execute(self, line: str, cell: str) -> Any:
        """Execute code in quantum context
        
        Usage: %%quantum_execute [context_id]
        """
        try:
            context_id = int(line) if line else self.context_stack[-1]
        except (ValueError, IndexError):
            print("Invalid context ID")
            return
            
        # Execute code and update quantum state
        try:
            # Parse and execute code
            tree = ast.parse(cell)
            result = self.shell.run_ast_nodes(tree.body, cell)
            
            # Update quantum state based on execution
            state_changes = self._compute_state_changes(result)
            self.entanglement.propagate_changes(context_id, state_changes)
            
            return result
        except Exception as e:
            print(f"Error executing code: {e}")
            
    @cell_magic
    def quantum_execute_adv(self, line: str, cell: str) -> Any:
        """Execute code in quantum context"""
        if not self.active_context:
            return "No active quantum context. Use %quantum_context first."
        
        # Execute in quantum context
        result = self.shell.run_cell(cell)
        return result

    @line_magic
    def quantum_superposition(self, line: str) -> None:
        """Create superposition of quantum states"""
        states = [s.strip() for s in line.split()]
        superposition = self.quantum_ops.create_superposition(states)
        return f"Created superposition with coherence: {self.quantum_ops.measure_coherence(states[0]):.3f}"

    @line_magic
    def quantum_gate(self, line: str) -> None:
        """Apply quantum gate to state"""
        state, gate = line.split()
        self.quantum_ops.apply_quantum_gate(state.strip(), gate.strip())
        return f"Applied {gate} gate to {state}"

    @line_magic
    def quantum_measure(self, line: str) -> None:
        """Measure quantum state coherence"""
        state = line.strip()
        coherence = self.quantum_ops.measure_coherence(state)
        return f"State coherence: {coherence:.3f}"

    @cell_magic
    def quantum_transform(self, line: str, cell: str) -> None:
        """Transform code using quantum interference"""
        if not self.active_context:
            return "No active quantum context. Use %quantum_context first."
            
        # Create quantum state for code
        code_state = self.quantum_ops.create_memory_state("code", cell)
        
        # Apply interference with active context
        interference = self.quantum_ops.apply_interference(
            "code", self.active_context.name
        )
        
        # Execute transformed code
        result = self.shell.run_cell(cell)
        return result

    @line_magic
    def ai_complete(self, line: str) -> None:
        """Use AI to complete code
        
        Usage: %ai_complete [prompt]
        """
        async def complete():
            try:
                completion = await self.nemotron.generate(line)
                print(completion)
            except Exception as e:
                print(f"Error generating completion: {e}")
                
        import asyncio
        asyncio.run(complete())
        
    @cell_magic
    def ai_transform(self, line: str, cell: str) -> None:
        """Transform code using AI
        
        Usage: %%ai_transform [instruction]
        """
        async def transform():
            try:
                prompt = f"""Transform the following code according to this instruction: {line}

Code:
```python
{cell}
```

Transformed code:"""
                
                result = await self.nemotron.generate(prompt)
                print(result)
            except Exception as e:
                print(f"Error transforming code: {e}")
                
        import asyncio
        asyncio.run(transform())
        
    @line_magic
    def quantum_inspect(self, line: str) -> None:
        """Inspect quantum context state
        
        Usage: %quantum_inspect [context_id]
        """
        try:
            context_id = int(line) if line else self.context_stack[-1]
            state = self.entanglement.states.get(context_id)
            if state:
                print(f"Context {context_id}:")
                print(f"Amplitude shape: {state.amplitude.shape}")
                print(f"Phase shape: {state.phase.shape}")
                print(f"Entangled with: {state.entangled_states}")
            else:
                print(f"No such context: {context_id}")
        except (ValueError, IndexError):
            print("Invalid context ID")
            
    def _print_contexts(self) -> None:
        """Print all quantum contexts"""
        print("\nQuantum Contexts:")
        for context_id, state in self.entanglement.states.items():
            entangled = ", ".join(map(str, state.entangled_states))
            print(f"{context_id}: Entangled with [{entangled}]")
            
    def _compute_state_changes(self, result: Any) -> np.ndarray:
        """Compute quantum state changes from execution result"""
        # Convert result to string representation
        result_str = str(result)
        
        # Hash the result to create a change vector
        import hashlib
        hash_val = int(hashlib.sha256(result_str.encode()).hexdigest(), 16)
        rng = np.random.RandomState(hash_val)
        
        # Create normalized change vector
        changes = rng.randn(self.config.quantum.state_dim)
        return changes / np.linalg.norm(changes)

class IPythonIntegration:
    """IPython integration for quantum IDE"""
    
    def __init__(self, config: IDEConfig):
        self.config = config
        self.shell = self._setup_shell()
        
    def _setup_shell(self) -> InteractiveShell:
        """Set up IPython shell with quantum magics"""
        shell = InteractiveShell.instance()
        
        # Register quantum magics
        quantum_magics = QuantumMagics(shell, self.config)
        shell.register_magics(quantum_magics)
        
        # Configure shell
        shell.colors = "Linux"  # Use Linux color scheme
        shell.confirm_exit = False
        shell.separate_in = ""
        
        return shell
        
    def execute(self, code: str) -> Any:
        """Execute code in IPython shell"""
        return self.shell.run_cell(code)
        
    def complete(self, code: str, cursor_pos: int) -> Dict[str, Any]:
        """Get code completions"""
        return self.shell.complete(code, cursor_pos)
        
    def inspect(self, code: str, cursor_pos: int, detail_level: int = 0) -> Dict[str, Any]:
        """Get object inspection"""
        return self.shell.object_inspect(code, cursor_pos, detail_level)
        
    def get_namespace(self) -> Dict[str, Any]:
        """Get current namespace"""
        return self.shell.user_ns

def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    ipython.register_magics(QuantumMagics)
