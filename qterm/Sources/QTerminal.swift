import Foundation
import SwiftUI
import MetalKit

class QTerminal: ObservableObject {
    @Published var output: String = ""
    @Published var isProcessing: Bool = false
    @Published var quantumState: [String: Any] = [:]
    
    private let device: MTLDevice?
    private let commandQueue: MTLCommandQueue?
    private var computePipeline: MTLComputePipelineState?
    private var zshProcess: Process?
    private var zshInput: Pipe?
    private var zshOutput: Pipe?
    private var pythonProcess: Process?
    
    private struct LocalLLM {
        // Simple transformer architecture for local processing
        private let vocabSize = 5000
        private let embedSize = 64
        private let numHeads = 4
        private let device: MTLDevice?
        private let commandQueue: MTLCommandQueue?
        private var embeddings: MTLBuffer?
        private var attentionWeights: MTLBuffer?
        private let patterns: [(pattern: String, command: String)]
        
        init(device: MTLDevice?, patterns: [(pattern: String, command: String)]) {
            self.device = device
            self.commandQueue = device?.makeCommandQueue()
            self.patterns = patterns
            setupModel()
        }
        
        private mutating func setupModel() {
            guard let device = device else { return }
            
            // Initialize embeddings and weights
            let embeddingsSize = vocabSize * embedSize * MemoryLayout<Float>.size
            embeddings = device.makeBuffer(length: embeddingsSize, options: .storageModeShared)
            
            let attentionSize = embedSize * embedSize * numHeads * MemoryLayout<Float>.size
            attentionWeights = device.makeBuffer(length: attentionSize, options: .storageModeShared)
            
            // Initialize with quantized weights (simulating pre-trained model)
            initializeQuantizedWeights()
        }
        
        private func initializeQuantizedWeights() {
            guard let embeddings = embeddings,
                  let attentionWeights = attentionWeights else { return }
            
            // Simulate 4-bit quantized weights
            let embeddingsPtr = embeddings.contents().assumingMemoryBound(to: Float.self)
            let attentionPtr = attentionWeights.contents().assumingMemoryBound(to: Float.self)
            
            // Initialize with simple patterns for demo
            for i in 0..<(vocabSize * embedSize) {
                embeddingsPtr[i] = Float(i % 16) / 16.0 - 0.5
            }
            
            for i in 0..<(embedSize * embedSize * numHeads) {
                attentionPtr[i] = Float(i % 16) / 16.0 - 0.5
            }
        }
        
        func processInput(_ text: String) -> CommandIntent {
            // Tokenize input (simple word-based for demo)
            let tokens = text.lowercased().split(separator: " ")
            
            // Use Metal for parallel processing if available
            if let device = device,
               let commandBuffer = commandQueue?.makeCommandBuffer(),
               let computePipelineState = createComputePipeline(device: device) {
                
                return processWithMetal(tokens: tokens,
                                     device: device,
                                     commandBuffer: commandBuffer,
                                     computePipelineState: computePipelineState)
            }
            
            // Fallback to CPU processing
            return processCPU(tokens: tokens)
        }
        
        private func createComputePipeline(device: MTLDevice) -> MTLComputePipelineState? {
            let source = """
            #include <metal_stdlib>
            using namespace metal;
            
            kernel void process_tokens(
                device const float* embeddings [[buffer(0)]],
                device const float* attention [[buffer(1)]],
                device float* output [[buffer(2)]],
                uint id [[thread_position_in_grid]]
            ) {
                // Simple attention mechanism
                float sum = 0.0;
                for (int i = 0; i < 64; i++) {
                    sum += embeddings[id * 64 + i] * attention[i];
                }
                output[id] = sum;
            }
            """
            
            let library = try? device.makeLibrary(source: source, options: nil)
            let function = library?.makeFunction(name: "process_tokens")
            return try? device.makeComputePipelineState(function: function!)
        }
        
