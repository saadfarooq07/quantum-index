import Foundation

/// QGitWorkflow - Quantum-aware Git workflow manager
public class QGitWorkflow {
    // MARK: - Properties
    private let workingDirectory: String
    private var currentBranch: String?
    private var stateCache: [String: String] = [:]
    
    // MARK: - Initialization
    public init(workingDirectory: String) throws {
        self.workingDirectory = workingDirectory
        try refreshCurrentBranch()
    }
    
    // MARK: - Branch Management
    private func refreshCurrentBranch() throws {
        let pipe = Pipe()
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/git")
        process.arguments = ["rev-parse", "--abbrev-ref", "HEAD"]
        process.currentDirectoryURL = URL(fileURLWithPath: workingDirectory)
        process.standardOutput = pipe
        try process.run()
        process.waitUntilExit()
        
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        currentBranch = String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines)
    }
    
    /// Check if branch exists
    public func branchExists(_ branch: String) throws -> Bool {
        let pipe = Pipe()
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/git")
        process.arguments = ["branch", "--list", branch]
        process.currentDirectoryURL = URL(fileURLWithPath: workingDirectory)
        process.standardOutput = pipe
        try process.run()
        process.waitUntilExit()
        
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        let output = String(data: data, encoding: .utf8) ?? ""
        return !output.isEmpty
    }
    
    /// Safely switch or create branch
    public func switchBranch(_ branch: String, createIfNeeded: Bool = true) throws {
        // Cache current state
        try cacheCurrentState()
        
        // Check if branch exists
        if try branchExists(branch) {
            let process = Process()
            process.executableURL = URL(fileURLWithPath: "/usr/bin/git")
            process.arguments = ["checkout", branch]
            process.currentDirectoryURL = URL(fileURLWithPath: workingDirectory)
            try process.run()
            process.waitUntilExit()
        } else if createIfNeeded {
            let process = Process()
            process.executableURL = URL(fileURLWithPath: "/usr/bin/git")
            process.arguments = ["checkout", "-b", branch]
            process.currentDirectoryURL = URL(fileURLWithPath: workingDirectory)
            try process.run()
            process.waitUntilExit()
        } else {
            throw GitError.branchNotFound
        }
        
        try refreshCurrentBranch()
    }
    
    // MARK: - State Management
    private func cacheCurrentState() throws {
        guard let branch = currentBranch else { return }
        
        let pipe = Pipe()
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/git")
        process.arguments = ["rev-parse", "HEAD"]
        process.currentDirectoryURL = URL(fileURLWithPath: workingDirectory)
        process.standardOutput = pipe
        try process.run()
        process.waitUntilExit()
        
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        if let sha = String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) {
            stateCache[branch] = sha
        }
    }
    
    /// Stage and commit changes
    public func commit(message: String) throws {
        // Stage changes
        let stage = Process()
        stage.executableURL = URL(fileURLWithPath: "/usr/bin/git")
        stage.arguments = ["add", "."]
        stage.currentDirectoryURL = URL(fileURLWithPath: workingDirectory)
        try stage.run()
        stage.waitUntilExit()
        
        // Commit with quantum-aware message
        let commit = Process()
        commit.executableURL = URL(fileURLWithPath: "/usr/bin/git")
        commit.arguments = ["commit", "-m", "🧠 \(message)"]
        commit.currentDirectoryURL = URL(fileURLWithPath: workingDirectory)
        try commit.run()
        commit.waitUntilExit()
        
        try refreshCurrentBranch()
    }
    
    /// Push changes safely
    public func push(force: Bool = false) throws {
        guard let branch = currentBranch else {
            throw GitError.noBranchDetected
        }
        
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/git")
        process.arguments = ["push", "origin", branch]
        if force {
            process.arguments?.append("--force")
        }
        process.currentDirectoryURL = URL(fileURLWithPath: workingDirectory)
        try process.run()
        process.waitUntilExit()
    }
    
    // MARK: - Error Handling
    public enum GitError: Error {
        case branchNotFound
        case noBranchDetected
        case pushFailed
        case stateError
    }
}
