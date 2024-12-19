import Foundation

/// Represents a command in qTerm
public enum QTermCommand {
    case help
    case state(QuantumState)
    case apply(QuantumGate)
    case measure
    case reset
    case device
    case exit
    
    /// Parse a command string into a QTermCommand
    public static func parse(_ input: String) -> QTermCommand {
        let components = input.split(separator: " ").map(String.init)
        guard let command = components.first else {
            return .help
        }
        
        switch command.lowercased() {
        case "help", "h", "?":
            return .help
        case "state", "s":
            guard components.count > 1 else { return .help }
            switch components[1].lowercased() {
            case "0", "zero": return .state(.zero)
            case "1", "one": return .state(.one)
            case "+", "plus": return .state(.plus)
            case "-", "minus": return .state(.minus)
            default: return .help
            }
        case "apply", "a":
            guard components.count > 1 else { return .help }
            switch components[1].lowercased() {
            case "h", "hadamard": return .apply(.hadamard)
            case "x", "not": return .apply(.pauliX)
            case "y": return .apply(.pauliY)
            case "z": return .apply(.pauliZ)
            case "p", "phase":
                if components.count > 2, let phi = Float(components[2]) {
                    return .apply(.phase(phi))
                }
                return .help
            default: return .help
            }
        case "measure", "m":
            return .measure
        case "reset", "r":
            return .reset
        case "device", "d":
            return .device
        case "exit", "quit", "q":
            return .exit
        default:
            return .help
        }
    }
}

/// Help text for qTerm commands
public struct CommandHelp {
    public static let text = """
    Available Commands:
      help (h, ?)              Show this help message
      state (s) [0,1,+,-]      Set quantum state (|0⟩, |1⟩, |+⟩, |-⟩)
      apply (a) [gate]         Apply quantum gate
        - h, hadamard          Hadamard gate
        - x, not               Pauli-X (NOT) gate
        - y                    Pauli-Y gate
        - z                    Pauli-Z gate
        - p, phase [angle]     Phase gate with angle in radians
      measure (m)              Measure quantum state
      reset (r)                Reset to |0⟩ state
      device (d)               Show device info
      exit (q)                 Exit qTerm
    
    Examples:
      state 0     Set state to |0⟩
      apply h     Apply Hadamard gate
      measure     Measure current state
    """
}