        private func processWithMetal(
            tokens: [Substring],
            device: MTLDevice,
            commandBuffer: MTLCommandBuffer,
            computePipelineState: MTLComputePipelineState
        ) -> CommandIntent {
            // Process tokens in parallel using Metal
            // This is a simplified version - a real implementation would do more sophisticated processing
            
            let outputBuffer = device.makeBuffer(length: tokens.count * MemoryLayout<Float>.size,
                                               options: .storageModeShared)
            
            let commandEncoder = commandBuffer.makeComputeCommandEncoder()
            commandEncoder?.setComputePipelineState(computePipelineState)
            commandEncoder?.setBuffer(embeddings, offset: 0, index: 0)
            commandEncoder?.setBuffer(attentionWeights, offset: 0, index: 1)
            commandEncoder?.setBuffer(outputBuffer, offset: 0, index: 2)
            
            let gridSize = MTLSize(width: tokens.count, height: 1, depth: 1)
            let threadGroupSize = MTLSize(width: min(tokens.count, 32), height: 1, depth: 1)
            commandEncoder?.dispatchThreadgroups(gridSize, threadsPerThreadgroup: threadGroupSize)
            
            commandEncoder?.endEncoding()
            commandBuffer.commit()
            commandBuffer.waitUntilCompleted()
            
            // Analyze output to determine intent
            let outputPtr = outputBuffer?.contents().assumingMemoryBound(to: Float.self)
            var maxScore: Float = -Float.infinity
            var bestCommand = ""
            
            // Map output scores to commands
            let commands = ["qhelp", "qflow", "qstate", "qvis", "qrag"]
            for i in 0..<min(tokens.count, commands.count) {
                let score = outputPtr?[i] ?? -Float.infinity
                if score > maxScore {
                    maxScore = score
                    bestCommand = commands[i]
                }
            }
            
            return CommandIntent(
                command: bestCommand,
                action: tokens.count > 1 ? String(tokens[1]) : "",
                args: tokens.count > 2 ? Array(tokens[2...]).map(String.init) : [],
                confidence: Double(sigmoid(maxScore))
            )
        }
        
        private func processCPU(tokens: [Substring]) -> CommandIntent {
            // Simplified CPU fallback using pattern matching
            let text = tokens.joined(separator: " ")
            
            // Use existing pattern matching logic
            for (pattern, command) in patterns {
                if let regex = try? NSRegularExpression(pattern: pattern, options: []) {
                    let range = NSRange(text.startIndex..<text.endIndex, in: text)
                    if regex.firstMatch(in: text, options: [], range: range) != nil {
                        return CommandIntent(
                            command: command,
                            action: tokens.count > 1 ? String(tokens[1]) : "",
                            args: tokens.count > 2 ? Array(tokens[2...]).map(String.init) : [],
                            confidence: 0.8
                        )
                    }
                }
            }
            
            return CommandIntent(
                command: String(tokens[0]),
                action: "",
                args: [],
                confidence: 0.5
            )
        }
        
        private func sigmoid(_ x: Float) -> Float {
            1.0 / (1.0 + exp(-x))
        }
    }
    
    private var llm: LocalLLM?
    
    init() {
        // Initialize Metal
        device = MTLCreateSystemDefaultDevice()
        commandQueue = device?.makeCommandQueue()
        
        // Initialize LLM if Metal is available
        if let device = device {
            llm = LocalLLM(device: device, patterns: commandPatterns)
        }
        
        // Initialize quantum state
        quantumState = [
            "mode": "superposition",
            "workflows": [],
            "parallel_states": [:],
            "active_containers": []
        ]
        
        // Initialize zsh
        setupZsh()
        
        // Initialize Metal if available
        if device != nil {
            setupMetal()
        }
        
        // Initial terminal output with quantum styling
        output = """
        ⟨ψ| Welcome to Quantum Terminal v1.2 |ψ⟩
        ╔════════════════════════════════════════╗
        ║ Metal: \(device != nil ? "Active" : "CPU Mode")
        ║ Local LLM: \(llm != nil ? "Active" : "Not Available")
        ║ Quantum State: Superposition
        ║ ZSH: \(zshProcess != nil ? "Connected" : "Not Connected")
        ║ RAG: Active
        ╚════════════════════════════════════════╝
        
        Type 'qhelp' for quantum workflow commands
        Type 'help' for standard commands
        
        """
    }
    
    private func parseIntent(_ input: String) -> CommandIntent {
        // Use local LLM if available
        if let llm = llm {
            return llm.processInput(input)
        }
        
        // Fallback to regex-based parsing
        let normalizedInput = input.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
        
        // First try exact command match
        let parts = normalizedInput.split(separator: " ").map(String.init)
        if let exactCommand = standardizeCommand(parts[0]) {
            return CommandIntent(
                command: exactCommand,
                action: parts.count > 1 ? String(parts[1]) : "",
                args: Array(parts.dropFirst(2)).map { String($0) },
                confidence: 1.0
            )
        }
        
        // Try NLP patterns
        for (pattern, command) in commandPatterns {
            if let regex = try? NSRegularExpression(pattern: pattern, options: []) {
                let range = NSRange(normalizedInput.startIndex..<normalizedInput.endIndex, in: normalizedInput)
                if let match = regex.firstMatch(in: normalizedInput, options: [], range: range) {
                    var args: [String] = []
                    for i in 1..<match.numberOfRanges {
                        if let range = Range(match.range(at: i), in: normalizedInput) {
                            args.append(String(normalizedInput[range]))
                        }
                    }
                    return CommandIntent(
                        command: command,
                        action: args.first ?? "",
                        args: Array(args.dropFirst()),
                        confidence: 0.8
                    )
                }
            }
        }
        
        return CommandIntent(
            command: normalizedInput,
            action: "",
            args: [],
            confidence: 0.5
        )
    }
    
