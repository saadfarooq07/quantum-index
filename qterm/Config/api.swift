import Foundation

enum APIConfig {
    static let deepseekAPIKey = "sk-29610c47c02d4d53a0e3031dd1da64c1"
    static let deepseekEndpoint = "https://api.deepseek.com/v1"
    
    static var headers: [String: String] {
        [
            "Authorization": "Bearer \(deepseekAPIKey)",
            "Content-Type": "application/json"
        ]
    }
}
