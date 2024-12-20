use crate::effects::quantum_effects::QuantumEffects;
use crate::daemon::resource_monitor::ResourceMonitor;
use crate::handlers::{BinaryStateHandler, LivingStateHandler};
use crate::state_bridge::StateTransition;
use std::sync::Arc;
use tokio::sync::mpsc;

pub struct App {
    effects: Arc<QuantumEffects>,
    monitor: Arc<ResourceMonitor>,
    binary_handler: BinaryStateHandler,
    living_handler: LivingStateHandler,
}

impl App {
    pub fn new() -> Self {
        let effects = Arc::new(QuantumEffects::new());
        let monitor = Arc::new(ResourceMonitor::new());
        
        let (tx, rx) = mpsc::channel(100);
        
        let binary_handler = BinaryStateHandler::new(
            Arc::clone(&effects),
            Arc::clone(&monitor),
            tx
        );
        
        let living_handler = LivingStateHandler::new(
            Arc::clone(&effects),
            Arc::clone(&monitor),
            rx
        );
        
        Self {
            effects,
            monitor,
            binary_handler,
            living_handler,
        }
    }

    pub async fn run(&mut self) {
        // Start resource monitoring
        let monitor = Arc::clone(&self.monitor);
        tokio::spawn(async move {
            monitor.start_monitoring().await;
        });
        
        // Start Living State handler
        let mut living_handler = std::mem::replace(
            &mut self.living_handler,
            LivingStateHandler::new(
                Arc::clone(&self.effects),
                Arc::clone(&self.monitor),
                mpsc::channel(1).1
            )
        );
        
        tokio::spawn(async move {
            living_handler.run().await;
        });
        
        // Main event loop
        self.event_loop().await;
    }

    async fn event_loop(&self) {
        loop {
            if let Some(command) = self.read_input().await {
                self.binary_handler.handle_command(&command).await;
            }
        }
    }

    async fn read_input(&self) -> Option<String> {
        // Read input from terminal
        // This would integrate with your terminal input system
        None
    }
}

