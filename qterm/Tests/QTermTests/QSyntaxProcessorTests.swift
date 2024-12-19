import XCTest
@testable import QTermCore

class QSyntaxProcessorTests: XCTestCase {
    var processor: QSyntaxProcessor!
    
    override func setUp() {
        super.setUp()
        processor = try! QSyntaxProcessor()
    }
    
    // MARK: - Basic Syntax Tests
    
    func testBasicQuantumSyntax() throws {
        // Test basic {{..}} pattern
        let input = "{{..Hello Quantum..}}"
        let result = try processor.processQuantumSyntax(input)
        
        XCTAssertEqual(result.content, "Hello Quantum")
        XCTAssertGreaterThan(result.realityScore, 0.9)
    }
    
    func testNestedQuantumSyntax() throws {
        // Test nested {{..{{..}}..}} pattern
        let input = "{{..Outer{{..Inner..}}End..}}"
        let result = try processor.processQuantumSyntax(input)
        
        XCTAssertEqual(result.content, "OuterInnerEnd")
        XCTAssertGreaterThan(result.realityScore, 0.8)
    }
    
    func testParallelQuantumBlocks() throws {
        // Test parallel {{..}} {{..}} patterns
        let input = "{{..First..}} {{..Second..}}"
        let result = try processor.processQuantumSyntax(input)
        
        XCTAssertTrue(result.content.contains("First"))
        XCTAssertTrue(result.content.contains("Second"))
    }
    
    // MARK: - Reality Anchoring Tests
    
    func testRealityScoring() throws {
        // Test reality score calculation
        let input = "{{..Reality Test..}}"
        let result = try processor.processQuantumSyntax(input)
        
        XCTAssertGreaterThanOrEqual(result.realityScore, 0.0)
        XCTAssertLessThanOrEqual(result.realityScore, 1.0)
    }
    
    func testLowRealityScore() throws {
        // Test handling of low reality scores
        let input = "{{..}}" // Empty content should have low reality
        XCTAssertThrowsError(try processor.processQuantumSyntax(input)) { error in
            XCTAssertTrue(error is QuantumError)
        }
    }
    
    // MARK: - Context Tests
    
    func testContextPreservation() throws {
        // Test context preservation across blocks
        let input = """
        {{..First Block..}}
        {{..Second Block with context..}}
        """
        let result = try processor.processQuantumSyntax(input)
        
        XCTAssertTrue(result.content.contains("First Block"))
        XCTAssertTrue(result.content.contains("Second Block"))
    }
    
    func testContextualRelationships() throws {
        // Test relationships between quantum blocks
        let input = """
        {{..Parent..}}
        {{..{{..Child..}}..}}
        """
        let result = try processor.processQuantumSyntax(input)
        
        XCTAssertTrue(result.content.contains("Parent"))
        XCTAssertTrue(result.content.contains("Child"))
    }
    
    // MARK: - Error Handling Tests
    
    func testUnbalancedBraces() {
        // Test handling of unbalanced braces
        let input = "{{..Unbalanced"
        XCTAssertThrowsError(try processor.processQuantumSyntax(input))
    }
    
    func testInvalidNesting() {
        // Test handling of invalid nesting
        let input = "{{..}}}.."
        XCTAssertThrowsError(try processor.processQuantumSyntax(input))
    }
    
    // MARK: - Performance Tests
    
    func testProcessingPerformance() throws {
        // Test processing performance
        measure {
            let input = String(repeating: "{{..Performance..}}", count: 100)
            XCTAssertNoThrow(try processor.processQuantumSyntax(input))
        }
    }
    
    func testNestedProcessingPerformance() throws {
        // Test nested processing performance
        measure {
            let input = String(repeating: "{{..Outer{{..Inner..}}..}}", count: 50)
            XCTAssertNoThrow(try processor.processQuantumSyntax(input))
        }
    }
    
    // MARK: - Integration Tests
    
    func testIntegrationWithStateManager() throws {
        // Test integration with quantum state manager
        let input = """
        {{..First State..}}
        {{..Second State..}}
        {{..{{..Nested State..}}..}}
        """
        let result = try processor.processQuantumSyntax(input)
        
        XCTAssertTrue(result.quantum.isValid)
        XCTAssertGreaterThan(result.realityScore, 0.7)
    }
    
    func testIntegrationWithMetalCompute() throws {
        // Test Metal acceleration integration
        let input = String(repeating: "{{..Metal Test..}}", count: 1000)
        let startTime = CFAbsoluteTimeGetCurrent()
        let result = try processor.processQuantumSyntax(input)
        let duration = CFAbsoluteTimeGetCurrent() - startTime
        
        XCTAssertLessThan(duration, 1.0) // Should process in under 1 second
        XCTAssertGreaterThan(result.realityScore, 0.8)
    }
}

// MARK: - Test Helpers

extension QuantumVector {
    var isValid: Bool {
        coherence >= 0 && coherence <= 1 &&
        realityScore >= 0 && realityScore <= 1
    }
}
