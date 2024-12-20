use crate::{
    binary_state::BinaryState,
    config::Config,
    error::{Error, Result},
    event_bus::{EventBus, EventType},
    init::SystemInitializer,
    living_state::LivingState,
    monitor::SystemMonitor,
    quantum_bridge::QuantumBridge,
    state_bridge::StateBridge,
};
use log::{debug, error, info, warn};
use tokio::sync::RwLock;
use std::{sync::Arc, time::Duration};

/// Main system orchestrator that coordinates all quantum terminal components
pub struct Orchestrator {
    config: Arc<RwLock<Config>>,
    event_bus: Arc<EventBus>,
    quantum_bridge: Arc<QuantumBridge>,
    state_bridge: Arc<StateBridge>,
    binary_state: Arc<RwLock<BinaryState>>,
    living_state: Arc<RwLock<LivingState>>,
    monitor: Arc<SystemMonitor>,
    initializer: SystemInitializer,
}

impl Orchestrator {
    /// Create a new orchestrator instance
    pub async fn new(config: Config) -> Result<Self> {
        info!("Initializing quantum terminal orchestrator");
        let config = Arc::new(RwLock::new(config));
        let event_bus = Arc::new(EventBus::new());
        let initializer = SystemInitializer::new(config.clone())?;
        
        let quantum_bridge = Arc::new(QuantumBridge::new(config.clone()).await?);
        let state_bridge = Arc::new(StateBridge::new(config.clone(), quantum_bridge.clone())?);
        let binary_state = Arc::new(RwLock::new(BinaryState::new()?));
        let living_state = Arc::new(RwLock::new(LivingState::new()?));
        let monitor = Arc::new(SystemMonitor::new(config.clone())?);

        Ok(Self {
            config,
            event_bus,
            quantum_bridge,
            state_bridge,
            binary_state,
            living_state, 
            monitor,
            initializer,
        })
    }

    /// Initialize the system and start all components
    pub async fn initialize(&self) -> Result<()> {
        info!("Starting system initialization");
        
        // Initialize core systems
        self.initializer.initialize().await?;
        
        // Start monitoring
        self.monitor.start_monitoring();
        
        // Initialize quantum systems
        self.quantum_bridge.initialize().await?;
        self.state_bridge.initialize().await?;
        
        // Initialize state management
        let mut binary = self.binary_state.write().await;
        binary.initialize()?;
        drop(binary);
        
        let mut living = self.living_state.write().await;
        living.initialize()?;
        drop(living);
        
        info!("System initialization complete");
        Ok(())
    }

    /// Handle system-wide state updates
    pub async fn update_states(&self) -> Result<()> {
        debug!("Processing state updates");
        
        // Update quantum states
        self.quantum_bridge.evolve_states().await?;
        
        // Update classical states
        let mut binary = self.binary_state.write().await;
        binary.update()?;
        drop(binary);
        
        // Update emotional/consciousness states
        let mut living = self.living_state.write().await;
        living.evolve().await?;
        drop(living);
        
        // Synchronize states
        self.state_bridge.synchronize().await?;
        
        Ok(())
    }

    /// Monitor system resources and performance
    pub async fn monitor_resources(&self) -> Result<()> {
        let metrics = self.monitor.collect_metrics().await?;
        
        if metrics.requires_optimization() {
            warn!("Resource constraints detected, initiating optimization");
            self.optimize_resources().await?;
        }
        
        Ok(())
    }

    /// Optimize resource usage based on monitoring data
    async fn optimize_resources(&self) -> Result<()> {
        debug!("Optimizing system resources");
        
        // Adjust quantum processing parameters
        let mut config = self.config.write().await;
        config.adjust_quantum_parameters()?;
        drop(config);
        
        // Optimize state management
        self.state_bridge.optimize().await?;
        self.quantum_bridge.optimize().await?;
        
        Ok(())
    }

    /// Handle error recovery and fault tolerance
    pub async fn handle_error(&self, error: Error) -> Result<()> {
        error!("System error detected: {:?}", error);
        
        // Notify components
        self.event_bus.publish(EventType::SystemError(error.clone())).await?;
        
        // Attempt recovery
        match error {
            Error::QuantumStateError(_) => {
                self.quantum_bridge.recover().await?;
            }
            Error::ResourceError(_) => {
                self.optimize_resources().await?;
            }
            _ => {
                // Default recovery: restart affected subsystem
                self.restart_subsystem(&error).await?;
            }
        }
        
        Ok(())
    }

    /// Restart a specific subsystem
    async fn restart_subsystem(&self, error: &Error) -> Result<()> {
        warn!("Restarting subsystem due to error: {:?}", error);
        
        // Determine affected subsystem and restart
        match error {
            Error::BinaryStateError(_) => {
                let mut binary = self.binary_state.write().await;
                binary.reset()?;
            }
            Error::LivingStateError(_) => {
                let mut living = self.living_state.write().await;
                living.reset()?;
            }
            _ => {
                // Full system restart if unknown error
                self.initialize().await?;
            }
        }
        
        Ok(())
    }

    /// Gracefully shut down the system
    pub async fn shutdown(&self) -> Result<()> {
        info!("Initiating system shutdown");
        
        // Stop monitoring
        self.monitor.stop_monitoring();
        
        // Save states
        let binary = self.binary_state.read().await;
        binary.save_state()?;
        drop(binary);
        
        let living = self.living_state.read().await;
        living.save_state()?;
        drop(living);
        
        // Clean up resources
        self.quantum_bridge.cleanup().await?;
        self.state_bridge.cleanup().await?;
        
        info!("System shutdown complete");
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_orchestrator_lifecycle() {
        let config = Config::default();
        let orchestrator = Orchestrator::new(config).await.unwrap();
        
        // Test initialization
        assert!(orchestrator.initialize().await.is_ok());
        
        // Test state updates
        assert!(orchestrator.update_states().await.is_ok());
        
        // Test monitoring
        assert!(orchestrator.monitor_resources().await.is_ok());
        
        // Test shutdown
        assert!(orchestrator.shutdown().await.is_ok());
    }
}