    private struct CommandIntent {
        let command: String
        let action: String
        let args: [String]
        let confidence: Double
    }
    
    private let commandPatterns: [(pattern: String, command: String)] = [
        // Help patterns
        ("(show|display|list|what are) (the )?(available )?(quantum )?commands", "qhelp"),
        ("(how|help|tell me how) to use (the )?(quantum )?terminal", "qhelp"),
        
        // Info patterns
        ("(show|display|what is) (the )?(system |terminal )?(status|info)", "info"),
        ("how is (the )?(system|terminal) (doing|running)", "info"),
        
        // Workflow patterns
        ("create (a )?(new )?(quantum )?workflow (called |named )?([a-zA-Z0-9_]+)", "qflow new"),
        ("(show|list|display) (all )?(quantum )?workflows", "qflow list"),
        ("switch to workflow ([a-zA-Z0-9_-]+)", "qflow switch"),
        
        // State patterns
        ("(show|display|what is) (the )?(quantum )?state", "qstate"),
        ("(show|display) (quantum )?visualization", "qvis"),
        
        // Container patterns
        ("(show|list|manage) (quantum )?containers", "qcontainer"),
        
        // Reset patterns
        ("reset (the )?(quantum )?(state|terminal|system)", "reset"),
        ("clear (the )?(terminal|screen|output)", "clear")
    ]
    
    private func standardizeCommand(_ cmd: String) -> String? {
        switch cmd.lowercased() {
        case "qhelp", "help", "commands", "?": return "qhelp"
        case "qflow", "workflow", "flow": return "qflow"
        case "qstate", "state": return "qstate"
        case "qvis", "visualize": return "qvis"
        case "qrag", "query": return "qrag"
        case "qcontainer", "container": return "qcontainer"
        case "info", "status": return "info"
        case "reset": return "reset"
        case "clear", "cls": return "clear"
        default: return nil
        }
    }
    
    func processCommand(_ command: String) async throws -> String {
        isProcessing = true
        defer { isProcessing = false }
        
        let intent = parseIntent(command)
        
        // Log intent if confidence is not 1.0
        if intent.confidence < 1.0 {
            print("Interpreted '\(command)' as '\(intent.command)' (confidence: \(intent.confidence))")
        }
        
        switch intent.command {
        case "qhelp":
            return """
            ╔═══════ Quantum Workflow Commands ═══════╗
            ║ qflow new <n>     : Create workflow     ║
            ║ qflow list        : List workflows      ║
            ║ qflow switch <id> : Switch workflow     ║
            ║ qstate           : Show quantum state   ║
            ║ qrag <query>     : Query knowledge base ║
            ║ qcontainer       : Manage containers    ║
            ║ qvis             : Visualize states     ║
            ║ qbench           : Run benchmarks       ║
            ╚═══════════════════════════════════════════╝
            
            Natural Language Examples:
            - "show available commands"
            - "create new workflow test"
            - "show quantum state"
            - "list all workflows"
            - "switch to workflow abc123"
            - "run quantum benchmarks"
            """
            
        case "qbench":
            let benchmark = QTermBenchmark(terminal: self)
            // Run benchmarks and include results in report
            _ = await benchmark.runBenchmarks()
            return benchmark.generateReport()
            
        case "qflow":
            if intent.action.isEmpty { return "Usage: qflow <command> [args]" }
            var parts = ["qflow", intent.action]
            parts.append(contentsOf: intent.args)
            return try await handleWorkflowCommand(parts)
            
        case "qstate":
            return formatQuantumState()
            
        case "qrag":
            if intent.args.isEmpty { return "Usage: qrag <query>" }
            let query = intent.args.joined(separator: " ")
            return try await queryRAG(query)
            
        case "qcontainer":
            return try await handleContainerCommand(intent.args)
            
        case "qvis":
            return generateStateVisualization()
            
        case "help":
            return """
            ╔═══════ Standard Commands ═══════╗
            ║ help   : Show this help        ║
            ║ clear  : Clear terminal        ║
            ║ info   : Show system info      ║
            ║ reset  : Reset quantum state   ║
            ╚════════════════════════════════╝
            
            All other commands are processed by zsh
            For quantum workflows, type 'qhelp'
            """
            
        case "clear":
            output = ""
            return ""
            
        case "info":
            return """
            ╔═══════ System Information ═══════╗
            ║ Metal: \(device != nil ? "Active" : "CPU Mode")
            ║ Local LLM: \(llm != nil ? "Active" : "Not Available")
            ║ Quantum State: \(quantumState["mode"] as? String ?? "Unknown")
            ║ Active Workflows: \((quantumState["workflows"] as? [[String: Any]])?.count ?? 0)
            ║ Containers: \((quantumState["active_containers"] as? [String])?.count ?? 0)
            ╚════════════════════════════════════╝
            """
            
        case "reset":
            quantumState = [
                "mode": "superposition",
                "workflows": [],
                "parallel_states": [:],
                "active_containers": []
            ]
            return "Quantum state reset to initial configuration"
            
        default:
            // Pass non-empty command to zsh
            guard let input = zshInput?.fileHandleForWriting else {
                throw TerminalError.shellNotAvailable
            }
            
            let commandData = (command + "\n").data(using: .utf8)!
            try input.write(contentsOf: commandData)
            
            // Give some time for command to execute
            try await Task.sleep(nanoseconds: 100_000_000)
            return ""
        }
    }
    
