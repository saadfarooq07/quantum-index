use super::gates::Gate;
use super::quantum_state::QuantumState;

pub struct CircuitBuilder {
    operations: Vec<(Box<dyn Gate>, usize)>,
}

impl CircuitBuilder {
    pub fn new() -> Self {
        Self {
            operations: Vec::new(),
        }
    }

    pub fn add_gate(&mut self, gate: Box<dyn Gate>, target: usize) -> &mut Self {
        self.operations.push((gate, target));
        self
    }

    pub fn build(self) -> Circuit {
        Circuit {
            operations: self.operations,
        }
    }
}

pub struct Circuit {
    operations: Vec<(Box<dyn Gate>, usize)>,
}

impl Circuit {
    pub fn execute(&self, state: &mut QuantumState) {
        for (gate, target) in &self.operations {
            state.apply_gate(gate.as_ref(), *target);
        }
    }
}

