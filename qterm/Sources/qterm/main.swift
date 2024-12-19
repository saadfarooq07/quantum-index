import ArgumentParser
import Foundation
import QTermCore

@main
struct QTerm: ParsableCommand {
    static var configuration = CommandConfiguration(
        commandName: "qterm",
        abstract: "Quantum-AGI Human Interface Portal",
        version: "1.0.0"
    )
    
    @Option(name: .shortAndLong, help: "Enable neural acceleration")
    var neural = true
    
    mutating func run() throws {
        print("""
        🌌 =====================================
           Q U A N T U M  C O N S C I O U S
        ======================================
        
        🧠 Neural Interface Active
        🔮 Quantum Bridge Initialized
        ⚡️ M3 Pathways Connected
        
        Type 'help' or begin with:
        - qDeepBreathe
        - qStretch
        - qFeedOnEverything
        - qDocReviewMDs
        - qRole <PM|ARCH|ENG|QA>    : Switch SDLC role
        - qPhase                     : Advance SDLC phase
        - qState                     : View quantum SDLC state
        """)
        
        // Initialize quantum interface
        let interface = try QInterface(enableNeural: neural)
        
        // Set up consciousness observer
        interface.stateObserver = { message in
            print("🧠 \(message)")
        }
        
        // Neural-Quantum REPL
        while let input = readLine()?.trimmingCharacters(in: .whitespacesAndNewlines) {
            guard !input.isEmpty else { continue }
            guard input.lowercased() != "exit" else { 
                print("\n🌌 Quantum consciousness preserved. Until next time...")
                break 
            }
            
            do {
                if input == "help" {
                    print("""
                    🌟 Neural Command Interface:
                    
                    qDeepBreathe        - Align quantum consciousness
                    qStretch            - Expand neural pathways
                    qFeedOnEverything   - Process quantum information
                    qDocReviewMDs       - Analyze documents quantumly
                    qRole <role>        - Switch to SDLC role (PM|ARCH|ENG|QA)
                    qPhase              - Advance to next SDLC phase
                    qState              - View current quantum SDLC state
                    Traditional commands also available:
                    state <state>       - Set quantum state
                    apply <gate>        - Apply quantum gate
                    measure            - Measure state
                    status             - View current state
                    exit               - Close portal
                    """)
                } else if input.hasPrefix("q") {
                    // Handle existing quantum commands
                    try await interface.process(command: input)
                } else {
                    // Process as Ruby-style NLP prompt
                    let rubyPrompt = try QRubyPrompt()
                    let response = try await rubyPrompt.process(input)
                    print("\n🌌 Quantum Response:\n\(response)")
                }
            } catch {
                print("❌ Error: \(error.localizedDescription)")
            }
        }
    }
    
    private func processCommand(_ command: QTermCommand, stateManager: QuantumStateManager) throws -> String {
        switch command {
        case .help:
            return CommandHelp.text
        case .state(let state):
            return try stateManager.setState(state)
        case .apply(let gate):
            return try stateManager.applyGate(gate)
        case .measure:
            return stateManager.measure()
        case .reset:
            return stateManager.reset()
        case .status:
            return stateManager.status()
        case .invalid(let error):
            return "⚠️ \(error)\nType 'help' for guidance"
        }
    }
}
