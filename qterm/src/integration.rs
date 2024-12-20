use std::sync::mpsc::{self, Sender, Receiver};
use tokio::sync::broadcast;
use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum StateMessage {
    BinaryUpdate(BinaryState),
    LivingUpdate(LivingState),
    ResourceUpdate(ResourceState),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BinaryState {
    pub command_active: bool,
    pub input_mode: InputMode,
    pub current_path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LivingState {
    pub emotional_level: f32,
    pub quantum_coherence: f32,
    pub interaction_confidence: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceState {
    pub gpu_utilization: f32,
    pub memory_pressure: f32,
    pub emotional_stability: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum InputMode {
    Normal,
    Insert,
    Command,
}

pub struct StateIntegration {
    binary_tx: Sender<StateMessage>,
    living_tx: broadcast::Sender<StateMessage>,
    binary_rx: Receiver<StateMessage>,
    living_rx: broadcast::Receiver<StateMessage>,
}

impl StateIntegration {
    pub fn new() -> Self {
        let (binary_tx, binary_rx) = mpsc::channel();
        let (living_tx, living_rx) = broadcast::channel(100);
        
        Self {
            binary_tx,
            living_tx,
            binary_rx,
            living_rx,
        }
    }

    pub fn send_binary_update(&self, state: BinaryState) {
        let _ = self.binary_tx.send(StateMessage::BinaryUpdate(state));
    }

    pub fn send_living_update(&self, state: LivingState) {
        let _ = self.living_tx.send(StateMessage::LivingUpdate(state));
    }

    pub fn receive_binary_updates(&self) -> Receiver<StateMessage> {
        self.binary_rx.clone()
    }

    pub fn receive_living_updates(&self) -> broadcast::Receiver<StateMessage> {
        self.living_tx.subscribe()
    }
}

