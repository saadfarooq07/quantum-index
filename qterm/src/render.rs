use crossterm::{
    cursor,
    event::{self, Event, KeyCode},
    execute,
    terminal::{self, ClearType},
};
use std::io::{self, Write};
use crate::event_bus::{StateEvent, BinaryState, LivingState};

pub struct Renderer {
    terminal: Terminal,
    state: RendererState,
    effects: QuantumEffects,
}

impl Renderer {
    pub fn new() -> io::Result<Self> {
        let terminal = Terminal::new()?;
        let state = RendererState::default();
        let effects = QuantumEffects::new();
        
        Ok(Self {
            terminal,
            state,
            effects,
        })
    }

    pub async fn render(&mut self, state: &BinaryState) -> io::Result<()> {
        self.terminal.clear()?;
        self.render_prompt(state)?;
        self.render_output(state)?;
        self.render_status_bar(state)?;
        self.effects.apply(&mut self.terminal)?;
        self.terminal.flush()?;
        Ok(())
    }

    fn render_prompt(&mut self, state: &BinaryState) -> io::Result<()> {
        let prompt = format!("quantum> {}", state.current_command);
        execute!(
            self.terminal.backend_mut(),
            cursor::MoveTo(0, self.terminal.size()?.height - 2),
            terminal::Clear(ClearType::CurrentLine)
        )?;
        self.terminal.write_all(prompt.as_bytes())
    }

    fn render_output(&mut self, state: &BinaryState) -> io::Result<()> {
        for (idx, line) in state.terminal_buffer.iter().enumerate() {
            execute!(
                self.terminal.backend_mut(),
                cursor::MoveTo(0, idx as u16),
                terminal::Clear(ClearType::CurrentLine)
            )?;
            self.terminal.write_all(line.as_bytes())?;
        }
        Ok(())
    }
}

