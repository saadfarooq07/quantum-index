use crate::error::{QTermError, Result};
use crossterm::event::{Event, KeyEvent};
use std::collections::HashMap;
use tokio::sync::mpsc;

pub struct Shell {
    history: Vec<String>,
    completions: HashMap<String, Vec<String>>,
    command_tx: mpsc::Sender<String>,
}

impl Shell {
    pub fn new(command_tx: mpsc::Sender<String>) -> Self {
        Self {
            history: Vec::new(),
            completions: HashMap::new(),
            command_tx,
        }
    }

    pub fn add_completion(&mut self, command: &str, options: Vec<String>) {
        self.completions.insert(command.to_string(), options);
    }

    pub async fn process_input(&mut self, input: &str) -> Result<()> {
        self.history.push(input.to_string());
        self.command_tx.send(input.to_string())
            .await
            .map_err(|e| QTermError::ShellError(e.to_string()))
    }

    pub fn get_completions(&self, partial: &str) -> Vec<String> {
        self.completions.iter()
            .filter(|(cmd, _)| cmd.starts_with(partial))
            .flat_map(|(_, options)| options.clone())
            .collect()
    }

    pub async fn handle_key_event(&mut self, event: KeyEvent) -> Result<Option<String>> {
        // Handle special key combinations and return command if needed
        match event.code {
            _ => Ok(None),
        }
    }

    pub fn get_history(&self) -> &[String] {
        &self.history
    }

    pub async fn initialize_completions(&mut self) {
        // Add default completions
        self.add_completion("quantum", vec![
            "create".to_string(),
            "apply".to_string(),
            "measure".to_string(),
            "visualize".to_string(),
        ]);

        self.add_completion("metal", vec![
            "status".to_string(),
            "optimize".to_string(),
            "metrics".to_string(),
        ]);

        self.add_completion("state", vec![
            "binary".to_string(),
            "living".to_string(),
            "transition".to_string(),
        ]);
    }
}

