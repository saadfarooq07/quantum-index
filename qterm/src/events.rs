use std::sync::Arc;
use tokio::sync::{broadcast, mpsc};
use crate::emotions::EmotionalState;

#[derive(Debug, Clone)]
pub enum Event {
    CommandExecuted {
        command: String,
        success: bool,
        output: String,
    },
    StateChanged {
        from: State,
        to: State,
        trigger: String,
    },
    EmotionalUpdate {
        previous: EmotionalState,
        current: EmotionalState,
    },
    ResourceUpdate {
        cpu_usage: f32,
        gpu_usage: f32,
        memory_usage: f32,
    },
}

#[derive(Debug, Clone, PartialEq)]
pub enum State {
    Binary,
    Living,
    Transitioning,
}

#[derive(Debug)]
pub struct StateTransition {
    pub from: State,
    pub to: State,
    pub emotional_state: EmotionalState,
}

pub struct EventSystem {
    event_tx: broadcast::Sender<Event>,
    event_rx: broadcast::Receiver<Event>,
    transition_tx: mpsc::Sender<StateTransition>,
    transition_rx: mpsc::Receiver<StateTransition>,
    current_state: State,
}

impl EventSystem {
    pub fn new() -> Self {
        let (event_tx, event_rx) = broadcast::channel(100);
        let (transition_tx, transition_rx) = mpsc::channel(100);

        Self {
            event_tx,
            event_rx,
            transition_tx,
            transition_rx,
            current_state: State::Binary,
        }
    }

    pub async fn process_events(&mut self) {
        while let Some(transition) = self.transition_rx.recv().await {
            let event = Event::StateChanged {
                from: self.current_state.clone(),
                to: transition.to.clone(),
                trigger: "state_transition".to_string(),
            };

            self.current_state = transition.to;
            self.event_tx.send(event).expect("Failed to send event");
        }
    }
}

