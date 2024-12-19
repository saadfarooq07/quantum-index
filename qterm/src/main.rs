use metal::{Device, CommandQueue};
use std::sync::Arc;

struct MetalContext {
    device: Device,
    command_queue: CommandQueue,
}

impl MetalContext {
    fn new() -> Option<Self> {
        let device = Device::system_default()?;
        let command_queue = device.new_command_queue();
        Some(MetalContext {
            device,
            command_queue,
        })
    }
}

fn main() {
    let runtime = tokio::runtime::Runtime::new()
        .expect("Failed to create Tokio runtime");
    
    let ctx = MetalContext::new()
        .expect("Failed to initialize Metal context");
        
    // Initialize quantum state
    let quantum_state = unsafe {
        quantum_bridge::quantum_create_state(16)
    };
    
    // Example quantum circuit
    unsafe {
        quantum_bridge::quantum_apply_gate(quantum_state, 0, 0); // Apply H gate
        let measurement = quantum_bridge::quantum_measure_state(quantum_state);
        println!("Measurement result: {}", measurement);
        quantum_bridge::quantum_destroy_state(quantum_state);
    }
}

