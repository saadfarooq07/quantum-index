import XCTest
@testable import QTermCore

class QWorkflowProcessorTests: XCTestCase {
    var processor: QWorkflowProcessor!
    
    override func setUp() {
        super.setUp()
        processor = try! QWorkflowProcessor()
    }
    
    // MARK: - Basic Workflow Tests
    
    func testBasicWorkflow() throws {
        // Test basic workflow command
        let input = "<qRebirth>..{qScaffold}...}}"
        let result = try processor.processWorkflow(input)
        
        XCTAssertTrue(result.workflow.contains("qRebirth"))
        XCTAssertTrue(result.workflow.contains("qScaffold"))
        XCTAssertGreaterThan(result.realityScore, 0.9)
    }
    
    func testMultipleCommands() throws {
        // Test multiple commands
        let input = "<qInit><qSetup>..{qBuild}{qTest}...}}"
        let result = try processor.processWorkflow(input)
        
        XCTAssertTrue(result.workflow.contains("qInit"))
        XCTAssertTrue(result.workflow.contains("qSetup"))
        XCTAssertTrue(result.workflow.contains("qBuild"))
        XCTAssertTrue(result.workflow.contains("qTest"))
    }
    
    // MARK: - Reality Tests
    
    func testRealityScoring() throws {
        // Test reality score calculation
        let input = "<qTest>..{qValidate}...}}"
        let result = try processor.processWorkflow(input)
        
        XCTAssertGreaterThanOrEqual(result.realityScore, 0.0)
        XCTAssertLessThanOrEqual(result.realityScore, 1.0)
    }
    
    func testLowRealityScore() throws {
        // Test handling of low reality scores
        let input = "<>..{}...}}" // Empty command should have low reality
        XCTAssertThrowsError(try processor.processWorkflow(input)) { error in
            XCTAssertTrue(error is QuantumError)
        }
    }
    
    // MARK: - Quantum Graph Tests
    
    func testGraphCoherence() throws {
        // Test quantum graph coherence
        let inputs = [
            "<qA>..{qX}...}}",
            "<qA>..{qY}...}}",
            "<qB>..{qX}...}}"
        ]
        
        var lastResult: WorkflowResult?
        
        for input in inputs {
            let result = try processor.processWorkflow(input)
            if let last = lastResult {
                XCTAssertNotEqual(result.confidence, last.confidence)
            }
            lastResult = result
        }
    }
    
    // MARK: - Error Handling Tests
    
    func testInvalidCommand() {
        // Test handling of invalid commands
        let input = "invalid"
        XCTAssertThrowsError(try processor.processWorkflow(input))
    }
    
    func testUnbalancedBrackets() {
        // Test handling of unbalanced brackets
        let input = "<qTest>..{qValidate..."
        XCTAssertThrowsError(try processor.processWorkflow(input))
    }
    
    // MARK: - Performance Tests
    
    func testProcessingPerformance() throws {
        // Test processing performance
        measure {
            let input = "<qPerf>..{qTest}...}}"
            XCTAssertNoThrow(try processor.processWorkflow(input))
        }
    }
    
    func testBatchProcessing() throws {
        // Test batch processing performance
        measure {
            let inputs = (0..<100).map { _ in "<qBatch>..{qProc}...}}" }
            for input in inputs {
                XCTAssertNoThrow(try processor.processWorkflow(input))
            }
        }
    }
    
    // MARK: - Integration Tests
    
    func testIntegrationWithStateManager() throws {
        // Test integration with quantum state manager
        let input = """
        <qInit>..{qSetup}...}}
        <qBuild>..{qTest}...}}
        <qDeploy>..{qMonitor}...}}
        """
        let commands = input.components(separatedBy: .newlines)
        
        for command in commands {
            let result = try processor.processWorkflow(command)
            XCTAssertGreaterThan(result.confidence, 0.7)
        }
    }
    
    func testIntegrationWithMetalCompute() throws {
        // Test Metal acceleration integration
        let input = String(repeating: "<qMetal>..{qAccel}...}}", count: 1000)
        let startTime = CFAbsoluteTimeGetCurrent()
        let result = try processor.processWorkflow(input)
        let duration = CFAbsoluteTimeGetCurrent() - startTime
        
        XCTAssertLessThan(duration, 1.0) // Should process in under 1 second
        XCTAssertGreaterThan(result.realityScore, 0.8)
    }
}