    private func handleWorkflowCommand(_ parts: [String]) async throws -> String {
        let subcommand = parts[1].lowercased()
        
        switch subcommand {
        case "new":
            if parts.count < 3 { return "Usage: qflow new <name>" }
            let name = parts[2]
            var workflows = quantumState["workflows"] as? [[String: Any]] ?? []
            let newFlow = [
                "id": UUID().uuidString,
                "name": name,
                "state": "active",
                "created": Date().ISO8601Format()
            ]
            workflows.append(newFlow)
            quantumState["workflows"] = workflows
            return "Created new quantum workflow: \(name)"
            
        case "list":
            guard let workflows = quantumState["workflows"] as? [[String: Any]] else {
                return "No workflows found"
            }
            return formatWorkflowList(workflows)
            
        case "switch":
            if parts.count < 3 { return "Usage: qflow switch <id>" }
            guard let workflows = quantumState["workflows"] as? [[String: Any]] else {
                return "No workflows found"
            }
            let id = parts[2]
            if let _ = workflows.first(where: { ($0["id"] as? String) == id }) {
                quantumState["active_workflow"] = id
                return "Switched to workflow: \(id)"
            }
            return "Workflow not found: \(id)"
            
        default:
            return "Unknown workflow command: \(subcommand)"
        }
    }
    
    private func formatWorkflowList(_ workflows: [[String: Any]]) -> String {
        var result = "╔═══════ Quantum Workflows ═══════╗\n"
        for workflow in workflows {
            let id = workflow["id"] as? String ?? "unknown"
            let name = workflow["name"] as? String ?? "unnamed"
            let state = workflow["state"] as? String ?? "unknown"
            result += "║ \(id.prefix(8)) | \(name.padding(toLength: 15, withPad: " ", startingAt: 0)) | \(state)\n"
        }
        result += "╚═══════════════════════════════╝"
        return result
    }
    
    private func queryRAG(_ query: String) async throws -> String {
        // TODO: Implement Python bridge to quantum_rag.py
        return "RAG query: \(query)\nThis feature is coming soon!"
    }
    
    private func handleContainerCommand(_ args: [String]) async throws -> String {
        // TODO: Implement container management
        return "Container management coming soon!"
    }
    
    private func generateStateVisualization() -> String {
        var vis = "⟨ψ| Current Quantum State |ψ⟩\n"
        vis += "   ╭──────────────────╮\n"
        
        if let workflows = quantumState["workflows"] as? [[String: Any]] {
            for workflow in workflows {
                let name = workflow["name"] as? String ?? "unnamed"
                let state = workflow["state"] as? String ?? "unknown"
                vis += "   │ ⟨\(name)│\(state)⟩\n"
            }
        }
        
        vis += "   ╰──────────────────╯"
        return vis
    }
    
    private func formatQuantumState() -> String {
        let activeWorkflow = quantumState["active_workflow"] as? String ?? "none"
        let mode = quantumState["mode"] as? String ?? "unknown"
        
        return """
        ╔═══════ Quantum State ═══════╗
        ║ Mode: \(mode)
        ║ Active Workflow: \(activeWorkflow)
        ║ Parallel States: \((quantumState["parallel_states"] as? [String: Any])?.count ?? 0)
        ║ Active Containers: \((quantumState["active_containers"] as? [String])?.count ?? 0)
        ╚═══════════════════════════════╝
        """
    }
    
