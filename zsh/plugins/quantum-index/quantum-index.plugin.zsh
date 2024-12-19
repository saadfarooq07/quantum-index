# quantum-index plugin main file

# Source functions and hooks
PLUGIN_DIR=${0:A:h}
source "$PLUGIN_DIR/quantum_functions.zsh"
source "$PLUGIN_DIR/warp_hooks.zsh"

# Ensure quantum tools are in PATH if installed in custom location
if [[ -d "$HOME/.quantum/bin" ]]; then
export PATH="$HOME/.quantum/bin:$PATH"
fi

# Optional aliases
alias qc='qcheck'
alias qcl='qclean'
alias qn='qnap'
alias qt='qterm'

# Configure q0rtex backend settings
export Q0RTEX_ENABLE_ML=true
export Q0RTEX_ML_MODELS="vectorized-metal-neural-embeddings"
export Q0RTEX_VECTOR_DB_IMPL="milvus"

# Initialize qterm if dependencies are available
if command -v qterm >/dev/null 2>&1; then
    # Set up ML chain configuration
    export QTERM_ML_CHAIN_CONFIG="${QTERM_ML_CHAIN_CONFIG:-${HOME}/.config/qterm/mlchain.yaml}"
    
    # Configure backend defaults
    export QTERM_DEFAULT_BACKEND="q0rtex"
    export QTERM_ENABLE_WARP_INTEGRATION=true
fi
