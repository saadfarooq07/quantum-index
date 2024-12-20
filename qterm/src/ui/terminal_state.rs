use std::collections::VecDeque;

const MAX_HISTORY: usize = 1000;
const MAX_OUTPUT_HISTORY: usize = 1000;
const SCROLL_STEP: usize = 3;

// Command documentation
struct CommandDoc {
    name: &'static str,
    desc: &'static str,
    usage: &'static str,
}

const COMMANDS: &[CommandDoc] = &[
    CommandDoc {
        name: "model",
        desc: "Model management commands (list, select, metrics)",
        usage: "model [list|select <name>|metrics]",
    },
    CommandDoc {
        name: "clear",
        desc: "Clear terminal output history",
        usage: "clear", 
    },
    CommandDoc {
        name: "reset",
        desc: "Reset quantum state to |0⟩",
        usage: "reset",
    },
    CommandDoc {
        name: "hadamard",
        desc: "Apply Hadamard gate to specified qubit",
        usage: "hadamard <qubit>",
    },
    CommandDoc {
        name: "measure",
        desc: "Measure specified qubit",
        usage: "measure <qubit>",
    },
    CommandDoc {
        name: "help",
        desc: "Display help information",
        usage: "help [command]",
    },
];
    "clear",
    "reset",
    "hadamard",
    "measure",
    "help",
];

#[derive(Default)]
pub struct TerminalState {
    history: VecDeque<String>,
    current_input: String,
    cursor_position: usize,
    history_index: Option<usize>,
    saved_input: String,
    output_history: Vec<String>,
    suggestions: Vec<String>,
    scroll_position: usize,
    selected_suggestion: Option<usize>,
    hover_suggestion: Option<usize>,
}

impl TerminalState {
    pub fn new() -> Self {
        Self {
            history: VecDeque::with_capacity(MAX_HISTORY),
            current_input: String::new(),
            cursor_position: 0,
            history_index: None,
            saved_input: String::new(),
            output_history: Vec::new(),
            suggestions: Vec::new(),
            scroll_position: 0,
        }
    }

    pub fn input_char(&mut self, c: char) {
        self.current_input.insert(self.cursor_position, c);
        self.cursor_position += 1;
        self.update_suggestions();
    }

    pub fn backspace(&mut self) {
        if self.cursor_position > 0 {
            self.cursor_position -= 1;
            self.current_input.remove(self.cursor_position);
            self.update_suggestions();
        }
    }

    pub fn move_cursor_left(&mut self) {
        if self.cursor_position > 0 {
            self.cursor_position -= 1;
        }
    }

    pub fn move_cursor_right(&mut self) {
        if self.cursor_position < self.current_input.len() {
            self.cursor_position += 1;
        }
    }

    pub fn history_up(&mut self) {
        if self.history.is_empty() {
            return;
        }

        let new_index = match self.history_index {
            None => {
                self.saved_input = self.current_input.clone();
                Some(self.history.len() - 1)
            }
            Some(i) if i > 0 => Some(i - 1),
            Some(_) => return,
        };

        if let Some(idx) = new_index {
            if let Some(cmd) = self.history.get(idx) {
                self.current_input = cmd.clone();
                self.cursor_position = self.current_input.len();
                self.history_index = Some(idx);
            }
        }
    }

    pub fn history_down(&mut self) {
        match self.history_index {
            None => return,
            Some(i) if i < self.history.len() - 1 => {
                let cmd = self.history.get(i + 1).unwrap().clone();
                self.current_input = cmd;
                self.history_index = Some(i + 1);
            }
            Some(_) => {
                self.current_input = self.saved_input.clone();
                self.history_index = None;
            }
        }
        self.cursor_position = self.current_input.len();
    }

    pub fn commit_command(&mut self) -> Option<String> {
        if self.current_input.trim().is_empty() {
            return None;
        }

        let command = self.current_input.clone();
        self.history.push_back(command.clone());
        if self.history.len() > MAX_HISTORY {
            self.history.pop_front();
        }

        self.current_input.clear();
        self.cursor_position = 0;
        self.history_index = None;
        self.saved_input.clear();
        self.suggestions.clear();

        Some(command)
    }

    pub fn handle_completion(&mut self) {
        if let Some(suggestion) = self.suggestions.first() {
            self.current_input = suggestion.clone();
            self.cursor_position = self.current_input.len();
            self.update_suggestions();
        }
    }

    pub fn get_current_input(&self) -> &str {
        &self.current_input
    }

    pub fn get_history(&self) -> Vec<&String> {
        self.output_history.iter().collect()
    }

    pub fn get_suggestions(&self) -> &[String] {
        &self.suggestions
    }

    pub fn scroll_position(&self) -> usize {
        self.scroll_position
    }

    pub fn get_output(&self) -> Vec<&String> {
        self.output_history.iter().collect()
    }

    pub fn scroll_up(&mut self) {
        if self.scroll_position + SCROLL_STEP < self.output_history.len() {
            self.scroll_position += SCROLL_STEP;
        } else {
            self.scroll_position = self.output_history.len();
        }
    }

    pub fn scroll_down(&mut self) {
        if self.scroll_position >= SCROLL_STEP {
            self.scroll_position -= SCROLL_STEP;
        } else {
            self.scroll_position = 0;
        }
    }

    pub fn add_output(&mut self, output: &str) {
        // Split output into lines and format each line
        for line in output.lines() {
            let formatted_line = if line.trim().is_empty() {
                String::new()
            } else {
                format!("  {}", line)
            };
            self.output_history.push(formatted_line);
        }
        self.truncate_output_history();
    }

    fn truncate_output_history(&mut self) {
        if self.output_history.len() > MAX_OUTPUT_HISTORY {
            let excess = self.output_history.len() - MAX_OUTPUT_HISTORY;
            self.output_history.drain(0..excess);
            if self.scroll_position > excess {
                self.scroll_position -= excess;
            } else {
                self.scroll_position = 0;
            }
        }
    }

    pub fn clear_history(&mut self) {
        self.output_history.clear();
        self.scroll_position = 0;
    }

    fn update_suggestions(&mut self) {
        self.suggestions.clear();
        let input = self.current_input.to_lowercase();
        if !input.is_empty() {
            self.suggestions = COMMANDS
                .iter()
                .filter(|cmd| cmd.name.starts_with(&input))
                .map(|cmd| cmd.name.to_string())
                .collect();
        }
        self.selected_suggestion = None;
        self.hover_suggestion = None;
    }

    pub fn get_command_doc(&self, command: &str) -> Option<(&'static str, &'static str)> {
        COMMANDS.iter()
            .find(|cmd| cmd.name == command)
            .map(|cmd| (cmd.desc, cmd.usage))
    }

    pub fn set_hover_suggestion(&mut self, index: Option<usize>) {
        self.hover_suggestion = index;
    }

    pub fn get_hover_suggestion(&self) -> Option<usize> {
        self.hover_suggestion
    }

    pub fn select_suggestion(&mut self, index: Option<usize>) {
        self.selected_suggestion = index;
    }

    pub fn get_selected_suggestion(&self) -> Option<usize> {
        self.selected_suggestion
    }
}