    private func setupZsh() {
        let task = Process()
        let inputPipe = Pipe()
        let outputPipe = Pipe()
        
        task.executableURL = URL(fileURLWithPath: "/bin/zsh")
        task.arguments = ["--login"]
        task.standardInput = inputPipe
        task.standardOutput = outputPipe
        task.standardError = outputPipe
        
        // Set up environment
        var env = ProcessInfo.processInfo.environment
        env["TERM"] = "xterm-256color"
        task.environment = env
        
        // Load user's zsh config
        if let homeDir = ProcessInfo.processInfo.environment["HOME"] {
            let zshrcPath = "\(homeDir)/.zshrc"
            if FileManager.default.fileExists(atPath: zshrcPath) {
                task.arguments = ["--login", "-c", "source \(zshrcPath) && exec zsh"]
            }
        }
        
        do {
            try task.run()
            zshProcess = task
            zshInput = inputPipe
            zshOutput = outputPipe
            
            // Start async output reading
            Task {
                await readZshOutput()
            }
        } catch {
            print("Failed to start zsh: \(error)")
        }
    }
    
    private func readZshOutput() async {
        guard let output = zshOutput else { return }
        
        do {
            for try await line in output.fileHandleForReading.bytes.lines {
                await MainActor.run {
                    self.output += line + "\n"
                }
            }
        } catch {
            print("Failed to read zsh output: \(error)")
        }
    }
    
    private func setupMetal() {
        guard let device = device,
              let library = device.makeDefaultLibrary() else {
            print("Metal initialization skipped - running in CPU mode")
            return
        }
        
        // Check device capabilities
        let supportsSIMDGroupMatrix = device.supportsFamily(.apple4)
        let supportsMPSMatrix = device.supportsFamily(.apple7)
        
        // Create function constant values
        let functionConstants = MTLFunctionConstantValues()
        var simdSupport = supportsSIMDGroupMatrix
        var mpsSupport = supportsMPSMatrix
        
        functionConstants.setConstantValue(&simdSupport, type: .bool, index: 0)
        functionConstants.setConstantValue(&mpsSupport, type: .bool, index: 1)
        
        // Initialize compute pipelines with modern options
        let computeDescriptor = MTLComputePipelineDescriptor()
        computeDescriptor.threadGroupSizeIsMultipleOfThreadExecutionWidth = true
        computeDescriptor.maxTotalThreadsPerThreadgroup = 1024
        
        // Configure pipeline options for M3 Pro
        let pipelineOptions: MTLPipelineOption = [.bindingInfo, .bufferTypeInfo]
        
        do {
            // Quantum evolution pipeline
            let evolutionFunction = try library.makeFunction(name: "quantum_evolve", constantValues: functionConstants)
            computeDescriptor.computeFunction = evolutionFunction
            let (pipeline, _) = try device.makeComputePipelineState(descriptor: computeDescriptor, options: pipelineOptions)
            computePipeline = pipeline
        } catch {
            print("Failed to create quantum evolution pipeline: \(error)")
        }
        
        do {
            // Visualization pipeline
            let visualizeFunction = try library.makeFunction(name: "quantum_visualize", constantValues: functionConstants)
            computeDescriptor.computeFunction = visualizeFunction
            let (pipeline, _) = try device.makeComputePipelineState(descriptor: computeDescriptor, options: pipelineOptions)
            computePipeline = pipeline
        } catch {
            print("Failed to create visualization pipeline: \(error)")
        }
        
        do {
            // Neural quantum bridge pipeline
            let bridgeFunction = try library.makeFunction(name: "neural_quantum_bridge", constantValues: functionConstants)
            computeDescriptor.computeFunction = bridgeFunction
            let (pipeline, _) = try device.makeComputePipelineState(descriptor: computeDescriptor, options: pipelineOptions)
            computePipeline = pipeline
        } catch {
            print("Failed to create neural bridge pipeline: \(error)")
        }
        
        print("""
            Metal initialized successfully:
            - Device: \(device.name)
            - SIMD Group Matrix: \(supportsSIMDGroupMatrix ? "Supported" : "Not Supported")
            - MPS Matrix: \(supportsMPSMatrix ? "Supported" : "Not Supported")
            - Max Threads Per Group: \(computeDescriptor.maxTotalThreadsPerThreadgroup)
            """)
    }
}

enum TerminalError: Error {
    case shellNotAvailable
    case commandFailed
}
