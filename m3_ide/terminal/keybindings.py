from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import vi_mode, vi_navigation_mode, vi_insert_mode
from prompt_toolkit.application import get_app
from typing import Callable, Dict, Any

class VimKeyBindings:
    """Vim-like keybindings for the terminal"""
    
    def __init__(self):
        self.kb = KeyBindings()
        self.register_navigation_keys()
        self.register_edit_keys()
        self.register_command_keys()
        self.mode = "normal"
        self.command_buffer = ""
        self.registers: Dict[str, str] = {}
        
    def register_navigation_keys(self) -> None:
        """Register Vim navigation keys"""
        
        @self.kb.add('h', filter=vi_navigation_mode)
        def _(event):
            """Move cursor left"""
            event.current_buffer.cursor_left()
            
        @self.kb.add('j', filter=vi_navigation_mode)
        def _(event):
            """Move cursor down"""
            event.current_buffer.cursor_down()
            
        @self.kb.add('k', filter=vi_navigation_mode)
        def _(event):
            """Move cursor up"""
            event.current_buffer.cursor_up()
            
        @self.kb.add('l', filter=vi_navigation_mode)
        def _(event):
            """Move cursor right"""
            event.current_buffer.cursor_right()
            
        @self.kb.add('w', filter=vi_navigation_mode)
        def _(event):
            """Move to next word"""
            buffer = event.current_buffer
            pos = buffer.document.find_next_word_beginning(count=event.arg)
            if pos:
                buffer.cursor_position += pos
                
        @self.kb.add('b', filter=vi_navigation_mode)
        def _(event):
            """Move to previous word"""
            buffer = event.current_buffer
            pos = buffer.document.find_previous_word_beginning(count=event.arg)
            if pos:
                buffer.cursor_position += pos
                
    def register_edit_keys(self) -> None:
        """Register Vim editing keys"""
        
        @self.kb.add('i', filter=vi_navigation_mode)
        def _(event):
            """Enter insert mode"""
            event.app.vi_state.input_mode = vi_insert_mode
            
        @self.kb.add('a', filter=vi_navigation_mode)
        def _(event):
            """Append after cursor"""
            event.current_buffer.cursor_right()
            event.app.vi_state.input_mode = vi_insert_mode
            
        @self.kb.add('o', filter=vi_navigation_mode)
        def _(event):
            """Open new line below"""
            buffer = event.current_buffer
            buffer.insert_line_below()
            event.app.vi_state.input_mode = vi_insert_mode
            
        @self.kb.add('O', filter=vi_navigation_mode)
        def _(event):
            """Open new line above"""
            buffer = event.current_buffer
            buffer.insert_line_above()
            event.app.vi_state.input_mode = vi_insert_mode
            
        @self.kb.add('d', 'd', filter=vi_navigation_mode)
        def _(event):
            """Delete current line"""
            buffer = event.current_buffer
            buffer.delete_line()
            
        @self.kb.add('y', 'y', filter=vi_navigation_mode)
        def _(event):
            """Yank current line"""
            buffer = event.current_buffer
            self.registers['"'] = buffer.document.current_line
            
        @self.kb.add('p', filter=vi_navigation_mode)
        def _(event):
            """Paste after cursor"""
            buffer = event.current_buffer
            if '"' in self.registers:
                buffer.insert_text(self.registers['"'])
                
    def register_command_keys(self) -> None:
        """Register Vim command keys"""
        
        @self.kb.add(':', filter=vi_navigation_mode)
        def _(event):
            """Enter command mode"""
            self.mode = "command"
            self.command_buffer = ""
            
        @self.kb.add('enter', filter=lambda: self.mode == "command")
        def _(event):
            """Execute command"""
            self._execute_command(self.command_buffer)
            self.mode = "normal"
            self.command_buffer = ""
            
        @self.kb.add('escape', filter=lambda: self.mode == "command")
        def _(event):
            """Exit command mode"""
            self.mode = "normal"
            self.command_buffer = ""
            
    def _execute_command(self, command: str) -> None:
        """Execute Vim command"""
        parts = command.split()
        if not parts:
            return
            
        cmd = parts[0]
        args = parts[1:]
        
        commands = {
            'w': self._write_file,
            'q': self._quit,
            'wq': self._write_and_quit,
            'set': self._set_option
        }
        
        if cmd in commands:
            commands[cmd](*args)
            
    def _write_file(self, *args) -> None:
        """Write buffer to file"""
        if not args:
            return
            
        filename = args[0]
        buffer = get_app().current_buffer
        with open(filename, 'w') as f:
            f.write(buffer.text)
            
    def _quit(self, *args) -> None:
        """Quit the application"""
        get_app().exit()
        
    def _write_and_quit(self, *args) -> None:
        """Write file and quit"""
        self._write_file(*args)
        self._quit()
        
    def _set_option(self, *args) -> None:
        """Set Vim option"""
        if not args:
            return
            
        option = args[0]
        value = args[1] if len(args) > 1 else None
        
        options = {
            'number': lambda v: self._toggle_line_numbers(v),
            'wrap': lambda v: self._toggle_line_wrap(v),
            'expandtab': lambda v: self._toggle_expand_tab(v)
        }
        
        if option in options:
            options[option](value)
            
    def _toggle_line_numbers(self, value: Optional[str]) -> None:
        """Toggle line numbers"""
        app = get_app()
        app.show_line_numbers = value != "no" if value else not app.show_line_numbers
        
    def _toggle_line_wrap(self, value: Optional[str]) -> None:
        """Toggle line wrap"""
        app = get_app()
        app.wrap_lines = value != "no" if value else not app.wrap_lines
        
    def _toggle_expand_tab(self, value: Optional[str]) -> None:
        """Toggle expand tab"""
        app = get_app()
        app.expand_tab = value != "no" if value else not app.expand_tab
        
    @property
    def bindings(self) -> KeyBindings:
        """Get key bindings"""
        return self.kb
