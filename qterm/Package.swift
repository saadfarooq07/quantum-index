// swift-tools-version: 5.7
import PackageDescription

let package = Package(
    name: "qterm",
    platforms: [
        .macOS(.v13)
    ],
    dependencies: [],
    targets: [
        .executableTarget(
            name: "qterm",
            path: "Sources",
            resources: [
                .process("Resources")
            ]
        )
    ]
)
