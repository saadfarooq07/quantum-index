import Foundation
import MetalKit

struct BenchmarkMetrics {
    var latency: Double // in seconds
    var tokensPerSecond: Double
    var accuracy: Double // percentage
    var memoryUsage: UInt64 // in bytes
    var contextSize: Int
    var confidenceScore: Double
}

struct BenchmarkResult {
    let name: String
    let metrics: BenchmarkMetrics
    let timestamp: Date
    
    var description: String {
        """
        ╔═══════ Benchmark: \(name) ═══════╗
        ║ Latency: \(String(format: "%.3f", metrics.latency))s
        ║ Tokens/s: \(String(format: "%.1f", metrics.tokensPerSecond))
        ║ Accuracy: \(String(format: "%.2f", metrics.accuracy))%
        ║ Memory: \(ByteCountFormatter.string(fromByteCount: Int64(metrics.memoryUsage), countStyle: .memory))
        ║ Context: \(metrics.contextSize) tokens
        ║ Confidence: \(String(format: "%.2f", metrics.confidenceScore))
        ╚════════════════════════════════╝
        """
    }
}

class QTermBenchmark {
    private let terminal: QTerminal
    private let testCases: [(input: String, expected: String)]
    private var results: [BenchmarkResult] = []
    
    init(terminal: QTerminal) {
        self.terminal = terminal
        
        // Standard test cases for NLP understanding
        self.testCases = [
            // MMLU-style command understanding
            ("show me all the quantum workflows", "qflow list"),
            ("I want to create a new workflow called test1", "qflow new test1"),
            ("what's the current state of the quantum system", "qstate"),
            
            // HumanEval-style command variations
            ("display available commands and their usage", "qhelp"),
            ("switch to the workflow with ID abc123", "qflow switch abc123"),
            ("visualize the quantum state please", "qvis"),
            
            // MATH-style numeric handling
            ("create 5 new quantum workflows", "qflow new 5"),
            ("show the last 10 commands", "history 10"),
            ("set quantum state to superposition 0.5", "qstate set 0.5"),
            
            // Multilingual command tests (MGSM-style)
            ("nuevo workflow quantum", "qflow new"),
            ("état quantum actuel", "qstate"),
            ("visualizar estado", "qvis"),
            
            // Tool use proficiency (BFCL-style)
            ("run quantum simulation with parameters alpha=0.5 beta=0.3", "qsim run alpha 0.5 beta 0.3"),
            ("export results to quantum.json", "qexport quantum.json"),
            ("connect to quantum backend at localhost:8080", "qconnect localhost 8080"),
            
            // Reasoning abilities (GPQA-style)
            ("optimize the quantum workflow for better performance", "qflow optimize"),
            ("analyze quantum state entropy", "qstate analyze entropy"),
            ("suggest optimal number of qubits for this workflow", "qflow analyze resources")
        ]
    }
    
    func runBenchmarks() async -> [BenchmarkResult] {
        results = []
        
        // Memory usage before benchmarks
        let startMemory = getMemoryUsage()
        
        // Run latency and throughput tests
        let latencyResult = await measureLatency()
        results.append(latencyResult)
        
        // Run accuracy tests
        let accuracyResult = await measureAccuracy()
        results.append(accuracyResult)
        
        // Run memory and context tests
        let memoryResult = measureMemoryAndContext(startMemory: startMemory)
        results.append(memoryResult)
        
        return results
    }
    
    private func measureLatency() async -> BenchmarkResult {
        var totalLatency = 0.0
        var totalTokens = 0
        
        for testCase in testCases {
            let startTime = DispatchTime.now()
            let tokens = testCase.input.split(separator: " ").count
            
            _ = try? await terminal.processCommand(testCase.input)
            
            let endTime = DispatchTime.now()
            let latency = Double(endTime.uptimeNanoseconds - startTime.uptimeNanoseconds) / 1_000_000_000
            
            totalLatency += latency
            totalTokens += tokens
        }
        
        let avgLatency = totalLatency / Double(testCases.count)
        let tokensPerSecond = Double(totalTokens) / totalLatency
        
        return BenchmarkResult(
            name: "Latency & Throughput",
            metrics: BenchmarkMetrics(
                latency: avgLatency,
                tokensPerSecond: tokensPerSecond,
                accuracy: 0,
                memoryUsage: 0,
                contextSize: totalTokens,
                confidenceScore: 0
            ),
            timestamp: Date()
        )
    }
    
    private func measureAccuracy() async -> BenchmarkResult {
        var correctCount = 0
        var totalConfidence = 0.0
        
        for testCase in testCases {
            if let response = try? await terminal.processCommand(testCase.input) {
                // Check if the command was interpreted correctly
                if response.contains(testCase.expected) {
                    correctCount += 1
                }
                
                // Extract confidence score if available
                if let confidenceRange = response.range(of: "confidence: ([0-9.]+)", options: .regularExpression),
                   let confidence = Double(response[confidenceRange]) {
                    totalConfidence += confidence
                }
            }
        }
        
        let accuracy = Double(correctCount) / Double(testCases.count) * 100
        let avgConfidence = totalConfidence / Double(testCases.count)
        
        return BenchmarkResult(
            name: "Accuracy & Confidence",
            metrics: BenchmarkMetrics(
                latency: 0,
                tokensPerSecond: 0,
                accuracy: accuracy,
                memoryUsage: 0,
                contextSize: 0,
                confidenceScore: avgConfidence
            ),
            timestamp: Date()
        )
    }
    
    private func measureMemoryAndContext(startMemory: UInt64) -> BenchmarkResult {
        let endMemory = getMemoryUsage()
        let memoryUsed = endMemory - startMemory
        
        // Calculate total context size from test cases
        let totalContextSize = testCases.reduce(0) { $0 + $1.input.split(separator: " ").count }
        
        return BenchmarkResult(
            name: "Memory & Context",
            metrics: BenchmarkMetrics(
                latency: 0,
                tokensPerSecond: 0,
                accuracy: 0,
                memoryUsage: memoryUsed,
                contextSize: totalContextSize,
                confidenceScore: 0
            ),
            timestamp: Date()
        )
    }
    
    private func getMemoryUsage() -> UInt64 {
        var info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4
        
        let kerr: kern_return_t = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_,
                         task_flavor_t(MACH_TASK_BASIC_INFO),
                         $0,
                         &count)
            }
        }
        
        return kerr == KERN_SUCCESS ? info.resident_size : 0
    }
    
    func generateReport() -> String {
        var report = """
        ⟨ψ| QTerm Benchmark Report |ψ⟩
        ═══════════════════════════════
        Timestamp: \(Date().ISO8601Format())
        Test Cases: \(testCases.count)
        
        """
        
        for result in results {
            report += "\n" + result.description + "\n"
        }
        
        return report
    }
}
