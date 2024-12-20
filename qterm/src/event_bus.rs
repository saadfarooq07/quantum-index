use tokio::sync::broadcast;
use serde::{Serialize, Deserialize};
use std::sync::Arc;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum Priority {
    High,
    Normal,
    Low,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum StateEvent {
    // Quantum operations
    QuantumStateUpdate(QuantumState),
    QuantumOperationComplete(QuantumResult),
    QuantumError(QuantumError),
    
    // GPU status
    GpuStatusUpdate(GpuStatus),
    GpuMetrics(GpuMetrics),
    GpuError(GpuError),
    
    // System events
    BinaryStateUpdate(BinaryState),
    LivingStateUpdate(LivingState),
    ResourceUpdate(ResourceMetrics),
    EmotionalUpdate(EmotionalState),
    CommandExecuted(CommandResult),
    ErrorOccurred(ErrorState),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BinaryState {
    pub current_command: String,
    pub terminal_buffer: Vec<String>,
    pub cursor_position: (u16, u16),
    pub mode: TerminalMode,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LivingState {
    pub quantum_field: QuantumField,
    pub emotional_state: EmotionalState,
    pub particle_system: ParticleState,
    pub transition_state: TransitionState,
}

pub struct PrioritizedEvent {
    priority: Priority,
    event: StateEvent,
    timestamp: std::time::SystemTime,
}

pub struct EventMetrics {
    processed_count: u64,
    error_count: u64,
    avg_processing_time: std::time::Duration,
    last_processed: std::time::SystemTime,
}

pub struct EventFilter {
    priority: Option<Priority>,
    event_types: Vec<String>,
    source: Option<String>,
}

pub struct EventBus {
    tx: broadcast::Sender<PrioritizedEvent>,
    rx: broadcast::Receiver<PrioritizedEvent>,
    state: Arc<EventState>,
    metrics: Arc<parking_lot::RwLock<EventMetrics>>,
    filters: Vec<EventFilter>,
}

impl EventBus {
    /// Creates a new EventBus instance with default settings
    pub fn new() -> Self {
        let (tx, rx) = broadcast::channel(1024);
        let state = Arc::new(EventState::default());
        let metrics = Arc::new(parking_lot::RwLock::new(EventMetrics {
            processed_count: 0,
            error_count: 0,
            avg_processing_time: std::time::Duration::from_secs(0),
            last_processed: std::time::SystemTime::now(),
        }));
        Self { 
            tx, 
            rx, 
            state,
            metrics,
            filters: Vec::new(),
        }
    }

    /// Adds a new event filter
    pub fn add_filter(&mut self, filter: EventFilter) {
        self.filters.push(filter);
    }

    /// Gets current event processing metrics
    pub fn get_metrics(&self) -> EventMetrics {
        self.metrics.read().clone()
    }

    /// Broadcasts an event with specified priority
    pub async fn broadcast(
        &self,
        event: StateEvent,
        priority: Priority,
    ) -> Result<(), broadcast::error::SendError<PrioritizedEvent>> {
        // Apply filters
        if !self.should_process(&event) {
            return Ok(());
        }

        let prioritized = PrioritizedEvent {
            priority,
            event,
            timestamp: std::time::SystemTime::now(),
        };

        self.tx.send(prioritized)
    }

    /// Determines if an event should be processed based on filters
    fn should_process(&self, event: &StateEvent) -> bool {
        for filter in &self.filters {
            // Apply filter logic here
            // Return false if event should be filtered out
        }
        true
    }

    pub async fn subscribe(&self) -> broadcast::Receiver<StateEvent> {
        self.tx.subscribe()
    }

    /// Handles an incoming event with metrics collection
    pub async fn handle_event(&self, prioritized: PrioritizedEvent) {
        let start_time = std::time::SystemTime::now();
        
        let result = match prioritized.event {
            // Quantum operations
            StateEvent::QuantumStateUpdate(state) => self.handle_quantum_update(state).await,
            StateEvent::QuantumOperationComplete(result) => self.handle_quantum_result(result).await,
            StateEvent::QuantumError(error) => self.handle_quantum_error(error).await,
            
            // GPU status 
            StateEvent::GpuStatusUpdate(status) => self.handle_gpu_status(status).await,
            StateEvent::GpuMetrics(metrics) => self.handle_gpu_metrics(metrics).await,
            StateEvent::GpuError(error) => self.handle_gpu_error(error).await,
            
            // System events
            StateEvent::BinaryStateUpdate(state) => self.handle_binary_update(state).await,
            StateEvent::LivingStateUpdate(state) => self.handle_living_update(state).await,
            StateEvent::ResourceUpdate(metrics) => self.handle_resource_update(metrics).await,
            StateEvent::EmotionalUpdate(state) => self.handle_emotional_update(state).await,
            StateEvent::CommandExecuted(result) => self.handle_command_result(result).await,
            StateEvent::ErrorOccurred(error) => self.handle_error(error).await,
        };

        // Update metrics
        let mut metrics = self.metrics.write();
        metrics.processed_count += 1;
        if result.is_err() {
            metrics.error_count += 1;
        }
        metrics.last_processed = std::time::SystemTime::now();
        metrics.avg_processing_time = (metrics.avg_processing_time + start_time.elapsed().unwrap()) / 2;
    }
}

