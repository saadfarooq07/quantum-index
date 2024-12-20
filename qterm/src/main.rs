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
    
    let ctx = Arc::new(MetalContext::new()
        .expect("Failed to initialize Metal context"));
        
    // Initialize states
    let binary_state = BinaryState::new();
    let living_state = LivingState::new(ctx.clone());
    
    // Initialize state bridge for communication
    let state_bridge = StateBridge::new(binary_state.clone(), living_state.clone());
    
    // Start visualization engine
    let vis_engine = visualization::Engine::new(ctx.clone());
    let vis_handle = tokio::spawn(async move {
        vis_engine.run().await;
    });
    
    // Run the binary state terminal interface
    let term_handle = tokio::spawn(async move {
        binary_state.run().await;
    });
    
    // Wait for completion
    runtime.block_on(async {
        tokio::try_join!(vis_handle, term_handle)
            .expect("Failed to run state handlers");
    });
}

