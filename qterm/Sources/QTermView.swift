import SwiftUI

struct QuantumGradient: ViewModifier {
    func body(content: Content) -> some View {
        content
            .background(
                LinearGradient(
                    gradient: Gradient(colors: [
                        Color(red: 0.1, green: 0.1, blue: 0.2),
                        Color(red: 0.05, green: 0.05, blue: 0.1)
                    ]),
                    startPoint: .top,
                    endPoint: .bottom
                )
            )
    }
}

struct QuantumBorder: ViewModifier {
    var isActive: Bool = true
    
    func body(content: Content) -> some View {
        content.overlay(
            RoundedRectangle(cornerRadius: 8)
                .strokeBorder(
                    LinearGradient(
                        gradient: Gradient(colors: [
                            Color.blue.opacity(isActive ? 0.6 : 0.2),
                            Color.purple.opacity(isActive ? 0.4 : 0.1)
                        ]),
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ),
                    lineWidth: 1
                )
        )
    }
}

struct QTermView: View {
    @StateObject private var terminal = QTerminal()
    @State private var input: String = ""
    @State private var commandHistory: [String] = []
    @State private var historyIndex: Int = 0
    @State private var isInputEnabled = true
    @State private var suggestions: [String] = []
    @State private var selectedSuggestion: Int = 0
    @FocusState private var isInputFocused: Bool
    
    let timer = Timer.publish(every: 0.5, on: .main, in: .common).autoconnect()
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("⟨ψ|")
                    .font(.system(.title2, design: .monospaced))
                    .foregroundColor(.blue.opacity(0.8))
                
                Text("Quantum Terminal")
                    .font(.system(.title2, design: .monospaced))
                    .foregroundColor(.white.opacity(0.9))
                
                Text("|ψ⟩")
                    .font(.system(.title2, design: .monospaced))
                    .foregroundColor(.purple.opacity(0.8))
                
                Spacer()
                
                // State indicator
                HStack(spacing: 4) {
                    Circle()
                        .fill(terminal.isProcessing ? Color.yellow : Color.green)
                        .frame(width: 8, height: 8)
                    Text(terminal.isProcessing ? "Processing" : "Ready")
                        .font(.system(.caption, design: .monospaced))
                        .foregroundColor(.gray)
                }
            }
            .padding()
            .modifier(QuantumGradient())
            .modifier(QuantumBorder())
            
            // Output Area with Quantum Visualization
            ScrollViewReader { scrollView in
                ScrollView {
                    VStack(alignment: .leading, spacing: 8) {
                        // Terminal output
                        Text(terminal.output)
                            .font(.system(.body, design: .monospaced))
                            .foregroundColor(.green.opacity(0.9))
                            .textSelection(.enabled)
                            .id("output")
                        
                        // Quantum state visualization
                        if let workflows = terminal.quantumState["workflows"] as? [[String: Any]], !workflows.isEmpty {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Quantum State")
                                    .font(.system(.caption, design: .monospaced))
                                    .foregroundColor(.blue.opacity(0.7))
                                
                                ForEach(workflows.indices, id: \.self) { index in
                                    let workflow = workflows[index]
                                    HStack {
                                        Text("⟨\(workflow["name"] as? String ?? "")|")
                                            .foregroundColor(.blue.opacity(0.6))
                                        Text(workflow["state"] as? String ?? "")
                                            .foregroundColor(.purple.opacity(0.6))
                                        Text("|ψ⟩")
                                            .foregroundColor(.blue.opacity(0.6))
                                    }
                                    .font(.system(.caption, design: .monospaced))
                                }
                            }
                            .padding()
                            .modifier(QuantumGradient())
                            .modifier(QuantumBorder(isActive: false))
                        }
                    }
                    .padding()
                }
                .onChange(of: terminal.output) { _ in
                    scrollView.scrollTo("output", anchor: .bottom)
                }
                .background(Color.black.opacity(0.95))
            }
            
            // Suggestions
            if !suggestions.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(suggestions.indices, id: \.self) { index in
                            Text(suggestions[index])
                                .font(.system(.caption, design: .monospaced))
                                .foregroundColor(.white)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(index == selectedSuggestion ? Color.blue.opacity(0.3) : Color.clear)
                                .cornerRadius(4)
                                .onTapGesture {
                                    input = suggestions[index]
                                }
                        }
                    }
                    .padding(.horizontal)
                }
                .frame(height: 30)
                .background(Color.black.opacity(0.8))
            }
            
            // Input Area
            HStack(spacing: 8) {
                Text("λ")
                    .font(.system(.body, design: .monospaced))
                    .foregroundColor(.blue.opacity(0.8))
                
                TextField("Enter quantum command...", text: $input)
                    .textFieldStyle(PlainTextFieldStyle())
                    .font(.system(.body, design: .monospaced))
                    .foregroundColor(.white)
                    .disabled(!isInputEnabled)
                    .focused($isInputFocused)
                    .onChange(of: input) { newValue in
                        updateSuggestions(for: newValue)
                    }
                    .onSubmit {
                        submitCommand()
                    }
            }
            .padding()
            .background(Color.black.opacity(0.95))
            .modifier(QuantumBorder(isActive: isInputFocused))
        }
        .background(Color.black)
        .onAppear {
            isInputFocused = true
            setupKeyboardHandlers()
        }
    }
    
    private func setupKeyboardHandlers() {
        NSEvent.addLocalMonitorForEvents(matching: .keyDown) { event in
            switch event.keyCode {
            case 125: // Down arrow
                if !commandHistory.isEmpty {
                    historyIndex = min(historyIndex + 1, commandHistory.count)
                    if historyIndex < commandHistory.count {
                        input = commandHistory[historyIndex]
                    } else {
                        input = ""
                    }
                }
                return nil
            case 126: // Up arrow
                if !commandHistory.isEmpty {
                    historyIndex = max(historyIndex - 1, 0)
                    input = commandHistory[historyIndex]
                }
                return nil
            case 48: // Tab
                if !suggestions.isEmpty {
                    selectedSuggestion = (selectedSuggestion + 1) % suggestions.count
                    input = suggestions[selectedSuggestion]
                }
                return nil
            default:
                return event
            }
        }
    }
    
    private func updateSuggestions(for input: String) {
        guard !input.isEmpty else {
            suggestions = []
            return
        }
        
        // Basic command suggestions
        let basicCommands = ["help", "clear", "qflow", "qstate", "qrag", "qvis", "qcontainer"]
        suggestions = basicCommands.filter { $0.starts(with: input.lowercased()) }
        
        // Add workflow suggestions
        if input.starts(with: "qflow") {
            suggestions.append(contentsOf: ["qflow new", "qflow list", "qflow switch"].filter { $0.starts(with: input.lowercased()) })
        }
        
        selectedSuggestion = 0
    }
    
    private func submitCommand() {
        guard !input.isEmpty else { return }
        
        let command = input
        commandHistory.append(command)
        historyIndex = commandHistory.count
        input = ""
        isInputEnabled = false
        suggestions = []
        
        Task {
            do {
                let response = try await terminal.processCommand(command)
                await MainActor.run {
                    if !response.isEmpty {
                        terminal.output += response + "\n"
                    }
                    isInputEnabled = true
                    isInputFocused = true
                }
            } catch {
                await MainActor.run {
                    terminal.output += "Error: \(error.localizedDescription)\n"
                    isInputEnabled = true
                    isInputFocused = true
                }
            }
        }
    }
}
