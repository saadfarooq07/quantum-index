# Wrapper function for qcheck
function qcheck() {
local usage="Usage: qcheck [-h|--help] [path]
Check quantum-index status for a repository or path

Arguments:
    path    Optional path to check (default: current directory)
Options:
    -h, --help    Show this help message"

# Handle help flag
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    echo "$usage"
    return 0
fi

# Pass through all arguments to qcheck
command qcheck "$@"
}

# Wrapper function for qclean
function qclean() {
local usage="Usage: qclean [-h|--help] [-f|--force] [path]
Clean quantum-index data for a repository

Arguments:
    path    Optional path to clean (default: current directory)
Options:
    -f, --force   Force clean without confirmation
    -h, --help    Show this help message"

if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    echo "$usage"
    return 0
fi

command qclean "$@"
}

# Wrapper function for qnap
function qnap() {
local usage="Usage: qnap [-h|--help] [-p|--parallel] [path]
Generate quantum-index snapshots for repositories

Arguments:
    path    Optional path to snapshot (default: current directory)
Options:
    -p, --parallel    Process multiple repositories in parallel
    -h, --help        Show this help message"

if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    echo "$usage"
    return 0
fi

command qnap "$@"
}

# Wrapper function for qterm
function qterm() {
    local usage="Usage: qterm [-h|--help] [-b|--backend NAME] [query]
Interactive quantum terminal with ML-powered assistance

Arguments:
    query    Optional initial query to process
Options:
    -b, --backend    Specify backend (default: q0rtex)
    -h, --help       Show this help message"

    if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        echo "$usage"
        return 0
    fi

    # Initialize vector DB connection
    if ! _qterm_init_vector_db; then
        echo "Error: Failed to initialize vector database connection"
        return 1
    fi

    # Parse backend option
    local backend="q0rtex"
    if [[ "$1" == "-b" ]] || [[ "$1" == "--backend" ]]; then
        backend="$2"
        shift 2
    fi

    # Configure ML chain settings
    export QTERM_ML_CHAIN=nlp,vision,reasoning
    export QTERM_BACKEND=${backend}

    command qterm "$@"
}

# Internal function to initialize vector database
function _qterm_init_vector_db() {
    if ! command -v milvus-client >/dev/null 2>&1; then
        echo "Error: Milvus client not found"
        return 1
    fi

    # Configure vector database settings
    export QTERM_VECTOR_DB=milvus
    export QTERM_VECTOR_DB_HOST=${QTERM_VECTOR_DB_HOST:-localhost}
    export QTERM_VECTOR_DB_PORT=${QTERM_VECTOR_DB_PORT:-19530}

    return 0
}
