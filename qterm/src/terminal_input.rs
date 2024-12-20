use rustyline::error::ReadlineError;
use rustyline::{Editor, Result};
use rustyline::completion::{Completer, Pair};
use rustyline::hint::Hinter;
use rustyline::validate::Validator;
use rustyline::highlight::Highlighter;
use rustyline::history::History;
use std::borrow::Cow::{self, Borrowed, Owned};

#[derive(Default)]
struct QuantumCompleter {
    commands: Vec<String>,
}

impl Completer for QuantumCompleter {
    type Candidate = Pair;

    fn complete(
        &self,
        line: &str,
        pos: usize,
        _ctx: &rustyline::Context<'_>,
    ) -> Result<(usize, Vec<Pair>)> {
        let mut matches: Vec<Pair> = Vec::new();
        
        for cmd in &self.commands {
            if cmd.starts_with(line) {
                matches.push(Pair {
                    display: cmd.clone(),
                    replacement: cmd.clone(),
                });
            }
        }
        
        Ok((0, matches))
    }
}

#[derive(Default)]
pub struct TerminalState {
    input: String,
    editor: Editor<QuantumCompleter>,
    history: Vec<String>,
    suggestions: Vec<String>,
}

impl TerminalState {
    pub fn new() -> Self {
        let mut editor = Editor::new().expect("Failed to create editor");
        let completer = QuantumCompleter {
            commands: vec![
                "measure".to_string(),
                "hadamard".to_string(),
                "cnot".to_string(),
                "phase".to_string(),
            ],
        };
        editor.set_completer(Some(completer));
        
        Self {
            input: String::new(),
            editor,
            history: Vec::new(),
            suggestions: Vec::new(),
        }
    }

    pub fn handle_input(&mut self, c: char) -> bool {
        if c == '\n' {
            if !self.input.trim().is_empty() {
                self.history.push(self.input.clone());
                self.input.clear();
            }
            return true;
        }
        
        if c == '\x08' || c == '\x7f' {  // Backspace
            self.input.pop();
        } else {
            self.input.push(c);
        }
        
        self.update_suggestions();
        false
    }

    pub fn update_suggestions(&mut self) {
        self.suggestions = self.editor
            .completer()
            .and_then(|c| c.complete(&self.input, self.input.len(), &rustyline::Context::new())
                .ok())
            .map(|(_, matches)| matches
                .into_iter()
                .map(|p| p.replacement)
                .collect())
            .unwrap_or_default();
    }

    pub fn get_current_input(&self) -> &str {
        &self.input
    }

    pub fn get_history(&self) -> &[String] {
        &self.history
    }

    pub fn get_suggestions(&self) -> &[String] {
        &self.suggestions
    }
}

