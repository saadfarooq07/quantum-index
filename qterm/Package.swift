// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "qterm",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .executable(
            name: "qterm",
            targets: ["qterm"]
        ),
        .library(
            name: "QTermCore",
            targets: ["QTermCore"]
        )
    ],
    dependencies: [
        .package(url: "https://github.com/apple/swift-argument-parser", from: "1.2.0"),
        .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0"),
        .package(url: "https://github.com/vapor/vapor.git", from: "4.89.0"),
        .package(url: "https://github.com/apple/swift-numerics", from: "1.0.0")
    ],
    targets: [
        .executableTarget(
            name: "qterm",
            dependencies: [
                "QTermCore",
                .product(name: "ArgumentParser", package: "swift-argument-parser"),
                .product(name: "Logging", package: "swift-log")
            ],
            path: "Sources/qterm"
        ),
        .target(
            name: "QTermCore",
            dependencies: [
                .product(name: "Vapor", package: "vapor"),
                .product(name: "Logging", package: "swift-log"),
                .product(name: "Numerics", package: "swift-numerics")
            ],
            path: "Sources/QTermCore",
            exclude: [
                "QSyntax/README.md",
                ".build/checkouts/swift-algorithms/Sources/Algorithms/Documentation.docc"
            ],
            resources: [
                .copy("Resources"),
                .process("Shaders.metal")
            ]
        ),
        .testTarget(
            name: "QTermTests",
            dependencies: ["QTermCore"],
            path: "Tests/QTermTests"
        )
    ]
)
