use std::io;
use std::sync::Arc;
use std::time::{Duration, Instant};
pub struct RAGMetrics {
    confidence: f64,
    token_states: Vec<TokenState>, 
    quantum_probabilities: Vec<f64>,
    state_coherence: f64,
}
mod terminal_state;
pub use terminal_state::TerminalState;
use terminal_state::TerminalState;
use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::CrosstermBackend,
    layout::{Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    symbols,
    text::{Span, Spans},
    widgets::{Block, Borders, Gauge, Paragraph, Wrap},
    Frame, Terminal,
};
use rand::Rng;

const PROBABILITY_UPDATE_RATE: Duration = Duration::from_millis(100);

pub struct RAGMetrics {
    confidence: f64,
    token_states: Vec<TokenState>,
    quantum_probabilities: Vec<f64>,
    state_coherence: f64,
}

pub struct TokenState {
    token: String,
    quantum_state: f64,
    confidence: f64,
    entanglement: f64,
}

pub struct QuantumUI {
    openrouter: Arc<OpenRouterClient>,
    metal_enabled: bool,
    quantum_state: Vec<Complex64>,
    probability_colors: Vec<Color>,
    last_probability_update: Instant,
    terminal_state: TerminalState,
    rag_metrics: RAGMetrics,
    token_animation_states: Vec<f64>,
    confidence_gradient: Vec<Color>,
    rag_metrics: RAGMetrics,
    token_animation_states: Vec<f64>,
    confidence_gradient: Vec<Color>,
}

impl QuantumUI {
    pub fn new(openrouter: Arc<OpenRouterClient>, metal_enabled: bool) -> Self {
        Self {
            openrouter,
            metal_enabled,
            probability_colors: vec![
                Color::Rgb(0, 255, 255),  // Cyan
                Color::Rgb(255, 0, 255),  // Magenta
                Color::Rgb(255, 255, 0),  // Yellow
            ],
            last_probability_update: Instant::now(),
            terminal_state: TerminalState::new(),
            rag_metrics: RAGMetrics {
                confidence: 0.0,
                token_states: Vec::new(),
                quantum_probabilities: Vec::new(),
                state_coherence: 0.0,
            },
            token_animation_states: Vec::new(),
            confidence_gradient: vec![
                Color::Rgb(255, 0, 0),    // Low confidence
                Color::Rgb(255, 255, 0),  // Medium confidence
                Color::Rgb(0, 255, 0),    // High confidence
            ],
        }
    }

    pub fn run(&mut self) -> io::Result<()> {
        enable_raw_mode()?;
        let mut stdout = io::stdout();
        execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
        let backend = CrosstermBackend::new(stdout);
        let mut terminal = Terminal::new(backend)?;

        let res = self.run_app(&mut terminal);

        disable_raw_mode()?;
        execute!(
            terminal.backend_mut(),
            LeaveAlternateScreen,
            DisableMouseCapture
        )?;
        terminal.show_cursor()?;

        res
    }

