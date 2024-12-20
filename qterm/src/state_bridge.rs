use tokio::sync::broadcast;
use std::sync::Arc;
use parking_lot::RwLock;

pub struct StateBridge {
    state_tx: broadcast::Sender<super::binary_state::StateUpdate>,
    shared_state: Arc<RwLock<SharedState>>,
    gpu_context: Arc<GpuContext>,
    event_bus: EventBus,
    persistence: StatePersistence,
}

#[derive(Clone, Debug)]
struct SharedState {
    quantum_state: QuantumState,
    emotional_state: EmotionalState,
    last_command: Option<String>,
    last_response: Option<String>,
    error_count: u32,
    processing_status: ProcessingStatus,
    metrics: StateMetrics,
}

#[derive(Clone, Debug)]
struct QuantumState {
    amplitudes: Vec<Complex64>,
    num_qubits: usize,
    gpu_buffer: Option<GpuBuffer>,
}

#[derive(Clone, Debug)]
struct EmotionalState {
    valence: f32,  // -1.0 to 1.0
    arousal: f32,  // 0.0 to 1.0
    dominance: f32,  // 0.0 to 1.0
}

#[derive(Clone, Debug)]
struct StateMetrics {
    last_transition_time: std::time::Duration,
    gpu_utilization: f32,
    state_fidelity: f32,
}

#[derive(Clone, Debug)]
enum ProcessingStatus {
    Idle,
    Processing,
    Error(StateError),
    Transitioning { progress: f32 },
    Recovering { checkpoint: u64 },
}

#[derive(Debug, thiserror::Error)]
enum StateError {
    #[error("GPU acceleration error: {0}")]
    GpuError(String),
    #[error("Invalid quantum state: {0}")]
    InvalidState(String),
    #[error("State persistence error: {0}")]
    PersistenceError(String),
    #[error("Emotional state error: {0}")]
    EmotionalError(String),
}

impl StateBridge {
    pub async fn new(
        state_tx: broadcast::Sender<super::binary_state::StateUpdate>,
        config: &Config,
    ) -> Result<Self, StateError> {
        let gpu_context = GpuContext::new(config).await?;
        let event_bus = EventBus::new();
        let persistence = StatePersistence::new(config)?;
        
        let initial_state = if let Some(saved) = persistence.load_last_checkpoint()? {
            saved
        } else {
            SharedState {
                quantum_state: QuantumState::new_ground_state(config.num_qubits),
                emotional_state: EmotionalState::default(),
                last_command: None,
                last_response: None,
                error_count: 0,
                processing_status: ProcessingStatus::Idle,
                metrics: StateMetrics::default(),
            }
        };

        Ok(Self {
            state_tx,
            shared_state: Arc::new(RwLock::new(initial_state)),
            gpu_context: Arc::new(gpu_context),
            event_bus,
            persistence,
        })
    }

    pub fn subscribe(&self) -> broadcast::Receiver<super::binary_state::StateUpdate> {
        self.state_tx.subscribe()
    }

    pub fn update_processing_status(&self, status: ProcessingStatus) {
        let mut state = self.shared_state.write();
        state.processing_status = status;
    }

    /// Records a command and updates the emotional state based on command sentiment
    pub async fn record_command(&self, command: String) -> Result<(), StateError> {
        let mut state = self.shared_state.write();
        state.last_command = Some(command.clone());
        
        // Update emotional state based on command sentiment
        let sentiment = self.analyze_sentiment(&command)?;
        self.update_emotional_state(sentiment).await?;
        
        // Notify monitoring
        self.event_bus.emit(Event::CommandRecorded { 
            command,
            timestamp: std::time::Instant::now(),
        });
        
        Ok(())
    }

    /// Performs a GPU-accelerated quantum state transition
    pub async fn transition_state(&self, new_amplitudes: Vec<Complex64>) -> Result<(), StateError> {
        let mut state = self.shared_state.write();
        
        // Validate new state
        if !self.is_valid_quantum_state(&new_amplitudes) {
            return Err(StateError::InvalidState("Invalid amplitude vector".into()));
        }
        
        // Prepare GPU buffers
        let gpu_buffer = self.gpu_context.prepare_buffer(&new_amplitudes)?;
        
        // Perform transition on GPU
        self.gpu_context.execute_transition(
            &state.quantum_state.gpu_buffer,
            &gpu_buffer,
            state.emotional_state.valence
        ).await?;
        
        // Update state
        state.quantum_state.amplitudes = new_amplitudes;
        state.quantum_state.gpu_buffer = Some(gpu_buffer);
        
        // Record metrics
        state.metrics.last_transition_time = std::time::Instant::now().duration_since(std::time::UNIX_EPOCH);
        
        // Create persistence checkpoint
        self.persistence.create_checkpoint(&state)?;
        
        Ok(())
    }

    /// Updates the emotional state and triggers quantum state influence
    pub async fn update_emotional_state(&self, valence: f32) -> Result<(), StateError> {
        let mut state = self.shared_state.write();
        
        // Update emotional parameters
        state.emotional_state.valence = valence.clamp(-1.0, 1.0);
        
        // Influence quantum state based on emotional state
        self.apply_emotional_influence().await?;
        
        Ok(())
    }

    pub fn record_response(&self, response: String) {
        let mut state = self.shared_state.write();
        state.last_response = Some(response);
    }

    pub fn record_error(&self) {
        let mut state = self.shared_state.write();
        state.error_count += 1;
    }

    pub fn get_status(&self) -> ProcessingStatus {
        self.shared_state.read().processing_status.clone()
    }
}