    fn run_app<B: ratatui::backend::Backend>(&mut self, terminal: &mut Terminal<B>) -> io::Result<()> {
        loop {
            // Update particle effects and animations
            self.update_particles();
            self.update_animations();
            
            terminal.draw(|f| self.ui(f))?;

            if event::poll(Duration::from_millis(50))? {
                match key.code {
                    KeyCode::Char('q') if key.modifiers.contains(event::KeyModifiers::CONTROL) => return Ok(()),
                    KeyCode::Char(c) => {
                        self.terminal_state.input_char(c);
                    },
                    KeyCode::Enter => {
                        let command = self.terminal_state.commit_command();
                        if let Some(cmd) = command {
                            // Trigger command execution effects
                            self.spawn_command_particles();
                            let result = self.process_command(&cmd)?;
                            // Show achievement if command was successful
                            if result.is_ok() {
                                self.show_achievement("Command Success", "Successfully executed command!");
                            }
                        }
                    },
                    KeyCode::Tab => {
                        self.terminal_state.handle_completion();
                    },
                    KeyCode::Up => {
                        self.terminal_state.history_up();
                    },
                    KeyCode::Down => {
                        self.terminal_state.history_down();
                    },
                    KeyCode::PageUp => {
                        self.terminal_state.scroll_up();
                    },
                    KeyCode::PageDown => {
                        self.terminal_state.scroll_down();
                    },
                    KeyCode::Backspace => {
                        self.terminal_state.backspace();
                    },
                    KeyCode::Left => {
                        self.terminal_state.move_cursor_left();
                    },
                    KeyCode::Right => {
                        self.terminal_state.move_cursor_right();
                    },
                    _ => {}
                        _ => {}
                    }
                }
            }

            self.update_probability_colors();
        }
    }
    }

    fn ui<B: ratatui::backend::Backend>(&self, f: &mut Frame<B>) {
        let size = f.size();
        
        // Create margin around entire UI
        let margin_vertical = size.height / 8;
        let margin_horizontal = size.width / 6;
        
        // Create main area with margins
        let main_area = Rect::new(
            margin_horizontal,
            margin_vertical,  
            size.width - (margin_horizontal * 2),
            size.height - (margin_vertical * 2)
        );
        
        // Create floating effect with shadow
        let shadow_area = Rect::new(
            main_area.x + 1,
            main_area.y + 1,
            main_area.width,
            main_area.height  
        );
        let shadow = Block::default()
            .style(Style::default().bg(Color::DarkGray));
        f.render_widget(shadow, shadow_area);
            margin_horizontal,
            margin_vertical,
            size.width - (margin_horizontal * 2),
            size.height - (margin_vertical * 2)
        );
        
        let chunks = Layout::default()
            .direction(Direction::Vertical)
            .constraints([
                Constraint::Length(3),     // Status bar
                Constraint::Min(10),       // Main content 
                Constraint::Length(3),     // Achievement bar
                Constraint::Length(5),     // Achievement notifications
            ].as_ref())
            .split(main_area);

        self.render_status_bar(f, chunks[0]);
        
        let main_chunks = Layout::default()
            .direction(Direction::Horizontal)
            .constraints([
                Constraint::Percentage(50),
                Constraint::Percentage(50),
            ].as_ref())
            .split(chunks[1]);

        // Render achievement notifications
        if let Some(achievement) = self.get_latest_achievement() {
            self.render_achievement(f, chunks[2], achievement);
        }

        // Split the left panel for metrics and quantum visualization
        let left_chunks = Layout::default()
            .direction(Direction::Vertical)
            .constraints([
                Constraint::Length(3),  // RAG confidence
                Constraint::Length(8),  // Token states
                Constraint::Min(0),     // Quantum visualization
            ].as_ref())
            .split(main_chunks[0]);

        self.render_rag_confidence(f, left_chunks[0]);
        self.render_token_states(f, left_chunks[1]);
        self.render_quantum_vis(f, left_chunks[2]);
        self.render_terminal(f, main_chunks[1]);
    }

    self.terminal_state.scroll_down();
    if parts[0] == "model" {
        self.terminal_state.update_suggestions();
    }
        let metal_status = if self.metal_enabled {
            Span::styled("Metal Acceleration: Active", Style::default().fg(Color::Green))
        } else {
            Span::styled("Metal Acceleration: Inactive", Style::default().fg(Color::Red))
        };

        let current_model = match self.openrouter.get_current_model().await {
            Some(model) => {
                let status_color = if model.ready {
                    Color::Green 
                } else {
                    Color::Yellow
                };
                Span::styled(
                    format!("Model: {} ({})", model.name, if model.ready { "Ready" } else { "Loading" }),
                    Style::default().fg(status_color)
                )
            },
            None => Span::styled(
                "Model: None",
                Style::default().fg(Color::Red)
            )
        };
        let model_status = current_model;
        
        let model_metrics = if let Some(model) = self.openrouter.get_current_model().await {
            if let Some(metrics) = self.openrouter.get_model_metrics(&model.id).await {
                Span::styled(
                    format!(
                        "Latency: {:.0}ms | Success: {:.1}% | Requests: {}",
                        metrics.avg_latency_ms,
                        metrics.success_rate * 100.0,
                        metrics.total_requests
                    ),
                    Style::default().fg(Color::Yellow)
                )
            } else {
                Span::styled("No metrics available", Style::default().fg(Color::DarkGray))
            }
        } else {
            Span::styled("No model selected", Style::default().fg(Color::DarkGray))
        };

        let status_text = vec![
            Spans::from(metal_status),
            Spans::from(model_status),
            Spans::from(model_metrics),
        ];

        let status_par = Paragraph::new(status_text)
            .block(Block::default()
                .borders(Borders::ALL)
                .border_style(Style::default().fg(Color::Cyan))
                .style(Style::default().bg(Color::Reset))) // Transparent background
            .wrap(Wrap { trim: true });

        f.render_widget(status_par, area);
    }

    fn render_rag_confidence<B: ratatui::backend::Backend>(&self, f: &mut Frame<B>, area: Rect) {
        let confidence = self.rag_metrics.confidence;
        let color = self.get_confidence_color(confidence);
        
        let gauge = Gauge::default()
            .block(Block::default()
                .title("RAG Confidence")
                .borders(Borders::ALL))
            .gauge_style(Style::default().fg(color))
            .ratio(confidence);
        
        f.render_widget(gauge, area);
    }

    fn render_token_states<B: ratatui::backend::Backend>(&self, f: &mut Frame<B>, area: Rect) {
        let block = Block::default()
            .title("Token States")
            .borders(Borders::ALL);
        
        let inner = block.inner(area);
        f.render_widget(block, area);

        let token_chunks = Layout::default()
            .direction(Direction::Vertical)
            .constraints(
                self.rag_metrics.token_states.iter()
                    .map(|_| Constraint::Length(2))
                    .collect::<Vec<_>>()
            )
            .split(inner);

        for (idx, (token_state, chunk)) in self.rag_metrics.token_states.iter()
            .zip(token_chunks.iter())
            .enumerate()
        {
            let animation_state = self.token_animation_states.get(idx).copied().unwrap_or(0.0);
            let color = self.get_quantum_color(token_state.quantum_state, animation_state);
            
            let gauge = Gauge::default()
                .block(Block::default().title(&token_state.token))
                .gauge_style(Style::default().fg(color))
                .ratio(token_state.confidence);
            
            f.render_widget(gauge, *chunk);
        }
    }

    fn get_confidence_color(&self, confidence: f64) -> Color {
        let idx = (confidence * (self.confidence_gradient.len() - 1) as f64).round() as usize;
        self.confidence_gradient[idx.min(self.confidence_gradient.len() - 1)]
    }

    fn get_quantum_color(&self, quantum_state: f64, animation_state: f64) -> Color {
        let phase = (quantum_state + animation_state) % 1.0;
        let r = ((phase * 2.0 * std::f64::consts::PI).sin() * 127.0 + 128.0) as u8;
        let g = ((phase * 2.0 * std::f64::consts::PI + 2.0/3.0 * std::f64::consts::PI).sin() * 127.0 + 128.0) as u8;
        let b = ((phase * 2.0 * std::f64::consts::PI + 4.0/3.0 * std::f64::consts::PI).sin() * 127.0 + 128.0) as u8;
        Color::Rgb(r, g, b)
    }

    fn render_quantum_vis<B: ratatui::backend::Backend>(&self, f: &mut Frame<B>, area: Rect) {
        let block = Block::default()
            .title("Quantum State")
            .borders(Borders::ALL)
            .border_style(Style::default().fg(Color::Cyan))
            .style(Style::default().bg(Color::Reset)); // Transparent background
        
        let inner = block.inner(area);
        f.render_widget(block, area);

        // Render probability bars with quantum-inspired colors
        if !self.quantum_state.is_empty() {
            let probabilities: Vec<f64> = self.quantum_state.iter()
                .map(|c| c.norm_sqr())
                .collect();

            let gauge_area = Layout::default()
                .direction(Direction::Vertical)
                .constraints(
                    vec![Constraint::Length(1); probabilities.len()]
                )
                .split(inner);

            for (idx, (prob, area)) in probabilities.iter().zip(gauge_area.iter()).enumerate() {
                let gauge = Gauge::default()
                    .block(Block::default())
                    .gauge_style(Style::default().fg(self.probability_colors[idx % self.probability_colors.len()]))
                    .ratio(*prob);
                f.render_widget(gauge, *area);
            }
        }
    }

    fn render_terminal<B: ratatui::backend::Backend>(&self, f: &mut Frame<B>, area: Rect) {
        let terminal_layout = Layout::default()
            .direction(Direction::Vertical)
            .constraints([
                Constraint::Min(3),      // Command output
                Constraint::Length(3),   // Command documentation 
                Constraint::Length(3),   // Command suggestions
                Constraint::Length(3),   // Input line
            ].as_ref())
            .split(area);

        // Create shadow effect by rendering a dark block offset from main terminal
        let shadow_area = Rect::new(
            area.x + 1,
            area.y + 1,
            area.width,
            area.height
        );
        let shadow = Block::default()
            .style(Style::default().bg(Color::DarkGray));
        f.render_widget(shadow, shadow_area);

        // Main terminal block with floating effect
        let block = Block::default()  
            .title("Terminal")
            .borders(Borders::ALL)
            .border_style(Style::default().fg(Color::Cyan))
            .style(Style::default().bg(Color::Reset)); // Transparent background
        f.render_widget(block, area);

        let inner = block.inner(area);

        // Render output history
        let output_text = self.terminal_state.get_output()
            .iter()
            .map(|line| Spans::from(line.as_str()))
            .collect::<Vec<_>>();

        let output = Paragraph::new(output_text)
            .wrap(Wrap { trim: true })
            .scroll((self.terminal_state.scroll_position() as u16, 0));
        f.render_widget(output, terminal_layout[0]);

        // Render command documentation if a suggestion is hovered
        let doc_text = if let Some(hover_idx) = self.terminal_state.get_hover_suggestion() {
            if let Some(cmd) = self.terminal_state.get_suggestions().get(hover_idx) {
                if let Some((desc, usage)) = self.terminal_state.get_command_doc(cmd) {
                    vec![
                        Spans::from(Span::styled(usage, Style::default().fg(Color::Yellow))),
                        Spans::from(Span::styled(desc, Style::default().fg(Color::Gray))),
                    ]
                } else {
                    vec![]
                }
            } else {
                vec![]
            }
        } else {
            vec![]
        };
        let doc_widget = Paragraph::new(doc_text);
        f.render_widget(doc_widget, terminal_layout[1]);

        // Render suggestions with hover highlighting
        let suggestions = self.terminal_state.get_suggestions()
            .iter()
            .enumerate()
            .map(|(idx, s)| {
                let style = if Some(idx) == self.terminal_state.get_hover_suggestion() {
                    Style::default().fg(Color::White).bg(Color::DarkGray)
                } else if Some(idx) == self.terminal_state.get_selected_suggestion() {
                    Style::default().fg(Color::Black).bg(Color::Gray)
                } else {
                    Style::default().fg(Color::DarkGray)
                };
                Spans::from(vec![Span::styled(s.as_str(), style)])
            })
            .collect::<Vec<_>>();

        let suggestions_widget = Paragraph::new(suggestions);
        f.render_widget(suggestions_widget, terminal_layout[1]);

        // Render current input with cursor
        let input = self.terminal_state.get_current_input();
        let cursor_pos = self.terminal_state.cursor_position();
        
        let mut input_spans = vec![Span::raw("> ")];
        
        // Split input at cursor position and add cursor indicator
        if cursor_pos == input.len() {
            input_spans.push(Span::styled(input, Style::default().fg(Color::White)));
            input_spans.push(Span::styled("█", Style::default().fg(Color::White).add_modifier(Modifier::SLOW_BLINK)));
        } else {
            let (before, after) = input.split_at(cursor_pos);
            input_spans.push(Span::styled(before, Style::default().fg(Color::White)));
            input_spans.push(Span::styled("█", Style::default().fg(Color::White).add_modifier(Modifier::SLOW_BLINK)));
            input_spans.push(Span::styled(after, Style::default().fg(Color::White)));
        }

        let input_line = Paragraph::new(Spans::from(input_spans))
            .style(Style::default());
        f.render_widget(input_line, terminal_layout[2]);
    }
    }

    fn update_particles(&mut self) {
        // Update particle positions and lifetimes
        for particle in &mut self.particles {
            particle.update();
        }
        // Remove dead particles
        self.particles.retain(|p| p.is_alive());
    }

    fn update_animations(&mut self) {
        // Update animation states
        for animation in &mut self.animations {
            animation.update();
        }
        // Remove completed animations
        self.animations.retain(|a| !a.is_complete());
    }

    fn spawn_command_particles(&mut self) {
        let mut rng = rand::thread_rng();
        for _ in 0..10 {
            self.particles.push(Particle::new(
                rng.gen_range(0.0..1.0),
                rng.gen_range(0.0..1.0),
                rng.gen_range(-1.0..1.0),
                rng.gen_range(-1.0..1.0),
            ));
        }
    }

    fn show_achievement(&mut self, title: &str, description: &str) {
        self.achievements.push(Achievement {
            title: title.to_string(),
            description: description.to_string(),
            shown_at: Instant::now(),
        });
    }

    fn update_probability_colors(&mut self) {
        if self.last_probability_update.elapsed() >= PROBABILITY_UPDATE_RATE {
            let mut rng = rand::thread_rng();
            
            // Update token animation states
            for state in &mut self.token_animation_states {
                *state = (*state + rng.gen_range(0.01..0.05)) % 1.0;
            }
            
            // Quantum-inspired color shifts
            for color in &mut self.probability_colors {
                if let Color::Rgb(r, g, b) = color {
                    let shift = rng.gen_range(-5..=5);
                    *r = (*r as i16 + shift).clamp(0, 255) as u8;
                    *g = (*g as i16 + shift).clamp(0, 255) as u8;
                    *b = (*b as i16 + shift).clamp(0, 255) as u8;
                }
            }
            
            self.last_probability_update = Instant::now();
        }
    }

    pub fn update_rag_metrics(&mut self, metrics: RAGMetrics) {
        self.rag_metrics = metrics;
        self.token_animation_states = vec![0.0; metrics.token_states.len()];
    }

    pub fn update_quantum_state(&mut self, new_state: Vec<Complex64>) {
        self.quantum_state = new_state;
    }

    fn process_command(&mut self, command: &str) -> io::Result<()> {
        // Split command into parts
        let parts: Vec<&str> = command.split_whitespace().collect();
        if parts.is_empty() {
            return Ok(());
        }

        match parts[0] {
            "model" => {
                if parts.len() < 2 {
                    self.terminal_state.add_output("Usage: model [list|select <name>|metrics]");
                    return Ok(());
                }
                match parts[1] {
                    "list" => {
                        let models = self.openrouter.list_models().await;
                        let mut output = String::from("Available models:");
                        for model in models {
                            output.push_str(&format!("\n  {} ({})", 
                                model.name,
                                if model.ready { "Ready" } else { "Loading" }
                            ));
                        }
                        self.terminal_state.add_output(&output);
                    },
                    "select" => {
                        if parts.len() < 3 {
                            self.terminal_state.add_output("Usage: model select <name>");
                            return Ok(());
                        }
                        let model_name = parts[2];
                        match self.openrouter.select_model(model_name).await {
                            Ok(_) => self.terminal_state.add_output(&format!("Selected model: {}", model_name)),
                            Err(e) => self.terminal_state.add_output(&format!("Error selecting model: {}", e)),
                        }
                    },
                    "metrics" => {
                        if let Some(model) = self.openrouter.get_current_model().await {
                            if let Some(metrics) = self.openrouter.get_model_metrics(&model.id).await {
                                self.terminal_state.add_output(&format!(
                                    "Model metrics for {}:\n  Latency: {:.0}ms\n  Success rate: {:.1}%\n  Total requests: {}",
                                    model.name,
                                    metrics.avg_latency_ms,
                                    metrics.success_rate * 100.0,
                                    metrics.total_requests
                                ));
                            } else {
                                self.terminal_state.add_output("No metrics available for current model");
                            }
                        } else {
                            self.terminal_state.add_output("No model currently selected");
                        }
                    },
                    _ => {
                        self.terminal_state.add_output("Unknown model command. Use: model [list|select <name>|metrics]");
                    }
                }
            },
            "clear" => {
                self.terminal_state.clear_history();
            },
            "reset" => {
                self.quantum_state.clear();
            },
            // Add more quantum command processing here
            // Example:
            // "hadamard" => { self.apply_hadamard(parts[1..].to_vec()); }
            // "measure" => { self.measure_qubit(parts[1..].to_vec()); }
            _ => {
                self.terminal_state.add_output(&format!("Unknown command: {}", command));
            }
        }
        Ok(())
    }
}
